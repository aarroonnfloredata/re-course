#!/usr/bin/env bash
# scan.sh: the tenth logkit tool. It searches a folder and all its
# subfolders for log files, and counts the requests in them that failed
# with a server error, a status from 500 to 599 (5xx).
#
# Usage: bash exercise/scan.sh DIR
#
# DIR is the folder to search, as a path from the current folder (for
# example logs, logs/october, or . for the current folder itself). It is
# always given and is always an existing folder. Its name can hold spaces,
# also several in a row and at the start ("  old logs"), and glob
# characters such as * ? [ ]. It never ends with "/", never starts with
# "-", "!" or "(", and never holds "=" or a newline.
#
# The log files are the regular files under DIR, directly in it or in a
# subfolder at any depth, whose names end in exactly .log, and that are
# not empty:
#
#   - access.log, "monday log.log" and 2026/09/access.log are log files
#     when they hold at least one request. access.log.old, server.LOG,
#     access.log.gz and notes.txt never are.
#   - An empty .log file (0 bytes) is not a log file here: leave it out.
#   - A folder is never a log file, also when its name ends in .log
#     (archive.log); the log files inside it are.
#
# The names of the files and folders under DIR can hold anything else a
# name can: spaces, also several in a row and at the start, glob
# characters such as * ? [ ], quotes (' and "), $ and ;, a leading "-",
# and even newlines. No name under DIR starts with "." or holds "=". DIR
# holds only files and folders, no links, and all of them can be read.
#
# Each line of a log file is one request, with six fields separated by
# single spaces: time, client IP, method, path, status and bytes. The time
# has the form 2026-10-06T10:15:32, the client IP is four numbers joined
# by dots (203.0.113.5), and the method is a word in capital letters (GET,
# POST). A path starts with "/" and holds no spaces; it can hold digits,
# even ones that look like a status (/errors/503.html). A status always
# has three digits, from 100 to 599. Bytes is a whole number, 0 or more;
# it can look like a status too (503). Every line ends with a newline, the
# last one too, and no line is empty or has a space at its end. Files that
# are not log files, such as notes.txt, can hold anything, 5xx requests
# included: they don't count.
#
# A request failed with a server error when its status, the fifth field,
# is from 500 to 599. A 5xx number in another field doesn't count. The
# grep pattern " 5[0-9][0-9] " that healthcheck.sh uses matches exactly
# these requests: a space, a 5, two more digits and a space. Only the
# status field can match it, as the bytes field ends the line.
#
# Print one line:
#   DIR: N 5xx requests in F log files
# where
#   DIR  is the folder exactly as given;
#   N    is the number of 5xx requests in all the log files together;
#   F    is the number of log files, the ones without a 5xx request
#        included.
# Both numbers can be 0, and the words stay the same when a number is 1
# ("1 5xx requests in 1 log files"). When DIR holds no log file, print
#   DIR: 0 5xx requests in 0 log files
# Neither number depends on the order in which find lists the files.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Print the line with echo: capture the output of one pipeline with $( )
# and print it after "DIR: ", as module 9 did with
#   echo "awk: [$(awk '{ print $2 }' spaced.txt)]"
# In that pipeline, find picks the log files with its tests and runs
# grep -c on each file on its own (-exec ... {} \;), so each count comes
# out alone on its line, as grep -c prints it for a single file. One awk
# program then counts those lines, adds them up and prints
# "N 5xx requests in F log files" (see "Tests: name, type and size",
# "Combining tests" and "Running a command on the files" in lesson.md).
#
# Examples, with a folder called logs holding access.log:
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0
#   2026-10-06T10:16:48 192.0.2.44 GET /errors/503.html 200 1024
# "old/monday log.log":
#   2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512
#   2026-10-05T09:13:02 203.0.113.5 POST /upload 500 0
#   2026-10-05T09:13:40 198.51.100.7 GET /api/stats 502 0
# old/clean.log:
#   2026-10-04T18:20:31 192.0.2.44 GET /index.html 200 503
# an empty file called empty.log; notes.txt, holding a copy of the 503
# request in access.log; and a folder called archive.log that holds only
# notes.txt:
#
#   bash exercise/scan.sh logs   prints
#     logs: 3 5xx requests in 3 log files
#
# and with a folder called "old logs" that holds only an empty file called
# empty.log:
#
#   bash exercise/scan.sh "old logs"   prints
#     old logs: 0 5xx requests in 0 log files
#
# To try it by hand, make a folder in the module folder, go into it, make
# a folder called logs and put an access.log in it (the example lines
# above will do). Then run
#   bash ../exercise/scan.sh logs
#
# Write it so that `learn check` passes.

dir="$1"
echo "$dir: $(find "$dir" -type f -name '*.log' ! -empty -exec grep -c " 5[0-9][0-9] " {} \; |
    awk '{ requests += $1; files++ } END { print requests + 0, "5xx requests in", files + 0, "log files" }')"
