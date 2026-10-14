# Editing Text with sed

grep picks lines out of a log; sed changes them. sed, the stream editor,
edits text as it flows through, read from the files you name or from
standard input. ([tlcl#sed]) With it you replace text in every line, move
fields around, and keep or drop lines by number or pattern. In this module
you add
[`exercise/anonymize.sh`](exercise/anonymize.sh) to logkit: it writes a copy
of a log with the client IPs partly hidden.

By the end of this module you can:

1. Replace text on every line with `sed 's/old/new/'` and the `g` flag
2. Reuse matched parts with `sed -E` groups and `\1`
3. Delete or print chosen lines with sed's `d` command and `-n` with `p`
4. Write the result to a new file, never to the file being read

**How to work through it:** sed commands go in single quotes, like grep
patterns in module 7, unless they hold a variable. Until the last section,
sed only prints its result: the files in the examples stay as they are.

## Replacing text with `s`

`s/index/home/` below is a substitution, sed's most used command: it
writes `home` in place of `index`. ([tlcl#sed]) sed runs it on one input
line after another, and with no address in front (see "Choosing lines"
below), no line is left out. ([tlcl#sed]) sed prints the result; the file
it reads stays as it was:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /index.html 404 153" >> access.log
sed 's/index/home/' access.log
echo "---"
cat access.log
```
```output
2026-10-06T10:15:32 203.0.113.5 GET /home.html 200 512
2026-10-06T10:15:40 198.51.100.7 GET /home.html 404 153
---
2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
2026-10-06T10:15:40 198.51.100.7 GET /index.html 404 153
```

The search part is a regular expression, a basic one unless you say
otherwise. ([tlcl#sed]) In a basic one, `^ $ . [ ] *` are metacharacters,
as in module 7. ([tlcl#posix-basic-vs-extended-regular-expressions]) A
backslash makes a metacharacter a literal, so `\.` is a real
dot. ([tlcl#metacharacters-and-literals])

### The `g` flag

`s` replaces only the first match on each line. The `g` flag, after the
last slash, replaces every match. ([tlcl#sed]) Python's `re.sub()` does
the opposite: it replaces every match unless you pass `count=1`.

```bash run
echo "2026-10-06T10:15:32" | sed 's/-/./'
echo "2026-10-06T10:15:32" | sed 's/-/./g'
```
```output
2026.10-06T10:15:32
2026.10.06T10:15:32
```

Only the search part is a regular expression: in the replacement, `.` is
a plain dot.

### Other delimiters

In paths, every slash would need a backslash, because `/` is the
delimiter. Any character can take that role: sed uses the one right after
the `s`. Choose one the text doesn't hold, such as `|`. ([tlcl#sed]) Both
commands below do the same:

```bash run
echo "GET /old/index.html 200" > requests.txt
sed 's/\/old\//\/new\//' requests.txt
sed 's|/old/|/new/|' requests.txt
```
```output
GET /new/index.html 200
GET /new/index.html 200
```

### Variables in the command

In single quotes, bash doesn't expand `$old`, so sed gets the text `$old`.
To put a variable's value into the command, use double
quotes. ([bashpitfalls#sed_.27s.2F.24foo.2Fgood_bye.2F.27])

```bash run
old="/old/"
new="/new/"
echo "GET /old/index.html 200" > requests.txt
sed 's|$old|$new|' requests.txt
sed "s|$old|$new|" requests.txt
```
```output
GET /old/index.html 200
GET /new/index.html 200
```

Use single quotes when there is no variable.

<!-- challenge id=c1 objective=1 -->
> **Challenge c1:** Open [`challenges/c1.sh`](challenges/c1.sh) and make it
> print LOGFILE, its first argument, as CSV: every space replaced by a
> comma. The line `2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512`
> becomes `2026-10-06T10:15:32,203.0.113.5,GET,/index.html,200,512`.
> Check it with `learn check c1`.

## Reusing what matched with groups

Parentheses in the search part make subexpressions, or groups. In the
replacement, `\1` to `\9` stand for the text the first to ninth group
matched. ([tlcl#sed]) Python's `re.sub()` uses the same `( )` and `\1`.
But sed has only `\1` to `\9`, so `\10` is group 1 followed by `0`, where
Python reads group 10. ([tlcl#sed])

```bash run
echo "file9.log" | sed -E 's/^([a-z]+)([0-9])\./\10\2./'
```
```output
file09.log
```

To group or repeat in a basic regular expression, sed needs a backslash:
`\(`, `\)`, `\{` and `\}`. Bare, those characters are
plain. ([tlcl#sed]) ([tlcl#posix-basic-vs-extended-regular-expressions])
An extended regular expression, the kind `grep -E` reads, is the other way
round: bare `( ) { }` group and
repeat. ([tlcl#posix-basic-vs-extended-regular-expressions]) sed reads one
with `-E`. Both commands below swap the last two fields, the status and
the bytes:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
sed 's/ \([0-9]\{3\}\) \([0-9]*\)$/ \2 \1/' access.log
sed -E 's/ ([0-9]{3}) ([0-9]*)$/ \2 \1/' access.log
```
```output
2026-10-06T10:15:32 203.0.113.5 GET /index.html 512 200
2026-10-06T10:15:32 203.0.113.5 GET /index.html 512 200
```

Only the matched part is replaced; the rest of the line stays. To move
fields around, match the whole line, from `^` to `$`, and build it again
from the groups. `[^ ]+` is one field: one or more characters that aren't
a space. A field you don't keep is matched the same way, outside any
group: text the pattern matches outside a group is gone, unless the
replacement writes it again. Here the method is dropped:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" >> access.log
sed -E 's/^([^ ]+) ([^ ]+) [^ ]+ ([^ ]+) .*$/\2 asked for \3 at \1/' access.log
```
```output
203.0.113.5 asked for /index.html at 2026-10-06T10:15:32
198.51.100.7 asked for /missing.html at 2026-10-06T10:15:40
```

<!-- challenge id=c2 objective=2 -->
> **Challenge c2:** Open [`challenges/c2.sh`](challenges/c2.sh) and make it
> print each request in LOGFILE, its first argument, as its status and its
> path: `2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153`
> becomes `404 /missing.html`. Check it with `learn check c2`.

## Choosing lines with `d` and `-n`

Before most commands you can put an address; the command then runs only
on the lines the address picks. ([tlcl#sed]) An address picks lines in
one of three ways:

- by pattern: `/ 404 /` picks the lines the regular expression matches.
  Slashes mark where it starts and ends, so a slash in it is written `\/`,
  as in `/ \/health /` below;
- by number: `1` is the first line and `$` the last. Inside a regular
  expression, `$` still means the end of a line;
- by range: `2,4` is lines 2 to 4, both included. Each end can be a
  number, `$` or a pattern. ([tlcl#sed])

The `d` command deletes the line, so sed doesn't print it. ([tlcl#sed])

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 127.0.0.1 GET /health 200 2" >> access.log
echo "2026-10-06T10:16:02 198.51.100.7 GET /missing.html 404 153" >> access.log
echo "without /health:"
sed '/ \/health /d' access.log
echo "without line 1:"
sed '1d' access.log
```
```output
without /health:
2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
2026-10-06T10:16:02 198.51.100.7 GET /missing.html 404 153
without line 1:
2026-10-06T10:15:40 127.0.0.1 GET /health 200 2
2026-10-06T10:16:02 198.51.100.7 GET /missing.html 404 153
```

The `p` command prints the line. But sed prints every line anyway, so
`p` alone prints the chosen lines twice. The `-n` option turns that
printing off: with it, sed prints only what `p` prints. ([tlcl#sed])

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:16:02 198.51.100.7 GET /missing.html 404 153" >> access.log
echo "2026-10-06T10:16:20 127.0.0.1 GET /health 200 2" >> access.log
echo "p without -n:"
sed '/ 404 /p' access.log
echo "-n with p:"
sed -n '/ 404 /p' access.log
echo "last line:"
sed -n '$p' access.log
```
```output
p without -n:
2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
2026-10-06T10:16:02 198.51.100.7 GET /missing.html 404 153
2026-10-06T10:16:02 198.51.100.7 GET /missing.html 404 153
2026-10-06T10:16:20 127.0.0.1 GET /health 200 2
-n with p:
2026-10-06T10:16:02 198.51.100.7 GET /missing.html 404 153
last line:
2026-10-06T10:16:20 127.0.0.1 GET /health 200 2
```

Line numbers can come from variables too. Use double quotes, as for `s`,
and write `${last}p` with braces: `$lastp` is a variable called `lastp`,
which is empty here. In double quotes, a `$` meant for sed can need a
backslash too. ([bashpitfalls#sed_.27s.2F.24foo.2Fgood_bye.2F.27]) For
sed's `$p`, the last line, write `\$p`; bash would read `$p` as its
variable `p`.

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:16:02 198.51.100.7 GET /missing.html 404 153" >> access.log
echo "2026-10-06T10:16:20 127.0.0.1 GET /health 200 2" >> access.log
echo "2026-10-06T10:16:48 203.0.113.5 GET /about.html 200 2048" >> access.log
first=2
last=3
echo "[$lastp] [${last}p]"
sed -n "${first},${last}p" access.log
echo "from line $first to the end:"
sed -n "${first},\$p" access.log
```
```output
[] [3p]
2026-10-06T10:16:02 198.51.100.7 GET /missing.html 404 153
2026-10-06T10:16:20 127.0.0.1 GET /health 200 2
from line 2 to the end:
2026-10-06T10:16:02 198.51.100.7 GET /missing.html 404 153
2026-10-06T10:16:20 127.0.0.1 GET /health 200 2
2026-10-06T10:16:48 203.0.113.5 GET /about.html 200 2048
```

<!-- challenge id=c3 objective=3 -->
> **Challenge c3:** Open [`challenges/c3.sh`](challenges/c3.sh) and make it
> print lines FIRST to LAST of LOGFILE, given as
> `bash challenges/c3.sh LOGFILE FIRST LAST`. With a five-line log,
> `2 4` prints lines 2, 3 and 4, and `4 9` prints lines 4 and 5. Check it
> with `learn check c3`.

## Writing to a new file

sed writes its result to standard output, so `>` saves it in a file. But
never in the file sed reads: you can't read from a file and write to it in
the same command or pipeline, and the file can end up
empty. ([bashpitfalls#cat_file_.7C_sed_s.2Ffoo.2Fbar.2F_.3E_file])

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
sed 's/ 203\.0\.113\.5 / 203.0.113.0 /' access.log > access.log
echo "access.log holds:"
cat access.log
echo "(end)"
```
```output
access.log holds:
(end)
```

Bash sets up `> access.log` before it runs sed, and that empties the
file, so sed reads an empty file. ([bashguide-io#File_Redirection-1])
Write to a new file instead. A dot can't be part of a
variable name, so `"$logfile.new"` is the value of `logfile` followed by
`.new`:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
logfile="access.log"
sed 's/ 203\.0\.113\.5 / 203.0.113.0 /' "$logfile" > "$logfile.new"
cat "$logfile"
cat "$logfile.new"
```
```output
2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
2026-10-06T10:15:32 203.0.113.0 GET /index.html 200 512
```

To change the original, write a temporary file, then move it over the
original with `mv`. That works with any
sed. ([bashpitfalls#cat_file_.7C_sed_s.2Ffoo.2Fbar.2F_.3E_file])

```bash run
echo "GET /old/index.html 200" > requests.txt
sed 's|/old/|/new/|' requests.txt > requests.tmp && mv requests.tmp requests.txt
cat requests.txt
ls requests.*
```
```output
GET /new/index.html 200
requests.txt
```

`mv` renamed `requests.tmp` to `requests.txt`, replacing the old file.

`&&` runs `mv` only when sed succeeded, with exit status 0, so a failed
sed leaves the original alone. ([bashguide-tests#Control_Operators_.28.26.26_and_.7C.7C.29])

## What's next

- **Exercise:** write [`exercise/anonymize.sh`](exercise/anonymize.sh),
  logkit's eighth tool, then run `learn check`.
  [`exercise/notfound.sh`](exercise/notfound.sh),
  [`exercise/count.sh`](exercise/count.sh),
  [`exercise/countall.sh`](exercise/countall.sh),
  [`exercise/healthcheck.sh`](exercise/healthcheck.sh),
  [`exercise/summary.sh`](exercise/summary.sh),
  [`exercise/top.sh`](exercise/top.sh) and
  [`exercise/suspicious.sh`](exercise/suspicious.sh) are the finished
  tools from modules 1 to 7; leave them unchanged.
- **Quiz:** run `learn quiz`.
- **Recap:** read [`recap.md`](recap.md).

[tlcl#sed]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=342 "The Linux Command Line, 20 Text Processing: Editing on the Fly: sed"
[bashpitfalls#cat_file_.7C_sed_s.2Ffoo.2Fbar.2F_.3E_file]: https://mywiki.wooledge.org/BashPitfalls#cat_file_.7C_sed_s.2Ffoo.2Fbar.2F_.3E_file "Bash Pitfalls, 13. cat file | sed s/foo/bar/ > file"
[bashpitfalls#sed_.27s.2F.24foo.2Fgood_bye.2F.27]: https://mywiki.wooledge.org/BashPitfalls#sed_.27s.2F.24foo.2Fgood_bye.2F.27 "Bash Pitfalls, 29. sed 's/$foo/good bye/'"
[tlcl#posix-basic-vs-extended-regular-expressions]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=302 "The Linux Command Line, 19 Regular Expressions: POSIX Basic vs. Extended Regular Expressions"
[tlcl#metacharacters-and-literals]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=294 "The Linux Command Line, 19 Regular Expressions: Metacharacters and Literals"
[bashguide-io#File_Redirection-1]: https://mywiki.wooledge.org/BashGuide/InputAndOutput#File_Redirection-1 "BashGuide, Input and Output: 4.1. File Redirection"
[bashguide-tests#Control_Operators_.28.26.26_and_.7C.7C.29]: https://mywiki.wooledge.org/BashGuide/TestsAndConditionals#Control_Operators_.28.26.26_and_.7C.7C.29 "BashGuide, Tests and Conditionals: 2. Control Operators (&& and ||)"
