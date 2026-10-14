#!/usr/bin/env bash
# suspicious.sh: the seventh logkit tool. It picks out the requests in a
# log file that look like attacks.
#
# Usage: bash exercise/suspicious.sh LOGFILE
#
# LOGFILE is the log file to read, as a path from the current folder (for
# example access.log, or logs/monday.log). It is always given and always
# exists. Its name can hold spaces, also several in a row, and glob
# characters such as * ? [ ], and it never starts with "-".
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. The method is
# always in uppercase (GET, POST, ...). A path starts with "/" and holds no
# spaces; it can hold letters in either case, digits, and characters such
# as . - _ and %. A status always has three digits. Every line ends with a
# newline, the last one too, and no line is empty. LOGFILE can be empty.
#
# A request looks like an attack when at least one of these is true:
#
#   1. Its path contains two dots in a row, anywhere: /../etc/passwd,
#      /static/..%2fconfig and /a..b do. Single dots don't count:
#      /index.html and /a.b.c don't.
#
#   2. Its path ends in .php or .env: /wp-login.php, /.env and
#      /config/.env do. These don't: /php and /env (no dot before them),
#      /index.php.bak (.php is not at the end), /phpinfo, /.environment.
#
#   3. It is a failed login: method POST, path exactly /login and status
#      401. These don't count: GET /login with 401, POST /login with 200,
#      POST /login/reset or POST /api/login with 401.
#
# Case doesn't matter in paths: /WP-LOGIN.PHP, /.Env and POST /Login with
# status 401 look like attacks too.
#
# Print every request that looks like an attack, unchanged and in the order
# of LOGFILE. Print each one once, also when it matches more than one of
# the rules above. Print nothing else, to stdout or to stderr. Don't create
# or change any file.
#
# Exit with status 0 when it printed at least one request, and with status
# 1 when it printed none (also when LOGFILE is empty). That is grep's own
# exit status.
#
# One grep command does it, with -E for | and ( ), and -i to ignore case
# (see "Alternatives and groups" and "Leaving lines out and ignoring case"
# in lesson.md).
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /../../etc/passwd 400 0
#   2026-10-06T10:16:02 192.0.2.44 GET /wp-login.php 404 153
#   2026-10-06T10:16:15 192.0.2.44 GET /php 404 153
#   2026-10-06T10:16:20 203.0.113.5 POST /login 401 64
#   2026-10-06T10:16:48 203.0.113.5 POST /login 200 128
#   2026-10-06T10:17:03 198.51.100.7 GET /.ENV 404 153
#   2026-10-06T10:17:30 192.0.2.44 GET /index.php.bak 404 153
#
#   bash exercise/suspicious.sh access.log   prints
#     2026-10-06T10:15:40 198.51.100.7 GET /../../etc/passwd 400 0
#     2026-10-06T10:16:02 192.0.2.44 GET /wp-login.php 404 153
#     2026-10-06T10:16:20 203.0.113.5 POST /login 401 64
#     2026-10-06T10:17:03 198.51.100.7 GET /.ENV 404 153
#   and exits with status 0
#
# and with clean.log holding only the first line of access.log:
#
#   bash exercise/suspicious.sh clean.log   prints nothing, exits with 1
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../exercise/suspicious.sh access.log
# To see its exit status, run echo $? right after it.
#
# Write it so that `learn check` passes.

# TODO: write suspicious.sh
echo "suspicious.sh is not written yet." >&2
exit 1
