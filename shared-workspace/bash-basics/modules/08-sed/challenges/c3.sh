#!/usr/bin/env bash
# Challenge c3 – see "Choosing lines with d and -n" in lesson.md.
#
# Usage: bash challenges/c3.sh LOGFILE FIRST LAST
#
# LOGFILE is a log file in the current folder. Its name can hold spaces,
# also several in a row, and it never starts with "-". FIRST and LAST are
# line numbers: whole numbers, 1 or more, written without leading zeros
# (3, never 03). FIRST is never bigger than LAST. All three are always
# given, and LOGFILE always exists.
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. Every line ends
# with a newline, the last one too, and no line is empty. LOGFILE can be
# empty.
#
# Print lines FIRST to LAST of LOGFILE, both included, unchanged and in
# the order of LOGFILE. Line 1 is the first line. When FIRST and LAST are
# the same, print that one line. When LOGFILE has fewer than LAST lines,
# print from line FIRST to its last line; when it has fewer than FIRST
# lines, print nothing.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0, also when nothing is printed.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:02 192.0.2.44 POST /login 401 64
#   2026-10-06T10:16:20 127.0.0.1 GET /health 200 2
#   2026-10-06T10:16:48 203.0.113.5 GET /about.html 200 2048
#
#   bash challenges/c3.sh access.log 2 4   prints
#     2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#     2026-10-06T10:16:02 192.0.2.44 POST /login 401 64
#     2026-10-06T10:16:20 127.0.0.1 GET /health 200 2
#
#   bash challenges/c3.sh access.log 3 3   prints
#     2026-10-06T10:16:02 192.0.2.44 POST /login 401 64
#
#   bash challenges/c3.sh access.log 4 9   prints
#     2026-10-06T10:16:20 127.0.0.1 GET /health 200 2
#     2026-10-06T10:16:48 203.0.113.5 GET /about.html 200 2048
#
#   bash challenges/c3.sh access.log 6 8   prints nothing
#
# Each of them exits with status 0.
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c3.sh access.log 2 4

# TODO: write c3.sh
echo "c3.sh is not written yet." >&2
exit 1
