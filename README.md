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
