# Muxup.com site repo

## About

This repository contains content and generator scripts for
[muxup.com](https://muxup.com). See the associated [implementation notes blog
post](https://muxup.com/2022q3/muxup-implementation-notes) for more
information.

## Dependencies

Arch packages:

    sudo pacman -S \
      darkhttpd \
      entr \
      flake8 \
      mypy \
      python-mistletoe \
      python-pygments \
      ruff

AUR packages:

* [terser](https://aur.archlinux.org/packages/terser)

Other:

* util-linux 2.40 or newer is needed for the `exch` utility (I don't list
  util-linux separately in the Arch dependency list as it's installed as a
  base package).

## Rebuilding with systemd-user

I have a user service running that rebuilds upon change. A small snippet of JS
that is inserted in the "for local serving" version changes the background
colour to a reddish pink if `/_had_error` exists (which is created if the `gen
build` had a non-zero exit code.

Create `muxup.service` in `~/.config/systemd/user`:

```systemd
[Unit]
Description=Muxup local server
After=network.target

[Service]
WorkingDirectory=%h/repos/muxup-site
ExecStart=/bin/dash -c 'while sleep 0.1; do find fragments/ pages/ static/ templates/ gen | entr -n -d dash -c "rm -f local_serve/_had_error; ./gen build --for-local-serve || touch local_serve/_had_error"; done & darkhttpd ./local_serve --port 5500 --addr 127.0.0.1 --default-mimetype text/html'
Restart=always
RestartSec=1

[Install]
WantedBy=default.target
```

Then enable with `systemctl --user enable --now muxup` and if check log output
with `journalctl --user -u muxup`.

## License

All source code (including CSS) is covered by the [MIT-0
license](https://github.com/muxup/muxup-site/blob/main/LICENSE), while all
content in the `pages/` subdirectory and any images are licensed under the
[Creative Commons Attribution 4.0
License](https://github.com/muxup/muxup-site/blob/main/LICENSE-CC-BY) (CC BY
4.0). SVGs in
`static/footer` are extracted from the [Quick, Draw!
dataset](https://github.com/googlecreativelab/quickdraw-dataset) (which is
also licensed under CC BY 4.0).
