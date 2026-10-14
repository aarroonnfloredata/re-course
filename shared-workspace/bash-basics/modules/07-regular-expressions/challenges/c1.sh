#!/usr/bin/env bash
# Challenge c1 – see "Sets of characters" in lesson.md.
#
# Usage: bash challenges/c1.sh LOGFILE
#
# LOGFILE is a log file in the current folder. It is always given and
# always exists. Its name can hold spaces, also several in a row, and it
# never starts with "-".
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. The time comes
# first and always has the form 2026-10-06T10:15:32: the date (year, month
# and day), a T, then hours, minutes and seconds. A path can hold a date
# too, such as /reports/2026-10-06.html. Every line ends with a newline,
# the last one too, and no line is empty. LOGFILE can be empty.
#
# Print the requests made on 5, 6 or 7 October 2026: the lines whose time
# starts with 2026-10-05, 2026-10-06 or 2026-10-07. Print them unchanged, in
# the order of LOGFILE. A date anywhere else in the line doesn't count: a
# request made on 2026-10-08 for /reports/2026-10-06.html is not printed.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file.
#
# Exit with status 0 when it printed at least one request, and with status
# 1 when it printed none (also when LOGFILE is empty). That is grep's own
# exit status.
#
# Examples, with access.log holding
#   2026-10-04T23:59:58 192.0.2.44 GET /index.html 200 512
#   2026-10-05T08:00:03 203.0.113.5 GET /about.html 200 2048
#   2026-10-07T17:45:12 198.51.100.7 GET /missing.html 404 153
#   2026-10-08T09:30:00 192.0.2.44 GET /reports/2026-10-06.html 200 1024
#   2026-10-15T10:15:32 203.0.113.5 GET /index.html 200 512
#
#   bash challenges/c1.sh access.log   prints
#     2026-10-05T08:00:03 203.0.113.5 GET /about.html 200 2048
#     2026-10-07T17:45:12 198.51.100.7 GET /missing.html 404 153
#   and exits with status 0
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c1.sh access.log

# TODO: write c1.sh
echo "c1.sh is not written yet." >&2
exit 1
