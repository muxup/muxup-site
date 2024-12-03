+++
published = 2024-12-03
description = "Using debootstrap to make a full rootfs for a different archiecture without root privileges"
+++

# Rootless cross-architecture debootstrap

As usual, let's start by introducing the problem. Suppose you want to produce
either a Debian-derived sysroot for cross-compilation, something you can
chroot into, or even a full image you can boot with QEMU or on real hardware.
[Debootstrap](https://salsa.debian.org/installer-team/debootstrap) can get you
started and has minimal external dependencies. If you wish to avoid using
`sudo`, Running `debootstrap` under `fakeroot` and `fakechroot` works if
building a rootfs for the same architecture as the current host, but it has
problems out of the box for a foreign architecture. These tools are packaged
and in the main repositories for at least Debian, Arch, and Fedora, so a
solution that works without additional dependencies is advantageous.

I'm presenting my preferred solution / approach in the first subheading and
relegating more discussion and background explanation to later on in the
article, in order to cater for those who just want something they can try out
without wading through lots of text.

**Warning**: I haven't found `fakeroot` to be as robust as I would like, even
knowing its fundamental limitations with e.g. statically linked binaries.
Specifically, a sporadically reproducible case involving installing lots of
packages on riscv64 sid resulted in
`/usr/lib/riscv64-linux-gnu/libcbor.so.0.10.2` being given the directory bit
in `fakeroot`'s database (which I haven't yet managed to track down to the
point I can file a useful bug report). I'm sharing this post because the
approach may still be useful to people, especially if you rely on `fakeroot`
for only the minimum needed to get a bootable image in qemu-system.

