#!/usr/bin/env bash
# Challenge c3 – see "Branching with if" in lesson.md.
#
# Usage: bash challenges/c3.sh LOGFILE
#
# LOGFILE is a log file in the current folder. It is always given and
# always exists. Its name can hold spaces, and the file can be empty.
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. The method is
# always GET or POST. A POST request is a line that contains " POST ", and
# a GET request a line that contains " GET ".
#
# Print one line, for the first of these cases that applies:
#
#   1. LOGFILE holds at least one POST request, with or without GET
#      requests: print
#        LOGFILE has POST requests
#
#   2. LOGFILE holds no POST request but at least one GET request: print
#        LOGFILE has only GET requests
#
#   3. LOGFILE holds neither, which happens only when it is empty: print
#        LOGFILE has no requests
#
# with LOGFILE exactly as given. Print nothing else, to stdout or to
# stderr. Don't create or change any file. Exit with status 0.
#
# Write it as one if with an elif and an else, with grep -q as each
# condition.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0
# "monday log.log" holding
#   2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512
#   2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153
# and an empty file called empty.log:
#
#   bash challenges/c3.sh access.log
#             prints "access.log has POST requests", exits with 0
#   bash challenges/c3.sh "monday log.log"
#             prints "monday log.log has only GET requests", exits with 0
#   bash challenges/c3.sh empty.log
#             prints "empty.log has no requests", exits with 0
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c3.sh access.log
# To see its exit status, run echo $? right after it.

# TODO: write c3.sh
echo "c3.sh is not written yet." >&2
exit 1
