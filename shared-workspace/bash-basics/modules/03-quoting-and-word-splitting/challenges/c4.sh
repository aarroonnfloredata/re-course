#!/usr/bin/env bash
# Challenge c4 – see "Passing arguments on: shift and "$@"" in lesson.md.
#
# Usage: bash challenges/c4.sh N FILE...
#
# logkit's server writes one log a day. Given the logs oldest first, the
# last lines of all of them together are the most recent requests.
#
# N is a whole number, 1 or more. FILE... is one or more log files, as paths
# from the current folder. N and at least one FILE are always given, every
# FILE exists, and no FILE starts with "-". A FILE name can hold anything
# else a file name can: spaces, also several in a row or at the start
# ("monday  log.log"), and characters that are special to bash, such as
# * ? [ ] $ and quotes ("*.log", "[old].log"). Each FILE stands for exactly
# the file it names, never for a pattern.
#
# Every line of a FILE, its last line included, ends with a newline. A FILE
# can be empty.
#
# Take the lines of all the FILEs together, in the order given: the lines of
# the first FILE, then those of the second, and so on. Print the last N of
# those lines, unchanged and in that order: all of them when there are N or
# fewer, nothing when every FILE is empty.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# cat prints the files it is given one after another, and tail -n N keeps
# the last N lines of its input.
#
# Examples, with "monday  log.log" (two spaces between the words) holding
#   2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512
#   2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153
# and access.log holding
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:02 203.0.113.5 POST /login 401 64
#   2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
#
#   bash challenges/c4.sh 4 "monday  log.log" access.log   prints
#     2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153
#     2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#     2026-10-06T10:16:02 203.0.113.5 POST /login 401 64
#     2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
#
#   bash challenges/c4.sh 2 access.log "monday  log.log"   prints
#     2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512
#     2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153
#
#   bash challenges/c4.sh 1 "monday  log.log"   prints
#     2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153
#
#   bash challenges/c4.sh 10 "monday  log.log" access.log   prints all five
#   lines: the two of "monday  log.log", then the three of access.log
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), make a copy with spaces in its
# name (cat access.log > "monday  log.log"), go into that folder and run
#   bash ../challenges/c4.sh 3 "monday  log.log" access.log

# TODO: write c4.sh
echo "c4.sh is not written yet." >&2
exit 1
