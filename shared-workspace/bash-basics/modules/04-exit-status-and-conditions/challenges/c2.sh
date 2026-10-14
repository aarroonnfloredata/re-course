#!/usr/bin/env bash
# Challenge c2 – see "&& and ||" in lesson.md.
#
# Usage: bash challenges/c2.sh LOGFILE
#
# LOGFILE is a log file in the current folder. It is always given and
# always exists. Its name can hold spaces, and it is never
# server-errors.log or notfound.log.
#
# Do two steps, in this order:
#
#   1. Save every request in LOGFILE with status 500, the lines that
#      contain " 500 ", to server-errors.log in the current folder,
#      unchanged and in the order of LOGFILE, replacing whatever
#      server-errors.log held before. Then, only when there was at least
#      one, print
#        500 requests saved to server-errors.log
#
#   2. Save every request with status 404, the lines that contain " 404 ",
#      to notfound.log in the same way. Then, only when there was none,
#      print
#        no 404 requests in LOGFILE
#      with LOGFILE exactly as given.
#
# Both files are written every time: a file with no matching request ends
# up empty.
#
# Print nothing else, to stdout or to stderr. Leave every other file as it
# is. Exit with status 0.
#
# Each step is one line: a grep command and an echo, joined by && or ||.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0
# and quiet.log holding just the first of those lines:
#
#   bash challenges/c2.sh access.log   prints
#     500 requests saved to server-errors.log
#   and leaves the 500 request in server-errors.log and the 404 request
#   in notfound.log
#
#   bash challenges/c2.sh quiet.log   prints
#     no 404 requests in quiet.log
#   and leaves server-errors.log and notfound.log empty
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c2.sh access.log
# then look at server-errors.log and notfound.log with cat.

# TODO: write c2.sh
echo "c2.sh is not written yet." >&2
exit 1
