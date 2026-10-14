#!/usr/bin/env bash
# bytes.sh: the ninth logkit tool. It adds up how many bytes a web server
# sent: for all requests, and for the ones that failed.
#
# Usage: bash exercise/bytes.sh LOGFILE
#
# LOGFILE is the log file to read, as a path from the current folder (for
# example access.log, or logs/monday.log). It is always given and always
# exists. Its name can hold spaces anywhere, also several in a row and at
# the start ("  tuesday   log.log"), and glob characters such as * ? [ ].
# It never holds "=" and never starts with "-".
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. A path starts
# with "/" and holds no spaces; it can hold digits, even ones that look
# like a status (/errors/404.html). A status always has three digits, from
# 100 to 599. Bytes is a whole number, 0 or more, written without leading
# zeros (0, 64 or 1024, never 064); it can look like a status too (404).
# Every line ends with a newline, the last one too, and no line is empty.
# LOGFILE can be empty.
#
# Print two lines:
#   total: T bytes
#   errors: E bytes
# where
#   T  is the sum of the bytes fields of all requests in LOGFILE;
#   E  is the sum of the bytes fields of the requests that failed: the
#      ones whose status is 400 or more (4xx and 5xx). Status 400 counts;
#      a status from 100 to 399 doesn't. A status or a bytes value in any
#      other field doesn't count either: only the status field decides.
# T and E are whole numbers, written as digits only, and either can be 0.
# E is 0 when no request failed. An empty LOGFILE prints
#   total: 0 bytes
#   errors: 0 bytes
# Neither sum goes above 1000000000 (one billion): you don't need to
# handle bigger sums.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# One awk program does it: an action without a pattern that adds up the
# bytes of every request, a pattern-action pair that adds up the bytes of
# the failed ones, and an END block that prints both sums (see "Adding up
# with END" and "Several totals in one program" in lesson.md).
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0
#   2026-10-06T10:16:48 192.0.2.44 GET /errors/503.html 200 1024
#   2026-10-06T10:17:03 203.0.113.5 POST /login 401 64
#   2026-10-06T10:17:45 192.0.2.44 GET /old.html 301 404
#
#   bash exercise/bytes.sh access.log   prints
#     total: 2157 bytes
#     errors: 217 bytes
#
# with clean.log holding only the first and fourth line of access.log:
#
#   bash exercise/bytes.sh clean.log   prints
#     total: 1536 bytes
#     errors: 0 bytes
#
# and with an empty file called "empty day.log":
#
#   bash exercise/bytes.sh "empty day.log"   prints
#     total: 0 bytes
#     errors: 0 bytes
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../exercise/bytes.sh access.log
#
# Write it so that `learn check` passes.

# TODO: write bytes.sh
echo "bytes.sh is not written yet." >&2
exit 1
