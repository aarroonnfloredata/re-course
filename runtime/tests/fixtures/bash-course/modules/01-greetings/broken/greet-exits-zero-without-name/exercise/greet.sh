#!/usr/bin/env bash
# Broken variant: exits with status 0 when NAME is missing.
# greet.sh: greet a guest and add them to the guest list.
#
# Usage: bash exercise/greet.sh NAME
#
# Print "Hello, NAME!", add NAME as a new line at the end of guests.txt in
# the current folder (creating the file if needed) and exit with status 0.
#
# Without a NAME, print "usage: greet.sh NAME" to stderr, leave guests.txt
# alone and exit with status 2.
#
# Examples:
#   bash exercise/greet.sh Ada   prints "Hello, Ada!" and adds Ada to guests.txt
#   bash exercise/greet.sh       prints "usage: greet.sh NAME" to stderr, exits with 2
#
# Write it so that `learn check` passes.

if [ "$#" -eq 0 ]; then
    echo "usage: greet.sh NAME" >&2
    exit 0
fi
echo "Hello, $1!"
echo "$1" >> guests.txt
