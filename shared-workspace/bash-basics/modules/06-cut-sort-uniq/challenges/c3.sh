#!/usr/bin/env bash
# Challenge c3 – see "Counting with uniq" in lesson.md.
#
# Usage: bash challenges/c3.sh LOGFILE
#
# LOGFILE is a log file in the current folder. It is always given and
# always exists. Its name can hold spaces, also several in a row, and it
# never starts with "-".
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. A status always
# has three digits, from 100 to 599. Every line ends with a newline, the
# last one too, and no line is empty. LOGFILE can be empty.
#
# For each status that occurs in LOGFILE, print one line:
#   STATUS COUNT
# where COUNT is the number of requests with that status. The line holds
# one space, between STATUS and COUNT, and no other spaces. Each status
# gets one line, however its requests are spread through LOGFILE, and the
# lines come in order of status, lowest first. An empty LOGFILE prints
# nothing.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:02 203.0.113.5 POST /login 401 64
#   2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 2048
#   2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0
#   2026-10-06T10:16:48 192.0.2.44 GET /index.html 200 512
#   2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
#
#   bash challenges/c3.sh access.log   prints
#     200 3
#     401 1
#     404 2
#     503 1
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c3.sh access.log

# TODO: write c3.sh
echo "c3.sh is not written yet." >&2
exit 1
