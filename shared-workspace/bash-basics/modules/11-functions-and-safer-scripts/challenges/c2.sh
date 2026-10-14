#!/usr/bin/env bash
# Challenge c2 – see "Giving results back" in lesson.md.
#
# This file holds only a function and comments: the check loads it with
# source and calls first_error.
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines below will do), go into that folder, start bash
# and run
#   source ../challenges/c2.sh
# source loads the file's function into your shell (see "Loading functions
# with source" in lesson.md). Then call first_error access.log, and run
# echo $? to see its return status. Run source again after each change to
# this file.

# first_error LOGFILE: print the first request in LOGFILE that failed, and
# tell through the return status whether there was one.
#
# LOGFILE is always given, as a path from the current folder. It may not
# exist, or be a folder. Its name can hold spaces anywhere, also several in
# a row and at the start, glob characters such as * ? [ ], and "=". It is
# never empty, never starts with "-" and never holds a newline.
#
# Each line of a log file is one request, with six fields separated by
# single spaces: time, client IP, method, path, status and bytes. A path
# starts with "/" and holds no spaces; it can hold digits, even ones that
# look like a status (/errors/404.html). A status always has three digits,
# from 100 to 599. Bytes is a whole number; it can look like a status too
# (404). Every line ends with a newline, the last one too, and no line is
# empty or has a space at its end. A log file can be empty.
#
# A request failed when its status, the fifth field, is from 400 to 599
# (4xx and 5xx). The grep pattern " [45][0-9][0-9] " matches exactly these
# requests: only the status field can match it, as the bytes field ends
# the line.
#
# Check these cases in this order, and stop at the first that applies:
#
#   1. LOGFILE is not a regular file (it doesn't exist, or it is a folder):
#      print
#        first_error: no such file: LOGFILE
#      to stderr, with LOGFILE exactly as given, print nothing to stdout,
#      and return status 2.
#
#   2. LOGFILE holds at least one failed request: print the first of them,
#      unchanged, as the only line on stdout, and return status 0.
#
#   3. LOGFILE holds no failed request (also when it is empty): print
#      nothing and return status 1.
#
# In cases 2 and 3, print nothing to stderr. Don't create or change any
# file.
#
# Use return, never exit: the caller goes on after the call. A script that
# runs
#   first_error missing.log
#   echo "status: $?"
# prints the message to stderr, then "status: 2".
#
# Test for a failed request with grep -q first, as healthcheck.sh does. A
# pipeline such as grep ... | head -n 1 ends with head's status, which is
# 0 even when grep found nothing.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /errors/503.html 200 404
#   2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0
#   2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
# and clean.log holding only its first two lines:
#
#   first_error access.log   prints
#     2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0
#   and returns 0
#
#   first_error clean.log    prints nothing, returns 1
#
#   first_error missing.log  prints "first_error: no such file: missing.log"
#                            to stderr, returns 2
first_error() {
    # TODO: write first_error()
    echo "first_error() is not written yet." >&2
    return 1
}
