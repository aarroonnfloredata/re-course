#!/usr/bin/env bash
# top.sh: the sixth logkit tool. It ranks the clients of a web server by
# how many requests they sent.
#
# Usage: bash exercise/top.sh LOGFILE N
#
# LOGFILE is the log file to read, as a path from the current folder (for
# example access.log, or logs/monday.log). It always exists. Its name can
# hold spaces, also several in a row, and glob characters such as * ? [ ],
# and it never starts with "-". N is a whole number, 1 or more, written
# without leading zeros (3, never 03). Both are always given.
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. The client IP is
# the second field: four numbers joined by dots, such as 203.0.113.5.
# Every line ends with a newline, the last one too, and no line is empty.
# LOGFILE can be empty.
#
# Count the requests from each client IP, and print the N IPs with the
# most requests, the IP with the most first, one line each:
#   IP COUNT
# where COUNT is the number of requests from that IP. The line holds one
# space, between IP and COUNT, and no other spaces.
#
# No two IPs in LOGFILE have the same number of requests, so the order is
# always clear. When LOGFILE holds N different IPs or fewer, print all of
# them. An empty LOGFILE prints nothing.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# One pipeline does it, built from cut, sort, uniq -c and head, and
# ending in a while read -r loop (see "Ranking with one pipeline" in
# lesson.md). The loop is needed because uniq -c puts spaces before each
# count, and how many depends on the system: it prints each line as
# "IP COUNT".
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:02 203.0.113.5 GET /about.html 200 2048
#   2026-10-06T10:16:15 192.0.2.44 GET /index.html 200 512
#   2026-10-06T10:16:48 203.0.113.5 GET /logo.png 200 4096
#   2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
#
#   bash exercise/top.sh access.log 2   prints
#     203.0.113.5 3
#     198.51.100.7 2
#
#   bash exercise/top.sh access.log 1   prints
#     203.0.113.5 3
#
#   bash exercise/top.sh access.log 5   prints all three IPs:
#     203.0.113.5 3
#     198.51.100.7 2
#     192.0.2.44 1
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../exercise/top.sh access.log 2
#
# Write it so that `learn check` passes.

# TODO: write top.sh
echo "top.sh is not written yet." >&2
exit 1
