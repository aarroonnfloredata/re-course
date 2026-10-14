# Scripts, Pipes and Redirection

This module shows how to keep commands in a script, where a command's output
and error messages go, and how to send them into files or into other
commands. You also start logkit, small bash scripts for checking a web
server's access log.

By the end of this module you can:

1. Write commands in a script file and run it with bash
2. Send a command's output to a file with `>` and `>>`, and feed a file to it
   with `<`
3. Keep error messages apart from output: send them to stderr with `>&2`, to a
   file with `2>`, or away to `/dev/null`
4. Connect commands with `|` and narrow lines down and count them with `grep`,
   `head` and `tail`

**How to work through it:** read top to bottom and try each example as you
reach it. An example's output block shows only what it prints on standard
output, not standard error (explained below).

## Scripts

A script is a sequence of commands in a file. Bash runs them in order, each
after the one before has ended. ([bashguide-commands#Scripts])
Save this one in your editor as `request.sh`:

```text
#!/usr/bin/env bash
# request.sh: print a sample request and its status.
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153"
echo "status: 404"   # the fifth field
```

The first line, starting with `#!`, is the shebang: it names the interpreter
that runs the file. ([tlcl#script-file-format]) It must be at the very start
of the file; `#!/usr/bin/env bash` looks for bash in your `PATH`. ([bashguide-commands#Scripts])

A `#` at the start of a word starts a comment: bash skips it and the rest
of the line. Inside a word, as in `GET#1`, it is an ordinary
character. ([bashguide-commands#Commands_and_Arguments])

```bash run
# A whole line can be a comment.
echo "first"    # bash ignores everything after the #
echo "second"
```
```output
first
second
```

Run the script by handing it to bash, the way you run `python3 request.py`:

```text
$ bash request.sh
2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
status: 404
```

Run this way, bash reads the file itself and the `#!` line is just a
comment. ([bashguide-commands#Scripts])

## Standard output and files

Every command starts with three standard streams. ([bashguide-io#File_Descriptors-1])
The table shows what each one carries and what it is connected to until you
redirect it. ([tlcl#standard-input-output-and-error])

| Stream | Carries | Connected to |
|---|---|---|
| standard input (stdin) | what the command reads | the keyboard |
| standard output (stdout) | its results | the screen |
| standard error (stderr) | its error messages | the screen |

Bash numbers them: stdin is 0, stdout 1 and stderr 2. ([bashguide-io#File_Descriptors-1])
They are Python's `sys.stdin`, `sys.stdout` and `sys.stderr`. Redirecting a
stream connects it to something else, such as a file. ([tlcl#standard-input-output-and-error])

### Sending output to a file

`>` sends a command's stdout to a file instead of the screen. ([tlcl#redirecting-standard-output])
Bash creates or empties the file before the command runs. ([bashguide-io#File_Redirection-1])
So the old contents are lost even if the command fails. ([tlcl#redirecting-standard-output])
`>>` adds to the end of the file instead, creating it if needed. ([tlcl#redirecting-standard-output])
`>` is like Python's `open(path, "w")`, `>>` like `open(path, "a")`.

`cat` prints the files you give it, one after another. ([bashguide-io#File_Redirection-1])

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" >> access.log
cat access.log
echo "---"
echo "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64" > access.log
cat access.log
```
```output
2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
---
2026-10-06T10:16:02 203.0.113.5 POST /login 401 64
```

With `>` or `>>`, `cat` copies files:

```bash run
echo "2026-10-05T23:59:01 192.0.2.44 GET /about.html 200 2048" > monday.log
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > tuesday.log
cat monday.log > week.log
cat tuesday.log >> week.log
cat week.log
```
```output
2026-10-05T23:59:01 192.0.2.44 GET /about.html 200 2048
2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
```

<!-- challenge id=c1 objective=2 -->
> **Challenge c1:** Open [`challenges/c1.sh`](challenges/c1.sh) and make it
> add the lines of `today.log` to the end of `archive.log` and copy them to
> `latest.log`, replacing what `latest.log` held; either file is created if
> missing. If `archive.log` holds one line and `today.log` two, `archive.log`
> ends up with three. Check it with `learn check c1`.

### Reading input from a file

`<` fills a command's stdin from a file. ([tlcl#redirecting-standard-input])
A pipe, `|`, fills it from another command instead (see "Pipes"). ([tlcl#pipelines])
`cat` reads stdin when you give it no file names. ([tlcl#redirecting-standard-input])
Below, `<` and `>` make it copy `today.log` to `copy.log`:

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > today.log
cat < today.log > copy.log
cat copy.log
```
```output
2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
```

## Finding lines with grep

`grep pattern file` prints the lines of the file that contain the
pattern. ([tlcl#grep-print-lines-matching-a-pattern]) Like `cat`, it reads
stdin when you give it no file. ([bashguide-io#File_Descriptor_Manipulation-1])

logkit's logs hold one request per line, with six fields separated by single
spaces: time, client IP, method, path, status and bytes. `grep` matches text
anywhere in a line, so `404` also finds a request that sent 404 bytes:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" >> access.log
echo "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404" >> access.log
grep 404 access.log
echo "---"
grep " 404 " access.log
```
```output
2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404
---
2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
```

With a space on each side, `" 404 "` matches only the status. Quote a
pattern that has spaces; module 3 explains why.

With `-c`, grep prints how many lines match instead of the lines. The first
line below holds `404` twice but counts once:

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /errors/404.html 404 153" > access.log
echo "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64" >> access.log
echo "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404" >> access.log
grep -c 404 access.log
grep -c " 404 " access.log
```
```output
2
1
```

## Keeping errors apart

Error messages go to stderr, so `>` doesn't catch them: they still appear on
the screen. ([tlcl#redirecting-standard-output]) grep, for example, reports a
missing file on stderr. ([bashguide-io#File_Descriptor_Manipulation-1])

### Errors to a file, or away: `2>` and `/dev/null`

To redirect stderr, put its number in front of the operator:
`2> errors.txt`. ([tlcl#redirecting-standard-error]) `2>>` adds to the file
instead. ([bashguide-io#File_Redirection-1]) To get rid of messages, send
them to `/dev/null`, a device file that discards whatever reaches it:
`2> /dev/null`. ([tlcl#disposing-of-unwanted-output])

```bash run
grep 404 missing.log 2> errors.txt
grep -c missing.log errors.txt
grep 404 missing.log 2> /dev/null
echo "done"
```
```output
1
done
```

Neither error reached the screen: one went into `errors.txt`, the other is
gone.

### Your own messages: `>&2`

Your scripts should send their own error messages to stderr too, by adding
`>&2` to `echo`. ([bashguide-io#File_Descriptors-1]) The `&` marks `2` as a
stream number, not a file name. ([bashguide-io#File_Descriptor_Manipulation-1])
Without it, `> 2` writes to a file named `2`:

```bash run
echo "logkit: access.log has an empty line" >&2
echo "3 requests"
echo "logkit: oops" > 2
echo "a file named 2 holds:"
cat 2
```
```output
3 requests
a file named 2 holds:
logkit: oops
```

In a terminal the stderr line shows too. ([tlcl#standard-input-output-and-error])

The next example writes a script, `count.sh`, that prints one line to each
stream (module 3 explains the single quotes):

```bash run
echo 'echo 3 requests' > count.sh
echo 'echo logkit: 1 line skipped >&2' >> count.sh
bash count.sh > report.txt 2> errors.txt
echo "report.txt holds:"
cat report.txt
echo "errors.txt holds:"
cat errors.txt
```
```output
report.txt holds:
3 requests
errors.txt holds:
logkit: 1 line skipped
```

<!-- challenge id=c2 objective=3 -->
> **Challenge c2:** Open [`challenges/c2.sh`](challenges/c2.sh) and make it
> print the lines of `access.log` that contain `POST`, throwing grep's error
> away, then print `logkit: done` to stderr. Without `access.log`, only
> `logkit: done` reaches the screen. Check it with `learn check c2`.

### Both streams in one file: `2>&1`

To save stdout and stderr in one file, redirect stdout first and then add
`2>&1`, which points stderr to where stdout points. ([tlcl#redirecting-standard-output-and-standard-error-to-one-file])
Bash reads redirections from left to right. `2>&1 > all.txt` first points
stderr where stdout points at that moment, the screen, and only then moves
stdout to `all.txt`. ([bashguide-io#File_Descriptor_Manipulation-1])

```bash run
echo 'echo 3 requests' > count.sh
echo 'echo logkit: 1 line skipped >&2' >> count.sh
bash count.sh > all.txt 2>&1
echo "all.txt holds:"
cat all.txt
echo "---"
bash count.sh 2>&1 > all.txt
echo "all.txt holds:"
cat all.txt
```
```output
all.txt holds:
3 requests
logkit: 1 line skipped
---
logkit: 1 line skipped
all.txt holds:
3 requests
```

The stray error is in the output block because, here, the example's stdout
is the screen.

## Pipes

A pipe, `|`, connects the stdout of one command to the stdin of the
next. ([tlcl#pipelines]) ([bashguide-io#Pipes-1]) Below, `cat` copies what
comes through the pipe into `piped.txt`. ([tlcl#redirecting-standard-input])

```bash run
echo 'echo 3 requests' > count.sh
echo 'echo logkit: 1 line skipped >&2' >> count.sh
bash count.sh | cat > piped.txt
echo "piped.txt holds:"
cat piped.txt
```
```output
piped.txt holds:
3 requests
```

The error still goes to the screen, where stderr points. ([bashguide-io#File_Descriptors-1])

After `|` comes a command; after `>`, a file name, even if it is a
command's name too. Bash creates or overwrites that file without a
warning. ([tlcl#pipelines]) Here `>` was typed instead of `|`:

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
grep 404 access.log > head
echo "a file named head holds:"
cat head
```
```output
a file named head holds:
2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
```

### First and last lines: `head` and `tail`

To keep only the start or the end of some lines, use `head -n N` for the
first N or `tail -n N` for the last N. Without `-n`, they keep 10 lines. ([tlcl#head-tail-print-first-last-part-of-files])
The example uses them on a file and after a `|`.

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" >> access.log
echo "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64" >> access.log
echo "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404" >> access.log
echo "2026-10-06T10:17:03 198.51.100.7 GET /old/page.html 404 153" >> access.log
head -n 1 access.log
echo "---"
grep GET access.log | tail -n 2
echo "---"
tail -n 2 access.log | grep -c " 404 "
```
```output
2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
---
2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404
2026-10-06T10:17:03 198.51.100.7 GET /old/page.html 404 153
---
1
```

<!-- challenge id=c3 objective=4 -->
> **Challenge c3:** Open [`challenges/c3.sh`](challenges/c3.sh) and make it
> print the first two lines of `access.log` that contain `GET`: after a POST
> request and three GET requests, the first two GET requests. Check it with
> `learn check c3`.

## What's next

- **Exercise:** write [`exercise/notfound.sh`](exercise/notfound.sh), the
  first logkit tool, as its header comment describes. Then run `learn check`.
- **Quiz:** run `learn quiz`.
- **Recap:** read [`recap.md`](recap.md).

[bashguide-commands#Commands_and_Arguments]: https://mywiki.wooledge.org/BashGuide/CommandsAndArguments#Commands_and_Arguments "BashGuide, Commands and Arguments"
[bashguide-commands#Scripts]: https://mywiki.wooledge.org/BashGuide/CommandsAndArguments#Scripts "BashGuide, Commands and Arguments: Scripts"
[tlcl#script-file-format]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=407 "The Linux Command Line, 24 Writing Your First Script: Script File Format"
[tlcl#standard-input-output-and-error]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=80 "The Linux Command Line, 6 Redirection: Standard Input, Output, and Error"
[tlcl#redirecting-standard-output]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=81 "The Linux Command Line, 6 Redirection: Redirecting Standard Output"
[tlcl#redirecting-standard-error]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=83 "The Linux Command Line, 6 Redirection: Redirecting Standard Error"
[tlcl#redirecting-standard-output-and-standard-error-to-one-file]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=84 "The Linux Command Line, 6 Redirection: Redirecting Standard Output and Standard Error to One File"
[tlcl#disposing-of-unwanted-output]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=85 "The Linux Command Line, 6 Redirection: Disposing of Unwanted Output"
[tlcl#redirecting-standard-input]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=85 "The Linux Command Line, 6 Redirection: Redirecting Standard Input"
[tlcl#pipelines]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=87 "The Linux Command Line, 6 Redirection: Pipelines"
[tlcl#grep-print-lines-matching-a-pattern]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=90 "The Linux Command Line, 6 Redirection: grep – Print Lines Matching a Pattern"
[tlcl#head-tail-print-first-last-part-of-files]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=91 "The Linux Command Line, 6 Redirection: head / tail – Print First / Last Part of Files"
[bashguide-io#File_Descriptors-1]: https://mywiki.wooledge.org/BashGuide/InputAndOutput#File_Descriptors-1 "BashGuide, Input and Output: 3. File Descriptors"
[bashguide-io#File_Redirection-1]: https://mywiki.wooledge.org/BashGuide/InputAndOutput#File_Redirection-1 "BashGuide, Input and Output: 4.1. File Redirection"
[bashguide-io#File_Descriptor_Manipulation-1]: https://mywiki.wooledge.org/BashGuide/InputAndOutput#File_Descriptor_Manipulation-1 "BashGuide, Input and Output: 4.2. File Descriptor Manipulation"
[bashguide-io#Pipes-1]: https://mywiki.wooledge.org/BashGuide/InputAndOutput#Pipes-1 "BashGuide, Input and Output: 5. Pipes"
