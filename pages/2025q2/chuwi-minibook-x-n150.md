+++
published = 2025-05-06
description = "The netbook isn't dead"
+++

# Chuwi MiniBook X N150

Cast your mind back to the late 2000s and one thing you might remember is the
excitement about [netbooks](https://en.wikipedia.org/wiki/Netbook). You
sacrifice something in raw computational power, but get a lightweight, low
cost and ultra-portable system. Their popularity peaked and started wane maybe
15 years ago now, but I was pleased to discover that the idea lives on in the
form of the [Chuwi MiniBook X
N150](https://www.chuwi.com/product/items/chuwi-minibook-x-n150.html) and have
been using it as my daily driver for about a month now. Read on for some notes
and thoughts on the device as well as more information than you probably want
about configuring Linux on it.

The bottom line is that I enjoy it, I'd buy it again. But there are real
limitations to keep in mind if you're considering following suit.

![Picture of Chuwi MiniBook X N150 with a Biro for scale](/static/minibook_x_n150.jpg "MiniBook X N150")

## Background

First a little detour. As many of my comments are made in reference to my
previous laptops it's probably worth fleshing out that history a little. The
first thing to understand is that my local computing needs are relatively
simple and minimal. I work on large C/C++ codebases (primarily LLVM) with
lengthy compile times, but I build and run tests on a remote machine. This
means I only need enough local compute to comfortably navigate codebases, do
whatever smaller local projects I want to do, and use any needed browser based
tools like videoconferencing or GDocs.

Looking back at my previous two laptops (oldest first):
* [Acer Swift
  SF114-32](https://store.acer.com/en-gb/swift-1-ultra-thin-sf114-32-silver-2).
  Purchased for £405 in December 2018.
  * Intel
    [N5000](https://www.intel.com/content/www/us/en/products/sku/128990/intel-pentium-silver-n5000-processor-4m-cache-up-to-2-70-ghz/specifications.html)
    processor, 4GiB RAM (huge weak point even then), 256GB SSD, 14" 1920x1080
    matte screen.
  * Fanless and absolutely silent.
  * A big draw was the long battery life. Claimed 17h by the manufacturer,
    [tested at ~12h20m 'light websurfing' in one
    review](https://www.notebookcheck.net/Acer-Swift-1-SF114-32-N5000-SSD-FHD-Laptop-Review.303606.0.html)
    which I found to be representative, with runtimes closer to 17h possible
    if e.g. mostly doing text editing when traveling without WiFi.
  * Three USB-A ports, one USB-C port, 3.5mm audio jack, HDMI, SD card slot.
    Charging via proprietary power plug.
  * 1.30kg weight and 32.3cm x 22.8cm dimensions.
  * Took design stylings of rather more expensive devices, with a metal
    chassis, the ability to fold flat, and a large touchpad.
* [Acer Swift
  SF114-34](https://store.acer.com/en-gb/acer-swift-1-ultra-thin-laptop-sf114-34-silver-nx-a77ek-007).
  Purchased for £450 in August 2021.
  * Intel
    [N6000](https://www.intel.com/content/www/us/en/products/sku/212330/intel-pentium-silver-n6000-processor-4m-cache-up-to-3-30-ghz/specifications.html)
    processor, 8GiB RAM (luxurious!), 512GB SSD, 14" 1920x1080 matte screen.
  * Still fanless and absolutely silent.
  * Claimed battery life reduced to 15h. I found it very similar in practice.
    But the battery has degraded significantly over time.
  * Two USB-A ports, one USB-C port, 3.5mm audio jack, HDMI. Charging via
    proprietary power plug.
  * 1.30kg weight and 32.3cm x 21.2cm dimensions.
  * Still a metal chassis, though sadly designed without the ability to fold
    the screen completely flat and the size of the touchpad was downgraded.

I think you can see a pattern here.
As for the processors, the N5000 was part of Intel "[Gemini
Lake](https://www.anandtech.com/show/12146/intel-launches-gemini-lake-pentium-silver-and-celeron-socs-new-cpu-media-features)"
which used the Goldmont Plus microarchitecture. This targets the same market
segment as earlier Atom branded processors (as used by many of those early
netbooks) but with substantially higher performance and a much more
complicated microarchitecture than the early Atom (which was [dual issue, in
order with a 16 stage pipeline](https://www.anandtech.com/show/2493/11)). The
best reference I can see for the microarchitectures used in the N5000 and
N6000 is AnandTech's [Tremont microarchitecture
write-up](https://www.anandtech.com/show/15009/intels-new-atom-microarchitecture-the-tremont-core)
(matching the
[N6000](https://www.anandtech.com/show/16388/intel-launches-jasper-lake-tremont-atom-cores-for-all)),
which makes copious reference to differences vs previous iterations. Both the
N5000 and N6000 have a TDP of 6W and 4 cores (no hyperthreading). Notably,
all these designs lack AVX support. 

The successor to Tremont, was the [Gracemont
microarchitecture](https://www.anandtech.com/show/16881/a-deep-dive-into-intels-alder-lake-microarchitectures/4),
this time featuring AVX2 and seeing much wider usage due to being used as the
"E-Core" design throughout Intel's chips pairing some number of more
performance-oriented P-Cores with energy efficiency optimised E-Cores. Low
TDP chips featuring just E-Cores were released such as the [N100 serving
as a successor to the
N6000](https://www.anandtech.com/show/18704/intel-announces-n-series-processors-for-entry-level-mobile-and-systems)
and later the N150 added as a slightly higher clocked version. There have been
further iterations on the microarchitecture since Gracemont with
[Crestmont](https://chipsandcheese.com/p/meteor-lakes-e-cores-crestmont-makes-incremental-progress) and
[Skymont](https://chipsandcheese.com/p/skymont-intels-e-cores-reach-for-the-sky),
but at the time of writing I don't believe these have made it into similar
E-Core only low TDP chips. I'd love to see competitive devices at similar
pricepoints using AMD or Arm chips (and one day RISC-V of course), but this
series of Intel chips seems to have really found a niche.

## Chuwi MiniBook X N150

On to the present day:
* [Chuwi MiniBook X
  N150](https://www.chuwi.com/product/items/chuwi-minibook-x-n150.html)
  purchased for ~£290 in March 2025.
  * Intel
    [N150](https://www.intel.com/content/www/us/en/products/sku/241636/intel-processor-n150-6m-cache-up-to-3-60-ghz/specifications.html),
    12 GiB RAM, 512GB SSD, 10.5" 1920x1200 glossy screen.
  * Sadly not fanless or silent.
  * 28.8Wh battery, seems to give 4-6h battery depending on what you're doing
    (possibly more if offline and text editing, I've not tried to push to the
    limits).
  * Two USB-C ports (both supporting charging via USB PD), 3.5mm audio jack.
  * 0.92kg weight and 24.4cm x 16.6cm dimensions.
  * Display is touchscreen, and can fold all the way around for tablet-style
    usage.

Just looking at the specs the key trade-offs are clear. There's a big drop in
battery life, but a newer faster processor and fun mini size.

Overall, it's a positive upgrade but there are definitely some downsides. Main
highlights:
* Smol! Reasonably light. The 10" display works well at 125% zoom.
* The keyboard is surprisingly pleasant to use. The trackpad is obviously
  small given size constraints, but again it works just fine for me. It feels
  like this is the smallest size where you can have a fairly normal experience
  in terms of display and input.
* With a metal chassis, the build quality feels good overall. Of course the
  real test is how it lasts.
* Charging via USB-C PD! I am so happy to be free of laptop power bricks.
* The N150 is a nice upgrade vs the N5000 and N6000. AVX2 support means
  we're much more likely to hit optimised codepaths for libraries that make
  use of it.

But of course there's a long list of niggles or drawbacks. As I say, overall
it works _for me_, but if it didn't have these drawbacks I'd probably move
more towards actively recommending it without lots of caveats:

* Battery life isn't fantastic. I'd be much happier with 10-12h. Though given
  the USB-C PD support, it's not hard to reach this with an external battery.
* I miss having a silent fanless machine. The fan doesn't come on frequently
  in normal usage, but of course it's noticeable when it does. My unit also
  suffers from some coil wine which is audible sometimes when scrolling.
  Neither is particularly loud but there is a _huge_ difference between never
  being able to hear your computer vs sometimes being able to hear it.
* Some tinkering needed for initial Linux setup. Depending on your mindset,
  this might be a pro! Regardless, I've documented what I've done down below.
  I should note that all the basic hardware does work including the
  touchscreen, webcam, and microphone. The fact the display is rotated is
  mostly an easy fix, but I haven't checked if the fact it shows as 1200x1920
  rather than 1920x1080 causes problems for e.g. games.
* In-built display is 50Hz rather than 60Hz and I haven't yet succeeded at
  overriding this in Linux (although it seems possible in Windows).
* It's unfortunate there's no ability to limit charging at e.g. 80% as
  supported by some charge controllers as a way of extending battery lifetime.
* It charges relatively slowly (~20W draw), which is a further incentive to
  have an external battery if out and about.
* It's a shame they went with the soldered on Intel AX101 WiFi module rather
  than spending a few dollars more for a better module from Intel's line-up.
* I totally understand why Chuwi don't/can't have different variants with
  different keyboards, but I would sure love a version with a UK key layout!
* Screen real estate is lost to the bezel. Additionally, the rounded corners
  of the bezel cutting off the corner pixels is annoying.

Do beware that the laptop ships with a 12V/3A charger with a USB-C connection
that apparently will use that voltage without any negotiation. It's best not
to use it at all due to the risk of plugging in something that can't handle
12V input.

**Conclusion**: It's not perfect machine but I'm a huge fan of this form
factor. I really hope we get future iterations or competing products.

## Appendix A: Accessories

YMMV, but I picked up the following with the most notable clearly being the
replacement SSD. Prices are the approximate amount paid including any
shipping.

* SSD replacement: 2TB [WD Black
  SN7100](https://documents.westerndigital.com/content/dam/doc-library/en_us/assets/public/western-digital/product/internal-drives/wd-black-ssd/data-sheet-wd-black-sn7100-nvme-ssd.pdf) (£102)
  * This replaces the included 512GB AirDisk SSD.
  * Installation was trivial. Undo 8 screws on the MiniBook underside and it
    comes off easily.
  * The spec is overkill for this laptop (PCIe Gen4 when the MiniBook only
    supports Gen3 speeds). But the price was good meaning it wasn't very
    attractive to spend a similar amount for a slower last-generation drive
    with worse random read/write performance.
  * I didn't do a benchmark comparison as I would have had to install Linux
    with encrypted root on the original SSD as well for a fair test. However
    [this user on Reddit made the same upgrade and has some KDiskMark
    numbers](https://old.reddit.com/r/Chuwi/comments/1k2d7p8/performance_mods_on_n150_minibook_x_ssd_and/).
* External battery: [Baseus Blade HD
  20000mAh](https://uk.baseus.com/products/fc-bayern-blade-hd-power-bank-100w-20000mah) (£45.50)
  * Unlike the MiniBook itself, charges very quickly. Also supports
    pass-through charging so you can charge the battery while also charging
    downstream devices, through a single wall socket.
  * Goes for a thin but wider squared shape vs many other batteries that are
    quick thick, though narrower. For me this is more convenient in most
    scenarios.
  * See also [this detailed video review I came
    across](https://www.youtube.com/watch?v=k4blN7k97a4).
* Dock/stand: [UGREEN 9-in-1 Steam Deck
  Dock](https://www.amazon.co.uk/dp/B0CR6JND4M) (£36)
  * Despite being designed for the Steam Deck, this actually works really nicely
    for holding it vertically. The part that holds the device is adjustable and
    comfortably holds it without blocking the air vents. I use this at my work
    desk and just need to plug in a single USB-C cable for power, monitor, and
    peripherals (and additionally the 3.5mm audio jack if using speakers).
  * I'd wondered if I might have to instead find some below-desk setup to keep
    cables out of the way, but placing this at the side of my desk and using
    right-angled cables (or adapters) that go straight down off the side means
    seems to work fairly well for keeping the spiders web of cables out of the
    way.
* Charger: [VoltMe Vito Go 35W travel
  charger](https://www.aliexpress.com/item/1005007988685543.html) (~£11)
  * Support 20V 1.75A when only a USB-C cable is connected, which is more than
    enough for charging the MiniBook.
  * Given all my devices when traveling are USB, I was interested in
    something compact that avoids the need for separate adapter plugs. This
    seems to fit the bill.
* Case: [11" Tablet
  case](https://www.aliexpress.com/item/1005007166469508.html) (~£2.50 when
  bought with some other things)
  * Took a gamble but this fits remarkably well, and has room for extra cables
    / adapters.

## Appendix B: Arch Linux setup

As much for my future reference as for anything else, here are notes on
installing and configuring Arch Linux on the MiniBook X to my liking, and
working through as many niggles as I can. I'm grateful to Sonny Piers' [GitHub
repo](https://github.com/sonnyp/linux-minibook-x) for some pointers on dealing
with initial challenges like screen rotation.

### Initial install

Download [an Arch Linux install image](https://archlinux.org/download/) and
write to a USB drive. Enter the BIOS by pressing F2 while booting and disable
secure boot. I found I had to do this, then save and exit for
it to stick. Then enter BIOS again on a subsequent boot and select the option
to boot straight into it (under the "Save and Exit" menu).

In order to have the screen rotated correctly, we need to set the boot
parameter `video=DSI-1:panel_orientation=right_side_up`. Do this by pressing
<kbd>e</kbd> at the boot menu and manually adding.

Then connect to WiFi (`iwctl` then `station wlan0 scan`, `station wlan0
get-networks`, `station wlan0 connect $NETWORK_NAME` and enter the WiFi
password). It's likely more convenient to do the rest of the setup via ssh,
which can be done by setting a temporary root password with `passwd` and then
connecting with
`ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
root@archiso`.

Set the SSD sector size to 4k:
```sh
# Confirm 4k sector sizes are available and supported.
nvme id-ns -H /dev/nvme0n1
# Shows:
# LBA Format  0 : Metadata Size: 0   bytes - Data Size: 512 bytes - Relative Performance: 0x2 Good (in use)
# LBA Format  1 : Metadata Size: 0   bytes - Data Size: 4096 bytes - Relative Performance: 0x1 Better
nvme format --lbaf=1 /dev/nvme0n1
```

Now partition disks and create filesystems (with encrypted rootfs):
```sh
sfdisk /dev/nvme0n1 <<EOF
label: gpt

start=1MiB, size=511MiB, type=uefi
start=512MiB, type=linux
EOF

mkfs.fat -F32 /dev/nvme0n1p1
cryptsetup -y -v luksFormat /dev/nvme0n1p2 # enter desired unlock password
cryptsetup --perf-no_read_workqueue --perf-no_write_workqueue --persistent open /dev/nvme0n1p2 root
cryptsetup luksDump /dev/nvme0n1p2 # check flags and sector size
mkfs.xfs /dev/mapper/root
```

Now mount and pacstrap:
```sh
mount /dev/mapper/root /mnt
mount --mkdir /dev/nvme0n1p1 /mnt/boot
pacstrap /mnt base linux linux-firmware efibootmgr \
  xfsprogs dosfstools mdadm cryptsetup \
  python3 openssh sudo net-tools git man-db man-pages vim \
  wireless_tools iwd brightnessctl bash-completion tig \
  pkgfile powertop fzf bluez bluez-utils acpi \
  base-devel clang lld ninja cmake ncdu lua wget \
  pkgfile unzip unrar 7zip pwgen entr \
  rclone dash rsync
genfstab -U /mnt >> /mnt/etc/fstab
arch-chroot /mnt
```

Perform additional setup within the chroot:
```sh
sed /etc/locale.gen -i -e "s/^\#en_GB.UTF-8 UTF-8.*/en_GB.UTF-8 UTF-8/"
locale-gen
# Ignore "System has not been booted with systemd" and "Failed to connect to bus" error for next command.
systemd-firstboot --locale=en_GB.UTF-8 --timezone=Europe/London --hostname="plurp"
ln -s /dev/null /etc/udev/rules.d/80-net-setup-link.rules # disable persistent network names
sed /etc/mkinitcpio.conf -i -e 's/^HOOKS=.*/HOOKS=(base udev autodetect microcode modconf kms keyboard keymap consolefont block encrypt filesystems fsck)/'
mkinitcpio -P
```

Configure EFI boot:
```sh
for BOOTNUM in $(efibootmgr | grep '^Boot0' | sed 's/^Boot\([0-9]*\).*/\1/'); do
  efibootmgr -b $BOOTNUM -B
done
efibootmgr \
  --disk /dev/nvme0n1 \
  --part 1 \
  --create \
  --label 'Arch Linux' \
  --loader /vmlinuz-linux \
  --unicode "root=/dev/mapper/root rw cryptdevice=UUID=$(blkid -s UUID -o value /dev/nvme0n1p2):root:allow-discards initrd=\initramfs-linux.img video=DSI-1:panel_orientation=right_side_up" \
  --verbose
```

Other setup:
```sh
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
printf "PasswordAuthentication no\n" > /etc/ssh/sshd_config.d/20-no-password-auth.conf
systemctl enable sshd.service
useradd -m -g users -G wheel -s /bin/bash asb
usermod --pass='!' root # disable root login
chmod +w /etc/sudoers
printf "%%wheel ALL=(ALL) ALL\n" >> /etc/sudoers
chmod -w /etc/sudoers
mkdir "/home/asb/.ssh"
export PUBLIC_SSH_KEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINkmWQkBZWTsPo6obkVIjQVZf7Jt2RMi1F/4hIjz4BeF asb@hoorg"
printf "%s\n" "$PUBLIC_SSH_KEY" > "/home/asb/.ssh/authorized_keys"
chmod 700 "/home/asb/.ssh"
chmod 600 "/home/asb/.ssh/authorized_keys"
chown -R "asb:users" "/home/asb/.ssh"
systemctl enable iwd.service systemd-networkd.service systemd-resolved.service systemd-timesyncd.service
cat - <<EOF > /etc/systemd/network/25-wireless.network
[Match]
Name=wlan0

[Link]
RequiredForOnline=routable

[Network]
DHCP=yes
IgnoreCarrierLoss=3s
EOF
pkgfile --update
cat - <<EOF >> /etc/bash.bashrc
if [[ -r /usr/share/doc/pkgfile/command-not-found.bash ]]; then
  . /usr/share/doc/pkgfile/command-not-found.bash
fi
EOF
```

Set user password:
```
passwd asb # and enter password
```

ctrl-d once to exit the sysroot and:
```
ln -sf ../run/systemd/resolve/stub-resolv.conf /mnt/etc/resolv.conf
```

You can now reboot into the fresh Arch install.

### Graphical environment setup after reboot

Install various additional packages:

```sh
sudo pacman -S xorg-server arandr firefox openbox xfce4-terminal pavucontrol \
  openbox pcmanfm xorg-xinit i3lock dmenu chromium cheese mpv mpg123 \
  vlc xorg-fonts-misc xorg-mkfontscale ttf-dejavu xdotool mesa-utils gvim \
  firefox-ublock-origin intel-media-driver libva-utils rclone file-roller \
  xclip discount python-requests wmctrl foliate llvm sox eog gimp inkscape audacity \
  pipewire wireplumber pipewire-pulse wmname polkit evince xorg-xev scrot \
  alsa-utils alsa-tools aichat xorg-xinput xsettingsd python-bleak \
  xorg-xrefresh kdeconnect
```

When launching X the screen is rotated. This can be fixed temporarily with
`xrandr -o right`. But to fix it properly:

```sh
sudo tee /etc/X11/xorg.conf.d/20-defaultrotatescreen.conf > /dev/null << 'EOF'
Section "Monitor"
  Identifier "DSI-1"
  Option     "rotate" "right"
EndSection
EOF
```

The touchscreen input also needs to be rotated to work properly. See
[here](https://wiki.ubuntu.com/X/InputCoordinateTransformation) for guidance
on the transformation matrix for `xinput` and confirm the name to match with
`xinput list`.

```sh
sudo tee /etc/X11/xorg.conf.d/20-defaultrotatetouchscreen.conf > /dev/null << 'EOF'
Section "InputClass"
  Identifier   "GoodixTouchscreen"
  MatchProduct "Goodix Capacitive TouchScreen"
  Option       "TransformationMatrix" "0 1 0 -1 0 1 0 0 1"
EndSection
EOF
```

Install some additional aur packages:
```sh
git clone https://aur.archlinux.org/yay.git && cd yay
makepkg -si
cd .. && rm -rf yay
yay xautolock
yay ps_mem
```

Use UK keymap and in X11 use caps lock as escape:
```sh
localectl set-keymap uk
localectl set-x11-keymap gb "" "" caps:escape
```

The device has a US keyboard layout which has [one less key than than the UK
layout](https://en.wikipedia.org/wiki/British_and_American_keyboards) and
several keys in different places. As I regularly use a UK layout external
keyboard, rather than just get used to this I set a UK layout and use AltGr
keycodes for backslash (<kbd>AltGr</kbd>+<kbd>-</kbd>) and pipe
(<kbd>AltGR</kbd>+<kbd>\`</kbd>).

For audio support, I didn't need to do anything other than get rid of
excessive microphone noise by opening `alsamixer` and turning "Interl Mic
Boost" down to zero.

### Suspend rather than shutdown when pressing power button

It's too easy to accidentally hit the power button especially when
plugging/unplugging usb-c devices, so lets make it just suspend rather than
shutdown.

```
sudo mkdir -p /etc/systemd/logind.conf.d
sudo tee /etc/systemd/logind.conf.d/power-button.conf > /dev/null << 'EOF'
[Login]
HandlePowerKey=suspend
EOF
```

Then `systemd reload systemd-logind`.


### Enabling deep sleep
See the [Arch
wiki](https://wiki.archlinux.org/title/Power_management/Suspend_and_hibernate)
for a discussion. s2idle and deep are reported as supported from
/sys/power/mem_sleep, but the discharge rate leaving the laptop suspended
overnight feels higher than I'd like. Let's enable deep sleep in the hope it
reduces it.

```
sudo mkdir -p /etc/systemd/sleep.conf.d
sudo tee /etc/systemd/sleep.conf.d/deep-sleep.conf > /dev/null << 'EOF'
[Sleep]
MemorySleepMode=deep
EOF
```

Check last sleep mode used with `sudo journalctl | grep "PM: suspend" | tail
-2`. And check the current sleep mode with `cat /sys/power/mem_sleep`.
Checking the latter after boot you're likely to be worried to see that s2idle
is still default. But try suspending and then checking the journal and you'll
see systemd switches it just prior to suspending. (i.e. the setting works as
expected, even if it's only applied lazily).

I haven't done a reasonably controlled test of the impact.

### Changing DPI

The strategy is to use [xsettingsd](https://codeberg.org/derat/xsettingsd) to
update applications on the fly that support it, and otherwuse update Xft.dpi
in Xresources. I've found a DPI of 120 works well for me. So add `systemctl
--user restart xsettingsd` to `.xinitrc` as well as a call to this `set_dpi`
script with the desired DPI:

```sh
!/bin/sh

DPI="$1"

if [ -z "$DPI" ]; then
  echo "Usage: $0 <dpi>"
  exit 1
fi

CONFIG_FILE="$HOME/.config/xsettingsd/xsettingsd.conf"
mkdir -p "$(dirname "$CONFIG_FILE")"
if ! [ -e "$CONFIG_FILE" ]; then
  touch "$CONFIG_FILE"
fi

if grep -q 'Xft/DPI' "$CONFIG_FILE"; then
  sed -i "s|Xft/DPI.*|Xft/DPI $(($DPI * 1024))|" "$CONFIG_FILE"
else
  echo "Xft/DPI $(($DPI * 1024))" >> "$CONFIG_FILE"
fi

systemctl --user restart xsettingsd.service

echo "Xft.dpi: $DPI" | xrdb -merge

echo "DPI set to $DPI"
```

If attaching to an external display where a different DPI is desirable, just
call `set_dpi` as needed.

### Enabing Jabra bluetooth headset

* `sudo systemctl enable --now bluetooth.service`
* Follow instructions in https://wiki.archlinux.org/title/bluetooth_headset to
  pair
  * Remember to do the 'trust' step so it automatically reconnects


### Configuring Logitech Marble Mouse

```sh
sudo tee /etc/X11/xorg.conf.d/10-libinput.conf > /dev/null << 'EOF'
Section "InputClass"
  Identifier   "Marble Mouse"
  MatchProduct "Logitech USB Trackball"
  Driver       "libinput"
  Option       "ScrollMethod"    "button"
  Option       "ScrollButton"    "8"
  Option       "MiddleEmulation" "on"
EndSection
EOF
```

### Automatically enabling/disabling display outputs upon plugging in a monitor

The [srandrd](https://github.com/jceb/srandrd) tool provides a handy way of
listening for changes in the plug/unplugged status of connections and
launching a shell script. First try it out with the following to observe
events:

```
yay srandrd
cat - <<'EOF' > /tmp/echo.sh
echo $SRANDRD_OUTPUT $SRANDRD_EVENT $SRANDRD_EDID
EOF
chmod +x /tmp/echo.sh
srandrd -n /tmp/echo.sh
# You should now see the events as you plug/unplug devices.
```

So this is simple - we just write a shell script that `srandrd` will invoke
which calls `xrandr` as desired when connect/disconnect of the device with the
target EDID happens? Almost. There are two problems I need to work around:

1) The monitor I use for work is fairly bad at picking up a 4k60Hz input
signal. As far as I can tell this is independent of the cable used or input
device. What does seem to reliably work is to output a 1080p signal, wait a
bit, and then reconfigure to 4k60Hz.
2) The USB-C cable I normally plug into in my sitting room is also connected
to the TV via HDMI (I often use this for my Steam Deck). I noticed occasional
graphical slowdowns and after more debugging found I could reliably see this
in hiccups / reduced measured frame rate in `glxgears` that correspond with
recurrent plug/unplug events. The issue disappears completely if video output
via the cable is configured once and then unconfigured again. Very weird, but
at least there's a way round it.

Solving both of the above can readily be addressed by producing a short
sequence of `xrandr` calls rather than just one. Except these `xrandr` calls
themselves [trigger new events that cause `srandrd` to reinvoke the
script](https://github.com/jceb/srandrd/issues/9). So I add a mechanism to
have the script ignore events if received in short succession. We end up with
the following:

```sh
#!/usr/bin/sh

EVENT_STAMP=/tmp/display-change-stamp

# Recognised displays (as reported by $SRANDRD_EDID).
WORK_MONITOR="720405518350B628"
TELEVISION="6D1E82C501010101"

msg() {
  printf "display-change-handler: %s\n" "$*" >&2
}

# Call xrandr, but refresh $EVENT_STAMP just before doing so. This causes
# connect/disconnect events generated by the xrandr operation to be skipped at
# the head of this script. Call xrefresh afterwards to ensure windows are
# redrawn if necessary.
wrapped_xrandr() {
  touch $EVENT_STAMP
  xrandr "$@"
  xrefresh
}

msg "received event '$SRANDRD_OUTPUT: $SRANDRD_EVENT $SRANDRD_EDID'"

# Suppress event if within 2 seconds of the timestamp file being updated.
if [ -f $EVENT_STAMP ]; then
  cur_time=$(date +%s)
  file_time=$(stat -c %Y $EVENT_STAMP)
  if [ $(( cur_time - file_time)) -le 2 ]; then
    msg "suppressing event (exiting)"
    exit 0
  fi
fi
touch $EVENT_STAMP

is_output_outputting() {
  xrandr --query | grep -q "^$1 connected.*[0-9]\+x[0-9]\++[0-9]\++[0-9]\+"
}

# When connecting the main 'docked' display, disable the internal screen. Undo
# this when disconnecting.
case "$SRANDRD_EVENT $SRANDRD_EDID" in
  "connected $WORK_MONITOR")
    msg "enabling 1920x1080 output on $SRANDRD_OUTPUT, disabling laptop display, and sleeping for 10 seconds"
    wrapped_xrandr --output DSI-1 --off --output $SRANDRD_OUTPUT --mode 1920x1080
    sleep 10
    msg "switching up to 4k output"
    wrapped_xrandr --output DSI-1 --off --output $SRANDRD_OUTPUT --preferred
    msg "done"
    exit
    ;;
  "disconnected $WORK_MONITOR")
    msg "re-enabling laptop display and disabling $SRANDRD_OUTPUT"
    wrapped_xrandr --output DSI-1 --preferred --rotate right --output $SRANDRD_OUTPUT --off
    msg "done"
    exit
    ;;
  "connected $TELEVISION")
    # If we get the 'connected' event and a resolution is already configured
    # and being emitted, then do nothing as the event was likely generated by
    # a manual xrandr call from outside this script.
    if is_output_outputting $SRANDRD_OUTPUT; then
      msg "doing nothing as manual reconfiguration suspected"
      exit 0
    fi
    msg "enabling then disabling output $SRANDRD_OUTPUT which seems to avoid subsequent disconnect/reconnects"
    wrapped_xrandr --output $SRANDRD_OUTPUT --mode 1920x1080
    sleep 1
    wrapped_xrandr --output $SRANDRD_OUTPUT --off
    msg "done"
    exit
    ;;
  *)
    msg "no handler for $SRANDRD_EVENT $SRANDRD_EDID"
    exit
    ;;
esac
```

### Outputting to in-built screen at 60Hz (not yet solved)

The screen is unfortunately limited to 50Hz out of the box, but at least on
Windows it's possible to use [Custom Resolution
Utility](https://www.monitortests.com/forum/Thread-Custom-Resolution-Utility-CRU)
to edit the EDID and add a 1200x1920 60Hz mode (reminder: the display is
rotated to the right which is why width x height is the opposite order to
normal). To add Custom Resolution utility:
* Open CRU
* Click to "add a detailed resolution"
* Select "Exact reduced" and enter Active: 1200 horizontal pixels, Vertical
  1920 lines, and Refresh rate: 60.000 Hz. This results in Horizontal:
  117.000kHz and pixel clock 159.12MHz. Leave interlaced unticked.
* I exported this to a file with the hope of reusing on Linux.

As is often the case, the Arch Linux wiki has some [relevant
guidance](https://wiki.archlinux.org/title/Kernel_mode_setting#Forcing_modes_and_EDID)
on configuring an EDID override on Linux. I tried to follow the guidance by:
* Copying the exported EDID file to
  /usr/lib/firmware/edid/minibook_x_60hz.bin.
* Adding `drm.edid_firmware=DSI-1:edid/minibook_x_60hz.bin` (DSI-1 is the
  internal display) to the kernel commandline using `efibootmgr`.
* Confirming this shows up in the kernel command line in `dmesg` but there are
  no DRM messages regarding EDID override or loading the file. I also verify
  it shows up in `cat /sys/module/drm/parameters/edid_firmware`.
* Attempt adding `/usr/lib/firmware/edid/minibook_x_60hz.bin` to `FILES` in
  `/etc/mkinitcpio.conf` and regenerating the initramfs. No effect.

So this remains unresolved for the time being.

### Avoiding screen tearing (not yet solved)

Screen tearing is quite noticeable when scrolling some sites. I'd hoped that
enabling a compositor like [picom](https://github.com/yshui/picom) would
address this, but no combination of options seemed to do the job. Looking at
the issue tracker, [there are known problems with tearing in a rotated
display](https://github.com/yshui/picom/issues/328) that [should be solved by
using a version of the Xorg modesetting driver supporting
`TearFree`](https://wiki.archlinux.org/title/Intel_graphics#With_the_Intel_driver_2).
As Xorg hasn't had a new release in forever this requires the
`xorg-server-git` AUR package. Unfortunately, after building this I found
`dwm` hangs at launch and haven't put aside the time to investigate further.

