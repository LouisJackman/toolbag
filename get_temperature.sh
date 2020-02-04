#!/bin/sh

set -o errexit
set -o nounset

path_1=/sys/class/thermal/thermal_zone0/temp
path_2=/sys/class/hwmon/hwmon0/temp1_input

if [ -f "$path_1" ]
then
    path_to_use=$path_1
elif [ -f "$path_2" ]
then
    path_to_use=$path_2
else
    echo 'Error: temperature paths not found; are you running outside of Linux or inside a container?' >&2
    exit 1
fi

normalise=$(cat <<'EOF'

{
    if (length($1) < 4) {
        temperature = $1
    } else {
        temperature = $1 / 1000
    }

    printf "%dC\n", temperature
}

EOF
)

awk "$normalise" "$path_to_use"

