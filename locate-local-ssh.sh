#!/bin/sh

set -o errexit
set -o nounset

nmap 192.168.0.1-255 -p 22 \
    | awk 'BEGIN { RS = "Nmap scan report for " } /22\/tcp open/ { print $1 }'

