#!/usr/bin/env bash
# Challenge c2 – see "Arguments" in lesson.md.
#
# Usage: bash challenges/c2.sh LOGFILE STATUS
#
# logkit's next tool will take a log file and a status as its arguments.
# This script is a dry run: it only reports what it was given.
#
# Print one line:
#   STATUS in LOGFILE (N arguments)
# where STATUS is the second argument, LOGFILE the first, and N the number
# of arguments the script got. Arguments after the second are counted but
# not printed. An argument that wasn't given prints as nothing, so the
# spaces around it stay. The line always says "arguments", even when N
# is 1. Print nothing else, to stdout or to stderr, and exit with status 0.
#
# Examples:
#   bash challenges/c2.sh access.log 404             prints "404 in access.log (2 arguments)"
#   bash challenges/c2.sh logs/monday.log 500 GET    prints "500 in logs/monday.log (3 arguments)"
#   bash challenges/c2.sh access.log                 prints " in access.log (1 arguments)"
#   bash challenges/c2.sh                            prints " in  (0 arguments)"

# TODO: write c2.sh
echo "c2.sh is not written yet." >&2
exit 1
