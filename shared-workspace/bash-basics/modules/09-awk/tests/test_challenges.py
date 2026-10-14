"""Checks for the inline challenges in lesson.md."""

import re

import pytest

from checks import check_run, log, name_error, spaces_hint
from helpers import lines, run_script

C1 = "challenges/c1.sh"
C2 = "challenges/c2.sh"
C3 = "challenges/c3.sh"

NOTES = log("Look into the 404s.")
ARGUMENT_HINT = 'Read the file the first argument names, "$1", whatever its name.'
STATUS_HINT = ("A script ends with the status of its last command: make awk the last one, and "
               "leave out the stub's exit 1.")


def check_challenge(script, name, files, expected, hint, diagnose=None, status_hint=STATUS_HINT):
    """Run `script` with the log file `name` in a folder holding `files`, and
    fail unless it printed just the `expected` lines, nothing to stderr,
    exited with 0 and left the files as they were. `diagnose(given, got,
    expected)` names a mistake the output shows; its hint wins over `hint`."""
    run = run_script(script, name, files=files)
    if " " in name and name_error(run):
        problem = spaces_hint(name)
    elif diagnose:
        problem = diagnose(lines(files[name]), lines(run.stdout), expected)
    else:
        problem = None
    check_run(run, expected, hint, problem, status_hint)


# c1

# Requests from the example in c1.sh.
C1_INDEX = "2026-10-06T10:15:32 203.0.113.5   GET  /index.html    200  512"
C1_MISSING = "2026-10-06T10:15:40 198.51.100.7  GET  /missing.html  404  153"
C1_LOGIN = "2026-10-06T10:16:02 192.0.2.44    POST /login         401  64"

# More requests, with other runs of spaces: wide, single, and mixed.
C1_HEALTH = "2026-10-06T10:16:20     127.0.0.1       HEAD    /health           200     0"
C1_DELETE = "2026-10-06T10:16:48 203.0.113.5 DELETE /api/items/7 204 0"
C1_REPORT = "2026-10-06T10:17:03  198.51.100.7 GET      /reports/2026-10-06.html 200   1024"
C1_MONDAY_INDEX = "2026-10-05T09:12:44   192.0.2.44   GET   /index.html   200   512"
C1_MONDAY_LOGO = "2026-10-05T09:13:02 203.0.113.5     GET /logo.png     200 4096"


def ip_and_path(*requests):
    """`requests` as c1 prints them: the client IP, a space and the path."""
    return [f"{request.split()[1]} {request.split()[3]}" for request in requests]


C1_HINT = ("The client IP is the second field and the path the fourth: in awk, print $2, $4 "
           "prints both with one space between them.")
C1_RUNS_HINT = ("cut -d ' ' sees an empty field between two spaces in a row. awk splits a line "
                "at every run of spaces, so $2 and $4 are the IP and the path on every line.")
C1_COMMA_HINT = ("Put a comma between the two fields: print $2, $4 prints one space between "
                 "them, print $2 $4 glues them together.")


def c1_mistake(given, got, expected):
    cut = [" ".join(line.split(" ")[1:4:2]) for line in given]
    if got != expected and got == cut:
        return C1_RUNS_HINT
    if got and all(" " not in line for line in got):
        return C1_COMMA_HINT
    return None


@pytest.mark.objective(1)
def test_c1_prints_the_ip_and_path_of_each_request():
    check_challenge(C1, "access.log",
                    {"access.log": log(C1_INDEX, C1_MISSING, C1_LOGIN), "notes.txt": NOTES},
                    ip_and_path(C1_INDEX, C1_MISSING, C1_LOGIN), C1_HINT, c1_mistake)
    check_challenge(C1, "access.log",
                    {"access.log": log(C1_HEALTH, C1_REPORT, C1_DELETE, C1_LOGIN)},
                    ip_and_path(C1_HEALTH, C1_REPORT, C1_DELETE, C1_LOGIN), C1_RUNS_HINT,
                    c1_mistake)
    check_challenge(C1, "access.log", {"access.log": log(C1_DELETE)}, ip_and_path(C1_DELETE),
                    C1_HINT, c1_mistake)
    check_challenge(C1, "empty.log", {"empty.log": "", "access.log": log(C1_INDEX, C1_MISSING)},
                    [], ARGUMENT_HINT)
    check_challenge(C1, "monday.log",
                    {"monday.log": log(C1_MONDAY_INDEX, C1_MONDAY_LOGO),
                     "access.log": log(C1_INDEX)},
                    ip_and_path(C1_MONDAY_INDEX, C1_MONDAY_LOGO), ARGUMENT_HINT, c1_mistake)
    check_challenge(C1, "monday  log.log",
                    {"monday  log.log": log(C1_MONDAY_LOGO, C1_HEALTH)},
                    ip_and_path(C1_MONDAY_LOGO, C1_HEALTH), spaces_hint("monday  log.log"),
                    c1_mistake)
    check_challenge(C1, "  tuesday   log.log", {"  tuesday   log.log": log(C1_REPORT)},
                    ip_and_path(C1_REPORT), spaces_hint("  tuesday   log.log"), c1_mistake)


