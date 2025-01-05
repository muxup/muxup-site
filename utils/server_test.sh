#!/bin/sh

# Copyright Muxup contributors.
# Distributed under the terms of the MIT-0 license, see LICENSE for details.
# SPDX-License-Identifier: MIT-0

BASE_URL="https://muxup.com"
BASE_URL_WWW="https://www.muxup.com"

check_404() {
  res=$(curl -sw ' - %{http_code}' "$BASE_URL$1")
  if [ "$res" = "404 Not Found - 404" ]; then
    printf "PASS: '%s' gives expected 404\n" "$BASE_URL$1"
  else
    printf "FAIL: '%s' doesn't give expected 404\n" "$BASE_URL$1"
  fi
}

check_405() {
  res=$(curl -X POST -sw ' - %{http_code}' "$BASE_URL$1")
  if [ "$res" = "405 Method Not Allowed - 405" ]; then
    printf "PASS: '%s' gives expected 405\n" "$BASE_URL$1"
  else
    printf "FAIL: '%s' doesn't give expected 405\n" "$BASE_URL$1"
  fi
}

check_308() {
  res=$(curl -sw '%{http_code} %{redirect_url}' "$BASE_URL$1")
  if [ "$res" != "308 $BASE_URL$2" ]; then
    printf "FAIL: '%s' doesn't give 308 redirect to '%s'\n" "$BASE_URL$1" "$2"
  else
    printf "PASS: '%s' gives expected 308 redirect\n" "$BASE_URL$1"
  fi
}

check_www_to_no_www() {
  res=$(curl -sw '%{http_code} %{redirect_url}' "$BASE_URL_WWW$1")
  if [ "$res" != "308 $BASE_URL$1" ]; then
    printf "FAIL: '%s' doesn't give 308 redirect to '%s'\n" "$BASE_URL_WWW$1" "$BASE_URL$1"
  else
    printf "PASS: '%s' gives expected 308 redirect to no-www\n" "$BASE_URL_WWW$1"
  fi
}

# Assumes a valid response has at least a 500 byte response.
check_200() {
  res=$(curl --output /dev/null -sw '%{http_code} %{size_download}' "$BASE_URL$1")
  http_code=$(echo "$res" | cut -d' ' -f 1)
  size_download=$(echo "$res" | cut -d' ' -f 2)
  if [ $http_code -ne 200 ]; then
    printf "FAIL: '%s' doesn't give 200 HTTP code'\n" "$BASE_URL$1"
  elif [ $size_download -lt 500 ]; then
    printf "FAIL: '%s' content body less than 500 bytes'\n" "$BASE_URL$1"
  else
    printf "PASS: '%s' gives expected 200 HTTP code and response > 500B\n" "$BASE_URL$1"
  fi
}

check_short_cache_control() {
  res=$(curl -si "$BASE_URL$1" | grep "^cache-control:" | tr -d '\r')
  if [ "$res" != "cache-control: max-age=3600" ]; then
    printf "FAIL: '%s' doesn't give short cache-control header\n" "$BASE_URL$1"
  else
    printf "PASS: '%s' gives short cache-control header\n" "$BASE_URL$1"
  fi
}

check_long_cache_control() {
  res=$(curl -si "$BASE_URL$1" | grep "^cache-control:" | tr -d '\r')
  if [ "$res" != "cache-control: max-age=2592000, stale-while-revalidate=2592000" ]; then
    printf "FAIL: '%s' doesn't give long cache-control header\n" "$BASE_URL$1"
  else
    printf "PASS: '%s' gives long cache-control header\n" "$BASE_URL$1"
  fi
}

# POST is disallowed.
check_405 /about
check_405 /non-existent
check_405 /about/
# TODO: fails. check_405 /index.html
# TODO: fails. check_405 /

# www redirects.
check_www_to_no_www /
# Would be better to redirect directly to muxup.com/about
check_www_to_no_www /about/
check_www_to_no_www /about
# Currently redirects, but I'd rather it 404s:
check_www_to_no_www /non-existent
check_www_to_no_www /index.html
check_www_to_no_www /index.html.br

# *.html and *.html.br files are hidden.
check_404 /index.html
check_404 /index.html.br
check_404 /about.html
check_404 /about.html.br

# Paths with trailing slashes that don't correspond to servable files give
# 404.
check_404 /doesnt-exist/
check_404 /2022q3/
check_404 /static/
check_404 /static/.

# Paths with trailing slashes or include `/./` that correspond to servable
# files result in a 308 redirect.
check_308 /robots.txt/ /robots.txt
check_308 /about/ /about
check_308 /2022q3/muxup-implementation-notes/ /2022q3/muxup-implementation-notes
check_308 /static/footer/0000.svg/ /static/footer/0000.svg
check_308 /2022q3/./muxup-implementation-notes/ /2022q3/muxup-implementation-notes
# TODO: fails. check_308 /static/./footer/0000.svg /static/footer/0000.svg

# 308 redirects have long cache-control header.
check_long_cache_control /feed.xml/
check_long_cache_control /feed.xml/.
check_long_cache_control /about/
check_long_cache_control /about/./.
check_long_cache_control /about/././
# TODO: fails. check_long_cache_control /2022q3/./muxup-implementation-notes
# TODO: fails. check_long_cache_control /static/./footer/././0000.svg

# / works and has short cache control
check_200 /
check_short_cache_control /

# Other URLs mapped to *.html files work and have short cache control.
check_200 /about
check_short_cache_control /about
check_200 /2022q3/muxup-implementation-notes
check_short_cache_control /2022q3/muxup-implementation-notes

# Other files gives 200 and long cache control.
check_200 /feed.xml
check_long_cache_control /feed.xml
check_200 /static/footer/0000.svg
check_long_cache_control /static/footer/0000.svg

# Non-existing files or existing directories give 404.
check_404 /doesnt-exist
check_404 /static
check_404 /2022q3
