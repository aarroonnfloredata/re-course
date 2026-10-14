#!/usr/bin/env bash
# Challenge c1 – see "A glob that matches nothing" in lesson.md.
#
# Usage: bash challenges/c1.sh
#
# It takes no arguments and works in the current folder. The folder holds
# only files, no folders. No file name starts with "-" or with a dot.
#
# For each file in the current folder whose name ends in .log, print one
# line:
#   FILE: N requests with status 404
# where FILE is the file's name and N is the number of requests in it with
# status 404: the lines that contain " 404 ". N can be 0, and the line
# always says "requests", even when N is 1. The files come in the order the
# glob *.log lists them, which is sorted by name.
#
# File names can hold spaces, also several in a row ("monday  log.log").
# Files whose names don't end in .log, such as notes.txt, are left out.
# When no file name ends in .log, print nothing.
#
# Every line of a .log file ends with a newline, the last one too, and no
# line is empty.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
# "monday log.log" holding
#   2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512
# and notes.txt holding a line of text:
#
#   bash challenges/c1.sh   prints
#     access.log: 2 requests with status 404
#     monday log.log: 0 requests with status 404
#
# and in a folder that holds only notes.txt:
#
#   bash challenges/c1.sh   prints nothing and exits with status 0
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c1.sh
# To see its exit status, run echo $? right after it.

# TODO: write c1.sh
echo "c1.sh is not written yet." >&2
exit 1
