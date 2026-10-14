# Finding Files with find and xargs

[`exercise/summary.sh`](exercise/summary.sh) reads only the `.log` files
directly in one folder, not those in its subfolders. `find` searches a
folder and all its subfolders for the files you ask for, and can run a
command on them itself. ([tlcl#find-find-files-the-hard-way]) `xargs` is
another way to hand them to a command. ([tlcl#improving-efficiency])

In this module you add [`exercise/scan.sh`](exercise/scan.sh) to logkit:
it counts the 5xx requests in every log file under a folder.

By the end of this module you can:

1. Find files by name, type and size with `find`'s tests
2. Combine tests with `!` and `-o`
3. Run a command on the found files with `-exec ... {} +`
4. Pass file names with spaces safely to `xargs` with `-print0` and `-0`

**How to work through it:** give each example a new empty folder:
leftover files change what `find` prints.

## Searching a folder tree

Given a folder, `find` lists the folder and everything below it, on
standard output. The examples pipe it through `sort`: `find` prints
entries in the order they sit on the
disk. ([tlcl#find-find-files-the-hard-way]) They build folder trees with
`mkdir -p`, which creates the parent folders a path needs, and
`touch file`, which creates an empty file if there is
none. ([tlcl#find-find-files-the-hard-way]) Each path starts with the
given folder:

```bash run
mkdir -p logs/old
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > logs/access.log
echo "Look into the 404s." > logs/notes.txt
touch logs/old/empty.log
find logs | sort
```
```output
logs
logs/access.log
logs/notes.txt
logs/old
logs/old/empty.log
```

## Tests: name, type and size

Tests narrow the list down. ([tlcl#find-find-files-the-hard-way])
`-type f` keeps regular files and `-type d` directories. `-name` keeps
names that match a wildcard pattern, like a glob. ([tlcl#tests]) The
pattern is matched against the name, not the whole path: below,
`-name 'e*'` finds `logs/old/empty.log`. Tests in a row must all be
true. ([tlcl#operators])

```bash run
mkdir -p logs/old logs/archive.log
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > logs/access.log
echo "Look into the 404s." > logs/notes.txt
touch logs/old/empty.log
echo "folders:"
find logs -type d | sort
echo "names ending in .log:"
find logs -name '*.log' | sort
echo "files ending in .log:"
find logs -type f -name '*.log' | sort
echo "names starting with e:"
find logs -name 'e*'
```
```output
folders:
logs
logs/archive.log
logs/old
names ending in .log:
logs/access.log
logs/archive.log
logs/old/empty.log
files ending in .log:
logs/access.log
logs/old/empty.log
names starting with e:
logs/old/empty.log
```

`archive.log` is a folder: `-name` matches it, and `-type f` drops it.

### Quote the pattern

Quote the pattern, so that bash doesn't expand it as a glob before
`find` sees it. ([tlcl#tests]) Unquoted, `*.log` is expanded whenever it
matches names in the current folder:

```bash run
mkdir logs
touch logs/access.log logs/error.log today.log
echo "quoted:"
find logs -name '*.log' | sort
echo "unquoted:"
find logs -name *.log
```
```output
quoted:
logs/access.log
logs/error.log
unquoted:
```

The second `find` was given `-name today.log`.

### Size

`-size +n` matches files bigger than n. A letter after the number sets
the unit: `c` for bytes, `k` for kilobytes (1,024 bytes), `M` for
megabytes. Without a letter, the unit is 512-byte blocks, so
`-size +1000` means more than 1,000 blocks, not bytes. With `c`, a
leading `-` means less than (`-size -100c`), and no sign exactly
(`-size 20c`). `-empty` matches empty files and folders. ([tlcl#tests])

```bash run
mkdir logs
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > logs/access.log
echo "Look into the 404s." > logs/notes.txt
touch logs/empty.log
echo "more than 30 bytes:"
find logs -type f -size +30c
echo "exactly 20 bytes:"
find logs -type f -size 20c
echo "empty:"
find logs -empty
```
```output
more than 30 bytes:
logs/access.log
exactly 20 bytes:
logs/notes.txt
empty:
logs/empty.log
```

<!-- challenge id=c1 objective=1 -->
> **Challenge c1:** Open [`challenges/c1.sh`](challenges/c1.sh) and make it
> print the regular files under DIR, its first argument, at any depth,
> whose names end in `.log` and that hold more than 1,024 bytes: a
> 1,500-byte `logs/old/monday log.log`, but not a 1,024-byte
> `logs/small.log`. Check it with `learn check c1`.

## Combining tests

`! -empty` matches what isn't empty: `!` turns a test around. `-o`
between two tests matches what passes either. Long forms: `-not`,
`-or`. A row of tests already means `-and` (`-a`) between
them. ([tlcl#operators])

```bash run
mkdir logs
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > logs/access.log
echo "2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512" > logs/access.log.old
echo "Look into the 404s." > logs/notes.txt
touch logs/empty.log
echo "not empty:"
find logs -type f ! -empty | sort
echo "ending in .log or .old:"
find logs -name '*.log' -o -name '*.old' | sort
```
```output
not empty:
logs/access.log
logs/access.log.old
logs/notes.txt
ending in .log or .old:
logs/access.log
logs/access.log.old
logs/empty.log
```

### Grouping with parentheses

`-and` binds tighter than `-o`, as `and` does over `or` in Python. So
the first command below means `-name '*.log' -o ( -name '*.old' -type f )`
and lists the folder `archive.log`. The second groups the two names with
`\(` and `\)`, spaces around each. The backslash stops bash from taking
`(` as its own syntax. ([tlcl#operators])

```bash run
mkdir -p logs/archive.log
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > logs/access.log
echo "2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512" > logs/access.log.old
echo "without parentheses:"
find logs -name '*.log' -o -name '*.old' -type f | sort
echo "with parentheses:"
find logs \( -name '*.log' -o -name '*.old' \) -type f | sort
```
```output
without parentheses:
logs/access.log
logs/access.log.old
logs/archive.log
with parentheses:
logs/access.log
logs/access.log.old
```

<!-- challenge id=c2 objective=2 -->
> **Challenge c2:** Open [`challenges/c2.sh`](challenges/c2.sh) and make it
> print the regular files under DIR, at any depth, whose names end in
> `.log` or `.old` and that are not empty. For the last example's files,
> it prints `logs/access.log` and `logs/access.log.old`, in any order.
> Check it with `learn check c2`.

## Running a command on the files

Each `find` so far had no action, so it used `-print`: one path per
match, on standard output. ([tlcl#predefined-actions]) `-exec` runs a
command instead. In `-exec grep -c " 404 " {} \;`, `find` runs grep with
the current match's path in place of `{}`; `\;` marks where grep's
arguments stop. ([tlcl#user-defined-actions]) A bare `;` would end the `find`
command for bash, as before `then` in module 4, so escape it as `\;` or
quote it, `';'`. ([tlcl#user-defined-actions]) `{}` can stay
bare. ([bashpitfalls#find_._-exec_sh_-c_.27echo_.7B.7D.27_.2BAFw.3B])

### One command for all the files

With `\;`, `find` runs the command once for each file. With `+` instead,
it collects the paths into one argument list and runs the command
once. ([tlcl#improving-efficiency]) `{}` is one argument, so
`monday log.log` arrives in one piece:

```bash run
mkdir -p logs/old
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > logs/access.log
echo "2026-10-05T09:12:44 192.0.2.44 GET /logo.png 200 1024" > "logs/old/monday log.log"
echo "one awk per file:"
find logs -name '*.log' -exec awk '{ total += $6 } END { print total + 0 }' {} \; | sort -n
echo "one awk for all files:"
find logs -name '*.log' -exec awk '{ total += $6 } END { print total + 0 }' {} +
```
```output
one awk per file:
512
1024
one awk for all files:
1536
```

As in module 3, `grep -c` given one file prints a bare count, and given
several, a `FILE:N` line for each:

```bash run
mkdir -p logs/old
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > logs/access.log
echo "2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153" > "logs/old/monday log.log"
echo "one grep per file:"
find logs -name '*.log' -exec grep -c " 404 " {} \;
echo "one grep for all files:"
find logs -name '*.log' -exec grep -c " 404 " {} + | sort
```
```output
one grep per file:
1
1
one grep for all files:
logs/access.log:1
logs/old/monday log.log:1
```

An action is joined to the tests before it by an implied `-and`, so it
runs only when they are true. ([tlcl#predefined-actions]) With `-o`,
group the tests, or the action belongs to the right side only:

```bash run
mkdir logs
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > logs/access.log
echo "2026-10-05T09:12:44 192.0.2.44 GET /logo.png 200 1024" > logs/access.log.old
echo "without parentheses:"
find logs -name '*.log' -o -name '*.old' -exec awk '{ total += $6 } END { print total + 0 }' {} +
echo "with parentheses:"
find logs \( -name '*.log' -o -name '*.old' \) -exec awk '{ total += $6 } END { print total + 0 }' {} +
```
```output
without parentheses:
1024
with parentheses:
1536
```

With an action given, there is no default `-print`, so
`logs/access.log` isn't printed. ([tlcl#predefined-actions])

<!-- challenge id=c3 objective=3 -->
> **Challenge c3:** Open [`challenges/c3.sh`](challenges/c3.sh) and make it
> print the total bytes of all requests in the `.log` files under DIR, at
> any depth, as one number, with one `find` and `-exec awk ... {} +`. For
> the awk example's two logs, it prints `1536`. Check it with
> `learn check c3`.

### File names are arguments, not code

`sh` is a shell, like bash, and `sh -c 'script'` runs a script given as
a string. In `find . -exec sh -c 'echo {}' \;`, the file name is put
into that script, so a name holding `;` or `$( )` may be executed as
code. Pass the name after the script instead, and read it there as
`"$1"`. ([bashpitfalls#find_._-exec_sh_-c_.27echo_.7B.7D.27_.2BAFw.3B])

```bash run
mkdir logs
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > 'logs/$(echo oops).log'
find logs -name '*.log' -exec sh -c 'echo "found {}"' \;
find logs -name '*.log' -exec sh -c 'echo "0: $0, 1: $1"' x {} \;
```
```output
found logs/oops.log
0: x, 1: logs/$(echo oops).log
```

In the first, sh ran the `echo oops` from the name, and its output
replaced `$(echo oops)`. In the second, the name stays text, and `x`
becomes `$0`.

## Passing names to xargs

In `find logs -name '*.log' | xargs grep -c " 404 "`, xargs reads the
paths on its standard input and runs grep with them as arguments, as
`-exec ... {} +` does. ([tlcl#xargs]) ([tlcl#improving-efficiency])
Here it is on a name with a space:

```bash run
mkdir logs
echo "2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153" > "logs/monday log.log"
echo "plain xargs:"
find logs -name '*.log' | xargs grep -c -H " 404 "
echo "with -print0 and -0:"
find logs -name '*.log' -print0 | xargs -0 grep -c -H " 404 "
```
```output
plain xargs:
with -print0 and -0:
logs/monday log.log:1
```

Plain xargs split its input at whitespace, so grep got two names,
`logs/monday` and `log.log`. ([bashpitfalls#Using_xargs_without_-0])
([tlcl#xargs]) Neither exists: grep printed only errors, to stderr. In
the second, `xargs -0` splits only at the null character, code 0, which
`-print0` puts between the paths. So every name arrives whole, even one
with spaces or newlines. ([tlcl#xargs]) Quotes break plain xargs too: a
lone quote, as in `dad's log.log`, makes it complain, and quotes that
pair up vanish without a warning. ([bashpitfalls#Using_xargs_without_-0]) `-H`
(module 3) keeps the `FILE:` part when xargs hands grep only one file.

<!-- challenge id=c4 objective=4 -->
> **Challenge c4:** Open [`challenges/c4.sh`](challenges/c4.sh) and make it
> print `FILE:N` for each `.log` file under DIR, at any depth, where N is
> its number of 404 requests, using `find -print0` and `xargs -0`. For the
> folder of the last example, it prints `logs/monday log.log:1`. Check it
> with `learn check c4`.

## What's next

- **Exercise:** write [`exercise/scan.sh`](exercise/scan.sh), logkit's
  tenth tool, then run `learn check`.
  [`exercise/notfound.sh`](exercise/notfound.sh),
  [`exercise/count.sh`](exercise/count.sh),
  [`exercise/countall.sh`](exercise/countall.sh),
  [`exercise/healthcheck.sh`](exercise/healthcheck.sh),
  [`exercise/summary.sh`](exercise/summary.sh),
  [`exercise/top.sh`](exercise/top.sh),
  [`exercise/suspicious.sh`](exercise/suspicious.sh),
  [`exercise/anonymize.sh`](exercise/anonymize.sh) and
  [`exercise/bytes.sh`](exercise/bytes.sh) are the finished tools from
  modules 1 to 9; leave them unchanged.
- **Quiz:** run `learn quiz`.
- **Recap:** read [`recap.md`](recap.md).

[tlcl#find-find-files-the-hard-way]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=258 "The Linux Command Line, 17 Searching for Files: find – Find Files the Hard Way"
[tlcl#tests]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=259 "The Linux Command Line, 17 Searching for Files: find – Find Files the Hard Way: Tests"
[tlcl#operators]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=261 "The Linux Command Line, 17 Searching for Files: find – Find Files the Hard Way: Operators"
[tlcl#predefined-actions]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=264 "The Linux Command Line, 17 Searching for Files: find – Find Files the Hard Way: Predefined Actions"
[tlcl#user-defined-actions]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=266 "The Linux Command Line, 17 Searching for Files: find – Find Files the Hard Way: User-Defined Actions"
[tlcl#improving-efficiency]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=267 "The Linux Command Line, 17 Searching for Files: find – Find Files the Hard Way: Improving Efficiency"
[tlcl#xargs]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=268 "The Linux Command Line, 17 Searching for Files: find – Find Files the Hard Way: xargs"
[bashpitfalls#Using_xargs_without_-0]: https://mywiki.wooledge.org/BashPitfalls#Using_xargs_without_-0 "Bash Pitfalls, 56. Using xargs without -0"
[bashpitfalls#find_._-exec_sh_-c_.27echo_.7B.7D.27_.2BAFw.3B]: https://mywiki.wooledge.org/BashPitfalls#find_._-exec_sh_-c_.27echo_.7B.7D.27_.2BAFw.3B "Bash Pitfalls, 52. find . -exec sh -c 'echo {}' \;"
