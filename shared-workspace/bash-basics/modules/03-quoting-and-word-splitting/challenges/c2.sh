#!/usr/bin/env bash
# Challenge c2 – see "Single quotes and backslashes" in lesson.md.
#
# Usage: bash challenges/c2.sh STATUS
#
# logkit's help shows the grep command that count.sh runs, so users can run
# it by hand. STATUS is a status code, such as 404 or 500. It is always
# given.
#
# Print one line, exactly this, with STATUS replaced by the argument:
#   grep -c " STATUS " "$logfile"
# Everything else stays as shown: the four double quotes, the space on each
# side of STATUS, and $logfile with its $, as text. It is not the value of a
# variable.
#
# Print nothing else, to stdout or to stderr, and exit with status 0.
#
# Examples:
#   bash challenges/c2.sh 404   prints the line
#     grep -c " 404 " "$logfile"
#   bash challenges/c2.sh 500   prints the line
#     grep -c " 500 " "$logfile"

# TODO: write c2.sh
echo "c2.sh is not written yet." >&2
exit 1
