#!/usr/bin/env bash
# Challenge c4 – see "Passing names to xargs" in lesson.md.
#
# Usage: bash challenges/c4.sh DIR
#
# DIR is a folder, as a path from the current folder (for example logs, or
# . for the current folder itself). It is always given and is always an
# existing folder. Its name can hold spaces, also several in a row and at
# the start ("  old logs"), and glob characters such as * ? [ ]. It never
# ends with "/", never starts with "-", "!" or "(", and never holds a
# newline.
#
# The log files are the files under DIR, directly in it or in a subfolder
# at any depth, whose names end in .log. DIR always holds at least one of
# them, and at least one of them holds a request with status 404. No folder
# under DIR has a name ending in .log. Other files, such as notes.txt or
# access.log.old, are left out.
#
# The names of the files and folders under DIR can hold spaces, also
# several in a row and at the start, glob characters such as * ? [ ],
# quotes (' and ") and a leading "-". They never hold a newline and never
# start with ".". DIR holds only files and folders: no links.
#
# Each line of a log file is one request, with six fields separated by
# single spaces: time, client IP, method, path, status and bytes. As in
# countall.sh, a request has status 404 when its line contains " 404 "
# (404 with a space on each side): 404 in the path (/errors/404.html) or as
# the bytes at the end of the line doesn't count. Every line ends with a
# newline, the last one too, and no line is empty. A log file can be empty.
#
# For each log file, print one line:
#   FILE:N
# where FILE is its path as find prints it (DIR exactly as given, a "/",
# then the path inside DIR, such as logs/old/monday log.log, or
# ./access.log when DIR is .) and N is the number of requests with status
# 404 in it. N can be 0. The line has the FILE: part also when DIR holds
# only one log file. Print the lines in any order: find doesn't sort the
# files, and they don't need sorting.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Use find with -print0, piped into xargs -0 running grep -c -H (see
# "Passing names to xargs" in lesson.md). grep exits with status 0 because
# at least one log file holds a 404 request.
#
# Examples, with a folder called logs holding access.log:
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:15 192.0.2.44 GET /errors/404.html 200 404
# "old/monday log.log":
#   2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153
#   2026-10-05T09:13:40 198.51.100.7 GET /favicon.ico 404 153
# "dad's log.log":
#   2026-10-04T18:20:31 192.0.2.44 GET /index.html 200 512
# an empty file called empty.log, and notes.txt:
#
#   bash challenges/c4.sh logs   prints, in any order,
#     logs/access.log:1
#     logs/old/monday log.log:2
#     logs/dad's log.log:0
#     logs/empty.log:0
#   and exits with status 0
#
# To try it by hand, make a folder in the module folder, go into it, make
# a folder called logs and put an access.log and a "monday log.log" in it
# (the example lines above will do). Then run
#   bash ../challenges/c4.sh logs

# TODO: write c4.sh
echo "c4.sh is not written yet." >&2
exit 1
