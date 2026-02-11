+++
published = 2026-02-11
description = "A simple shared sandbox using unshare+nsenter."
+++

# shandbox

[`shandbox`](https://github.com/muxup/medley/blob/main/shandbox) is a simple
Linux sandboxing script that serves my needs well. Perhaps it works for you
too? No dependencies between a shell and util-linux (`unshare` and `nsenter`).

In short, it aims to provide fairly good isolation for personal files (i.e.
your `$HOME`) while being very convenient for day to day use. It's designed to
be run as an unprivileged user - as long as you can make new namespaces you
should be good to go. By default `/home/youruser/sandbox` shows up as
`/home/sandbox` within the sandbox, and other than standard paths like `/usr`,
`/etc`, `/tmp`, and so on it's left for you to either copy things into the
sandbox or expose them via a mount. There's a single shared sandbox (i.e.
processes within the sandbox can see and interact with each other, and the
exposed sandbox filesystem is shared as well), which trades off some ease of
use for the security you might get with a larger number of more targeted
sandboxes. On the other hand, you only gain security from a sandbox if you
actually use it and this is a setup that offers very low friction for me. The
network is not namespaced (although this is something you could change with a
simple edit).

Usability is both subjective and highly dependent on your actual use case, so
the tradeoffs may or may not align with what is interesting for you!
[Bubblewrap](https://github.com/containers/bubblewrap) is an example of a
mature alternative unprivileged sandboxing
tool that offers a lot of configurability as well as options with greater
degrees of sandboxing. Beyond that, look to
[Firecracker](https://firecracker-microvm.github.io/) based solutions or
[gvisor](https://gvisor.dev/). `shandbox` obviously aims to provide a
reasonable sandbox as much as Linux namespaces alone are able to offer, but if
you're looking for a security property stronger than "makes it harder for
something to edit or access unwanted files" it's down to you to both carefully
review its implementation and consider alternatives.

## Usage example

```
$ shandbox run uvx pycowsay
Installed 1 package in 5ms

  ------------
< Hello, world >
  ------------
   \   ^__^
    \  (oo)\_______
       (__)\       )\/\
           ||----w |
           ||     ||
$ shandbox status
running (pid 1589364)

log:
  2026-02-11 13:02:51 stopped
  2026-02-11 13:05:06 started (pid 1589289)
$ shandbox add-mount ~/repos/llvm-project /home/sandbox/llvm-project
mounted /home/asb/repos/llvm-project -> /home/sandbox/llvm-project
$ shandbox run touch /home/sandbox/llvm-project/write-attempt
touch: cannot touch '/home/sandbox/llvm-project/write-attempt': Read-only file system
$ shandbox remove-mount /home/sandbox/llvm-project
unmounted /home/sandbox/llvm-project
$ shandbox add-mount --read-write ~/repos/llvm-project /home/sandbox/llvm-project
mounted /home/asb/repos/llvm-project -> /home/sandbox/llvm-project
$ shandbox run touch /home/sandbox/llvm-project/write-attempt
```

`shandbox enter` will open a shell within the sandbox for easy interactive
usage. As a convenience, if the current working directory is in
`$HOME/sandbox` (e.g. `$HOME/sandbox/foo`) then the working directory within
the sandbox for `shandbox run` or `shandbox enter` will be set to the
appropriate path within the sandbox (`/home/sandbox/foo` in this case). i.e.,
the case where this mapping is trivial. Environment variables are not passed
through.

## Functionality overview

* `shandbox start`: Start the sandbox, creating the necessary namespaces and
  mount layout. Fails if the sandbox is already running.
* `shandbox stop`: Stop the sandbox by killing the process holding the
  namespaces. Fails if the sandbox is not running.
* `shandbox restart`: Stop the sandbox and start it again.
* `shandbox status`: Print whether the sandbox is running and if it is, the
  pid. Also print the last 20 lines of the log.
* `shandbox enter`: Open bash within the sandbox, starting the sandbox first
  if it's not already running.
* `shandbox run <command> [args...]`: Run a command inside the sandbox. The
  current working directory is translated to an in-sandbox path if it falls
  within the sandbox home directory. Starts the sandbox first if it isn't
  already running.
* `shandbox add-mount [--read-write] <host-path> <sandbox-path>`: Bind-mount a
  host path into the running sandbox. Mounts are read-only by default; pass
  `--read-write` to allow writes. The sandbox must already be running.
  Both directories and individual files are supported.
* `shandbox remove-mount <sandbox-path>`: Remove a previously added bind mount
  from the running sandbox.

## Implementation approach

The core sandboxing functionality is provided by the Linux namespaces
functionality exposed by
[`unshare`](https://manpages.debian.org/unstable/util-linux/unshare.1.en.html)
and
[`nsenter`](https://manpages.debian.org/unstable/util-linux/nsenter.1.en.html).
The [script's
implementation](https://github.com/muxup/medley/blob/main/shandbox) should be
quite readable but I'll try to summarise some key points here.

The goal is that:
* Within the sandbox, you appear as an unprivileged user, with uid and gid
  equal to your usual Linux user.
* It should be possible to expose additional files or directories to the
  sandbox once it's running.
* Applications running within the sandbox have no way (modulo bugs or
  vulnerabilities in the kernel or accessible applications) of reaching files
  on the host filesystem that aren't explicitly exposed.
  * To underline: This is a goal, it is _not_ a guarantee.
* It's possible to launch multiple processes within the sandbox which can all
  see each other, and have the same shared sandboxed filesystem.
* This is all doable as an unprivileged user.

To implement that:
* Two sets of namespaces are used to provide this isolation: the outer
  'shandbox_root' has the user mapped to root within the namespace and retains
  access to standard / (allowing us to mount additional paths into after the
  sandbox has started). The inner 'shandbox_user' represents a new user
  namepsace mapping our uid/gid to an unprivileged user, but other namespaces
  are shared with 'shandbox_root'. Sandboxed processes are launched within the
  namespaces of 'shandbox_user'.
* The process IDs of the initial process within 'sandbox_root' and
  'sandbox_user' are saved and recalled so the script can use `nsenter` to
  enter the namespace.
* To help make it easier to tell when you're in the sandbox, a dummy
  `/etc/passwd` is bind-mounted naming the current user as `sandbox`.
* When `shandbox start` is executed, the necessary directories are bind
  mounted in a directory that will be used as root (`/`) for the user sandbox
  in `.local/share/shandbox/root`. This happens within the sandbox_root
  namespace, which then uses `unshare` again to create a new user namespace
  with an unprivileged user, executing within a chroot.
* 'sandbox_root' retains access to the host filesystem, which is necessary to
  allow mounting additional paths after the fact. Without this requirement, we
  could likely rewrite `shandbox start` to use `pivot_root`.

## Making it your own

The script should be straight-forward enough to customise to your needs if
they're not too dissimilar to what is offered out of the box. Some variables
at the top provide things you may be more likely to want to change, such as
the home directory location, and a list of files or directories in `$HOME` to
always bind-mount into the sandbox home:

```sh
SANDBOX_HOME_DIR="$HOME/sandbox"
HOME_FILES_TO_MAP=".bashrc .vimrc"
HOME_DIRS_TO_MAP=".vim bin"
SB_HOME="/home/sandbox"
SB_PATH="$SB_HOME/bin:/usr/local/bin:/usr/bin"
```
