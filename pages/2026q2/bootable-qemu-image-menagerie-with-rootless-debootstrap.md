+++
published = 2026-05-04
description = "Rootlessly building bootable Debian images for QEMU across several architectures"
+++

# Bootable QEMU image menagerie with rootless debootstrap

Quite some time ago I shared a script and methodology for [performing a
cross-architecture debootstrap in a rootless
way](/pages/2024q4/rootless-cross-architecture-debootstrap.md). I had a short
note on producing an image bootable in QEMU, but it was fairly minimal. This
page provides a cookbook / quick reference on producing such images across
various Debian target architectures supported by QEMU. The goal is that the
starting point here "gets the basics right" for local experimentation, but of
course you are encouraged to evolve the recipe for your needs.

The basic process is to:

1. Build a root filesystem with `rootless-debootstrap-wrapper`.
2. Configure just enough networking, DNS, serial login, and SSH.
3. Create a 30 GiB ext4 filesystem image directly with `mkfs.ext4`.
4. Boot it with `qemu-system-*`, passing the Debian kernel and initrd directly.

We use Debian trixie for amd64, arm64, armhf, ppc64el, riscv64, and s390x.
We use sid for ppc64 big endian and loong64. I ran all of this on a current
Arch Linux install.

## Common setup

```sh
sudo pacman -S debootstrap fakeroot qemu-user-static qemu-user-static-binfmt \
  qemu-emulators-full e2fsprogs socat debian-archive-keyring debian-ports-archive-keyring
```

