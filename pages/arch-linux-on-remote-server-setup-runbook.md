+++
published = 2024-10-01
description = "Notes on how I set up Arch on an remote server with encrypted root and remote unlock"
+++

# Arch Linux on remote server setup runbook

As I develop, I tend to offload a lot of the computationally heavy build or
test tasks to a remote build machine. It's convenient for this to match the
distribution I use on my local machine, and I so far haven't felt it would be
advantageous to add another more server-oriented distro to the mix to act as a
host to an Arch Linux container. This post acts as a quick reference / runbook
for me on the occasions I want to spin up a new machine with this setup. To be
very explicit, this is shared as something that might happen to be helpful if
you have similar requirements, or to give some ideas if you have different
ones. I definitely don't advocate that you blindly copy it.

Although this is something that could be fully automated, I find structuring
this kind of thing as a series of commands to copy and paste and check/adjust
manually hits the sweetspot for my usage. As always, the Arch Linux wiki and
its [install guide](https://wiki.archlinux.org/title/Installation_guide) is a
fantastic reference that you should go and check if you're unsure about
anything listed here.

## Details about my setup

* I'm typically targeting Hetzner servers with two SSDs. I'm not worried about
  data loss or minor downtime waiting for a disk to be replaced before
  re-imaging, so RAID0 is just fine. The commands below assume this setup.
* I do want encrypted root just in case anything sensitive is ever copied to
  the machine. As it is a remote machine, remote unlock over SSH must be
  supported (i.e. initrd contains an sshd that will accept the passphrase for
  unlocking the root partition before continuing the boot process).
  * The described setup means that if the disk is thrown away or given to
    another customer, you shouldn't have anything plain text in the root
    partition lying around it. As the boot partition is unencrypted, there are
    a whole bunch of threat models where someone is able to modify that boot
    partition which wouldn't be addressed by this approach.
* The setup also assumes you start from some kind of rescue environment (in my
  case Hetzner's) that means you can freely repartition and overwrite the disk
  drives.
* If you're not on Hetzner, you'll have to use different mirrors as they're
  not available externally.
* Hosts typically provide their own base images and installer scripts. The
  approach detailed here is good if you'd rather control the process yourself,
  and although there are a few hoster-specific bits in here it's easy enough
  to replace them.
* For simplicity I use UEFI boot and EFI stub. If you have problems with
  efibootmgr, you might want to use systemd-boot instead.
* Disclaimer: As is hopefully obvious, the below instructions will overwrite
  anything on the hard drive of the system you're running them on.

## Setting up and chrooting into Arch bootstrap environment from rescue system

See the [docs on the Hetzner rescue
system](https://docs.hetzner.com/robot/dedicated-server/troubleshooting/hetzner-rescue-system/)
for details on how to enter it. If you've previously used this server, you
likely want to remove old `known_hosts` entries with `ssh-keygen -R
your.server`.

Now ssh in and do the following:

```sh
wget http://mirror.hetzner.de/archlinux/iso/latest/archlinux-bootstrap-x86_64.tar.zst
tar -xvf archlinux-bootstrap-x86_64.tar.zst --numeric-owner
sed -i '1s;^;Server=https://mirror.hetzner.de/archlinux/$repo/os/$arch\n\n;' root.x86_64/etc/pacman.d/mirrorlist
mount --bind root.x86_64/ root.x86_64/ # See <https://bugs.archlinux.org/task/46169>
printf "About to enter bootstrap chroot\n===============================\n"
./root.x86_64/bin/arch-chroot root.x86_64/
```

You are now chrooted into the Arch boostrap environment. We will do as much
work from there as possible so as to minimise dependency on tools in the
Hetzner rescue system.

## Set up drives and create and chroot into actual rootfs

The goal is now to set up the drives, perform an Arch Linux bootstrap, and
chroot into it. The UEFI partition is placed at 1MiB pretty much guaranteed to
be properly aligned for any reasonable physical sector size (remembering space
must be left at the beginning of the disk for the partition table itself).

We'll start by collecting info that will be used throughout the process:

```sh
printf "Enter the desired new hostname:\n"
read NEW_HOST_NAME; export NEW_HOST_NAME
printf "Enter the desired passphrase for unlocking the root partition:\n"
read ROOT_PART_PASSPHRASE
printf "Enter the public ssh key (e.g. cat ~/.ssh/id_ed22519.pub) that will be used for access:\n"
read PUBLIC_SSH_KEY; export PUBLIC_SSH_KEY
printf "Enter the name of the main user account to be created:\n"
read NEW_USER; export NEW_USER
printf "You've entered the following information:\n"
printf "NEW_HOST_NAME: %s\n" "$NEW_HOST_NAME"
printf "ROOT_PART_PASSPHRASE: %s\n" "$ROOT_PART_PASSPHRASE"
printf "PUBLIC_SSH_KEY: %s\n" "$PUBLIC_SSH_KEY"
printf "NEW_USER: %s\n" "$NEW_USER"
```

And now proceed to set up the disks, create filesystems, perform an initial
bootstrap and chroot into the new rootfs:

```sh
pacman-key --init
pacman-key --populate archlinux
pacman -Sy --noconfirm xfsprogs dosfstools mdadm cryptsetup

for M in /dev/md?; do mdadm --stop $M; done
for DRIVE in /dev/nvme0n1 /dev/nvme1n1; do
  sfdisk $DRIVE <<EOF
label: gpt

start=1MiB, size=255MiB, type=uefi
start=256MiB, type=raid
EOF
done

# Warning from mdadm about falling back to creating md0 via node seems fine to ignore
yes | mdadm --create --verbose --level=0 --raid-devices=2 --homehost=any /dev/md/0 /dev/nvme0n1p2 /dev/nvme1n1p2

mkfs.fat -F32 /dev/nvme0n1p1
printf "%s\n" "$ROOT_PART_PASSPHRASE" | cryptsetup -y -v luksFormat --batch-mode /dev/md0
printf "%s\n" "$ROOT_PART_PASSPHRASE" | cryptsetup open /dev/md0 root
unset ROOT_PART_PASSPHRASE

mkfs.xfs /dev/mapper/root # rely on this calaculating appropriate sunit and swidth

mount /dev/mapper/root /mnt
mkdir /mnt/boot
mount /dev/nvme0n1p1 /mnt/boot
pacstrap /mnt base linux linux-firmware efibootmgr \
  xfsprogs dosfstools mdadm cryptsetup \
  mkinitcpio-netconf mkinitcpio-tinyssh mkinitcpio-utils python3 \
  openssh sudo net-tools git man-db man-pages vim
genfstab -U /mnt >> /mnt/etc/fstab
# Note that sunit and swidth in fstab confusingly use different units vs those shown by xfs <https://superuser.com/questions/701124/xfs-mount-overrides-sunit-and-swidth-options>

mdadm --detail --scan >> /mnt/etc/mdadm.conf
printf "About to enter newrootfs chroot\n===============================\n"
arch-chroot /mnt
```

## Do final configuration from within the new rootfs chroot

Unfortunately I wasn't able to find a way to get ipv6 configured via DHCP on
Hetzner's network, so we rely on hardcoding it (which seems to be [their
recommendation](https://docs.hetzner.com/robot/dedicated-server/network/network-configuration-using-systemd-networkd/).

We set up sudo and also configure ssh to disable password-based login. A small
swapfile is configured in order to allow the kernel to move allocated but not
actively used pages there if deemed worthwhile.

```sh
sed /etc/locale.gen -i -e "s/^\#en_GB.UTF-8 UTF-8.*/en_GB.UTF-8 UTF-8/"
locale-gen
# Ignore "System has not been booted with systemd" and "Failed to connect to bus" error for next command.
systemd-firstboot --locale=en_GB.UTF-8 --timezone=UTC --hostname="$NEW_HOST_NAME"
ln -s /dev/null /etc/udev/rules.d/80-net-setup-link.rules # disable persistent network names

ssh-keygen -A # generate openssh host keys for the tinyssh hook to pick up
printf "%s\n" "$PUBLIC_SSH_KEY" > /etc/tinyssh/root_key
sed /etc/mkinitcpio.conf -i -e 's/^HOOKS=.*/HOOKS=(base udev autodetect microcode modconf kms keyboard keymap consolefont block mdadm_udev netconf tinyssh encryptssh filesystems fsck)/'
# The call to tinyssh-convert in mkinitcpio-linux is incorrect, so do it
# manually <https://github.com/grazzolini/mkinitcpio-tinyssh/issues/10>
tinyssh-convert /etc/tinyssh/sshkeydir < /etc/ssh/ssh_host_ed25519_key
mkinitcpio -p linux

printf "efibootmgr before changes:\n==========================\n"
efibootmgr -u
# Clean up any other efibootmgr entries from previous installs
for BOOTNUM in $(efibootmgr | grep '^Boot0' | grep -v PXE | sed 's/^Boot\([0-9]*\).*/\1/'); do
  efibootmgr -b $BOOTNUM -B
done
# Set up efistub
efibootmgr \
  --disk /dev/nvme0n1 \
  --part 1 \
  --create \
  --label 'Arch Linux' \
  --loader /vmlinuz-linux \
  --unicode "root=/dev/mapper/root rw cryptdevice=UUID=$(blkid -s UUID -o value /dev/md0):root:allow-discards initrd=\initramfs-linux.img ip=:::::eth0:dhcp" \
  --verbose
efibootmgr -o 0001,0000 # prefer PXE boot. May need to check IDs
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

## Set user password and reboot

```sh
# The next command will ask for the user password (needed for sudo).
passwd "$NEW_USER"
```

Then <kbd>ctrl</kbd>+<kbd>d</kbd> twice and `reboot`.

## Unlocking rootfs and logging in

Firstly, you likely want to remove any saved host public keys as there will be
a new one for the newly provisioned machine `ssh-keygen -R
your.server`. The server will have a different host key for the root
key unlock so I'd recommend using a different `known_hosts` file for unlock.
e.g. `ssh -o UserKnownHostsFile=~/.ssh/known_hosts_unlock
root@your.server`. If you put something like the following in your
`~/.ssh/config` you could just `ssh unlock-foo-host`:

```
Host unlock-foo-host
HostName your.server
User root
UserKnownHostsFile ~/.ssh/known_hosts_unlock
```

Once you've successfully entered the key to unlock the rootfs, you can just
ssh as normal to the server.
