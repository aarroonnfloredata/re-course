"""Checks for the inline challenges in lesson.md."""

import posixpath

import pytest

from checks import (as_found, check_run, folders, inside, log, name_error, pattern_error,
                    sized)
from helpers import lines, run_script

C1 = "challenges/c1.sh"
C2 = "challenges/c2.sh"
C3 = "challenges/c3.sh"
C4 = "challenges/c4.sh"

NOTES = log("Look into the 404s.")
GLOB_CHARACTERS = set("*?[]")

PATTERN_HINT = ("Quote the pattern, as in -name '*.log': unquoted, bash expands it to the "
                "matching names in the current folder, such as today.log, before find sees it.")
WHERE_HINT = ('Search the folder from the first argument, find "$1" ...: find prints each path '
              "starting with DIR exactly as given.")
DEPTH_HINT = ('find searches the subfolders of "$1" at any depth by itself: give it "$1" and '
              'let its tests pick the files, instead of a glob such as "$1"/*.log.')


def quote_hint(folder):
    return (f'Put $1 in double quotes: find "$1" keeps {folder!r} in one piece, its runs of '
            "spaces too.")


def glob_hint(folder, other):
    return (f"Put $1 in double quotes: quoted, the * ? [ ] in {folder!r} are plain text. "
            f"Unquoted, they make a glob that can match other folders, such as {other}.")


def search_problem(run, folder, files, paths=True):
    """A hint when the run split DIR, let bash expand a pattern, or searched
    another folder. With `paths`, the run prints paths starting with DIR."""
    if " " in folder and name_error(run):
        return quote_hint(folder)
    if pattern_error(run):
        return PATTERN_HINT
    if paths and any(not line.startswith(folder + "/") for line in lines(run.stdout)):
        others = sorted(name for name in folders(files) if "/" not in name and name != folder)
        if GLOB_CHARACTERS & set(folder) and others:
            return glob_hint(folder, others[0])
        if " " in folder:
            return quote_hint(folder)
        return WHERE_HINT
    return None


def found_folders(folder, files):
    """The folders find prints when it searches `folder`."""
    return {folder} | {as_found(folder, name) for name in folders(files) if inside(folder, name)}


def sizes(folder, files):
    """The size of each file under `folder`, by its path as find prints it."""
    return {as_found(folder, path): len(content.encode())
            for path, content in files.items() if inside(folder, path)}


def depth(folder, path):
    """How many subfolders deep under `folder` the printed `path` is."""
    return path[len(folder) + 1:].count("/")


def unquoted(files, endings):
    """What -name keeps when the patterns *<ending> are left unquoted: a
    function of a file's name. bash expands each pattern to the matching
    names in the run's folder. None when no pattern matches there, or one
    matches several names, which makes find fail."""
    matches = {ending: [path for path in files if "/" not in path and path.endswith(ending)]
               for ending in endings}
    if not any(matches.values()) or any(len(names) > 1 for names in matches.values()):
        return None

    def keeps(name):
        return any(name.endswith(ending) and (not names or name == names[0])
                   for ending, names in matches.items())
    return keeps


def limited_problem(folder, files, got, expected, endings, path_of=lambda line: line):
    """A hint when the run printed only some of the `expected` lines: those
    of the files directly in DIR, or those an unquoted pattern keeps."""
    alternatives = [([line for line in expected if not depth(folder, path_of(line))],
                     DEPTH_HINT)]
    keeps = unquoted(files, endings)
    if keeps:
        alternatives.append(([line for line in expected
                              if keeps(posixpath.basename(path_of(line)))], PATTERN_HINT))
    hints = {hint for lines_, hint in alternatives
             if sorted(lines_) == sorted(got) != sorted(expected)}
    return hints.pop() if len(hints) == 1 else None


def name_hint(name, endings):
    if name.lower().endswith(endings):
        return (f"-name is case-sensitive, -iname isn't: use -name, so that {name} is left "
                "out.")
    patterns = " or ".join(f"'*{ending}'" for ending in endings)
    return f"Match names that end in exactly {' or '.join(endings)}, with -name {patterns}: " \
           f"{name} doesn't."


# c1


def big_logs(folder, files):
    """What c1 prints: the .log files under `folder` of more than 1024 bytes."""
    return [as_found(folder, path) for path, content in files.items()
            if inside(folder, path) and path.endswith(".log") and len(content.encode()) > 1024]


