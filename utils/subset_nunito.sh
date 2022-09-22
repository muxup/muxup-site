#!/bin/sh
die () {
  printf "%s\n" "$*" >&2
  exit 1
}

[ -z "$1" ] && die "Must specify output filename fragment (e.g. v1) as argument"

if ! [ -f cache/Nunito.tff ]; then
  wget "https://github.com/googlefonts/nunito/raw/43d16f963c5c341c10efa0bfe7a82aa1bea8a938/fonts/variable/Nunito%5Bwght%5D.ttf" -O cache/Nunito.ttf || die "can't download nunito"
fi

pyftsubset cache/Nunito.ttf \
  --text-file=utils/subset_text.txt \
  --layout-features=kern,liga \
  --flavor=woff2 \
  --output-file=static/Nunito.var."$1".woff2 || die "pftsubset failed"
printf "Success!\n"
