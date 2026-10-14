#!/usr/bin/env bash
# Challenge c3 – see "Stopping at the first error" and "pipefail" in
# lesson.md.
#
# Usage: bash challenges/c3.sh LOGFILE
#
# LOGFILE is always given, as a path from the current folder (for example
# access.log, or logs/monday.log). It is either an existing regular file
# holding at least one request, or a path where nothing exists. Its name
# can hold spaces anywhere, also several in a row and at the start, glob
# characters such as * ? [ ], and "=". It never starts with "-" and never
# holds a newline.
#
# Each line of a log file is one request, with six fields separated by
# single spaces: time, client IP, method, path, status and bytes. The
# client IP is the second field, such as 203.0.113.5. Every line ends with
# a newline, the last one too, and no line is empty.
#
# When LOGFILE exists, print one line:
#   LOGFILE: busiest client IP
# where LOGFILE is the name exactly as given and IP is the client IP that
# sent the most requests. No two IPs have the same number of requests, so
# there is always one busiest client. Print nothing else, to stdout or to
# stderr, and exit with status 0.
#
# When LOGFILE doesn't exist, print nothing to stdout, and exit with status
# 1, cut's status. cut prints its own error message to stderr, whose
# wording depends on the system.
#
# Write it like this, and let set -e and pipefail stop the script, instead
# of checking LOGFILE yourself:
#   - Make set -euo pipefail its first command.
#   - Find the IP with one pipeline, and capture its output in a variable
#     with $( ). The pipeline takes the client IPs out with cut, ranks them
#     with sort, uniq -c and sort -nr, keeps the first line with sed -n 1p,
#     and takes the IP out of that line with awk '{ print $2 }' (uniq -c
#     puts spaces before each count; awk skips them).
#   - Then print the line with echo.
# When cut fails, pipefail makes the pipeline, and so the assignment, fail
# with cut's status, and set -e stops the script before echo. Without
# pipefail, the pipeline would succeed, as its last command did.
#
# Don't create or change any file.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:02 203.0.113.5 GET /about.html 200 2048
#
#   bash challenges/c3.sh access.log    prints
#     access.log: busiest client 203.0.113.5
#   and exits with status 0
#
#   bash challenges/c3.sh missing.log   prints nothing to stdout, prints
#                                       cut's error message to stderr, and
#                                       exits with status 1
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c3.sh access.log
# To see its exit status, run echo $? right after it.

# TODO: write c3.sh
echo "c3.sh is not written yet." >&2
exit 1
