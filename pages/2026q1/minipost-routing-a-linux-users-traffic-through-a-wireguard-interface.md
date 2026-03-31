+++
published = 2026-03-31
description = "Setting up a user on Arch Linux where all network traffic goes through wg0"
+++

# Routing a Linux user's traffic through a WireGuard interface

Simple goal: take advantage of my home router's WireGuard support and have one
of my external servers connect using this, and pass all traffic from a certain
user through that interface.

## Create WireGuard credentials

This part of the note won't be that useful to you unless you're using a
Fritzbox router. But if you're me or someone suspiciously like me you may want
to know to:

* Navigate to `https://192.168.178.1/#/access/wireguard`
* Click "Add WireGuard connection" and ensure "Connect a single device" is
  selected on the modal that appears. Then click "Next".
* Enter a unique name for the connection (I typically use
  `$remote_host_name-wg`) and click Finish. Follow request to confirm by
  pressing a button on the router.
* Click "Download settings" and a `wg_config.conf` will be downloaded.

## Add user

```sh
VPN_USER=asbvpn
sudo useradd -m -g users -G wheel -s /bin/bash "$VPN_USER"
sudo passwd "$VPN_USER"
```

## Configure systemd-networkd

First, extracting the relevant values from the `wg_config.conf`:

```sh
WG_CONF=wg_config.conf
PRIVATE_KEY="$(sed -n 's/^PrivateKey = //p' "$WG_CONF")"
PUBLIC_KEY="$(sed -n 's/^PublicKey = //p' "$WG_CONF")"
PRESHARED_KEY="$(sed -n 's/^PresharedKey = //p' "$WG_CONF")"
ENDPOINT="$(sed -n 's/^Endpoint = //p' "$WG_CONF")"

ADDRS="$(sed -n 's/^Address = //p' "$WG_CONF")"
IPV4_ADDR="$(printf '%s\n' "$ADDRS" | cut -d, -f1)"
IPV6_ADDR="$(printf '%s\n' "$ADDRS" | cut -d, -f2)"
```

What we want to do is:
* Define the wireguard interface `wg0` and specify the necessary keys, IP
  addresses etc for it to be brought up successfully.
* Specify a routing policy so that all traffic from the given user account
  goes via that interface.
  * As you can see below, we specify a RouteTable called "vpn", associate that
    with the interface, and specify rules for that table.
  * Ideally this would "fail closed" and no traffic from the user would be
    routed if `wg0` is down. That appears to use additional rules managed
    outside of systemd-networkd. I haven't tried to implement this.

The above can be achieved with:

```sh
sudo mkdir -p /etc/systemd/networkd.conf.d
sudo tee /etc/systemd/networkd.conf.d/90-vpn-table.conf >/dev/null <<'EOF'
[Network]
RouteTable=vpn:100
EOF

sudo tee /etc/systemd/network/50-wg0.netdev >/dev/null <<EOF
[NetDev]
Name=wg0
Kind=wireguard

[WireGuard]
PrivateKey=$PRIVATE_KEY
RouteTable=vpn

[WireGuardPeer]
PublicKey=$PUBLIC_KEY
PresharedKey=$PRESHARED_KEY
AllowedIPs=0.0.0.0/0
AllowedIPs=::/0
Endpoint=$ENDPOINT
EOF

sudo tee /etc/systemd/network/50-wg0.network >/dev/null <<EOF
[Match]
Name=wg0

[Network]
Address=$IPV4_ADDR
Address=$IPV6_ADDR

[RoutingPolicyRule]
User=$VPN_USER
Table=vpn
Priority=10000
Family=both
EOF

sudo chgrp systemd-network /etc/systemd/network/50-wg0.netdev
sudo chmod 0640 /etc/systemd/network/50-wg0.netdev
sudo systemctl restart systemd-networkd
```

Doing it this way, we've stored the secret keys in the 50-wg0.netdev file
itself but restricted access to the file. It's possible to have the keys
stored in a separate file, but for my setup it didn't seem worthwhile.

Then check the status with e.g.:

```sh
sudo networkctl status wg0
sudo ip rule show
sudo ip route show table 100
sudo wg show wg0
sudo -u $VPN_USER curl https://ifconfig.me/all
```

IPv6 does not work in this setup (`curl -6 google.com` will fail),

## Copying authorized_keys to new user

This is more a note to myself than anything else:

```sh
sudo install -d -m 700 -o $VPN_USER -g users /home/$VPN_USER/.ssh
sudo install -m 600 -o $VPN_USER -g users "$HOME/.ssh/authorized_keys" /home/$VPN_USER/.ssh/authorized_keys
```