# c2


def request(path, status, size=153, ip="198.51.100.7", time="2026-10-06T10:15:40"):
    return f"{time} {ip} GET {path} {status} {size}"


# Requests from the example in c2.sh.
C2_EXAMPLE = [
    "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512",
    "2026-10-06T10:15:40 198.51.100.7 GET /img/logo.png 404 153",
    "2026-10-06T10:16:02 192.0.2.44 GET /img/photo.jpg 200 2048",
    "2026-10-06T10:16:20 203.0.113.5 GET /missing.html 404 153",
    "2026-10-06T10:16:48 192.0.2.44 GET /img/logo.png.bak 404 153",
    "2026-10-06T10:17:03 198.51.100.7 GET /anim.gif 404 153",
]


def missing_images(*requests):
    """The paths c2 prints: those of the 404 requests for a .png, .jpg or
    .gif, in order."""
    found = []
    for line in requests:
        path, status = line.split(" ")[3:5]
        if status == "404" and re.search(r"\.(png|jpg|gif)$", path):
            found.append(path)
    return found


C2_HINT = ("Use one awk program: the pattern $5 == 404 && $4 ~ /\\.(png|jpg|gif)$/ chooses the "
           "missing images, and the action prints the path, $4.")
C2_EXTENSION_HINT = ("Match the end of the path, dot included: $4 ~ /\\.(png|jpg|gif)$/. In a "
                     "regular expression . matches any character, so write \\. for a dot, and $ "
                     "ties the match to the end of the path.")
C2_DOT_HINT = ("In a regular expression . matches any character, and without it png matches "
               "anywhere: write \\. for the dot before the extension, as in /\\.(png|jpg|gif)$/.")
C2_END_HINT = ("The extension must end the path: put $ after it, as in $4 ~ /\\.(png|jpg|gif)$/, "
               "and match it against the path, $4, where the line's end can't get in the way.")
C2_JPEG_HINT = "Only .png, .jpg and .gif count: /photo.jpeg doesn't end in .jpg."
C2_STATUS_HINT = ("Compare the status field alone: $5 == 404. A 404 elsewhere in the line, in "
                  "the path or the bytes, doesn't count, and neither does another 4xx or 5xx.")
C2_PATH_HINT = "Print the path alone: print $4."
C2_EVERY_TIME_HINT = ("Print a missing image every time it is requested, in the order of "
                      "LOGFILE: leave out sort and uniq.")
C2_EXIT_HINT = ("Exit with 0 also when no request is a missing image: make awk the last "
                "command. grep, for one, exits with 1 when it finds nothing.")


def c2_mistake(given, got, expected):
    if got == expected:
        return None
    if any(" " in path for path in got):
        return C2_PATH_HINT
    status_of = {line.split(" ")[3]: line.split(" ")[4] for line in given}
    for path in got:
        if path in expected:
            continue
        if path.endswith(".jpeg"):
            return C2_JPEG_HINT
        if not re.search(r"\.(png|jpg|gif)$", path):
            if re.search(r"\.(png|jpg|gif)", path):
                return C2_END_HINT
            if re.search(r"(png|jpg|gif)$", path):
                return C2_DOT_HINT
            return C2_EXTENSION_HINT
        if status_of.get(path) != "404":
            return C2_STATUS_HINT
    if set(got) == set(expected):  # duplicates left out, or the order changed
        return C2_EVERY_TIME_HINT
    return None