C1_HINT = ("find \"$1\" -type f -name '*.log' -size +1024c keeps the regular files whose names "
           "end in .log and that hold more than 1024 bytes.")
C1_UNIT_HINT = ("Give the size in bytes, with c: -size +1024c. Without a letter, -size counts "
                "512-byte blocks.")
C1_1024_HINT = ("1024 bytes is not more than 1024: -size +1024c keeps the files of 1025 bytes "
                "or more.")
C1_SIZE_HINT = "-size +1024c keeps the files of more than 1024 bytes, and only those."


def c1_problem(run, folder, files):
    problem = search_problem(run, folder, files)
    if problem:
        return problem
    got, expected, size = lines(run.stdout), big_logs(folder, files), sizes(folder, files)
    for path in got:
        if path in expected:
            continue
        if path in found_folders(folder, files):
            return f"{path} is a folder: add -type f to keep only regular files."
        if path not in size:
            continue
        if not path.endswith(".log"):
            return name_hint(posixpath.basename(path), (".log",))
        if size[path] == 1024:
            return C1_1024_HINT
        if size[path] < 1024:
            return C1_SIZE_HINT
    missing = [path for path in expected if path not in got]
    if any(size[path] == 1025 for path in missing):
        return C1_1024_HINT
    return limited_problem(folder, files, got, expected, (".log",))


# The 64 empty files make the folder archive.log itself bigger than 1024
# bytes on most file systems, so that -size alone doesn't leave it out.
ARCHIVE = {f"logs/archive.log/request-{number:02d}.txt": "" for number in range(1, 65)}

C1_CASES = [
    ("logs", {"logs/access.log": sized(2000), "logs/small.log": sized(1024),
              "logs/empty.log": "", "logs/notes.txt": sized(3000),
              "logs/old/monday log.log": sized(1500), "logs/archive.log/old.txt": sized(1100)},
     C1_HINT),
    ("logs", {"logs/1 byte.log": sized(1), "logs/1023 bytes.log": sized(1023),
              "logs/1024 bytes.log": sized(1024), "logs/1025 bytes.log": sized(1025),
              "logs/1026 bytes.log": sized(1026), "logs/4096 bytes.log": sized(4096),
              "logs/100000 bytes.log": sized(100000)},
     C1_UNIT_HINT),
    ("logs", {"logs/access.log": sized(2000), "logs/error.log": sized(1025),
              "logs/access.log.old": sized(2000), "logs/server.LOG": sized(2000),
              "logs/access.log.gz": sized(2000), "logs/catalog": sized(2000),
              "logs/notes.txt": sized(2000)},
     name_hint("access.log.old", (".log",))),
    ("logs", {"logs/access.log": sized(2000), "logs/old/monday.log": sized(1500),
              "logs/2026/09/30/night.log": sized(1100), "logs/2026/09/30/tiny.log": sized(10),
              "logs/2026/notes.txt": sized(5000)},
     DEPTH_HINT),
    ("logs", {"logs/access.log": sized(2000), "logs/archive.log/old.log": sized(1500),
              "logs/archive.log/old.txt": sized(1100), **ARCHIVE},
     "A folder is never a log file, also when its name ends in .log: add -type f."),
    ("logs", {"logs/dad's log.log": sized(2000), 'logs/say "hi".log': sized(2000),
              "logs/-rf.log": sized(2000), "logs/[ab]*?.log": sized(1500),
              "logs/  two  spaces.log": sized(1200), "logs/-small.log": sized(10)},
     "Print each path just as find prints it, whatever characters its name holds."),
    ("logs", {"today.log": sized(2000), "logs/access.log": sized(2000),
              "logs/old/monday log.log": sized(1500)},
     PATTERN_HINT),
    (".", {"access.log": sized(2000), "small.log": sized(100), "notes.txt": sized(3000),
           "old/monday log.log": sized(1500)},
     WHERE_HINT),
    ("  old  logs", {"  old  logs/access.log": sized(2000), "  old  logs/small.log": sized(10),
                     "  old  logs/2026/night.log": sized(1500)},
     quote_hint("  old  logs")),
    ("logs*", {"logs*/access.log": sized(2000), "logs-old/access.log": sized(2000)},
     glob_hint("logs*", "logs-old")),
    ("logs", {"logs/small.log": sized(1024), "logs/notes.txt": sized(3000),
              "logs/old/empty.log": ""},
     C1_SIZE_HINT),
]


