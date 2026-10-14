#!/usr/bin/env bash
# notfound.sh: the first logkit tool. It finds the requests in a web
# server's access log that failed with status 404 (Not Found).
#
# Usage: bash exercise/notfound.sh
#
# It works in the current folder: it reads access.log there and writes
# notfound.log and errors.txt there.
#
# Each line of access.log is one request, with six fields separated by
# single spaces: time, client IP, method, path, status and bytes. A request
# has status 404 when its line contains " 404 " (404 with a space on each
# side). A line with 404 only in another field is not a 404 request, for
# example the path /errors/404.html, or 404 as the bytes at the end of the
# line.
#
# One grep command with its redirections handles both cases below: no if
# is needed.
#
# When access.log exists:
#   1. Save every 404 request to notfound.log, unchanged and in the order of
#      access.log, replacing whatever notfound.log held before. With no 404
#      requests, notfound.log ends up empty.
#   2. Then print the last three lines of notfound.log: all of them when
#      there are three or fewer, nothing when there are none.
#   errors.txt ends up empty, and nothing is printed to stderr.
#
# When access.log is missing:
#   grep's error message goes to errors.txt instead of the screen:
#   errors.txt ends up holding just that message, one line that names
#   access.log. Its exact wording depends on the system. Nothing is
#   printed, to stdout or to stderr, and notfound.log ends up empty.
#
# In both cases notfound.log and errors.txt are replaced, never added to,
# and the script exits with status 0.
#
# Status 0 means success; a script ends with the status of its last command.
#
# Example, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:02 203.0.113.5 GET /old/page.html 404 153
#   2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404
#   2026-10-06T10:16:48 192.0.2.44 GET /errors/404.html 200 1024
#   2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
#   2026-10-06T10:17:30 192.0.2.44 POST /login.php 404 153
#
#   bash exercise/notfound.sh   writes the four 404 requests (10:15:40,
#                               10:16:02, 10:17:03 and 10:17:30) to
#                               notfound.log, leaves errors.txt empty and
#                               prints
#     2026-10-06T10:16:02 203.0.113.5 GET /old/page.html 404 153
#     2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
#     2026-10-06T10:17:30 192.0.2.44 POST /login.php 404 153
#
# and in a folder without access.log:
#
#   bash exercise/notfound.sh   prints nothing, leaves notfound.log empty
#                               and errors.txt holding grep's error message
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../exercise/notfound.sh
# then look at notfound.log and errors.txt with cat. Remove access.log to
# try the other case.
#
# Write it so that `learn check` passes.

grep " 404 " access.log > notfound.log 2> errors.txt
tail -n 3 notfound.log
