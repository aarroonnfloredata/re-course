#!/usr/bin/env bash
# Challenge c1 – see "Runs of spaces" in lesson.md.
#
# Usage: bash challenges/c1.sh LOGFILE
#
# LOGFILE is a log file in the current folder. It is always given and
# always exists. Its name can hold spaces anywhere, also several in a row
# and at the start ("  tuesday   log.log"). It never holds "=" and never
# starts with "-".
#
# LOGFILE comes from a server that lines up its columns. Each line is one
# request with six fields: time, client IP, method, path, status and
# bytes. Fields are separated by one or more spaces, and how many differs
# from line to line. No field holds a space. Every line ends with a
# newline, the last one too, and no line is empty. LOGFILE can be empty.
#
# For each request, in the order of LOGFILE, print its client IP and its
# path, separated by one space:
#   IP PATH
# such as "203.0.113.5 /index.html". An empty LOGFILE prints nothing.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5   GET  /index.html    200  512
#   2026-10-06T10:15:40 198.51.100.7  GET  /missing.html  404  153
#   2026-10-06T10:16:02 192.0.2.44    POST /login         401  64
#
#   bash challenges/c1.sh access.log   prints
#     203.0.113.5 /index.html
#     198.51.100.7 /missing.html
#     192.0.2.44 /login
#   and exits with status 0
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c1.sh access.log

# TODO: write c1.sh
echo "c1.sh is not written yet." >&2
exit 1