@pytest.mark.objective(1)
def test_c1_prints_the_big_log_files():
    for folder, files, hint in C1_CASES:
        run = run_script(C1, folder, files=files)
        check_run(run, big_logs(folder, files), contents=False, any_order=True, hint=hint,
                  problem=c1_problem(run, folder, files))


# c2


def kept_logs(folder, files):
    """What c2 prints: the non-empty .log and .old files under `folder`."""
    return [as_found(folder, path) for path, content in files.items()
            if inside(folder, path) and path.endswith((".log", ".old")) and content]


C2_HINT = ("find \"$1\" -type f ! -empty \\( -name '*.log' -o -name '*.old' \\) keeps the "
           "regular, non-empty files whose names end in .log or .old.")
C2_EMPTY_HINT = "Leave out the empty files with ! -empty: a file is kept only if it holds a byte."
C2_GROUP_HINT = ("Put the two names in parentheses, \\( -name '*.log' -o -name '*.old' \\): "
                 "without them, -o splits the tests in two, and -type f and ! -empty apply to "
                 "one name only.")
C2_OR_HINT = "Keep both kinds of names: join -name '*.log' and -name '*.old' with -o."


def c2_problem(run, folder, files):
    problem = search_problem(run, folder, files)
    if problem:
        return problem
    got, expected, size = lines(run.stdout), kept_logs(folder, files), sizes(folder, files)
    every_folder = found_folders(folder, files)
    endings = (".log", ".old")
    empty, folder_endings = set(), set()
    for path in got:
        if path in expected:
            continue
        if path in every_folder:
            folder_endings.add(path[-4:])
        elif path in size and not path.endswith(endings):
            return name_hint(posixpath.basename(path), endings)
        elif size.get(path) == 0:
            empty.add(path[-4:])
    if empty or folder_endings:
        unprinted_empty = {path[-4:] for path, bytes_ in size.items()
                           if bytes_ == 0 and path.endswith(endings) and path not in got}
        if len(empty) == 1 and unprinted_empty - empty:
            return C2_GROUP_HINT
        if len(folder_endings) == 1 and empty:
            return C2_GROUP_HINT
        if folder_endings:
            return "A folder is never kept: add -type f, before the parentheses."
        return C2_EMPTY_HINT
    missing = [path for path in expected if path not in got]
    missing_endings = {path[-4:] for path in missing}
    if len(missing_endings) == 1 and not missing_endings & {path[-4:] for path in got}:
        return C2_OR_HINT
    return limited_problem(folder, files, got, expected, endings)


LINE = log("2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512")

C2_CASES = [
    ("logs", {"logs/access.log": LINE, "logs/access.log.old": LINE, "logs/empty.log": "",
              "logs/empty.old": "", "logs/notes.txt": NOTES, "logs/archive.old/monday.log": LINE},
     C2_HINT),
    ("logs", {"logs/access.log": LINE, "logs/monday.old": LINE, "logs/access.log.old": LINE,
              "logs/access.old.log": LINE, "logs/server.LOG": LINE, "logs/tuesday.OLD": LINE,
              "logs/access.log.gz": LINE, "logs/access.old.gz": LINE, "logs/catalog": LINE,
              "logs/bold": LINE, "logs/notes.txt": NOTES},
     name_hint("access.log.gz", (".log", ".old"))),
    ("logs", {"logs/a.log": "", "logs/b.old": "", "logs/c.log": LINE, "logs/d.old": LINE,
              "logs/old/e.log": "", "logs/old/f.old": "", "logs/one byte.log": "x",
              "logs/one byte.old": "x"},
     C2_EMPTY_HINT),
    ("logs", {"logs/access.log": LINE, "logs/archive.old/monday.log": LINE,
              "logs/archive.log/tuesday.old": LINE, "logs/archive.log/notes.txt": NOTES},
     "A folder is never kept: add -type f, before the parentheses."),
    ("logs", {"logs/access.log": LINE, "logs/old/monday.old": LINE,
              "logs/2026/09/30/night.log": LINE, "logs/2026/09/30/empty.old": "",
              "logs/2026/notes.txt": NOTES},
     DEPTH_HINT),
    ("logs", {"logs/empty.log": "", "logs/empty.old": "", "logs/notes.txt": NOTES,
              "logs/access.log.gz": LINE, "logs/old/empty.log": ""},
     "When no file is to be kept, print nothing."),
    ("logs", {"logs/dad's log.log": LINE, 'logs/say "hi".old': LINE, "logs/-rf.log": LINE,
              "logs/[ab]*?.old": LINE, "logs/  two  spaces.log": LINE, "logs/-empty.old": ""},
     "Print each path just as find prints it, whatever characters its name holds."),
    ("logs", {"today.log": LINE, "today.old": LINE, "logs/access.log": LINE,
              "logs/old/monday.old": LINE},
     PATTERN_HINT),
    (".", {"access.log": LINE, "access.log.old": LINE, "empty.log": "", "notes.txt": NOTES,
           "old/monday log.old": LINE},
     WHERE_HINT),
    ("  old  logs", {"  old  logs/access.log": LINE, "  old  logs/empty.old": "",
                     "  old  logs/2026/monday.old": LINE},
     quote_hint("  old  logs")),
    ("logs*", {"logs*/access.log": LINE, "logs-old/access.old": LINE},
     glob_hint("logs*", "logs-old")),
]


