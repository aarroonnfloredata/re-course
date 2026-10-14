#!/usr/bin/env bash
# loglib.sh: logkit's library. It holds the functions that logkit.sh loads
# with source: count_status, top_clients and die.
#
# This file holds only functions and comments, so loading it defines the
# functions and runs nothing else (see "Loading functions with source" in
# lesson.md). Don't add any other command, set -euo pipefail included:
# that belongs in logkit.sh.
#
# Write each function so that `learn check` passes. The tests load this
# file with source and call one function at a time, in a folder that holds
# the log files they give it.
#
# For every function here:
#
#   - LOGFILE is a log file, as a path from the current folder (for example
#     access.log, or logs/monday.log). It always exists and is a regular
#     file. Its name can hold spaces anywhere, also several in a row and at
#     the start ("  tuesday   log.log"), glob characters such as * ? [ ],
#     and "=". It is never empty, never starts with "-" and never holds a
#     newline.
#
#   - Each line of a log file is one request, with six fields separated by
#     single spaces: time, client IP, method, path, status and bytes. The
#     time has the form 2026-10-06T10:15:32. The client IP is four numbers
#     from 0 to 255 joined by dots, such as 203.0.113.5. The method is a
#     word in capital letters (GET, POST). A path starts with "/" and holds
#     no spaces; it can hold digits, even ones that look like a status
#     (/errors/404.html). A status always has three digits, from 100 to 599.
#     Bytes is a whole number, 0 or more; it can look like a status too
#     (404). Every line ends with a newline, the last one too, and no line
#     is empty or has a space at its end. A log file can be empty.
#
#   - Every variable a function sets is local (see "Local variables" in
#     lesson.md): after a call, the caller's variables hold what they held
#     before, also ones with the same names as the function's.
#
# To try the functions by hand, make a folder in the module folder, put an
# access.log in it (the example lines below will do), go into that folder,
# start bash and run
#   source ../exercise/loglib.sh
# Then call a function, such as count_status access.log 404, and run
# echo $? to see its return status. Run source again after each change to
# this file. die ends the shell it runs in, so try it in a small script
# instead, as in its example below.
#
# The examples below use access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:02 203.0.113.5 GET /about.html 200 2048
#   2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404
#   2026-10-06T10:16:48 203.0.113.5 GET /errors/404.html 200 1024
#   2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153

# count_status LOGFILE STATUS: count the requests in LOGFILE that have
# status STATUS. Give the count back as output, and whether there were any
# as the return status, the way grep -c does.
#
# STATUS is always given and is always three digits, from 100 to 599, such
# as 404 or 500. As in count.sh, a request has status STATUS when its line
# contains STATUS with a space on each side (" 404 " for 404). A line with
# STATUS only in another field doesn't count: 404 in the path
# /errors/404.html, or as the bytes at the end of the line.
#
# Print one line: N, the number of requests in LOGFILE with status STATUS,
# as digits only (0, 2, 15). Print nothing else, to stdout or to stderr.
#
# Return status 0 when N is 1 or more, and 1 when N is 0 (also when LOGFILE
# is empty). The return status is the last command's when the function
# ends without return (see "Giving results back" in lesson.md).
#
# Keep LOGFILE and STATUS in local variables called logfile and status.
# Any other variable you set must be local too.
#
# Don't create or change any file.
#
# Examples, with access.log as above:
#   count_status access.log 404   prints "2", returns 0
#   count_status access.log 200   prints "4", returns 0
#   count_status access.log 500   prints "0", returns 1
#
# and, called directly (not inside $( ), which would run it apart from
# the caller's variables), in a shell that first ran
#   logfile=mine
#   status=mine
#   count_status access.log 404
#   echo "$logfile $status"
# prints "2" and then "mine mine": the call leaves logfile and status as
# they were.
count_status() {
    # TODO: write count_status()
    echo "count_status() is not written yet." >&2
    return 1
}

# top_clients LOGFILE N: rank the clients in LOGFILE by how many requests
# they sent, as top.sh does, and print the N with the most.
#
# N is always given. It is a whole number, 1 or more, written without
# leading zeros (3, never 03), except when logkit.sh passes on a bad
# argument: then it is a word of letters only, such as abc.
#
# For a whole number N, print one line for each client IP, the IP with the
# most requests first:
#   IP COUNT
# where COUNT is the number of requests from that IP. The line holds one
# space, between IP and COUNT, and no other spaces. No two IPs in LOGFILE
# have the same number of requests, so the order is always clear. Print
# the first N of these lines: all of them when LOGFILE holds N different
# IPs or fewer, and nothing when LOGFILE is empty. Print nothing else, to
# stdout or to stderr, and return status 0.
#
# Use the pipeline of top.sh, with one change: keep the first N lines with
# sed -n "1,${n}p" (module 8) instead of head -n "$n". head stops reading
# after N lines, and under pipefail, which logkit.sh turns on, a command
# that stops reading early can make the command before it fail on a long
# log (see "pipefail" in lesson.md). sed reads all its input.
#
# For a word N, sed fails: it prints its own error message to stderr, whose
# wording depends on the system, and nothing reaches stdout. Make the
# pipeline the function's last command, so that the function returns the
# pipeline's status: 1 when the caller has turned on set -o pipefail, as
# logkit.sh does, because sed failed; 0 without pipefail, because the
# pipeline's last command, the while loop, succeeded.
#
# Keep LOGFILE and N in local variables called logfile and n. Any other
# variable you set must be local too. The count and IP that the while read
# loop at the end of the pipeline reads need no local: the loop runs apart
# from the caller, in the pipe, so its variables are gone when it ends, as
# module 6 showed.
#
# Don't create or change any file.
#
# Examples, with access.log as above:
#   top_clients access.log 2   prints
#     203.0.113.5 3
#     198.51.100.7 2
#
#   top_clients access.log 5   prints all three IPs:
#     203.0.113.5 3
#     198.51.100.7 2
#     192.0.2.44 1
#
# and with an empty file called "empty day.log":
#   top_clients "empty day.log" 3   prints nothing, returns 0
#
# and, called directly, in a shell that first ran
#   logfile=mine
#   n=mine
#   top_clients access.log 1
#   echo "$logfile $n"
# prints "203.0.113.5 3" and then "mine mine": the call leaves logfile and
# n as they were.
top_clients() {
    # TODO: write top_clients()
    echo "top_clients() is not written yet." >&2
    return 1
}

# die MESSAGE: report an error and end the whole script.
#
# MESSAGE is always given, as one argument, and is never empty. It can hold
# spaces, also several in a row and at the start, glob characters such as
# * ? [ ], and characters such as $ ; = and quotes. It never holds a
# backslash or a newline. No argument follows it.
#
# Print one line to stderr:
#   logkit: MESSAGE
# with MESSAGE exactly as given. Print nothing to stdout.
#
# Then end the script with exit status 2: use exit, not return (see
# "Giving results back" in lesson.md). No command after the call runs, also
# when die is called from inside another function.
#
# Don't create or change any file.
#
# Examples:
#   die "no such file: monday  log.log"
#                       prints "logkit: no such file: monday  log.log" to
#                       stderr, and the script ends with status 2
#
# and in a script holding the three lines
#   source exercise/loglib.sh
#   die "stop here"
#   echo "after die"
# the script prints "logkit: stop here" to stderr, never prints
# "after die", and ends with status 2.
die() {
    # TODO: write die()
    echo "die() is not written yet." >&2
    return 1
}
