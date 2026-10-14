#!/usr/bin/env bash
# Challenge c1 – see "Where a name ends: ${ }" in lesson.md.
#
# logkit keeps a dated copy of each log. Make a copy of access.log (in the
# current folder; it always exists) named after the log and the day:
# access_2026-10-06.log, that is the name access, an underscore, the day
# 2026-10-06 and .log.
#
#   1. Copy the lines of access.log to access_2026-10-06.log, replacing
#      whatever access_2026-10-06.log held before (create it if it doesn't
#      exist). Leave access.log as it is. Copy it the way module 1 did,
#      with cat and >: cat today.log > latest.log copies the lines of
#      today.log to latest.log.
#   2. Then print one line:
#        saved access.log as access_2026-10-06.log
#
# Print nothing else, to stdout or to stderr, and exit with status 0.
#
# The check looks only at the result: what the script prints and the file
# it leaves. Building the names is the point of the practice: start the
# script with two variables, name=access and day=2026-10-06, and build both
# file names from them with $ and ${ } instead of typing the text again.
#
# Example, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#
#   bash challenges/c1.sh   prints "saved access.log as access_2026-10-06.log"
#                           and leaves access_2026-10-06.log holding the
#                           same two lines as access.log
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c1.sh
# then look at access_2026-10-06.log with cat.

# TODO: write c1.sh
echo "c1.sh is not written yet." >&2
exit 1