@pytest.mark.objective(2)
def test_c2_prints_the_logs_to_keep():
    for folder, files, hint in C2_CASES:
        run = run_script(C2, folder, files=files)
        check_run(run, kept_logs(folder, files), contents=False, any_order=True, hint=hint,
                  problem=c2_problem(run, folder, files))


# c3


def request(status, size, path="/index.html", ip="203.0.113.5", time="2026-10-06T10:15:32"):
    return f"{time} {ip} GET {path} {status} {size}"


def sized_requests(*sizes):
    """One request per size in `sizes`, with that many bytes."""
    return [request(200, size, f"/page/{number}.html", f"192.0.2.{number}",
                    f"2026-10-06T11:{number:02d}:00")
            for number, size in enumerate(sizes, start=1)]


def bytes_of(content):
    """The sum of the bytes fields of the requests in `content`."""
    total = 0
    for line in lines(content):
        fields = line.split(" ")
        if len(fields) == 6 and fields[5].isdigit():
            total += int(fields[5])
    return total


def total_bytes(folder, files, counts=lambda path: path.endswith(".log")):
    """What c3 prints: the bytes of all requests in the files under `folder`
    that `counts`."""
    return sum(bytes_of(content) for path, content in files.items()
               if inside(folder, path) and counts(path))


C3_HINT = ("find \"$1\" -name '*.log' -exec awk '{ total += $6 } END { print total + 0 }' {} + "
           "runs one awk on all the log files, which adds up their bytes and prints the "
           "total once.")
C3_PLUS_HINT = ("End -exec with +, not \\;: with \\; find runs awk once for each file, and "
                "each awk prints its own total.")
C3_ZERO_HINT = ("When awk reads no lines, the total stays empty: print total + 0, so that it "
                "prints 0.")
C3_NAME_HINT = ("Only the files whose names end in exactly .log count: -name '*.log' leaves out "
                "access.log.old, server.LOG and notes.txt.")
C3_SPLIT_HINT = ("Let find pass the names to awk, with -exec awk ... {} +: each path arrives "
                 "whole, its spaces and quotes too.")


def c3_problem(run, folder, files):
    if name_error(run) and " " not in folder:
        return C3_SPLIT_HINT
    problem = search_problem(run, folder, files, paths=False)
    if problem:
        return problem
    got = lines(run.stdout)
    if len(got) > 1:
        return C3_PLUS_HINT
    expected = str(total_bytes(folder, files))
    if expected == "0" and got in ([], [""]):
        return C3_ZERO_HINT
    if not got or got[0] == expected:
        return None
    alternatives = [
        (total_bytes(folder, files, lambda path: True), C3_NAME_HINT),
        (total_bytes(folder, files, lambda path: ".log" in path.lower()), C3_NAME_HINT),
        (total_bytes(folder, files, lambda path: path.endswith(".log")
                     and not depth(folder, as_found(folder, path))), DEPTH_HINT),
    ]
    keeps = unquoted(files, (".log",))
    if keeps:
        alternatives.append((total_bytes(folder, files,
                                         lambda path: keeps(posixpath.basename(path))),
                             PATTERN_HINT))
    hints = {hint for total, hint in alternatives if got[0] == str(total)}
    return hints.pop() if len(hints) == 1 else None


C3_EXAMPLE = {
    "logs/access.log": log("2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512",
                           "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153"),
    "logs/old/monday log.log": log("2026-10-05T09:12:44 192.0.2.44 GET /logo.png 200 1024"),
    "logs/access.log.old": log("2026-10-04T18:20:31 192.0.2.44 GET /index.html 200 512"),
    "logs/empty.log": "",
}

