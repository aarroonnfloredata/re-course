#!/usr/bin/env bash
# Challenge c2 – see "Reusing what matched with groups" in lesson.md.
#
# Usage: bash challenges/c2.sh LOGFILE
#
# LOGFILE is a log file in the current folder. It is always given and
# always exists. Its name can hold spaces, also several in a row, and it
# never starts with "-".
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. A path starts
# with "/" and holds no spaces; it can hold digits and dots, even ones that
# look like a status or an IP (/errors/404.html, /geo/192.0.2.44). A status
# always has three digits. Every line ends with a newline, the last one
# too, and no line is empty. LOGFILE can be empty.
#
# For each request, in the order of LOGFILE, print its status and its path,
# in that order, separated by one space:
#   STATUS PATH
# such as "404 /missing.html". Print the status and the path as they are in
# the line, and nothing else of it. An empty LOGFILE prints nothing.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Use sed -E with groups (see "Reusing what matched with groups" in
# lesson.md).
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:02 192.0.2.44 POST /login 401 64
#   2026-10-06T10:16:20 203.0.113.5 GET /errors/500.html 200 1024
#
#   bash challenges/c2.sh access.log   prints
#     200 /index.html
#     404 /missing.html
#     401 /login
#     200 /errors/500.html
#   and exits with status 0
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c2.sh access.log

# TODO: write c2.sh
echo "c2.sh is not written yet." >&2
exit 1
