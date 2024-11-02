#!/bin/sh

die () {
  printf "%s\n" "$*" >&2
  exit 1
}

mypy --ignore-missing-imports --strict build.py || die "mypy failed"
ruff check --target-version py312 --select I --diff build.py || die "Import sorting needed"
ruff format --target-version py312 --diff build.py || die "Reformatting needed"
flake8 --max-line-length 88 --extend-ignore=E203,E302,E501,W291 build.py || die "flake8 found issues"
