#!/usr/bin/env bash
# healthcheck.sh: the fourth logkit tool. It checks a log file for requests
# that failed with a server error, a status from 500 to 599 (5xx), and
# tells through its exit status whether there were any.
#
# Usage: bash exercise/healthcheck.sh LOGFILE
#
# LOGFILE is the log file to check, as a path from the current folder (for
# example access.log, or logs/monday.log). Its name can hold spaces, also
# several in a row, and glob characters such as * ? [ ]. When given, it is
# never the empty string, and it never starts with "-".
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. A status always
# has three digits. A request failed with a server error when its status is
# from 500 to 599, that is, when its line contains a space, a 5, two more
# digits and a space. The grep pattern " 5[0-9][0-9] " matches exactly that:
# [0-9] matches any one digit. The double quotes keep the pattern, spaces
# included, as one argument and stop bash from treating the brackets as a
# glob (see "Branching with if" in lesson.md). A 5xx number in another
# field doesn't count, for example 503 in the path /errors/503.html, or 512
# as the bytes at the end of the line.
#
# Check these cases in this order, and stop at the first that applies:
#
#   1. Not exactly one argument (none, or two or more): print
#        usage: healthcheck.sh LOGFILE
#      to stderr and exit with status 2.
#
#   2. LOGFILE is not a regular file (it doesn't exist, or it is a folder):
#      print
#        healthcheck.sh: no such file: LOGFILE
#      to stderr, with LOGFILE exactly as given, and exit with status 2.
#
#   3. LOGFILE holds at least one request with a 5xx status: print each of
#      them, unchanged and in the order of LOGFILE, and exit with status 1.
#
#   4. LOGFILE holds no request with a 5xx status (also when it is empty):
#      print
#        LOGFILE: no 5xx errors
#      with LOGFILE exactly as given, and exit with status 0.
#
# Print nothing else. In cases 1 and 2 nothing goes to stdout; in cases 3
# and 4 nothing goes to stderr. Don't create or change any file.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0
#   2026-10-06T10:16:48 192.0.2.44 GET /errors/503.html 200 1024
#   2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0
# "monday log.log" holding
#   2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512
#   2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153
# and a folder called logs:
#
#   bash exercise/healthcheck.sh access.log   prints
#     2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0
#     2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0
#   and exits with status 1
#
#   bash exercise/healthcheck.sh "monday log.log"
#                     prints "monday log.log: no 5xx errors", exits with 0
#
#   bash exercise/healthcheck.sh
#   bash exercise/healthcheck.sh access.log "monday log.log"
#                     each print "usage: healthcheck.sh LOGFILE" to stderr,
#                     exit with 2
#
#   bash exercise/healthcheck.sh missing.log
#                     prints "healthcheck.sh: no such file: missing.log" to
#                     stderr, exits with 2
#
#   bash exercise/healthcheck.sh logs
#                     prints "healthcheck.sh: no such file: logs" to stderr,
#                     exits with 2
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../exercise/healthcheck.sh access.log
# To see its exit status, run echo $? right after it.
#
# Write it so that `learn check` passes.

# TODO: write healthcheck.sh
echo "healthcheck.sh is not written yet." >&2
exit 1