Not explored in this article: using newuidmap/newgidmap with appropriate
/etc/subuid (see
[here](https://rootlesscontaine.rs/getting-started/common/subuid/)), though
note one-off setup is needed to allow your user to set sufficient UIDs.

## My preferred solution

Assuming you have `debootstrap` and `fakeroot` installed (`sudo pacman -S
debootstrap fakeroot` will suffice on Arch), and to support transparent
emulation of binaries for other architectures you also have user-mode QEMU
installed and set to execute via binfmt_misc (`sudo pacman -S qemu-user-static
qemu-user-static-binfmt` on Arch) we proceed to:

* Do the first stage debootstrap under `fakeroot` on the host, saving the
  state (the uid/gid and permissions set after operations like chown/chmod) to
  a file, and including `fakeroot` in the list of packages to install for the
  target.
* Extract the contents of the fakeroot and libfakeroot `.deb`s into the directory tree
  created by debootstrap directory (as we need to be able to use it as a
  pre-requisite of initiating the second-stage debootstrap which extracts and
  installs all the packages).
* Make use of user namespaces to `chroot` into the debootstrapped sysroot
  without needing root permissions. Then give the illusion of permissions to
  set arbitrary uid/gid and other permissions on files via `fakeroot` (loading
  the environment saved earlier).
* Run the second stage debootstrap.

Translated into shell commands (and later [a
script](https://github.com/muxup/medley/blob/main/rootless-debootstrap-wrapper)),
you can do this by:

```sh
SYSROOT_DIR=sysroot-deb-riscv64-sid
TMP_FAKEROOT_ENV=$(mktemp)
fakeroot -s "$TMP_FAKEROOT_ENV" debootstrap \
  --variant=minbase \
  --include=fakeroot,symlinks \
  --arch=riscv64 --foreign \
  sid \
  "$SYSROOT_DIR"
mv "$TMP_FAKEROOT_ENV" "$SYSROOT_DIR/.fakeroot.env"
fakeroot -i "$SYSROOT_DIR/.fakeroot.env" -s "$SYSROOT_DIR/.fakeroot.env" sh <<EOF
ar p "$SYSROOT_DIR"/var/cache/apt/archives/libfakeroot_*.deb 'data.tar.xz' | tar xv -J -C "$SYSROOT_DIR"
ar p "$SYSROOT_DIR"/var/cache/apt/archives/fakeroot_*.deb 'data.tar.xz' | tar xv -J -C "$SYSROOT_DIR"
ln -s fakeroot-sysv "$SYSROOT_DIR/usr/bin/fakeroot"
EOF
cat <<'EOF' > "$SYSROOT_DIR/_enter"
#!/bin/sh
export PATH=/usr/sbin:$PATH
FAKEROOTDONTTRYCHOWN=1 unshare -fpr --mount-proc -R "$(dirname -- "$0")" \
  fakeroot -i .fakeroot.env -s .fakeroot.env "$@"
EOF
chmod +x "$SYSROOT_DIR/_enter"
"$SYSROOT_DIR/_enter" debootstrap/debootstrap --second-stage
```

You'll note this creates a helper `_enter` within the root of the rootfs for
chrooting into it and executing `fakeroot` with appropriate arguments.

If you want to use this rootfs as a sysroot for cross-compiling, you'll need
to convert any absolute symlinks to relative symlinks so that they resolve
properly when being accessed outside of a chroot. We use the symlinks utility
installed within the target filesystem for this:

```sh
"$SYSROOT_DIR/_enter" symlinks -cr .
```

I've written a slightly more robust and configurable encapsulation of the
above logic in the form of
[rootless-debootstrap-wrapper](https://github.com/muxup/medley/blob/main/rootless-debootstrap-wrapper)
which I would recommend using/adapting in preference to the above. Further
code examples in the rest of this post use the `rootless-debootstrap-wrapper`
script for convenience.

## Further discussion

Depending on how you look at it, `fakeroot` is either a horrendous hack or a
clever use of `LD_PRELOAD` developed at a time where there weren't lots of
options for syscall interposition. As there's been so much development in that
area I'd hope there are other alternatives by now, but I didn't see something
that's quite so easy to use, well tested for this use case, widely packaged,
and up to date.

I've avoided using `fakechroot` both because I couldn't get it to work
reliably in the cross-architecture bootstrap scenario, and also because
thinking through how it logically _should_ work in that scenario is fairly
complex. Given we're able to use user namespaces to `chroot`, let's save
ourselves the hassle and do that. Except there was a slight hiccup in that
`chown` was failing (running under `fakeroot`) when `chroot`ed in this way.
Thankfully the folks in the buildroot project had [run into the same
issue](https://patchwork.ozlabs.org/project/buildroot/patch/20190403201325.31664-1-peter@korsgaard.com/)
and their patch alerted me to the undocumented `FAKEROOTDONTTRYCHOWN`
environment variable. As written up in that commit message, the issue is that
under a user namespace with limited uid/gid mappings (in my case, just one),
`chown` returns `EINVAL` which isn't masked by `fakeroot` unless this
environment variable is set.

There has of course been previous work on rootless debootstrap, notably
[Johannes Schauer's blog
post](https://blog.mister-muffin.de/2011/04/02/foreign-debian-bootstrapping-without-root-priviliges-with-fakeroot,-fakechroot-and-qemu-user-emulation/)
that takes a slightly different route (by my understanding, including
communication between `LD_PRELOAD`ed fakeroot on the target and a `faked`
running on the host). A variant of this approach is used in
[mmdebstrap](https://gitlab.mister-muffin.de/josch/mmdebstrap) from the same
author.

## Limitations

* See the **warning** near the top of this article about correctness issues I've
encountered in some cases.
* As the file permissions info stored in `fakeroot.env` is keyed by the inode,
you may lose important permissions information if you copy the rootfs. You
should instead `tar` it under `fakeroot`, and if extracting in an unprivileged
environment again then untar it under `fakeroot`, creating a new
`fakeroot.env`.
* The use of `unshare` requires that unprivileged user namespace support is
enabled. I believe this is the case in all common distributions by now, but
please check your distro's guidance if not.

## Litmus test across many architectures

Just to demonstrate how this working, here is how you can debootstrap all
architectures supported by Debian + QEMU (except for mips, where I had issues
with qemu) then run a trivial test - compiling and running a hello world:

```sh
#!/bin/sh

error() {
  printf "!!!!!!!!!! Error: %s !!!!!!!!!!\n" "$*" >&2
  exit 1
}

# TODO: mips skipped due to QEMU issues.
ARCHES="amd64 arm64 armel armhf i386 ppc64el riscv64 s390x"
mkdir -p "$HOME/debcache"

for arch in $ARCHES; do
  rootless-debootstrap-wrapper \
    --arch=$arch \
    --suite=sid \
    --cache-dir="$HOME/debcache" \
    --target-dir=debootstrap-all-test-$arch \
    --include=build-essential || error "Debootstrap failed for arch $arch"
done

for arch in $ARCHES; do
  rootfs_dir="./debootstrap-all-test-$arch"
  cat <<EOF > "$rootfs_dir/hello.c"
#include <stdio.h>
#include <sys/utsname.h>

int main() {
  struct utsname buffer;
  if (uname(&buffer) != 0) {
      perror("uname");
      return 1;
    }
  printf("Hello from %s\n", buffer.machine);
  return 0;
}
EOF
  ./debootstrap-all-test-$arch/_enter sh -c "gcc hello.c && ./a.out"
done
```

Executing the above script eventually gives you:
```
Hello from x86_64
Hello from aarch64
Hello from armv7l
Hello from armv7l
Hello from x86_64
Hello from ppc64le
Hello from riscv64
Hello from s390x
```

(The repeated "armv7l" is because armel and armhf differ in ABI rather than
the architecture as returned by uname).

## Making a RISC-V image bootable in QEMU

Here is how to use the tool to build a bootable RISC-V image. First build the
rootfs:

```sh
TGT=riscv-sid-for-qemu
rootless-debootstrap-wrapper \
  --arch=riscv64 \
  --suite=sid \
  --cache-dir="$HOME/debcache" \
  --target-dir=$TGT \
  --include=linux-image-riscv64,zstd,default-dbus-system-bus || error "Debootstrap failed"
cat - <<EOF > $TGT/etc/resolv.conf
nameserver 1.1.1.1
EOF
"$TGT/_enter" sh -e <<EOF
ln -s /dev/null /etc/udev/rules.d/80-net-setup-link.rules # disable persistent network names
cat - <<INNER_EOF > /etc/systemd/network/10-eth0.network
[Match]
Name=eth0

[Network]
DHCP=yes
INNER_EOF
systemctl enable systemd-networkd
echo root:root | chpasswd
ln -sf /dev/null /etc/systemd/system/serial-getty@hvc0.service
EOF
```

Then produce an ext4 partition and extract the kernel and initrd:
```sh
fakeroot -i riscv-sid-for-qemu/.fakeroot.env sh <<EOF
ln -L riscv-sid-for-qemu/vmlinuz kernel
ln -L riscv-sid-for-qemu/initrd.img initrd
fallocate -l 30GiB rootfs.img
mkfs.ext4 -d riscv-sid-for-qemu rootfs.img
EOF
```

And boot it in qemu:
```sh
qemu-system-riscv64 \
  -machine virt \
  -cpu rv64 \
  -smp 4 \
  -m 8G \
  -device virtio-blk-device,drive=hd \
  -drive file=rootfs.img,if=none,id=hd,format=raw \
  -device virtio-net-device,netdev=net \
  -netdev user,id=net,hostfwd=tcp:127.0.0.1:10222-:22 \
  -bios /usr/share/qemu/opensbi-riscv64-generic-fw_dynamic.bin \
  -kernel kernel \
  -initrd initrd \
  -object rng-random,filename=/dev/urandom,id=rng \
  -device virtio-rng-device,rng=rng \
  -nographic \
  -append "rw noquiet root=/dev/vda console=ttyS0"
```

You can then log in with user `root` and password `root`. We haven't installed
`sshd` so far, but the above command line sets up forwarding from port 10222
on the local interface to port 22 on the guest in anticipation of that.
