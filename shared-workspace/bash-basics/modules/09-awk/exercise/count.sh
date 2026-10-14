#!/usr/bin/env bash
# count.sh: the second logkit tool. It counts the requests in a log file
# that have a given status.
#
# Usage: bash exercise/count.sh LOGFILE STATUS
#
# LOGFILE is the log file to read, as a path from the current folder (for
# example access.log, or logs/monday.log). It always exists: checking that
# comes in module 4. STATUS is a status code, such as 404 or 500.
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. As in
# notfound.sh, a request has status STATUS when its line contains STATUS
# with a space on each side (" 404 " for 404). A line with STATUS only in
# another field doesn't count, for example 404 in the path /errors/404.html,
# or as the bytes at the end of the line. Nor does a longer status that
# starts with STATUS: with STATUS 40, a 404 request doesn't count.
#
# Print one line:
#   LOGFILE: N requests with status STATUS
# where LOGFILE and STATUS are the two arguments exactly as given, and N is
# the number of requests in LOGFILE with that status. N can be 0, and the
# line always says "requests", even when N is 1.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0, also when N is 0.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:02 203.0.113.5 POST /login 401 64
#   2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404
#   2026-10-06T10:16:48 192.0.2.44 GET /errors/404.html 200 1024
#   2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
#
#   bash exercise/count.sh access.log 404   prints "access.log: 2 requests with status 404"
#   bash exercise/count.sh access.log 200   prints "access.log: 3 requests with status 200"
#   bash exercise/count.sh access.log 401   prints "access.log: 1 requests with status 401"
#   bash exercise/count.sh access.log 500   prints "access.log: 0 requests with status 500"
#
# and with the same lines in logs/monday.log:
#
#   bash exercise/count.sh logs/monday.log 404
#                         prints "logs/monday.log: 2 requests with status 404"
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../exercise/count.sh access.log 404
#
# Write it so that `learn check` passes.

logfile="$1"
status="$2"
count=$(grep -c " $status " "$logfile")
echo "$logfile: $count requests with status $status"
