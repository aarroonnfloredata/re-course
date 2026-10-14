#!/usr/bin/env bash
# Challenge c4 – see "Numbers" in lesson.md.
#
# Usage: bash challenges/c4.sh LOGFILE LIMIT
#
# LOGFILE is a log file in the current folder; it always exists and its
# name can hold spaces. LIMIT is a whole number, 0 or more, written with
# digits only and without leading zeros, such as 0, 5 or 10 (never 05 or
# 010). Both are always given.
#
# Count N, the number of requests in LOGFILE with status 404: the lines
# that contain " 404 ". Then compare N with LIMIT as numbers (10 is more
# than 9, and 2 is not more than 10):
#
#   - When N is more than LIMIT, print
#       N requests with status 404: more than LIMIT
#     and exit with status 1.
#
#   - Otherwise, when N is LIMIT or less, print
#       N requests with status 404: OK
#     and exit with status 0.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
#
#   bash challenges/c4.sh access.log 1
#             prints "2 requests with status 404: more than 1", exits with 1
#   bash challenges/c4.sh access.log 2
#             prints "2 requests with status 404: OK", exits with 0
#   bash challenges/c4.sh access.log 10
#             prints "2 requests with status 404: OK", exits with 0
#
# and with ten 404 requests in access.log:
#
#   bash challenges/c4.sh access.log 9
#             prints "10 requests with status 404: more than 9", exits with 1
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c4.sh access.log 1
# To see its exit status, run echo $? right after it.

# TODO: write c4.sh
echo "c4.sh is not written yet." >&2
exit 1
