#!/usr/bin/env bash
# Challenge c3 – see "Leaving lines out and ignoring case" in lesson.md.
#
# Usage: bash challenges/c3.sh LOGFILE
#
# LOGFILE is a log file in the current folder. It is always given and
# always exists. Its name can hold spaces, also several in a row, and it
# never starts with "-".
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. The method is
# always in uppercase (GET, POST, ...). A path starts with "/", holds no
# spaces and can hold letters in either case. Every line ends with a
# newline, the last one too, and no line is empty. LOGFILE can be empty.
#
# Print every request except those for the path /health, in any mix of
# upper- and lowercase: /health, /Health and /HEALTH are left out. Only that
# exact path is left out: /healthz, /health/db and /api/health are printed.
# Print the requests unchanged, in the order of LOGFILE.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file.
#
# Exit with status 0 when it printed at least one request, and with status
# 1 when it printed none (every request was for /health, or LOGFILE is
# empty). That is grep's own exit status.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 127.0.0.1 GET /health 200 2
#   2026-10-06T10:16:02 127.0.0.1 GET /Health 200 2
#   2026-10-06T10:16:15 192.0.2.44 GET /healthz 404 153
#   2026-10-06T10:16:20 198.51.100.7 GET /api/health 200 17
#   2026-10-06T10:16:48 127.0.0.1 GET /HEALTH 200 2
#
#   bash challenges/c3.sh access.log   prints
#     2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#     2026-10-06T10:16:15 192.0.2.44 GET /healthz 404 153
#     2026-10-06T10:16:20 198.51.100.7 GET /api/health 200 17
#   and exits with status 0
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c3.sh access.log

# TODO: write c3.sh
echo "c3.sh is not written yet." >&2
exit 1
