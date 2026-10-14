#!/usr/bin/env bash
# Challenge c1 – see "Double quotes" in lesson.md.
#
# Usage: bash challenges/c1.sh LOGFILE
#
# LOGFILE is the name of a log file in the current folder. It always exists
# and holds at least one line. Its name can hold spaces, also several in a
# row or at the start, and glob characters such as * ? [ ].
#
# Print two lines:
#   Last request in LOGFILE:
#   the last line of LOGFILE, unchanged
# where LOGFILE in the first line is the name exactly as given, with all its
# spaces.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Examples, with "monday  log.log" (two spaces between the words) holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#
#   bash challenges/c1.sh "monday  log.log"   prints
#     Last request in monday  log.log:
#     2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#
# and with access.log holding just the first of those two lines:
#
#   bash challenges/c1.sh access.log   prints
#     Last request in access.log:
#     2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#
# To try it by hand, make a folder in the module folder, put a log with
# spaces in its name in it (cat access.log > "monday  log.log" makes one
# from an access.log), go into that folder and run
#   bash ../challenges/c1.sh "monday  log.log"

# TODO: write c1.sh
echo "c1.sh is not written yet." >&2
exit 1
