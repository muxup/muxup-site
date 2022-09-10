#!/bin/sh

die () {
  printf "%s\n" "$*" >&2
  exit 1
}

[ -e build.py ] || die "Running from unexpected cwd"
[ -d dist ] || die "dist/ folder not present"
rm -rf tmp
cp -prL dist tmp
find tmp \( -name '*.html' -o -name '*.svg' \) -print0 | xargs -0 -P$(nproc) brotli -q 11 -k -f
rsync -avcz --no-t --delete tmp/ asbradbury.org:/var/www/muxup.com/htdocs/
rm -rf tmp
