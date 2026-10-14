#!/usr/bin/env bash
# anonymize.sh: the eighth logkit tool. It writes a copy of a log file with
# the client IPs partly hidden, so the copy can be shared.
#
# Usage: bash exercise/anonymize.sh LOGFILE
#
# LOGFILE is the log file to read, as a path from the current folder (for
# example access.log, or logs/monday.log). It is always given and always
# exists. Its name can hold spaces, also several in a row, and glob
# characters such as * ? [ ], and it never starts with "-".
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. The time has the
# form 2026-10-06T10:15:32. The client IP is the second field: four numbers
# from 0 to 255 joined by dots, such as 203.0.113.5, each written without
# leading zeros. A path starts with "/" and holds no spaces; it can hold
# digits and dots, even ones that look like an IP (/geo/192.0.2.44). Every
# line ends with a newline, the last one too, and no line is empty. LOGFILE
# can be empty.
#
# Write a new file, LOGFILE.anon: the path LOGFILE with ".anon" added at
# the end, so it lands in the same folder as LOGFILE (access.log.anon,
# logs/monday.log.anon, "monday log.log.anon"). It holds every line of
# LOGFILE, in the same order, with one change: the last number of the
# client IP is replaced by 0.
#
#   - 203.0.113.5 becomes 203.0.113.0, and 198.51.100.254 becomes
#     198.51.100.0. An IP whose last number is already 0 stays the same.
#   - The first three numbers of the IP stay as they are, also when they
#     hold the same digits as the last one: 5.5.5.5 becomes 5.5.5.0, and
#     203.0.113.113 becomes 203.0.113.0.
#   - Every other field stays as it is, an IP in the path included.
#
# An empty LOGFILE gives an empty LOGFILE.anon. When LOGFILE.anon already
# exists, replace what it held: never add to it.
#
# Leave LOGFILE itself unchanged, and don't create or change any file other
# than LOGFILE.anon. Print nothing, to stdout or to stderr. Exit with
# status 0.
#
# One sed command does it, with -E and a group, writing its result with >
# (see "Reusing what matched with groups" and "Writing to a new file" in
# lesson.md).
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.254 GET /missing.html 404 153
#   2026-10-06T10:16:02 5.5.5.5 GET /geo/192.0.2.44 200 1024
#   2026-10-06T10:16:20 192.0.2.0 POST /login 401 64
#
#   bash exercise/anonymize.sh access.log   prints nothing, leaves
#   access.log as it was, and writes access.log.anon holding
#     2026-10-06T10:15:32 203.0.113.0 GET /index.html 200 512
#     2026-10-06T10:15:40 198.51.100.0 GET /missing.html 404 153
#     2026-10-06T10:16:02 5.5.5.0 GET /geo/192.0.2.44 200 1024
#     2026-10-06T10:16:20 192.0.2.0 POST /login 401 64
#
# and with the same lines in "logs/monday log.log":
#
#   bash exercise/anonymize.sh "logs/monday log.log"
#                     writes "logs/monday log.log.anon" with the four lines
#                     above, and prints nothing
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../exercise/anonymize.sh access.log
# then look at access.log.anon with cat.
#
# Write it so that `learn check` passes.

# TODO: write anonymize.sh
echo "anonymize.sh is not written yet." >&2
exit 1
