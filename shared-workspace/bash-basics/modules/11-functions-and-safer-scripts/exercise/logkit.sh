#!/usr/bin/env bash
# shellcheck disable=SC1091
# logkit.sh: the last logkit tool, and the one command that brings logkit
# together. It loads its functions from loglib.sh and runs one of three
# subcommands: count, top or health.
#
# (Line 2 is for ShellCheck, which `learn check` runs on this file.
# ShellCheck checks only the files it is given, and `learn check` gives it
# logkit.sh without asking it to follow source into loglib.sh, so it would
# say that it doesn't look inside loglib.sh. Line 2 turns that message
# off. Leave it as it is.)
#
# Usage: bash exercise/logkit.sh count LOGFILE STATUS
#        bash exercise/logkit.sh top LOGFILE N
#        bash exercise/logkit.sh health LOGFILE
#
# How to write it:
#
#   - Its first command is set -euo pipefail (see "Stopping at the first
#     error" in lesson.md).
#
#   - Then it loads exercise/loglib.sh with source. loglib.sh is in the same
#     folder as logkit.sh, and logkit.sh must find it from any current
#     folder: build its path from $0 with dirname (see "Loading functions
#     with source" in lesson.md). The tests run logkit.sh from another
#     folder, as bash /path/to/exercise/logkit.sh.
#
#   - It uses the functions of loglib.sh: count_status for count,
#     top_clients for top, and die for every error. It needs no functions
#     of its own.
#
# The arguments:
#
#   - The first argument is the subcommand: count, top or health. Any
#     other first argument, the empty string included, is an error (case 1
#     below).
#
#   - LOGFILE is a log file, as a path from the current folder (for example
#     access.log, or logs/monday.log). It may not exist, or be a folder.
#     Its name can hold spaces anywhere, also several in a row and at the
#     start ("  tuesday   log.log"), glob characters such as * ? [ ], and
#     "=". It is never empty, never starts with "-" and never holds a
#     newline.
#
#   - STATUS is always three digits, from 100 to 599, such as 404 or 500.
#
#   - N is a whole number, 1 or more, written without leading zeros (3,
#     never 03), or a word of letters only, such as abc. logkit doesn't
#     check N itself: see "top" below.
#
# Each line of a log file is one request, with six fields separated by
# single spaces: time, client IP, method, path, status and bytes, such as
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
# The time has the form 2026-10-06T10:15:32. The client IP is four numbers
# from 0 to 255 joined by dots. The method is a word in capital letters
# (GET, POST). A path starts with "/" and holds no spaces; it can hold
# digits, even ones that look like a status (/errors/503.html). A status
# always has three digits, from 100 to 599. Bytes is a whole number, 0 or
# more; it can look like a status too (503). Every line ends with a
# newline, the last one too, and no line is empty or has a space at its
# end. A log file can be empty.
#
# Check these cases in this order, and stop at the first that applies:
#
#   1. There is no argument; or the first argument is not count, top or
#      health; or the number of arguments after it is wrong (count and top
#      take exactly two, health exactly one). Call die with the message
#        usage: logkit.sh count LOGFILE STATUS | top LOGFILE N | health LOGFILE
#      so logkit prints
#        logkit: usage: logkit.sh count LOGFILE STATUS | top LOGFILE N | health LOGFILE
#      to stderr and exits with status 2. Under set -u, reading $1 when
#      there is no argument is an error that stops the script: check $#
#      before you read $1 (see "Stopping at the first error" in lesson.md).
#
#   2. LOGFILE is not a regular file (it doesn't exist, or it is a folder):
#      call die with the message "no such file: LOGFILE", with LOGFILE
#      exactly as given, so logkit prints
#        logkit: no such file: LOGFILE
#      to stderr and exits with status 2.
#
#   3. Otherwise, run the subcommand:
#
#      count LOGFILE STATUS
#        When COUNT, the number of requests in LOGFILE with status STATUS
#        (as count_status counts them), is 1 or more, print
#          LOGFILE: COUNT requests with status STATUS
#        as count.sh does (always "requests", also when COUNT is 1), and
#        exit with status 0.
#        When COUNT is 0, print nothing and exit with status 1, as grep does
#        when it finds nothing. With set -e, this takes no code of its own:
#        capture the count with n=$(count_status ...) before you print. When
#        count_status returns 1, the assignment fails with that status, and
#        set -e stops logkit before the line is printed. Don't call
#        count_status inside echo's arguments: echo's status would hide
#        count_status's (see "What set -e misses" in lesson.md).
#        This uses on purpose what "Stopping at the first error" in
#        lesson.md warns about: set -e can't tell an error from a "no".
#        Like grep -c, count reports "none" through its status, and set -e
#        turns that into logkit's exit status. A tool meant for people
#        would check the count itself, and print a line for 0 too.
#
#      top LOGFILE N
#        Print what top_clients prints for LOGFILE and N, and exit with
#        status 0.
#        When N is a word, such as abc, sed fails inside top_clients: it
#        prints its own error message to stderr, whose wording depends on
#        the system, and nothing reaches stdout. pipefail makes top_clients
#        return sed's status, 1, and set -e stops logkit with it. So logkit
#        prints nothing to stdout and exits with status 1. Without
#        pipefail, it would exit with 0, as if all had gone well.
#
#      health LOGFILE
#        As healthcheck.sh does: when LOGFILE holds at least one request
#        that failed with a server error, a status from 500 to 599, print
#        each of them, unchanged and in the order of LOGFILE, and exit with
#        status 1. The grep pattern " 5[0-9][0-9] " matches exactly these
#        requests. When it holds none (also when it is empty), print
#          LOGFILE: no 5xx errors
#        with LOGFILE exactly as given, and exit with status 0.
#        Test for 5xx requests with if and grep -q, as healthcheck.sh does:
#        set -e ignores a command that if tests, but a grep that finds
#        nothing on a line of its own would stop logkit.
#
# Print nothing else. Nothing goes to stdout in cases 1 and 2, or when top
# stops on a bad N; nothing goes to stderr in case 3, except sed's message
# for a bad N. Don't create or change any file.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:02 203.0.113.5 GET /about.html 200 2048
#   2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0
#   2026-10-06T10:16:48 203.0.113.5 GET /errors/503.html 200 1024
#   2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0
# "monday log.log" holding
#   2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512
#   2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153
# and a folder called logs:
#
#   bash exercise/logkit.sh count access.log 200
#                     prints "access.log: 3 requests with status 200",
#                     exits with 0
#   bash exercise/logkit.sh count "monday log.log" 404
#                     prints "monday log.log: 1 requests with status 404",
#                     exits with 0
#   bash exercise/logkit.sh count access.log 401
#                     prints nothing, exits with 1
#
#   bash exercise/logkit.sh top access.log 2   prints
#     203.0.113.5 3
#     198.51.100.7 2
#   and exits with 0
#
#   bash exercise/logkit.sh top access.log abc
#                     prints sed's error message to stderr and nothing to
#                     stdout, exits with 1
#
#   bash exercise/logkit.sh health access.log   prints
#     2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0
#     2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0
#   and exits with 1
#
#   bash exercise/logkit.sh health "monday log.log"
#                     prints "monday log.log: no 5xx errors", exits with 0
#
#   bash exercise/logkit.sh
#   bash exercise/logkit.sh list access.log
#   bash exercise/logkit.sh count access.log
#   bash exercise/logkit.sh health access.log "monday log.log"
#                     each print
#                       logkit: usage: logkit.sh count LOGFILE STATUS | top LOGFILE N | health LOGFILE
#                     to stderr, exit with 2
#
#   bash exercise/logkit.sh top missing.log 3
#   bash exercise/logkit.sh health logs
#                     print "logkit: no such file: missing.log" and
#                     "logkit: no such file: logs" to stderr, exit with 2
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../exercise/logkit.sh count access.log 200
# To see its exit status, run echo $? right after it.
#
# Write it so that `learn check` passes.

# TODO: write logkit.sh
echo "logkit.sh is not written yet." >&2
exit 1
