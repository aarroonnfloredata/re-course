#!/usr/bin/env bash
# summary.sh: the fifth logkit tool. It sums up every log file in a folder:
# how many requests each one holds, how many of them failed, and how many
# bytes they sent.
#
# Usage: bash exercise/summary.sh DIR
#
# DIR is a folder, as a path from the current folder (for example logs,
# logs/october, or . for the current folder itself). It is always given and
# is always an existing folder, and it doesn't end with "/". Its name can
# hold spaces, also several in a row, and glob characters such as * ? [ ].
#
# The log files are the files directly in DIR whose names end in .log, such
# as access.log or "monday log.log". Their names can hold spaces, also
# several in a row, and glob characters such as * ? [ ]. Other files in DIR,
# such as notes.txt or access.log.old, are left out, and so are the files in
# DIR's subfolders. No name in DIR starts with a dot, and no subfolder of
# DIR has a name ending in .log.
#
# Each line of a log file is one request, with six fields separated by
# single spaces: time, client IP, method, path, status and bytes. A status
# always has three digits, from 100 to 599. Bytes is a whole number, 0 or
# more, written without leading zeros (0, 64 or 1024, never 064). A path can
# hold backslashes, also at its end (/scripts/..\..\ is one path). Every
# line ends with a newline, the last one too, and no line is empty. A log
# file can be empty.
#
# For each log file, in the order the glob DIR/*.log lists them (sorted by
# name), print one line:
#   FILE: R requests, E errors, B bytes
# where
#   FILE  is the file as the glob gives it: DIR exactly as given, a "/" and
#         the file's name, such as logs/access.log ("./access.log" when DIR
#         is .);
#   R     is the number of requests in the file (its lines);
#   E     is the number of those requests that failed: the ones whose
#         status is from 400 to 599 (4xx and 5xx);
#   B     is the sum of their bytes fields.
# Each line counts its own file only, and every number can be 0: an empty
# log file gives "FILE: 0 requests, 0 errors, 0 bytes". The words stay the
# same when a number is 1 ("1 requests, 1 errors").
#
# When DIR holds no log file, print nothing.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Loop over the log files with for, read each one line by line with
# while read -r, sort each status into its class with case, and count and
# add with arithmetic. No grep is needed.
#
# Examples, with a folder called logs holding access.log:
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0
#   2026-10-06T10:16:48 192.0.2.44 GET /errors/503.html 200 1024
#   2026-10-06T10:17:45 192.0.2.44 GET /old.html 301 0
# "monday log.log":
#   2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512
#   2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153
# an empty file called empty.log, and notes.txt; and with a folder called
# "old logs" that holds only notes.txt:
#
#   bash exercise/summary.sh logs   prints
#     logs/access.log: 5 requests, 2 errors, 1689 bytes
#     logs/empty.log: 0 requests, 0 errors, 0 bytes
#     logs/monday log.log: 2 requests, 1 errors, 665 bytes
#
#   bash exercise/summary.sh "old logs"   prints nothing
#
# To try it by hand, make a folder in the module folder, go into it, make a
# folder called logs and put an access.log in it (the example lines above
# will do). Then run
#   bash ../exercise/summary.sh logs
#
# Write it so that `learn check` passes.

dir="$1"
for file in "$dir"/*.log; do
    [[ -e $file ]] || continue
    requests=0
    errors=0
    total=0
    while read -r _ _ _ _ status bytes; do
        (( requests++ ))
        case "$status" in
            4[0-9][0-9]|5[0-9][0-9]) (( errors++ )) ;;
        esac
        (( total += bytes ))
    done < "$file"
    echo "$file: $requests requests, $errors errors, $total bytes"
done
