#!/usr/bin/env bash
# Challenge c3 – see "Pipes" in lesson.md.
#
# Print the first two GET requests in access.log (in the current folder):
# the first two lines that contain GET, in their order in the file. When
# there are fewer than two, print the ones there are; when there are none,
# print nothing. The script exits with status 0.
#
# Status 0 means success; a script ends with the status of its last command.
#
# Example, with access.log holding
#   2026-10-06T10:15:20 192.0.2.44 POST /login 401 64
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
#   2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 2048
#
#   bash challenges/c3.sh   prints
#                             2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#                             2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153

# TODO: write c3.sh
echo "c3.sh is not written yet." >&2
exit 1
