#!/usr/bin/env bash
# Challenge c1 – see "Sending output to a file" in lesson.md.
#
# logkit keeps every request it has seen in archive.log, and the latest
# batch in latest.log. Both files are in the current folder, next to
# today.log, which always exists.
#
# Add the lines of today.log to the end of archive.log, keeping the lines
# archive.log already holds (create archive.log if it doesn't exist). Then
# copy the lines of today.log to latest.log, replacing whatever latest.log
# held before (create latest.log if it doesn't exist). Leave today.log as
# it is, print nothing and exit with status 0.
#
# Status 0 means success; a script ends with the status of its last command.
#
# Example, with today.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
# archive.log holding
#   2026-10-05T23:59:01 192.0.2.44 GET /about.html 200 2048
# and latest.log holding
#   2026-10-05T23:59:01 192.0.2.44 GET /about.html 200 2048
#
#   bash challenges/c1.sh   prints nothing, and leaves archive.log holding
#                           the 2026-10-05 line followed by the two lines of
#                           today.log, and latest.log holding only the two
#                           lines of today.log

# TODO: write c1.sh
echo "c1.sh is not written yet." >&2
exit 1
