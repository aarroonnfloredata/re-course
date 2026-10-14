#!/usr/bin/env bash
# Challenge c1 – see "Tests: name, type and size" in lesson.md.
#
# Usage: bash challenges/c1.sh DIR
#
# DIR is a folder, as a path from the current folder (for example logs, or
# . for the current folder itself). It is always given and is always an
# existing folder. Its name can hold spaces, also several in a row and at
# the start ("  old logs"), and glob characters such as * ? [ ]. It never
# ends with "/", never starts with "-", "!" or "(", and never holds a
# newline.
#
# Find the big log files: the regular files under DIR, directly in it or in
# a subfolder at any depth, whose names end in exactly .log and that hold
# more than 1024 bytes.
#
#   - A file of 1025 bytes or more is big; one of 1024 bytes or fewer is
#     not.
#   - access.log.old, server.LOG and notes.txt are never log files,
#     whatever their size. Nor is a folder, also when its name ends in .log
#     (archive.log); the files inside it can be.
#   - What a file holds doesn't matter, only its name, type and size.
#
# The names of the files and folders under DIR can hold spaces, also
# several in a row and at the start, glob characters such as * ? [ ],
# quotes (' and ") and a leading "-". They never hold a newline and never
# start with ".". DIR holds only files and folders: no links.
#
# Print the path of each big log file on a line of its own, as find prints
# it: DIR exactly as given, a "/", then the path inside DIR, such as
# logs/old/monday log.log ("./access.log" when DIR is .). Print the paths
# in any order: find doesn't sort them, and they don't need sorting. When
# there is no big log file, print nothing.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Examples, with a folder called logs holding
#   access.log            2000 bytes
#   small.log             1024 bytes
#   empty.log             0 bytes
#   notes.txt             3000 bytes
#   old/monday log.log    1500 bytes
#   archive.log           a folder, holding a 1100-byte old.txt
#
#   bash challenges/c1.sh logs   prints, in any order,
#     logs/access.log
#     logs/old/monday log.log
#   and exits with status 0
#
# To try it by hand, make a folder in the module folder and go into it.
# Run mkdir -p logs/old, make a big file with cat ../lesson.md > logs/big.log
# and a small one with echo hello > logs/old/small.log. Then run
#   bash ../challenges/c1.sh logs
# It prints logs/big.log.

# TODO: write c1.sh
echo "c1.sh is not written yet." >&2
exit 1
