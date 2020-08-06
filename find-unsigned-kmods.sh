#!/bin/sh

set -o errexit
set -o nounset

find /lib/modules -name '*.ko' -exec grep -FL '~Module signature appended~' {} \+

