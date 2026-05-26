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
simple edit). If you do want more than one sandbox environment, see the
relevant section below.

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
review its implementation and consider alternatives. The recent spate of
disclosed [local](https://copy.fail/)
[privilege](https://github.com/V4bel/dirtyfrag)
[escalation](https://github.com/v12-security/pocs/tree/main/fragnesia)
[vulnerabilities](https://ubuntu.com/blog/pintheft-linux-kernel-vulnerability-mitigation)
is helpful to keep in mind as a reminder of the limits of this namespacing
based approach.

## Usage example

```
$ shandbox run uvx pycowsay
initialised sandbox at /home/asb/sandbox
created default ssh config at /home/asb/sandbox/.ssh/config
to add an init hook, create an executable script at: /home/asb/sandbox/.shandbox_meta/init
started (pid 1589289)
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
$ shandbox add-mount ~/repos/medley
mounted /home/asb/repos/medley -> /home/sandbox/medley
$ shandbox run ls -lh /home/sandbox/medley/README.md
-rw-r--r-- 1 sandbox users 2.7K Feb 11 20:02 /home/sandbox/medley/README.md
$ shandbox run touch /home/sandbox/medley/write-attempt
touch: cannot touch '/home/sandbox/medley/write-attempt': Read-only file system
$ shandbox remove-mount /home/sandbox/medley
unmounted /home/sandbox/medley
$ shandbox add-mount --read-write ~/repos/medley
mounted /home/asb/repos/medley -> /home/sandbox/medley
$ shandbox run touch /home/sandbox/medley/write-attempt
$ shandbox list-mounts
/home/sandbox                /dev/mapper/root[/home/asb/sandbox]
/home/sandbox/medley         /dev/mapper/root[/home/asb/repos/medley]
```


`shandbox enter` will open a shell within the sandbox for easy interactive
usage. As a convenience, if the current working directory is in
`$HOME/sandbox` (e.g. `$HOME/sandbox/foo`) then the working directory within
the sandbox for `shandbox run` or `shandbox enter` will be set to the
appropriate path within the sandbox (`/home/sandbox/foo` in this case). i.e.,
the case where this mapping is trivial. Environment variables are not passed
through.

You can also explicitly control the working directory used by `shandbox run`
or `shandbox enter` by setting `SB_PWD` to an absolute in-sandbox path. If
`SB_PWD` isn't set, paths within the sandbox home are translated to
`/home/sandbox/...`, and some host paths that are directly visible in the
sandbox (such as `/tmp`, `/usr`, `/etc`, and similar) are used as-is.

## Functionality overview

* `shandbox new <dir>`: Initialise a sandbox directory, setting up the
  `.shandbox_meta` layout and a default `.ssh/config` suitable for use with
  `share-ssh`. If `${XDG_CONFIG_HOME:-$HOME/.config}/shandbox/default-init`
  exists it is copied to `.shandbox_meta/init`.
* `shandbox start`: Start the sandbox, creating the necessary namespaces and
  mount layout. Fails if the sandbox is already running. If the selected
  `$SANDBOX_DIR` hasn't been initialised yet, it is initialised first. If
  present, the init script in `.shandbox_meta/init` is always run.
* `shandbox stop`: Stop the sandbox by killing the process holding the
  namespaces. Fails if the sandbox is not running.
* `shandbox status`: Print whether the sandbox is running and if it is, the
  pid. Also print the last 20 lines of the log.
* `shandbox enter`: Open bash within the sandbox, starting the sandbox first
  if it's not already running.
* `shandbox enter-root`: Open bash within the outer "root" namespace. This is
  mostly useful for debugging the namespace or mount layout.
* `shandbox run <command> [args...]`: Run a command inside the sandbox. The
  current working directory is translated to an in-sandbox path when this is
  straightforward, and `SB_PWD` can be used to override it explicitly. Starts
  the sandbox first if it isn't already running.
* `shandbox add-mount [--read-write] <host-path> [<sandbox-path>]`: Bind-mount
  a host path into the running sandbox. Mounts are read-only by default; pass
  `--read-write` to allow writes. The sandbox must already be running. Both
  directories and individual files are supported, and if no sandbox path is
  provided the host path basename is mounted under `/home/sandbox`.
* `shandbox remove-mount <sandbox-path>`: Remove a previously added bind mount
  from the running sandbox.
* `shandbox list-mounts [--all]`: List mounts visible from the sandbox. By
  default this is restricted to mounts under `/home/sandbox`; `--all` shows
  the full namespace mount table.
* `shandbox share-ssh <socket-name> <ssh-target> [ssh args...]`: Expose a
  host-side ssh ControlMaster connection inside the sandbox without copying
  private keys or ssh-agent state into the sandbox. The sandbox directory must
  already have been initialised with `shandbox new`. See below.

## Self-contained sandbox directories

A sandbox is represented by a normal directory, defaulting to `$HOME/sandbox`.
The files visible as `/home/sandbox` live directly in that directory, and
`shandbox`'s own state lives under `.shandbox_meta` inside it. That means a
sandbox is self-contained: you can create another one with `shandbox new
~/other-sandbox`, select it by setting `SANDBOX_DIR` (using the absolute path
it prints, or a shell-expanded path such as `~/other-sandbox`), and it will
have its own root layout, runtime directory, pid files, log, init hook, and
ssh socket directory.

For example:

```sh
$ shandbox new ~/other-sandbox
$ SANDBOX_DIR=~/other-sandbox shandbox run pwd
/home/sandbox
$ shandbox new ~/throwaway-sandbox
$ SANDBOX_DIR=~/throwaway-sandbox shandbox status
stopped
```

Sandboxes in different `SANDBOX_DIR` have independent state and home
directories. The contents of `.shandbox_meta` is hidden from inside the
sandbox by mounting an empty tmpfs over it. I don't personally use separate
sandboxes outside of testing purposes. But it's simple functionality to
provide and it's easy to imagine cases where this is useful.

## Sharing ssh connections

One aspect of this I'm pretty pleased with is the mechanism for exposing an
ssh connection without having to share any key material or password, or set up
credentials specifically for the sandbox. `shandbox share-ssh` will create an
ssh ControlMaster and expose the control socket in the sandbox home directory.
The sandbox can use this connection for as long as that ssh process lives.

e.g.:

```
$ shandbox share-ssh buildbox user@example.com
shandbox share-ssh: connecting (user@example.com) using /home/asb/sandbox/.ssh/sockets/ext%buildbox
shandbox share-ssh: connected
shandbox share-ssh: from inside the sandbox, use ssh ext%buildbox
```

Then from inside the sandbox:

```sh
ssh ext%buildbox
```

The `ext%...` name format is recognised thanks to a config fragment installed
in `~/.ssh/config` within the sandbox.

## Init hooks

The main way of customising sandbox setup outside of hacking on the `shandbox`
script yourself is through an "init script" which will be called for every
`shandbox start` (implicit or explicit). Just place your script in
`.shandbox_meta/init`, and if you want a default one that is copied into that
location for you when creating a new sandbox then put it in
`$XDG_CONFIG_HOME/.shandbox/default-init`.

As the script is executed for each `shandbox start`, you should either ensure
it is idempotent or have it create and check for some marker file so it exits
early for subsequent invocations.

The following environment variables are passed through:

* `SHANDBOX_SELF`: Path to the `shandbox` script being run.
* `SANDBOX_DIR`: The host-side sandbox directory.
* `SB_HOME`: The in-sandbox home path.
* `SB_PATH`: The path used for sandboxed commands.

A trivial example that adds a default mount:

```sh
#!/bin/sh

"$SHANDBOX_SELF" add-mount ~/repos/src src
```

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
  enter the namespace. On newer systems this uses util-linux's `getino` to
  store a pid:inode pid reference while on older systems it stores pid plus
  process start time.
* To help make it easier to tell when you're in the sandbox, a dummy
  `/etc/passwd` is bind-mounted naming the current user as `sandbox`.
* When `shandbox start` is executed, the necessary directories are bind
  mounted in a directory that will be used as root (`/`) for the user sandbox
  in `$SANDBOX_DIR/.shandbox_meta/root`. This happens within the sandbox_root
  namespace, which then uses `unshare` again to create a new user namespace
  with an unprivileged user, executing within a chroot.
* A small private `/dev` is created rather than exposing the host `/dev`
  wholesale. Basic devices such as `/dev/null`, `/dev/zero`, `/dev/random`,
  and `/dev/tty` are provided, along with a private devpts instance.
* 'sandbox_root' retains access to the host filesystem, which is necessary to
  allow mounting additional paths after the fact. Without this requirement, we
  could likely rewrite `shandbox start` to use `pivot_root`.
* The host-side `.shandbox_meta` directory is hidden inside the sandbox by
  mounting an empty unreadable tmpfs over `/home/sandbox/.shandbox_meta`.
* When `/etc/ssh/ssh_config.d` exists, `shandbox` stages a user-owned copy of
  that directory and bind-mounts it over the original inside the sandbox. This
  avoids OpenSSH refusing to process included config snippets that appear as
  owned by `nobody` in the inner user namespace.

## Article changelog
* 2026-05-26: Update article to reflect a wide range of improvements to the script.
  * share-ssh functionality.
  * init hooks
  * Easy to use support for multiple independent sandboxes (with sandbox state
    now localised to a single directory).
  * list-mounts
