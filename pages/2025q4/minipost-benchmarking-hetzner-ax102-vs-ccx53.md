+++
published = 2025-11-30
description = "Dedicated server vs 'dedicated resource' VPS benchmarked compiling LLVM."
+++


# Benchmarking the Hetzner AX102 vs CCX53

I recently had reason to do a quick comparison of the performance of the
[Hetzner AX102](https://www.hetzner.com/dedicated-rootserver/ax102/) dedicated
server and the high-end 'dedicated' CCX53 VPS on [Hetzner
Cloud](https://www.hetzner.com/cloud/) and thought I may as well write up the
results for posterity. I'm incapable of starting a post without some kind of
disclaimer so here comes the one for this post: naturally the two products
have major differences in terms of flexibility (spin-up/down at will, vs pay a
small setup fee and endure a wait time depending on hardware availability). So
depending on your use case, your requirements with respect to that flexibility
may override any cost differential.

## Specs

All costs are exclusive of VAT, assuming the lowest cost data center location,
and inclusive of IPv4 address.

**AX102**:
* 16 core Ryzen 9 7950X3D (32 threads)
* 128GB DDR5 RAM
* 2 x 1.92TB NVMe
* 104 EUR/month, 39 EUR one-off setup fee.

**CCX53**
* Unknown AMD CPU exposing 32vCPU (physical cores? threads?)
* 128GB RAM
* 600GB NVMe
* 192.49 EUR/month maximum charge. 0.3085 EUR per hour (if you keep the same
  VPS active over the month it won't exceed the monthly price cap, so you
  effectively get a small discount on the per-hour cost).

## Benchmark

Building Clang+LLVM+LLD, everyone's favourite workload! Both systems are
running an up to date Arch Linux (more details on setting this up on the CCX53
in the appendix below) with clang 21.1.6. The dedicated machine has the
advantage of RAID 0 across the two SSDs, but also has encrypted rootfs
configured. I didn't bother to set that up for the CCX53 VPS.

```sh
sudo pacman -Syu --needed clang lld cmake ninja wget
LLVM_VER=21.1.6
wget https://github.com/llvm/llvm-project/releases/download/llvmorg-${LLVM_VER}/llvm-project-${LLVM_VER}.src.tar.xz
tar -xvf llvm-project-${LLVM_VER}.src.tar.xz
cd llvm-project-${LLVM_VER}.src

cmake -G Ninja \
  -DLLVM_ENABLE_PROJECTS='clang;lld' \
  -DLLVM_TARGETS_TO_BUILD="all" \
  -DLLVM_CCACHE_BUILD=OFF \
  -DCMAKE_C_COMPILER=clang \
  -DCMAKE_CXX_COMPILER=clang++ \
  -DLLVM_ENABLE_LLD=ON \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLVM_ENABLE_ASSERTIONS=ON \
  -S llvm \
  -B build
time cmake --build build

printf "### Version info ###\n"
clang --version | head -n 1
```

On both machines, ninja shows 5575 build steps.

Results:
* AX102
  * 10m27s (627s)
* CCX53
  * 14m11s (851s, about 1.36x the AX102)

Running the clang and LLVM tests with `./build/bin/llvm-lit -s --order=lexical
llvm/test clang/test` (which shows 9402 tests) gives:
* AX102
  * 3m39s (219s)
* CCX53
  * 4m28s (268s, about 1.24x the AX102)

I ran these multiple times, and in the case of the CCX53 across two different
VMs in different regions and saw only a few percentage points variance.

Focusing on the results for build clang/llvm/lld, let's figure out the cost
for 1000 from-scratch builds. Not so much as it's a representative workload, but
because it gives an easy to compare metric that captures both the difference
in price and in performance. So calculating `time_per_build_in_hours * 1000 *
cost_per_hour`:
* AX102
  * (626.6 / 3600) * 1000 * (104/720) = **25.14 EUR**
  * Or if you include the setup fee and assume it's amortised over 12 months:
    * (626.6/3600) * 1000 * ((104 + (39/12))/720) = **25.93 EUR**
* CCX53
  * (850.6 / 3600) * 1000 * (192.49/720) = **63.17 EUR**
  * Or using the 0.3085 EUR/hr price which you would pay if you didn't run for
    the whole month:
    * (850.6 / 3600) * 1000 * 0.3085 = **72.89 EUR**

## Appendix: CCX53 Arch Linux setup

This could be scripted, but I just created the VPS via their web UI. Then after
it was provisioned, used that web UI to have it boot into a rescue system.
Then do an Arch bootstrap that roughly mirrors the [one I use on a dedicated
build machine](/pages/arch-linux-on-remote-server-setup-runbook.md) except
that we don't bother with encrypting the rootfs. The CCX* server types at
least [use
UEFI](https://docs.hetzner.cloud/changelog#2023-08-23-new-server-types-with-dedicated-amd-vcpus)
so we can keep using efistub for boot.

First get a bootstrap environment and enter it:

```sh
wget http://mirror.hetzner.de/archlinux/iso/latest/archlinux-bootstrap-x86_64.tar.zst
tar -xvf archlinux-bootstrap-x86_64.tar.zst --numeric-owner
sed -i '1s;^;Server=https://mirror.hetzner.de/archlinux/$repo/os/$arch\n\n;' root.x86_64/etc/pacman.d/mirrorlist
mount --bind root.x86_64/ root.x86_64/ # See <https://bugs.archlinux.org/task/46169>
printf "About to enter bootstrap chroot\n===============================\n"
./root.x86_64/bin/arch-chroot root.x86_64/
```

Now set info that will be used throughout the process:

```sh
export NEW_HOST_NAME=archvps
export PUBLIC_SSH_KEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOfpPQ1j+XLsapAhONAQmvu6TZGT5y8jeziM4Vio1NrA asb@plurp"
export NEW_USER=asb
```

And now proceed to set up the disks, create filesystems, perform an initial
bootstrap and chroot into the new rootfs:

```sh
pacman-key --init
pacman-key --populate archlinux
pacman -Sy --noconfirm xfsprogs dosfstools

sfdisk /dev/sda <<EOF
label: gpt

start=1MiB, size=255MiB, type=uefi
start=256MiB, type=linux
EOF

mkfs.fat -F32 /dev/sda1
mkfs.xfs /dev/sda2

mount /dev/sda2 /mnt
mkdir /mnt/boot
mount /dev/sda1 /mnt/boot
pacstrap /mnt base linux linux-firmware efibootmgr \
  xfsprogs dosfstools \
   python3 \
  openssh sudo net-tools git man-db man-pages vim
genfstab -U /mnt >> /mnt/etc/fstab

printf "About to enter newrootfs chroot\n===============================\n"
arch-chroot /mnt
```

Do final configuration from within the chroot:

```sh
sed /etc/locale.gen -i -e "s/^\#en_GB.UTF-8 UTF-8.*/en_GB.UTF-8 UTF-8/"
locale-gen
# Ignore "System has not been booted with systemd" and "Failed to connect to bus" error for next command.
systemd-firstboot --locale=en_GB.UTF-8 --timezone=UTC --hostname="$NEW_HOST_NAME"
ln -s /dev/null /etc/udev/rules.d/80-net-setup-link.rules # disable persistent network names

# No longer need to disable large fallback image as Arch stopped generating it
# by default

printf "efibootmgr before changes:\n==========================\n"
efibootmgr -u
# Set up efistub
efibootmgr \
  --disk /dev/sda \
  --part 1 \
  --create \
  --label 'Arch Linux' \
  --loader /vmlinuz-linux \
  --unicode "root=/dev/sda2 rw initrd=\initramfs-linux.img" \
  --verbose
printf "efibootmgr after changes:\n=========================\n"
efibootmgr -u

mkswap --size=8G --file /swapfile
cat - <<EOF > /etc/systemd/system/swapfile.swap
[Unit]
Description=Swap file

[Swap]
What=/swapfile

[Install]
WantedBy=multi-user.target
EOF
systemctl enable swapfile.swap

cat - <<EOF > /etc/systemd/network/10-eth0.network
[Match]
Name=eth0

[Network]
DHCP=yes
Address=$(ip -6 addr show dev eth0 scope global | grep "scope global" | cut -d' ' -f6)
Gateway=$(ip route show | head -n 1 | cut -d' ' -f 3)
Gateway=fe80::1
EOF
systemctl enable systemd-networkd.service systemd-resolved.service systemd-timesyncd.service
printf "PasswordAuthentication no\n" > /etc/ssh/sshd_config.d/20-no-password-auth.conf
systemctl enable sshd.service
useradd -m -g users -G wheel -s /bin/bash "$NEW_USER"
usermod --pass='!' root # disable root login
chmod +w /etc/sudoers
printf "%%wheel ALL=(ALL) ALL\n" >> /etc/sudoers
chmod -w /etc/sudoers
mkdir "/home/$NEW_USER/.ssh"
printf "%s\n" "$PUBLIC_SSH_KEY" > "/home/$NEW_USER/.ssh/authorized_keys"
chmod 700 "/home/$NEW_USER/.ssh"
chmod 600 "/home/$NEW_USER/.ssh/authorized_keys"
chown -R "$NEW_USER:users" "/home/$NEW_USER/.ssh"
```

Now set password:
```
passwd "$NEW_USER"
```

Then ctrl-d twice and set a symlink for resolv.conf:

```
ln -sf ../run/systemd/resolve/stub-resolv.conf root.x86_64/mnt/etc/resolv.conf
```

Finally, `reboot`.

Remember to `ssh-keygen -R $THE_IP_ADDRESS` so you don't get ssh host
verification errors.
