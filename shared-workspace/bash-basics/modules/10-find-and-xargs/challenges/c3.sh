#!/usr/bin/env bash
# Challenge c3 – see "One command for all the files" in lesson.md.
#
# Usage: bash challenges/c3.sh DIR
#
# DIR is a folder, as a path from the current folder (for example logs, or
# . for the current folder itself). It is always given and is always an
# existing folder. Its name can hold spaces, also several in a row and at
# the start ("  old logs"), and glob characters such as * ? [ ]. It never
# ends with "/", never starts with "-", "!" or "(", and never holds "=" or
# a newline.
#
# The log files are the files under DIR, directly in it or in a subfolder
# at any depth, whose names end in .log. DIR always holds at least one of
# them. No folder under DIR has a name ending in .log. Other files, such as
# notes.txt or access.log.old, are left out.
#
# The names of the files and folders under DIR can hold spaces, also
# several in a row and at the start, glob characters such as * ? [ ],
# quotes (' and ") and a leading "-". They never hold "=" or a newline and
# never start with ".". DIR holds only files and folders: no links.
#
# Each line of a log file is one request, with six fields separated by
# single spaces: time, client IP, method, path, status and bytes. Bytes is
# a whole number, 0 or more, written without leading zeros (0, 64 or 1024,
# never 064). Every line ends with a newline, the last one too, and no line
# is empty. A log file can be empty.
#
# Print one line: the sum of the bytes fields of all requests in all the
# log files together, as a whole number written as digits only, such as
# 1689. When every log file is empty, print 0. The sum never goes above
# 1000000000 (one billion).
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Use one find command that runs one awk program on all the log files at
# once, with -exec ... {} + (see "One command for all the files" in
# lesson.md).
#
# Examples, with a folder called logs holding access.log:
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
# "old/monday log.log":
#   2026-10-05T09:12:44 192.0.2.44 GET /logo.png 200 1024
# access.log.old:
#   2026-10-04T18:20:31 192.0.2.44 GET /index.html 200 512
# and an empty file called empty.log:
#
#   bash challenges/c3.sh logs    prints "1689", exits with status 0
#
# and with a folder called quiet holding only an empty file called
# empty.log:
#
#   bash challenges/c3.sh quiet   prints "0", exits with status 0
#
# To try it by hand, make a folder in the module folder, go into it, make
# a folder called logs and put an access.log in it (the example lines
# above will do). Then run
#   bash ../challenges/c3.sh logs

# TODO: write c3.sh
echo "c3.sh is not written yet." >&2
exit 1
