#!/usr/bin/env bash
# Challenge c1 – see "Ending a script with exit" in lesson.md.
#
# Usage: bash challenges/c1.sh LOGFILE
#
# LOGFILE is a log file in the current folder. It is always given and
# always exists. Its name can hold spaces.
#
# Run grep -c " 404 " on LOGFILE: it prints the number of requests with
# status 404, the lines that contain " 404 ". Then print
#   grep exited with S
# where S is grep's exit status: 0 when LOGFILE holds at least one 404
# request, 1 when it holds none. Then exit with status S as well.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
# and quiet.log holding just the first of those lines:
#
#   bash challenges/c1.sh access.log   prints
#     2
#     grep exited with 0
#   and exits with status 0
#
#   bash challenges/c1.sh quiet.log   prints
#     0
#     grep exited with 1
#   and exits with status 1
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c1.sh access.log
# To see its exit status, run echo $? right after it.

# TODO: write c1.sh
echo "c1.sh is not written yet." >&2
exit 1
