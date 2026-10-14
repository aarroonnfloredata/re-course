#!/usr/bin/env bash
# Challenge c1 – see "Functions" and "Local variables" in lesson.md.
#
# This file holds only a function and comments: the check loads it with
# source and calls report_404.
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines below will do), go into that folder, start bash
# and run
#   source ../challenges/c1.sh
# source loads the file's function into your shell (see "Loading functions
# with source" in lesson.md). Then call report_404 access.log. Run source
# again after each change to this file.

# report_404 LOGFILE...: for each LOGFILE, in the order given, print one
# line
#   LOGFILE: N
# where LOGFILE is the name exactly as given and N is the number of 404
# requests in it, as digits only. N can be 0. A LOGFILE given twice gets
# two lines. With no LOGFILE at all, print nothing.
#
# Each LOGFILE is a path from the current folder. It always exists and is a
# regular file. Its name can hold spaces anywhere, also several in a row
# and at the start, glob characters such as * ? [ ], and "=". It never
# starts with "-" and never holds a newline.
#
# Each line of a log file is one request, with six fields separated by
# single spaces: time, client IP, method, path, status and bytes. As in
# count.sh, a request has status 404 when its line contains " 404 " (404
# with a space on each side): 404 in the path (/errors/404.html) or as the
# bytes at the end of the line doesn't count. Every line ends with a
# newline, the last one too, and no line is empty. A log file can be
# empty.
#
# Loop over the function's own arguments with for and "$@". Keep the loop
# variable and the count in local variables called logfile and count: after
# a call, a caller's own logfile and count hold what they held before.
# Any other variable you set must be local too.
#
# Print nothing else, to stdout or to stderr. Return status 0. Don't create
# or change any file.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404
#   2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
# and "monday log.log" holding
#   2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512
#
#   report_404 access.log "monday log.log"   prints
#     access.log: 2
#     monday log.log: 0
#
# and after logfile=mine and count=mine, in the same shell:
#   report_404 access.log   prints "access.log: 2"; logfile and count
#                           still hold mine
report_404() {
    # TODO: write report_404()
    echo "report_404() is not written yet." >&2
    return 1
}
