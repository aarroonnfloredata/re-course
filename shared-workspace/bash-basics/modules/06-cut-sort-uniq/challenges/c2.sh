#!/usr/bin/env bash
# Challenge c2 – see "Sorting with sort" in lesson.md.
#
# Usage: bash challenges/c2.sh LOGFILE
#
# LOGFILE is a log file in the current folder. It is always given and
# always exists. Its name can hold spaces, also several in a row, and it
# never starts with "-".
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. Bytes is a whole
# number, 0 or more, written without leading zeros (0, 64 or 1024, never
# 064). Every line ends with a newline, the last one too, and no line is
# empty. LOGFILE can be empty.
#
# Print the bytes field of every request, one number per line, sorted as
# numbers, biggest first. A number that several requests have is printed
# once for each of them. An empty LOGFILE prints nothing.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:02 203.0.113.5 POST /login 401 64
#   2026-10-06T10:16:48 192.0.2.44 GET /logo.png 200 4096
#   2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
#   2026-10-06T10:17:30 192.0.2.44 POST /upload 500 0
#
#   bash challenges/c2.sh access.log   prints
#     4096
#     512
#     153
#     153
#     64
#     0
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c2.sh access.log

# TODO: write c2.sh
echo "c2.sh is not written yet." >&2
exit 1
