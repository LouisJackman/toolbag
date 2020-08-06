#!/bin/sh

set -o errexit
set -o nounset

readonly priv=$1
readonly der=$2
shift
shift

for kmod in "$@"
do
    echo sudo "/usr/src/kernels/$(uname -r)/scripts/sign-file" \
        sha256 \
        "$priv" \
        "$der" \
        "$(modinfo -n "$kmod")"
done

