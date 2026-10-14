#!/usr/bin/env bash
# Challenge c2 – see "Keeping errors apart" in lesson.md.
#
# Print the lines of access.log (in the current folder) that contain POST,
# in their order in the file. When access.log is missing, throw grep's
# error message away by sending it to /dev/null, so it never reaches the
# screen. Then, in both cases, print "logkit: done" to stderr. The script
# exits with status 0.
#
# One grep command with its redirections handles both cases: no if is
# needed.
#
# Status 0 means success; a script ends with the status of its last command.
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:16:02 203.0.113.5 POST /login 401 64
#
#   bash challenges/c2.sh   prints "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64"
#                           and prints "logkit: done" to stderr
#
# and in a folder without access.log:
#
#   bash challenges/c2.sh   prints nothing, and prints only "logkit: done"
#                           to stderr

# TODO: write c2.sh
echo "c2.sh is not written yet." >&2
exit 1
