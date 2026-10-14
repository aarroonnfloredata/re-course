#!/usr/bin/env bash
# Challenge c2 – see "Combining tests" in lesson.md.
#
# Usage: bash challenges/c2.sh DIR
#
# DIR is a folder, as a path from the current folder (for example logs, or
# . for the current folder itself). It is always given and is always an
# existing folder. Its name can hold spaces, also several in a row and at
# the start ("  old logs"), and glob characters such as * ? [ ]. It never
# ends with "/", never starts with "-", "!" or "(", and never holds a
# newline.
#
# Find the logs to keep: the regular files under DIR, directly in it or in
# a subfolder at any depth, whose names end in .log or in .old, and that
# are not empty (they hold at least one byte).
#
#   - access.log, access.log.old, monday.old and "old/monday log.log" are
#     kept when they are not empty. notes.txt, access.log.gz and
#     server.LOG never are.
#   - An empty file (0 bytes) is never kept, whatever its name.
#   - A folder is never kept, also when its name ends in .log or .old
#     (archive.old); the files inside it can be.
#   - What a file holds doesn't matter, only its name, its type and
#     whether it is empty.
#
# The names of the files and folders under DIR can hold spaces, also
# several in a row and at the start, glob characters such as * ? [ ],
# quotes (' and ") and a leading "-". They never hold a newline and never
# start with ".". DIR holds only files and folders: no links.
#
# Print the path of each file to keep on a line of its own, as find prints
# it: DIR exactly as given, a "/", then the path inside DIR, such as
# logs/old/monday log.log ("./access.log" when DIR is .). Print the paths
# in any order: find doesn't sort them, and they don't need sorting. When
# there is no file to keep, print nothing.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Examples, with a folder called logs holding
#   access.log            a line of text
#   access.log.old        a line of text
#   empty.log             nothing (0 bytes)
#   empty.old             nothing (0 bytes)
#   notes.txt             a line of text
#   archive.old           a folder, holding monday.log with a line of text
#
#   bash challenges/c2.sh logs   prints, in any order,
#     logs/access.log
#     logs/access.log.old
#     logs/archive.old/monday.log
#   and exits with status 0
#
# To try it by hand, make a folder in the module folder and go into it.
# Build the logs folder above with mkdir -p, echo and touch (see "Combining
# tests" in lesson.md), then run
#   bash ../challenges/c2.sh logs

# TODO: write c2.sh
echo "c2.sh is not written yet." >&2
exit 1
