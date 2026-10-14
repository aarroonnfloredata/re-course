#!/usr/bin/env bash
# Challenge c3 – see "Globs and quotes" in lesson.md.
#
# Usage: bash challenges/c3.sh MONTH
#
# logkit's server writes one log a day into the current folder, named
# access-YYYY-MM-DD.log: access-2026-10-05.log is the log of 5 October 2026.
# MONTH is a month written as YYYY-MM, such as 2026-10. It is always given,
# and at least one log of that month exists. The folder can hold other
# files too: logs of other months, access.log, notes.txt and so on.
#
# Count the requests with status 404 in all the logs of MONTH together: the
# files whose names start with access-MONTH- and end with .log. As in
# count.sh, a request has status 404 when its line contains " 404 " (404
# with a space on each side). Lines in other files don't count.
#
# Print one line:
#   MONTH: N requests with status 404
# where MONTH is the argument as given and N is the total. N can be 0, and
# the line always says "requests", even when N is 1.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0, also when N is 0.
#
# Build the file names from MONTH with a glob, keeping MONTH in double quotes
# and the glob characters outside them. cat prints the files it is given one
# after another, so its output can go through a pipe to grep -c.
#
# Examples, with these files in the folder:
#   access-2026-09-30.log holding
#     2026-09-30T23:50:12 192.0.2.44 GET /missing.html 404 153
#   access-2026-10-05.log holding
#     2026-10-05T23:59:01 192.0.2.44 GET /about.html 200 2048
#     2026-10-05T23:59:30 203.0.113.5 GET /old/page.html 404 153
#   access-2026-10-06.log holding
#     2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#     2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
#   access.log holding
#     2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#
#   bash challenges/c3.sh 2026-10   prints "2026-10: 3 requests with status 404"
#   bash challenges/c3.sh 2026-09   prints "2026-09: 1 requests with status 404"
#
# To try it by hand, make a folder in the module folder, put a few daily
# logs in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c3.sh 2026-10

# TODO: write c3.sh
echo "c3.sh is not written yet." >&2
exit 1
