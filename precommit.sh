#!/bin/sh

die () {
  printf "%s\n" "$*" >&2
  exit 1
}

mypy --ignore-missing-imports --strict build.py || die "mypy failed"
isort --profile black -c build.py || die "quitting"
black --check build.py || die "black reports build.py needs reformatting"
flake8 --max-line-length 88 --extend-ignore=E203,E302,E501,W291 build.py || die "flake8 found issues"
