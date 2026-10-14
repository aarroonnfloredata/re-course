#!/usr/bin/env bash
# Challenge c3 – see "Adding up with END" in lesson.md.
#
# Usage: bash challenges/c3.sh LOGFILE
#
# LOGFILE is a log file in the current folder. It is always given and
# always exists. Its name can hold spaces anywhere, also several in a row
# and at the start ("  tuesday   log.log"). It never holds "=" and never
# starts with "-".
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. Bytes is a whole
# number, 0 or more, written without leading zeros (0, 64 or 1024, never
# 064). Every line ends with a newline, the last one too, and no line is
# empty. LOGFILE can be empty.
#
# Print one line: the sum of the bytes fields of all requests in LOGFILE,
# as a whole number written as digits only, such as 1689. An empty
# LOGFILE prints 0. The sum never goes above 1000000000 (one billion):
# you don't need to handle bigger sums.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:48 192.0.2.44 GET /logo.png 200 1024
#   2026-10-06T10:17:03 203.0.113.5 GET /api/stats 503 0
#
#   bash challenges/c3.sh access.log   prints "1689", exits with status 0
#
# and with an empty file called empty.log:
#
#   bash challenges/c3.sh empty.log    prints "0", exits with status 0
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c3.sh access.log

# TODO: write c3.sh
echo "c3.sh is not written yet." >&2
exit 1
