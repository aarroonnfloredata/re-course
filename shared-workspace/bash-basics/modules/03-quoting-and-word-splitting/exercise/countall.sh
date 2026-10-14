#!/usr/bin/env bash
# countall.sh: the third logkit tool. It counts the requests with a given
# status in each of several log files.
#
# Usage: bash exercise/countall.sh STATUS FILE...
#
# STATUS is a status code, such as 404 or 500. FILE... is one or more log
# files, as paths from the current folder (for example access.log, or
# logs/monday.log). STATUS and at least one FILE are always given and
# every FILE exists (checking that comes in module 4), and no FILE starts
# with "-".
#
# A FILE name can hold anything else a file name can: spaces, also several
# in a row or at the start ("monday  log.log"), and characters that are
# special to bash, such as * ? [ ] $ and quotes ("*.log", "logs/[old].log").
# Each FILE stands for exactly the file it names, never for a pattern.
#
# Each line of a log file is one request, with six fields separated by
# single spaces: time, client IP, method, path, status and bytes. As in
# count.sh, a request has status STATUS when its line contains STATUS with a
# space on each side (" 404 " for 404). A line with STATUS only in another
# field doesn't count, for example 404 in the path /errors/404.html, or as
# the bytes at the end of the line. Nor does a longer status that starts
# with STATUS: with STATUS 40, a 404 request doesn't count.
#
# For each FILE, in the order given, print one line:
#   FILE:N
# where FILE is the name exactly as given and N is the number of requests in
# that FILE with status STATUS. N can be 0. The line has the "FILE:" part
# also when only one FILE is given, and a FILE given twice gets two lines.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file.
#
# Exit with status 0 when at least one FILE holds a request with status
# STATUS, and with status 1 when none does (every N is 0). That is grep's own
# exit status: grep exits with 1 when it finds no matching line, and a
# script ends with the status of its last command.
#
# One grep command does the counting for all the files: no loop is needed.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404
#   2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
# "monday log.log" holding
#   2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512
#   2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153
# and "logs/tuesday [old].log" holding
#   2026-10-04T18:20:31 192.0.2.44 POST /upload 500 0
#
#   bash exercise/countall.sh 404 access.log "monday log.log"   prints
#     access.log:2
#     monday log.log:1
#
#   bash exercise/countall.sh 404 "monday log.log"   prints
#     monday log.log:1
#
#   bash exercise/countall.sh 500 access.log "monday log.log" "logs/tuesday [old].log"   prints
#     access.log:0
#     monday log.log:0
#     logs/tuesday [old].log:1
#
#   bash exercise/countall.sh 401 access.log "monday log.log"   prints
#     access.log:0
#     monday log.log:0
#   and exits with status 1
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), make a copy with a space in its
# name (cat access.log > "monday log.log"), go into that folder and run
#   bash ../exercise/countall.sh 404 access.log "monday log.log"
# To see its exit status, run echo $? right after it.
#
# Write it so that `learn check` passes.

# TODO: write countall.sh
echo "countall.sh is not written yet." >&2
exit 1