C3_CASES = [
    ("logs", C3_EXAMPLE, C3_HINT),
    ("quiet", {"quiet/empty.log": ""}, C3_ZERO_HINT),
    ("quiet", {"quiet/a.log": "", "quiet/old/b.log": "", "quiet/notes.txt": log(
        *sized_requests(999))}, C3_ZERO_HINT),
    ("logs", {"logs/access.log": log(*sized_requests(2048))}, C3_HINT),
    ("logs", {"logs/access.log": log(*sized_requests(512, 153, 0)),
              "logs/error.log": log(*sized_requests(64)),
              "logs/old/a.log": log(*sized_requests(1024, 1)),
              "logs/old/b.log": log(*sized_requests(7)),
              "logs/old/c.log": log(*sized_requests(0)),
              "logs/2026/09/d.log": log(*sized_requests(300, 30, 3)),
              "logs/2026/09/e.log": "",
              "logs/2026/10/f.log": log(*sized_requests(4096))},
     C3_PLUS_HINT),
    ("logs", {"logs/access.log": log(*sized_requests(600000000)),
              "logs/old/big.log": log(*sized_requests(399999999, 1))},
     "Print the total as a whole number, digits only, such as 1000000000."),
    ("logs", {"logs/access.log": log(*sized_requests(512)),
              "logs/access.log.old": log(*sized_requests(1000)),
              "logs/server.LOG": log(*sized_requests(2000)),
              "logs/access.log.gz": log(*sized_requests(4000)),
              "logs/catalog": log(*sized_requests(8000)),
              "logs/notes.txt": log(*sized_requests(16000))},
     C3_NAME_HINT),
    ("logs", {"logs/dad's log.log": log(*sized_requests(100)),
              'logs/say "hi".log': log(*sized_requests(200, 3)),
              "logs/-v.log": log(*sized_requests(400)),
              "logs/[ab]*?.log": log(*sized_requests(800)),
              "logs/  two  spaces.log": log(*sized_requests(1600)),
              "logs/old logs/monday.log": log(*sized_requests(3200))},
     C3_SPLIT_HINT),
    (".", {"access.log": log(*sized_requests(512, 153)), "error.log": log(*sized_requests(64)),
           "notes.txt": log(*sized_requests(999)),
           "old/monday log.log": log(*sized_requests(1024))},
     C3_HINT),
    ("  old  logs", {"  old  logs/access.log": log(*sized_requests(512)),
                     "  old  logs/2026/monday.log": log(*sized_requests(64))},
     quote_hint("  old  logs")),
    ("logs*", {"logs*/access.log": log(*sized_requests(512)),
               "logs-old/access.log": log(*sized_requests(1024))},
     glob_hint("logs*", "logs-old")),
    ("logs", {"today.log": log(*sized_requests(4096)),
              "logs/access.log": log(*sized_requests(512)),
              "logs/old/monday log.log": log(*sized_requests(1024))},
     PATTERN_HINT),
]


@pytest.mark.objective(3)
def test_c3_prints_the_total_bytes():
    for folder, files, hint in C3_CASES:
        run = run_script(C3, folder, files=files)
        check_run(run, [str(total_bytes(folder, files))], hint=hint,
                  problem=c3_problem(run, folder, files))


# c4


def not_found_counts(folder, files, counts=lambda line: " 404 " in line):
    """What c4 prints: FILE:N for each .log file under `folder`, where N is
    the number of its lines that `counts`."""
    return [f"{as_found(folder, path)}:{sum(map(counts, lines(content)))}"
            for path, content in files.items() if inside(folder, path) and path.endswith(".log")]


C4_HINT = ("find \"$1\" -name '*.log' -print0 | xargs -0 grep -c -H ' 404 ' prints FILE:N for "
           "every log file.")
C4_H_HINT = ("Add -H: with -c, grep puts the file name before the count only when it has more "
             "than one file, and -H makes it do so always.")
C4_ZERO_HINT = ("Use find -print0 with xargs -0: plain xargs splits names at spaces and takes "
                "' and \" as quotes, so such names don't arrive whole.")
C4_PATTERN_HINT = ("Search for ' 404 ', with a space on each side: 404 in the path "
                   "(/errors/404.html) or as the bytes at the end of the line doesn't count.")
C4_NAME_HINT = ("Only the files whose names end in exactly .log count: -name '*.log' leaves out "
                "access.log.old, server.LOG and notes.txt.")


