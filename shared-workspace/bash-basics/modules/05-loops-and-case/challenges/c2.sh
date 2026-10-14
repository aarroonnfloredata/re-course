#!/usr/bin/env bash
# Challenge c2 – see "Counting in a loop" in lesson.md.
#
# Usage: bash challenges/c2.sh LOGFILE
#
# LOGFILE is a log file in the current folder. It is always given and
# always exists. Its name can hold spaces, also several in a row.
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. Bytes is a whole
# number, 0 or more, written without leading zeros (0, 64 or 1024, never
# 064). Every line ends with a newline, the last one too, and no line is
# empty. LOGFILE can be empty.
#
# Read LOGFILE line by line and print one line:
#   LOGFILE: R requests, B bytes
# where LOGFILE is exactly as given, R is the number of requests (lines) in
# it and B is the sum of their bytes fields. For an empty LOGFILE, R and B
# are both 0. The line always says "requests", even when R is 1.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0
# and an empty file called empty.log:
#
#   bash challenges/c2.sh access.log   prints "access.log: 3 requests, 665 bytes"
#   bash challenges/c2.sh empty.log    prints "empty.log: 0 requests, 0 bytes"
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c2.sh access.log

# TODO: write c2.sh
echo "c2.sh is not written yet." >&2
exit 1
