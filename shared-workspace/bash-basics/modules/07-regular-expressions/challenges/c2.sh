#!/usr/bin/env bash
# Challenge c2 – see "Repeating with *, +, ? and { }" in lesson.md.
#
# Usage: bash challenges/c2.sh LOGFILE
#
# LOGFILE is a log file in the current folder. It is always given and
# always exists. Its name can hold spaces, also several in a row, and it
# never starts with "-".
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. Bytes, the last
# field, is a whole number, 0 or more, written without leading zeros (0, 64
# or 1024, never 064). Other fields hold digits too: the time always does
# (2026-10-06T10:15:32), and a path can (/reports/2026.html). Every line
# ends with a newline, the last one too, and no line is empty. LOGFILE can
# be empty.
#
# Print the requests that sent 1000 bytes or more: the lines whose bytes
# field is 1000 or bigger. Print them unchanged, in the order of LOGFILE.
# Digits in the other fields don't count.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file.
#
# Exit with status 0 when it printed at least one request, and with status
# 1 when it printed none (also when LOGFILE is empty). That is grep's own
# exit status.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /about.html 200 1000
#   2026-10-06T10:16:02 192.0.2.44 GET /reports/2026.html 200 999
#   2026-10-06T10:16:15 192.0.2.44 GET /logo.png 200 40960
#   2026-10-06T10:16:20 203.0.113.5 GET /missing.html 404 0
#
#   bash challenges/c2.sh access.log   prints
#     2026-10-06T10:15:40 198.51.100.7 GET /about.html 200 1000
#     2026-10-06T10:16:15 192.0.2.44 GET /logo.png 200 40960
#   and exits with status 0
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c2.sh access.log

# TODO: write c2.sh
echo "c2.sh is not written yet." >&2
exit 1
