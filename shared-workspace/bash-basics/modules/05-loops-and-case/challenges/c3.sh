#!/usr/bin/env bash
# Challenge c3 – see "Choosing with case" in lesson.md.
#
# Usage: bash challenges/c3.sh REQUEST_PATH
#
# REQUEST_PATH is the path of a request, the fourth field of a log line,
# such as /index.html or /api/stats. It is always given, starts with "/"
# and holds no spaces. (Don't call your variable PATH: bash uses that name
# to find commands.)
#
# Print one line:
#   REQUEST_PATH: KIND
# with REQUEST_PATH exactly as given, and KIND one of:
#   page    when REQUEST_PATH ends with .html, or with / (a folder's index
#           page, such as / or /blog/)
#   image   when REQUEST_PATH ends with .png, .jpg or .gif
#   other   for every other REQUEST_PATH
#
# The ending must be at the very end: /index.html.bak and /logo.png?v=2 are
# other. Upper and lower case letters differ: /LOGO.PNG is other.
#
# Print nothing else, to stdout or to stderr. Don't create or change any
# file. Exit with status 0.
#
# Examples:
#   bash challenges/c3.sh /index.html       prints "/index.html: page"
#   bash challenges/c3.sh /blog/            prints "/blog/: page"
#   bash challenges/c3.sh /photos/cat.jpg   prints "/photos/cat.jpg: image"
#   bash challenges/c3.sh /index.html.bak   prints "/index.html.bak: other"
#   bash challenges/c3.sh /api/stats        prints "/api/stats: other"

# TODO: write c3.sh
echo "c3.sh is not written yet." >&2
exit 1