@pytest.mark.objective(2)
def test_c2_prints_the_path_of_each_missing_image():
    def c2_check(name, requests, hint, files=None):
        check_challenge(C2, name, {name: log(*requests), **(files or {})},
                        missing_images(*requests), hint, c2_mistake, C2_EXIT_HINT)

    c2_check("access.log", C2_EXAMPLE, C2_HINT, {"notes.txt": NOTES})
    c2_check("access.log", [request("/logo.png", 404), request("/index.html", 200, 512),
                            request("/img/photo.jpg", 404), request("/a.b.gif", 404)],
             C2_EXTENSION_HINT)
    c2_check("access.log", [request("/png", 404), request("/logo_png", 404),
                            request("/logo.png.bak", 404), request("/photo.jpeg", 404),
                            request("/images/cat.gif", 404), request("/gif", 404),
                            request("/xjpg", 404), request("/a.jpg.html", 404),
                            request("/img.png/index.html", 404)],
             C2_EXTENSION_HINT)
    c2_check("access.log", [request("/img/a.png", 200), request("/img/b.png", 403),
                            request("/img/c.jpg", 500), request("/img/d.gif", 401),
                            request("/img/e.png", 410), request("/img/f.jpg", 304),
                            request("/img/g.png", 404), request("/img/h.gif", 200, 404),
                            request("/img/404.png", 200, 512), request("/img/404.jpg", 404, 512),
                            request("/missing.html", 404)],
             C2_STATUS_HINT)
    c2_check("access.log", [request("/img/logo.png", 404), request("/index.html", 200, 512),
                            request("/anim.gif", 404), request("/img/logo.png", 404),
                            request("/img/logo.png", 404)],
             C2_EVERY_TIME_HINT)
    c2_check("access.log", [request("/index.html", 404), request("/img/logo.png", 200, 512),
                            request("/logo.png.bak", 404)],
             C2_HINT)
    c2_check("empty.log", [], ARGUMENT_HINT, {"access.log": log(*C2_EXAMPLE)})
    c2_check("monday.log", [request("/icons/home.gif", 404), request("/about.html", 200)],
             ARGUMENT_HINT, {"access.log": log(*C2_EXAMPLE)})
    c2_check("monday  log.log", [request("/img/x.jpg", 404), request("/img/y.png", 404)],
             spaces_hint("monday  log.log"))
    c2_check("  tuesday   log.log", [request("/index.html", 200), request("/img/z.gif", 404)],
             spaces_hint("  tuesday   log.log"))


# c3

# Requests from the example in c3.sh.
C3_EXAMPLE = [
    "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512",
    "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153",
    "2026-10-06T10:16:48 192.0.2.44 GET /logo.png 200 1024",
    "2026-10-06T10:17:03 203.0.113.5 GET /api/stats 503 0",
]


def sized(*sizes):
    """One request per size in `sizes`, with that many bytes."""
    return [f"2026-10-06T11:{minute:02d}:00 192.0.2.{minute} GET /page/{minute}.html 200 {size}"
            for minute, size in enumerate(sizes, start=1)]


def total(requests):
    return [str(sum(int(line.split(" ")[5]) for line in requests))]


C3_HINT = ("Add the bytes field, $6, of every line to a total with total += $6, and print the "
           "total once, in an END block.")
C3_ZERO_HINT = ("With no lines, the action never runs and the total stays empty: print "
                "total + 0 in END, so an empty LOGFILE prints 0.")
C3_PLUS_HINT = "Add each line's bytes to the total with +=: = keeps only the last line's bytes."
C3_END_HINT = ("Print the total once, in an END block: a print in the action for every line "
               "prints a running total on each line.")


def c3_mistake(given, got, expected):
    if got == expected:
        return None
    if len(got) > 1:
        return C3_END_HINT
    if not given and got in ([], [""]):
        return C3_ZERO_HINT
    if len(given) > 1 and got == [given[-1].split(" ")[5]]:
        return C3_PLUS_HINT
    return None


@pytest.mark.objective(3)
def test_c3_prints_the_total_bytes():
    def c3_check(name, requests, hint, files=None):
        check_challenge(C3, name, {name: log(*requests), **(files or {})}, total(requests), hint,
                        c3_mistake)

    c3_check("access.log", C3_EXAMPLE, C3_HINT, {"notes.txt": NOTES})
    c3_check("empty.log", [], C3_ZERO_HINT, {"access.log": log(*C3_EXAMPLE)})
    c3_check("access.log", sized(2048), C3_HINT)
    c3_check("access.log", sized(2048, 64, 7), C3_PLUS_HINT)
    c3_check("access.log", sized(0, 0, 0), C3_HINT)
    c3_check("access.log", sized(*range(1, 13)), C3_HINT)
    c3_check("access.log", sized(600000000, 399999999, 1), C3_HINT)
    c3_check("monday.log", sized(4096, 404), ARGUMENT_HINT, {"access.log": log(*C3_EXAMPLE)})
    c3_check("monday  log.log", sized(153, 64), spaces_hint("monday  log.log"))
    c3_check("  tuesday   log.log", sized(512), spaces_hint("  tuesday   log.log"))
