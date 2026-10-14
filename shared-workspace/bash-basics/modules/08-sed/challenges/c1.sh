#!/usr/bin/env bash
# Challenge c1 – see "Replacing text with s" in lesson.md.
#
# Usage: bash challenges/c1.sh LOGFILE
#
# LOGFILE is a log file in the current folder. It is always given and
# always exists. Its name can hold spaces, also several in a row, and it
# never starts with "-".
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. No field holds a
# space or a comma. Every line ends with a newline, the last one too, and
# no line is empty. LOGFILE can be empty.
#
# Print LOGFILE as CSV (comma-separated values): every line, in the order
# of LOGFILE, with each of its spaces replaced by a comma. So each line
# printed holds five commas and no spaces, and its fields stay as they
# were. An empty LOGFILE prints nothing.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:02 192.0.2.44 POST /login 401 64
#
#   bash challenges/c1.sh access.log   prints
#     2026-10-06T10:15:32,203.0.113.5,GET,/index.html,200,512
#     2026-10-06T10:15:40,198.51.100.7,GET,/missing.html,404,153
#     2026-10-06T10:16:02,192.0.2.44,POST,/login,401,64
#   and exits with status 0
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c1.sh access.log

# TODO: write c1.sh
echo "c1.sh is not written yet." >&2
exit 1
