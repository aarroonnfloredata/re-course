#!/usr/bin/env bash
# Challenge c4 – see "Alternatives and groups" in lesson.md.
#
# Usage: bash challenges/c4.sh LOGFILE
#
# LOGFILE is a log file in the current folder. It is always given and
# always exists. Its name can hold spaces, also several in a row, and it
# never starts with "-".
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. A path starts
# with "/" and holds no spaces, and its letters are always lowercase. Every
# line ends with a newline, the last one too, and no line is empty.
# LOGFILE can be empty.
#
# Print the requests for the admin and login pages: those whose path is
# exactly /admin or /login, or starts with /admin/ or /login/, whatever the
# method. So /admin, /admin/, /admin/users, /login and /login/reset are
# printed. These are not:
#   - paths that only start with the same letters: /administrator,
#     /admin-tips, /login.php, /loginhelp;
#   - paths that hold admin or login further on: /api/login,
#     /blog/admin/tips.
# Print the requests unchanged, in the order of LOGFILE.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file.
#
# Exit with status 0 when it printed at least one request, and with status
# 1 when it printed none (also when LOGFILE is empty). That is grep's own
# exit status.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /admin 200 2048
#   2026-10-06T10:15:40 198.51.100.7 GET /administrator 404 153
#   2026-10-06T10:16:02 203.0.113.5 POST /login 401 64
#   2026-10-06T10:16:15 192.0.2.44 GET /login.php 404 153
#   2026-10-06T10:16:20 192.0.2.44 GET /admin/users 200 4096
#   2026-10-06T10:16:48 198.51.100.7 POST /api/login 200 128
#   2026-10-06T10:17:03 192.0.2.44 GET /login/reset 200 512
#   2026-10-06T10:17:30 203.0.113.5 GET /blog/admin/tips 200 1024
#
#   bash challenges/c4.sh access.log   prints
#     2026-10-06T10:15:32 203.0.113.5 GET /admin 200 2048
#     2026-10-06T10:16:02 203.0.113.5 POST /login 401 64
#     2026-10-06T10:16:20 192.0.2.44 GET /admin/users 200 4096
#     2026-10-06T10:17:03 192.0.2.44 GET /login/reset 200 512
#   and exits with status 0
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c4.sh access.log

# TODO: write c4.sh
echo "c4.sh is not written yet." >&2
exit 1