Put
[`rootless-debootstrap-wrapper`](https://github.com/muxup/medley/blob/main/rootless-debootstrap-wrapper)
somewhere in your `PATH`, then create a working directory:

```sh
mkdir -p qemu-debian-images
cd qemu-debian-images
mkdir -p "$HOME/debcache"
```

Paste the following into your terminal, which will be called to do the common
guest-side configuration.

```sh
configure_qemu_rootfs() {
  rootfs=$1
  console=$2
  suite=$3
  hostname=$4

  "$rootfs/_enter" sh -e <<EOF
mkdir -p /etc/systemd/network /etc/ssh/sshd_config.d

cat > /etc/systemd/network/10-qemu.network <<'INNER'
[Match]
Name=eth*

[Network]
DHCP=yes
INNER

cat > /etc/ssh/sshd_config.d/20-qemu-login.conf <<'INNER'
PermitRootLogin yes
PasswordAuthentication yes
INNER
rm -f /etc/ssh/ssh_host_*_key /etc/ssh/ssh_host_*_key.pub

/usr/bin/systemd-firstboot --locale=C.UTF-8 --hostname=${hostname} --force
ln -sf ../locale.conf /etc/default/locale
printf '127.0.1.1 %s\n' "$hostname" >> /etc/hosts
printf 'uninitialized\n' > /etc/machine-id
mkdir -p /var/lib/dbus
rm -f /var/lib/dbus/machine-id
ln -sf /etc/machine-id /var/lib/dbus/machine-id

systemctl enable systemd-networkd systemd-resolved systemd-timesyncd ssh || true
systemctl enable serial-getty@${console}.service || true

ln -sf ../run/systemd/resolve/resolv.conf /etc/resolv.conf
printf 'root:root\n' | chpasswd
adduser --gecos ",,," --disabled-password user || true
usermod -aG sudo user || true
printf 'user:user\n' | chpasswd
EOF

  if [ "$suite" = trixie ]; then
    cat >> "$rootfs/etc/apt/sources.list" <<'EOF'
deb https://security.debian.org/debian-security trixie-security main
deb https://deb.debian.org/debian trixie-updates main
EOF
  fi
}
```

This should _not_ be exposed on any public network without further
configuration. You can ssh in to either the root user or `user` via ssh, using
password `root` or `user` respectively. The commands below expose ssh via a
unix domain socket. One potential gotcha: this unix domain socket must not
have any `-` in its name as that collides with the splitting done for the
`hostfwd` argument. The examples given below avoid this issue.  The boot
commands pass `net.ifnames=0`, so the single QEMU network device is
consistently named `eth0` and matched by the networkd config above (I found
this more reliable than `ln -sf /dev/null
/etc/udev/rules.d/80-net-setup-link.rules`).

For simplicity we make use of `mkfs.ext4`'s ability to populate the image from
a directory. Pleasingly, `mkfs.xfs` gained a similar ability in the [xfsprogs
6.17.0 release](https://lwn.net/Articles/1042751/) in Oct 2025. If you have
a new enough version, and you prefer an XFS rootfs over ext4 you can tweak the
recipes below to do the following for the final image population step:

```sh
fakeroot -i "$ROOTFS/.fakeroot.env" \
  mkfs.xfs -f -q -L rootfs \
    -d file,name="$WORK/rootfs.img",size=30g \
    -p "$ROOTFS",atime=0
```

## amd64 / x86-64

Build:

```sh
WORK=$PWD/amd64-trixie-qemu
ROOTFS=$WORK/rootfs
mkdir -p "$WORK"

rootless-debootstrap-wrapper \
  --arch=amd64 \
  --suite=trixie \
  --mirror=https://deb.debian.org/debian \
  --cache-dir="$HOME/debcache" \
  --target-dir="$ROOTFS" \
  --include=linux-image-amd64,zstd,dbus,systemd-resolved,systemd-timesyncd,openssh-server,sudo

configure_qemu_rootfs "$ROOTFS" ttyS0 trixie qemu-amd64-trixie
cp -f "$ROOTFS"/boot/vmlinuz-* "$WORK/kernel"
cp -f "$ROOTFS"/boot/initrd.img-* "$WORK/initrd"
fakeroot -i "$ROOTFS/.fakeroot.env" \
  mkfs.ext4 -q -L rootfs -d "$ROOTFS" "$WORK/rootfs.img" 30G
```

Boot:

```sh
cd amd64-trixie-qemu
qemu-system-x86_64 \
  -accel kvm \
  -machine q35 \
  -cpu host \
  -smp 2 \
  -m 8G \
  -drive file=rootfs.img,if=none,id=hd,format=raw \
  -device virtio-blk-pci,drive=hd \
  -netdev user,id=net,hostfwd=unix:/tmp/qemu_amd64.sock-:22 \
  -device virtio-net-pci,netdev=net \
  -object rng-random,filename=/dev/urandom,id=rng \
  -device virtio-rng-pci,rng=rng \
  -kernel kernel \
  -initrd initrd \
  -nographic \
  -append "rw root=LABEL=rootfs console=ttyS0 net.ifnames=0"
```

The above assumes you are running on a x86-64 host, hence enables KVM. If not,
then drop `-accel kvm` and use `-cpu max` instead of `-cpu host`.

## arm64 / AArch64

Build:

```sh
WORK=$PWD/arm64-trixie-qemu
ROOTFS=$WORK/rootfs
mkdir -p "$WORK"

rootless-debootstrap-wrapper \
  --arch=arm64 \
  --suite=trixie \
  --mirror=https://deb.debian.org/debian \
  --cache-dir="$HOME/debcache" \
  --target-dir="$ROOTFS" \
  --include=linux-image-arm64,zstd,dbus,systemd-resolved,systemd-timesyncd,openssh-server,sudo

configure_qemu_rootfs "$ROOTFS" ttyAMA0 trixie qemu-arm64-trixie
cp -f "$ROOTFS"/boot/vmlinuz-* "$WORK/kernel"
cp -f "$ROOTFS"/boot/initrd.img-* "$WORK/initrd"
fakeroot -i "$ROOTFS/.fakeroot.env" \
  mkfs.ext4 -q -L rootfs -d "$ROOTFS" "$WORK/rootfs.img" 30G
```

Boot:

```sh
cd arm64-trixie-qemu
qemu-system-aarch64 \
  -machine virt \
  -cpu cortex-a57 \
  -smp 2 \
  -m 8G \
  -drive file=rootfs.img,if=none,id=hd,format=raw \
  -device virtio-blk-device,drive=hd \
  -netdev user,id=net,hostfwd=unix:/tmp/qemu_arm64.sock-:22 \
  -device virtio-net-device,netdev=net \
  -object rng-random,filename=/dev/urandom,id=rng \
  -device virtio-rng-device,rng=rng \
  -kernel kernel \
  -initrd initrd \
  -nographic \
  -append "rw root=LABEL=rootfs console=ttyAMA0 net.ifnames=0"
```

## armhf / 32-bit ARM

For this one I had to add the relevant virtio modules to the initrd.

Build:

```sh
WORK=$PWD/armhf-trixie-qemu
ROOTFS=$WORK/rootfs
mkdir -p "$WORK"

rootless-debootstrap-wrapper \
  --arch=armhf \
  --suite=trixie \
  --mirror=https://deb.debian.org/debian \
  --cache-dir="$HOME/debcache" \
  --target-dir="$ROOTFS" \
  --include=linux-image-armmp,zstd,dbus,systemd-resolved,systemd-timesyncd,openssh-server,sudo

configure_qemu_rootfs "$ROOTFS" ttyAMA0 trixie qemu-armhf-trixie
printf '%s\n' virtio_mmio virtio_blk virtio_net >> "$ROOTFS/etc/initramfs-tools/modules"
"$ROOTFS/_enter" update-initramfs -u -k all
cp -f "$ROOTFS"/boot/vmlinuz-* "$WORK/kernel"
cp -f "$ROOTFS"/boot/initrd.img-* "$WORK/initrd"
fakeroot -i "$ROOTFS/.fakeroot.env" \
  mkfs.ext4 -q -L rootfs -d "$ROOTFS" "$WORK/rootfs.img" 30G
```

Boot:

```sh
cd armhf-trixie-qemu
qemu-system-arm \
  -machine virt \
  -cpu cortex-a15 \
  -smp 2 \
  -m 4G \
  -drive file=rootfs.img,if=none,id=hd,format=raw \
  -device virtio-blk-device,drive=hd \
  -netdev user,id=net,hostfwd=unix:/tmp/qemu_armhf.sock-:22 \
  -device virtio-net-device,netdev=net \
  -object rng-random,filename=/dev/urandom,id=rng \
  -device virtio-rng-device,rng=rng \
  -kernel kernel \
  -initrd initrd \
  -nographic \
  -append "rw root=LABEL=rootfs console=ttyAMA0 net.ifnames=0"
```

## riscv64

Build:

```sh
WORK=$PWD/riscv64-trixie-qemu
ROOTFS=$WORK/rootfs
mkdir -p "$WORK"

rootless-debootstrap-wrapper \
  --arch=riscv64 \
  --suite=trixie \
  --mirror=https://deb.debian.org/debian \
  --cache-dir="$HOME/debcache" \
  --target-dir="$ROOTFS" \
  --include=linux-image-riscv64,zstd,dbus,systemd-resolved,systemd-timesyncd,openssh-server,sudo

configure_qemu_rootfs "$ROOTFS" ttyS0 trixie qemu-riscv64-trixie
cp -f "$ROOTFS"/boot/vmlinux-* "$WORK/kernel"
cp -f "$ROOTFS"/boot/initrd.img-* "$WORK/initrd"
fakeroot -i "$ROOTFS/.fakeroot.env" \
  mkfs.ext4 -q -L rootfs -d "$ROOTFS" "$WORK/rootfs.img" 30G
```

Boot:

```sh
cd riscv64-trixie-qemu
qemu-system-riscv64 \
  -machine virt \
  -cpu rv64 \
  -smp 2 \
  -m 8G \
  -drive file=rootfs.img,if=none,id=hd,format=raw \
  -device virtio-blk-device,drive=hd \
  -netdev user,id=net,hostfwd=unix:/tmp/qemu_riscv64.sock-:22 \
  -device virtio-net-device,netdev=net \
  -object rng-random,filename=/dev/urandom,id=rng \
  -device virtio-rng-device,rng=rng \
  -bios /usr/share/qemu/opensbi-riscv64-generic-fw_dynamic.bin \
  -kernel kernel \
  -initrd initrd \
  -nographic \
  -append "rw root=LABEL=rootfs console=ttyS0 net.ifnames=0"
```

The above assumes you have opensbi installed in /usr/share/qemu (it is put
here by the qemu-system-riscv-firmware package on Arch).

## ppc64el

Build:

```sh
WORK=$PWD/ppc64el-trixie-qemu
ROOTFS=$WORK/rootfs
mkdir -p "$WORK"

rootless-debootstrap-wrapper \
  --arch=ppc64el \
  --suite=trixie \
  --mirror=https://deb.debian.org/debian \
  --cache-dir="$HOME/debcache" \
  --target-dir="$ROOTFS" \
  --include=linux-image-powerpc64le,zstd,dbus,systemd-resolved,systemd-timesyncd,openssh-server,sudo

configure_qemu_rootfs "$ROOTFS" hvc0 trixie qemu-ppc64el-trixie
cp -f "$ROOTFS"/boot/vmlinux-* "$WORK/kernel"
cp -f "$ROOTFS"/boot/initrd.img-* "$WORK/initrd"
fakeroot -i "$ROOTFS/.fakeroot.env" \
  mkfs.ext4 -q -L rootfs -d "$ROOTFS" "$WORK/rootfs.img" 30G
```

Boot:

```sh
cd ppc64el-trixie-qemu
qemu-system-ppc64 \
  -machine pseries \
  -cpu power9 \
  -smp 2 \
  -m 8G \
  -drive file=rootfs.img,if=none,id=hd,format=raw \
  -device virtio-blk-pci,drive=hd \
  -netdev user,id=net,hostfwd=unix:/tmp/qemu_ppc64el.sock-:22 \
  -device virtio-net-pci,netdev=net \
  -object rng-random,filename=/dev/urandom,id=rng \
  -device virtio-rng-pci,rng=rng \
  -kernel kernel \
  -initrd initrd \
  -nographic \
  -append "rw root=LABEL=rootfs console=hvc0 net.ifnames=0"
```

## s390x (SystemZ)

Build:

```sh
WORK=$PWD/s390x-trixie-qemu
ROOTFS=$WORK/rootfs
mkdir -p "$WORK"

rootless-debootstrap-wrapper \
  --arch=s390x \
  --suite=trixie \
  --mirror=https://deb.debian.org/debian \
  --cache-dir="$HOME/debcache" \
  --target-dir="$ROOTFS" \
  --include=linux-image-s390x,zstd,dbus,systemd-resolved,systemd-timesyncd,openssh-server,sudo

configure_qemu_rootfs "$ROOTFS" ttysclp0 trixie qemu-s390x-trixie
cp -f "$ROOTFS"/boot/vmlinuz-* "$WORK/kernel"
cp -f "$ROOTFS"/boot/initrd.img-* "$WORK/initrd"
fakeroot -i "$ROOTFS/.fakeroot.env" \
  mkfs.ext4 -q -L rootfs -d "$ROOTFS" "$WORK/rootfs.img" 30G
```

Boot:

```sh
cd s390x-trixie-qemu
qemu-system-s390x \
  -machine s390-ccw-virtio \
  -smp 2 \
  -m 8G \
  -drive file=rootfs.img,if=none,id=hd,format=raw \
  -device virtio-blk-ccw,drive=hd \
  -netdev user,id=net,hostfwd=unix:/tmp/qemu_s390x.sock-:22 \
  -device virtio-net-ccw,netdev=net \
  -object rng-random,filename=/dev/urandom,id=rng \
  -device virtio-rng-ccw,rng=rng \
  -kernel kernel \
  -initrd initrd \
  -nographic \
  -append "rw root=LABEL=rootfs console=ttysclp0 net.ifnames=0"
```

## ppc64 big-endian

This is a Debian ports target, so we use `sid` and the ports mirror.

Build:

```sh
WORK=$PWD/ppc64-sid-qemu
ROOTFS=$WORK/rootfs
mkdir -p "$WORK"

rootless-debootstrap-wrapper \
  --arch=ppc64 \
  --suite=sid \
  --mirror=https://deb.debian.org/debian-ports \
  --cache-dir="$HOME/debcache" \
  --target-dir="$ROOTFS" \
  --keyring=/usr/share/keyrings/debian-ports-archive-keyring.gpg \
  --include=linux-image-powerpc64,zstd,dbus,systemd-resolved,systemd-timesyncd,openssh-server,sudo

configure_qemu_rootfs "$ROOTFS" hvc0 sid qemu-ppc64-sid
cp -f "$ROOTFS"/boot/vmlinux-* "$WORK/kernel"
cp -f "$ROOTFS"/boot/initrd.img-* "$WORK/initrd"
fakeroot -i "$ROOTFS/.fakeroot.env" \
  mkfs.ext4 -q -L rootfs -d "$ROOTFS" "$WORK/rootfs.img" 30G
```

Boot:

```sh
cd ppc64-sid-qemu
qemu-system-ppc64 \
  -machine pseries \
  -cpu power9 \
  -smp 2 \
  -m 8G \
  -drive file=rootfs.img,if=none,id=hd,format=raw \
  -device virtio-blk-pci,drive=hd \
  -netdev user,id=net,hostfwd=unix:/tmp/qemu_ppc64.sock-:22 \
  -device virtio-net-pci,netdev=net \
  -object rng-random,filename=/dev/urandom,id=rng \
  -device virtio-rng-pci,rng=rng \
  -kernel kernel \
  -initrd initrd \
  -nographic \
  -append "rw root=LABEL=rootfs console=hvc0 net.ifnames=0"
```

## loong64 / LoongArch

For this one, we need EDK2 which you can obtain from Debian's
qemu-efi-loongarch64 package (`QEMU_EFI.fd`).

Build:

```sh
WORK=$PWD/loong64-sid-qemu
ROOTFS=$WORK/rootfs
mkdir -p "$WORK"

rootless-debootstrap-wrapper \
  --arch=loong64 \
  --suite=sid \
  --mirror=https://deb.debian.org/debian \
  --cache-dir="$HOME/debcache" \
  --target-dir="$ROOTFS" \
  --include=linux-image-loong64,zstd,dbus,systemd-resolved,systemd-timesyncd,openssh-server,sudo

configure_qemu_rootfs "$ROOTFS" ttyS0 sid qemu-loong64-sid
cp -f "$ROOTFS"/boot/vmlinuz-* "$WORK/kernel"
cp -f "$ROOTFS"/boot/initrd.img-* "$WORK/initrd"
fakeroot -i "$ROOTFS/.fakeroot.env" \
  mkfs.ext4 -q -L rootfs -d "$ROOTFS" "$WORK/rootfs.img" 30G
```

Boot:

```sh
cd loong64-sid-qemu
cp ../QEMU_EFI.fd .
qemu-system-loongarch64 \
  -machine virt,firmware=QEMU_EFI.fd \
  -smp 2 \
  -m 8G \
  -drive file=rootfs.img,if=none,id=hd,format=raw \
  -device virtio-blk-pci,drive=hd \
  -netdev user,id=net,hostfwd=unix:/tmp/qemu_loong64.sock-:22 \
  -device virtio-net-pci,netdev=net \
  -object rng-random,filename=/dev/urandom,id=rng \
  -device virtio-rng-pci,rng=rng \
  -kernel kernel \
  -initrd initrd \
  -nographic \
  -append "rw root=LABEL=rootfs console=ttyS0 net.ifnames=0"
```

## Logging in

As noted above, you can log in with `root`/`root` or `user`/`user`. The launch
commands above will show you the QEMU terminal.

Once the guest is booted, you can connect via ssh to the Unix domain socket
that forwards to guest port 22. e.g.:

```sh
ssh -o "ProxyCommand=socat - UNIX-CONNECT:/tmp/qemu_amd64.sock" root@vm
```

Or with OpenBSD netcat:

```sh
ssh -o "ProxyCommand=nc -U /tmp/qemu_amd64.sock" root@vm
```

If you'd rather use a TCP port, replace the `-netdev` part of the qemu launch
command with something like this and connect to `localhost:2222`:

```sh
-netdev user,id=net,hostfwd=tcp:127.0.0.1:2222-:22
```

## Article changelog
* 2026-05-07: (minor) Add note about how to use an XFS rootfs.
* 2026-05-05: (minor) Use `net.ifnames=0` command line argument rather than
  `ln -sf /dev/null /etc/udev/rules.d/80-net-setup-link.rules`.
