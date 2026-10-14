#!/usr/bin/env bash
# Challenge c3 – see "Capturing output: $( )" in lesson.md.
#
# Count the GET and the POST requests in access.log (in the current folder;
# it always exists) and print both counts on one line:
#   N GET, M POST
# where N is the number of lines that contain " GET " (GET with a space on
# each side) and M the number of lines that contain " POST ". Either count
# can be 0. Print nothing else, to stdout or to stderr, and exit with status 0.
#
# Examples, with access.log holding
#   2026-10-06T10:15:20 192.0.2.44 POST /login 401 64
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 2048
#
#   bash challenges/c3.sh   prints "3 GET, 1 POST"
#
# and with an empty access.log:
#
#   bash challenges/c3.sh   prints "0 GET, 0 POST"
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c3.sh

# TODO: write c3.sh
echo "c3.sh is not written yet." >&2
exit 1