def c4_problem(run, folder, files):
    if name_error(run):
        if " " in folder:
            return (f'Put $1 in double quotes, find "$1", and pass the names with -print0 and '
                    f"xargs -0: both keep {folder!r} and the names under it in one piece.")
        return C4_ZERO_HINT
    got, expected = lines(run.stdout), not_found_counts(folder, files)
    if got and all(":" not in line for line in got):
        return C4_H_HINT
    problem = search_problem(run, folder, files)
    if problem:
        return problem
    log_paths = {line.rsplit(":", 1)[0] for line in expected}
    if any(line.rsplit(":", 1)[0] not in log_paths for line in got):
        return C4_NAME_HINT
    for counts in (lambda line: "404" in line, lambda line: " 404" in line,
                   lambda line: "404 " in line):
        if sorted(got) == sorted(not_found_counts(folder, files, counts)):
            return C4_PATTERN_HINT
    return limited_problem(folder, files, got, expected, (".log",),
                           lambda line: line.rsplit(":", 1)[0])


C4_EXAMPLE = {
    "logs/access.log": log("2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512",
                           "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153",
                           "2026-10-06T10:16:15 192.0.2.44 GET /errors/404.html 200 404"),
    "logs/old/monday log.log": log("2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153",
                                   "2026-10-05T09:13:40 198.51.100.7 GET /favicon.ico 404 153"),
    "logs/dad's log.log": log("2026-10-04T18:20:31 192.0.2.44 GET /index.html 200 512"),
    "logs/empty.log": "",
    "logs/notes.txt": NOTES,
}

MISSING = request(404, 153, "/missing.html", "198.51.100.7", "2026-10-06T10:15:40")
INDEX = request(200, 512)

C4_CASES = [
    ("logs", C4_EXAMPLE, C4_HINT),
    ("logs", {"logs/access.log": log(INDEX, MISSING), "logs/notes.txt": log(MISSING),
              "logs/access.log.old": log(MISSING, MISSING)},
     C4_H_HINT),
    ("logs", {"logs/access.log": log(MISSING, request(200, 512, "/errors/404.html"),
                                     request(200, 404), request(404, 404, "/404"),
                                     request(301, 4040, "/old"), request(410, 153, "/gone"),
                                     request(403, 404, "/admin")),
              "logs/old/monday.log": log(request(200, 512, "/404"), MISSING)},
     C4_PATTERN_HINT),
    ("logs", {"logs/access.log": log(MISSING), "logs/old/monday.log": log(INDEX),
              "logs/access.log.old": log(MISSING), "logs/server.LOG": log(MISSING),
              "logs/access.log.gz": log(MISSING, MISSING), "logs/notes.txt": log(MISSING),
              "logs/catalog": log(MISSING)},
     C4_NAME_HINT),
    ("logs", {"logs/dad's log.log": log(MISSING), 'logs/say "hi".log': log(MISSING, MISSING),
              "logs/  two  spaces.log": log(INDEX), "logs/-n.log": log(MISSING),
              "logs/[ab]*?.log": log(INDEX), "logs/old logs/monday.log": log(MISSING)},
     C4_ZERO_HINT),
    ("logs", {"logs/access.log": log(MISSING), "logs/2026/09/30/night.log": log(MISSING, INDEX),
              "logs/2026/10/quiet.log": log(INDEX)},
     DEPTH_HINT),
    (".", {"access.log": log(MISSING), "error.log": log(INDEX),
           "old/monday log.log": log(MISSING, MISSING), "notes.txt": log(MISSING)},
     WHERE_HINT),
    ("  old  logs", {"  old  logs/access.log": log(MISSING),
                     "  old  logs/2026/monday.log": log(INDEX)},
     quote_hint("  old  logs")),
    ("logs*", {"logs*/access.log": log(MISSING), "logs-old/access.log": log(MISSING)},
     glob_hint("logs*", "logs-old")),
    ("logs", {"today.log": log(MISSING), "logs/access.log": log(MISSING),
              "logs/old/monday log.log": log(INDEX)},
     PATTERN_HINT),
]


@pytest.mark.objective(4)
def test_c4_prints_the_404_count_of_each_log_file():
    for folder, files, hint in C4_CASES:
        run = run_script(C4, folder, files=files)
        check_run(run, not_found_counts(folder, files), any_order=True, hint=hint,
                  problem=c4_problem(run, folder, files))
