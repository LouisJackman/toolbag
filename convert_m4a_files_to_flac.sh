#!/usr/bin/env sh

set -o errexit
set -o nounset

# Set to the number of logical processors the device has.
procs=16

find_to_convert() {
    find "$1" -type f -iname '*.m4a'
}

convert_file() {
    ffmpeg -i "$1" -map_metadata 0 "${1%.*}.flac" && rm "$1"
}

convert() (
    local file

    IFS='
'
    while :
    do
        for _ in seq 1 "$procs"
        do
            read file
            convert_file "$file" &
        done
        wait
    done
)

find_to_convert "$1" | convert

