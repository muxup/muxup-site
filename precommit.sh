#!/bin/sh

die () {
  printf "%s\n" "$*" >&2
  exit 1
}

HAD_WARN=0

warn() {
  HAD_WARN=1
  printf "!!!!!!!!! %s !!!!!!!!!\n" "$*"
}

printf "Checking types:\n"
mypy --ignore-missing-imports --strict gen || warn "Mypy failed"
printf "Checking import sorts:\n"
ruff check --target-version py312 --select I --diff gen || warn "Import sort check filed"
printf "Checking formatting:\n"
ruff format --target-version py312 --diff gen || warn "Reformatting needed"
printf "Checking flake8 lints:\n"
flake8 --max-line-length 88 --extend-ignore=E203,E302,E501,W291 gen || warn "Flake8 found issues"
if [ $HAD_WARN -ne 0 ]; then
  warn "Exiting with failures"
  exit 1
fi
