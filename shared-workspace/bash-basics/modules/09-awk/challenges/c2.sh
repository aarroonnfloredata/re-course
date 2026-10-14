#!/usr/bin/env bash
# Challenge c2 – see "Choosing lines" in lesson.md.
#
# Usage: bash challenges/c2.sh LOGFILE
#
# LOGFILE is a log file in the current folder. It is always given and
# always exists. Its name can hold spaces anywhere, also several in a row
# and at the start ("  tuesday   log.log"). It never holds "=" and never
# starts with "-".
#
# Each line of LOGFILE is one request, with six fields separated by single
# spaces: time, client IP, method, path, status and bytes. A path starts
# with "/" and holds no spaces; it holds only lowercase letters, digits and
# the characters / . - and _. A status always has three digits. Every line
# ends with a newline, the last one too, and no line is empty. LOGFILE can
# be empty.
#
# Find the missing images: the requests whose path ends in .png, .jpg or
# .gif and whose status is 404. For each one, in the order of LOGFILE,
# print its path alone on a line. A path requested twice is printed twice.
#
#   - These paths end in an image extension: /logo.png, /img/photo.jpg,
#     /a.b.gif. These don't: /png, /logo.png.bak, /photo.jpeg, /logo_png.
#   - The status must be exactly 404: an image with status 200, 403 or 500
#     is left out, and so is a 404 request for /index.html.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0, also when nothing is printed.
#
# Use one awk program with a pattern (see "Choosing lines" in lesson.md).
#
# Examples, with access.log holding
#   2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
#   2026-10-06T10:15:40 198.51.100.7 GET /img/logo.png 404 153
#   2026-10-06T10:16:02 192.0.2.44 GET /img/photo.jpg 200 2048
#   2026-10-06T10:16:20 203.0.113.5 GET /missing.html 404 153
#   2026-10-06T10:16:48 192.0.2.44 GET /img/logo.png.bak 404 153
#   2026-10-06T10:17:03 198.51.100.7 GET /anim.gif 404 153
#
#   bash challenges/c2.sh access.log   prints
#     /img/logo.png
#     /anim.gif
#   and exits with status 0
#
# To try it by hand, make a folder in the module folder, put an access.log
# in it (the example lines above will do), go into that folder and run
#   bash ../challenges/c2.sh access.log

# TODO: write c2.sh
echo "c2.sh is not written yet." >&2
exit 1
