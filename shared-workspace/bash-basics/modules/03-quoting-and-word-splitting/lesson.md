# Quoting, Word Splitting and Globs

logkit's [`exercise/count.sh`](exercise/count.sh) counts one status in one
log file. A server writes a log every day, though, and a log's name can hold
spaces or characters such as `*` that mean something to bash. This module
shows how bash turns a command line into words, how quotes change that, and
how globs pick files by name. With them you add
[`exercise/countall.sh`](exercise/countall.sh) to logkit: it counts a status
in any number of log files.

By the end of this module you can:

1. Predict how bash splits an unquoted expansion into words and expands
   globs in it
2. Quote expansions with double quotes so values with spaces stay one
   argument
3. Stop `$` and other special characters with single quotes and backslashes
4. Match file names with `*`, `?` and `[...]`, keeping the glob outside the
   quotes
5. Pass the remaining arguments on unchanged with `shift` and `"$@"`

**How to work through it:** try each example in bash as you reach it. Many
examples run `args.sh`, a one-line script that prints its argument count
and first three arguments in brackets, showing where bash split a line. If
a glob example prints extra names, other files in your folder match it.

## Words and arguments

Bash divides each line into words at whitespace: spaces and tabs. The first
word is the command and the others are its arguments. How much whitespace
separates them doesn't matter. ([bashguide-commands#Commands_and_Arguments])
Quotes group everything inside them into one argument, and bash removes the
quotes before the command gets it. ([bashguide-commands#Commands_and_Arguments])

```bash run
echo 'echo "$# arguments: [$1] [$2] [$3]"' > args.sh
cat args.sh
bash args.sh monday.log    404
bash args.sh "monday   log.log" 404
```
```output
echo "$# arguments: [$1] [$2] [$3]"
2 arguments: [monday.log] [404] []
2 arguments: [monday   log.log] [404] []
```

In Python, quotes make a string. In bash nearly everything is a string
already: quotes only take away the special meaning of characters, such as
the space that separates arguments. ([bashguide-practices#Quoting])

### Word splitting

Bash splits words once more after it expands `$name` or `$( )`. When the
expansion is not in quotes, its result is split into words at spaces, tabs
and newlines. This is word splitting. ([bashguide-practices#Quoting]) ([tlcl#double-quotes])
The variable still holds its value; only the command sees it in
pieces. ([bashpitfalls#echo_.24foo])

```bash run
echo 'echo "$# arguments: [$1] [$2] [$3]"' > args.sh
logfile="monday   log.log"
bash args.sh $logfile
bash args.sh "$logfile"
echo $logfile
echo "$logfile"
```
```output
2 arguments: [monday] [log.log] []
1 arguments: [monday   log.log] [] []
monday log.log
monday   log.log
```

`echo` prints its arguments with one space between
them. ([bashguide-commands#Commands_and_Arguments])
A newline is a split point too. ([tlcl#double-quotes]) Unquoted, the two
lines in `$found` come out of `echo` as one:

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
echo "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153" >> access.log
found=$(grep " 404 " access.log)
echo "$found" | tail -n 1
echo $found | tail -n 1
```
```output
2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153 2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
```

A word from the split that holds `*`, `?` or `[` is then a glob, a
file-name pattern: if file names match it, bash replaces it with
them. ([bashpitfalls#cp_.24file_.24target]) ([bashpitfalls#echo_.24foo])

```bash run
echo "2026-09-30T23:50:12 192.0.2.44 GET /index.html 200 512" > access-2026-09-30.log
echo "2026-10-05T23:59:01 192.0.2.44 GET /about.html 200 2048" > access-2026-10-05.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access-2026-10-06.log
tip="Try: bash countall.sh 404 access-2026-10-*.log"
echo "$tip"
echo $tip
```
```output
Try: bash countall.sh 404 access-2026-10-*.log
Try: bash countall.sh 404 access-2026-10-05.log access-2026-10-06.log
```

## Double quotes

Between double quotes, `$name` and `$( )` still expand, but the result is
neither split into words nor matched as a glob. Only `$`, `\` and the
backquote stay special there. ([tlcl#double-quotes]) So `"$status"` is one
argument, even when empty:

```bash run
echo 'echo "$# arguments: [$1] [$2] [$3]"' > args.sh
status=""
bash args.sh $status access.log
bash args.sh "$status" access.log
```
```output
1 arguments: [access.log] [] []
2 arguments: [] [access.log] []
```

So double-quote every expansion. `cp $file $target` breaks when a name
holds a space, or a glob character that matches files. Write
`cp -- "$file" "$target"`: the `--` handles names starting with
`-`. ([bashpitfalls#cp_.24file_.24target])

<!-- challenge id=c1 objective=2 -->
> **Challenge c1:** Open [`challenges/c1.sh`](challenges/c1.sh) and make it
> print `Last request in LOGFILE:` and then the last line of LOGFILE, its
> argument. The name can hold runs of spaces: for a file called
> `monday  log.log`, the first line is `Last request in monday  log.log:`.
> Check it with `learn check c1`.

## Single quotes and backslashes

Writing `$1` into a script needs care: at your prompt no arguments are
set, so an unquoted `$1` is empty. ([tlcl#quoting]) Double quotes expand it
too. ([tlcl#double-quotes]) Single quotes stop all expansions: everything
inside them is taken as it is. ([tlcl#single-quotes]) ([bashguide-special-characters#Special_characters])
That's how `echo '...' > args.sh` keeps its `$1`, and `last.sh` here
keeps its own, while `lost.sh` loses it:

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
echo tail -n 1 $1 > lost.sh
echo 'tail -n 1 "$1"' > last.sh
cat lost.sh last.sh
bash last.sh access.log
```
```output
tail -n 1
tail -n 1 "$1"
2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
```

A backslash quotes just the next character. ([tlcl#escaping-characters])
It works outside quotes and inside double
quotes. ([bashguide-special-characters#Special_characters]) Between single
quotes it is plain text. Elsewhere, `\\` gives a backslash and `\$` a dollar
sign. ([tlcl#escaping-characters]) Pieces quoted in different ways,
or not at all, make one word when nothing separates them, as in the second
`echo`:

```bash run
logfile="monday log.log"
echo "Quote it: \"\$logfile\" is $logfile."
# Three pieces, nothing between them: 'Quote it: "$logfile" is '  "$logfile"  .
echo 'Quote it: "$logfile" is '"$logfile".
echo monday\ \ log.log 'back\slash' "back\\slash"
echo "404 | 500 > errors.txt; # not a comment"
```
```output
Quote it: "$logfile" is monday log.log.
Quote it: "$logfile" is monday log.log.
monday  log.log back\slash back\slash
404 | 500 > errors.txt; # not a comment
```

Quoted, `|`, `>` and `<` lose their special meaning as well, as the last
line shows. ([bashguide-practices#Quoting])

<!-- challenge id=c2 objective=3 -->
> **Challenge c2:** Open [`challenges/c2.sh`](challenges/c2.sh) and make it
> print the grep command that counts the requests with status STATUS, its
> argument, with the `$` and the double quotes kept:
> `bash challenges/c2.sh 404` prints `grep -c " 404 " "$logfile"`. Check it
> with `learn check c2`.

## Globs

A glob is a pattern for file names. Bash replaces it with the names of the
files that match, sorted, before the command runs. ([bashguide-patterns#Glob_Patterns-1])
This is called pathname expansion. ([tlcl#pathname-expansion]) Three
characters are special in a glob. ([bashguide-patterns#Glob_Patterns-1])

- `*` matches any string, including an empty one.
- `?` matches any single character.
- `[...]` matches any one of the characters inside.

A glob must match the whole name: `a*` matches `abc`, but not
`cat`. ([bashguide-patterns#Glob_Patterns-1])

```bash run
echo "2026-09-30T23:50:12 192.0.2.44 GET /index.html 200 512" > access-2026-09-30.log
echo "2026-10-05T23:59:01 192.0.2.44 GET /about.html 200 2048" > access-2026-10-05.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access-2026-10-06.log
echo access-*.log
echo access-2026-10-*.log
echo access-2026-??-30.log
echo access-2026-10-0[45].log
echo access-2025-*.log
```
```output
access-2026-09-30.log access-2026-10-05.log access-2026-10-06.log
access-2026-10-05.log access-2026-10-06.log
access-2026-09-30.log
access-2026-10-05.log
access-2025-*.log
```

A glob that matches no file stays as it is, like `access-2025-*.log`
above. Bash expands globs after word splitting, so a name that a glob
produces stays one argument, spaces and all. ([bashguide-patterns#Glob_Patterns-1])

```bash run
echo 'echo "$# arguments: [$1] [$2] [$3]"' > args.sh
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > "old access.log"
bash args.sh old*
```
```output
1 arguments: [old access.log] [] []
```

### Globs and quotes

Inside quotes, a glob is plain text: double quotes stop pathname
expansion. ([tlcl#double-quotes]) To build a glob from a variable, quote the
variable and leave the glob characters outside:

```bash run
echo "2026-09-30T23:50:12 192.0.2.44 GET /index.html 200 512" > access-2026-09-30.log
echo "2026-10-05T23:59:01 192.0.2.44 GET /about.html 200 2048" > access-2026-10-05.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access-2026-10-06.log
month=2026-10
echo "access-$month-*.log"
echo "access-$month"-*.log
```
```output
access-2026-10-*.log
access-2026-10-05.log access-2026-10-06.log
```

<!-- challenge id=c3 objective=4 -->
> **Challenge c3:** Open [`challenges/c3.sh`](challenges/c3.sh) and make it
> print one total: the 404 requests in all the daily logs of MONTH, its
> argument. The logs are named like `access-2026-10-05.log`, and the
> file's header comment shows how to count across files.
> `bash challenges/c3.sh 2026-10` prints `2026-10: 1 requests with status 404`
> for the three logs above. Check it with `learn check c3`.

## Passing arguments on: `shift` and `"$@"`

Given `"monday log.log" access.log`, a script's `"$@"` is two words,
exactly those arguments, and its `"$*"` is one word, the arguments joined
by spaces. Neither includes `$0`. ([tlcl#handling-positional-parameters-en-masse])
Without quotes, both give the words of the arguments, split
again. ([bashpitfalls#for_arg_in_.24.2A]) Only `"$@"` hands each argument on
as it came, like `*args` in a Python call, so use it to pass arguments to
another command. ([tlcl#handling-positional-parameters-en-masse]) ([bashpitfalls#for_arg_in_.24.2A])
`"$*"` suits a message:

```bash run
echo 'echo "$# arguments: [$1] [$2] [$3]"' > args.sh
echo 'echo "Counting 404s in: $*"' > report.sh
echo 'bash args.sh "$@"' >> report.sh
cat report.sh
bash report.sh "monday log.log" access.log
```
```output
echo "Counting 404s in: $*"
bash args.sh "$@"
Counting 404s in: monday log.log access.log
2 arguments: [monday log.log] [access.log] []
```

After `shift`, `$#` is one less: the first argument is gone, and the
second is now `$1`. ([tlcl#shift-getting-access-to-many-arguments]) So a
script can keep its first argument in a variable and pass all the others
on:

```bash run
echo 'echo "$# arguments: [$1] [$2] [$3]"' > args.sh
echo 'status=$1' > first.sh
echo 'shift' >> first.sh
echo 'echo "status $status, then $# files:"' >> first.sh
echo 'bash args.sh "$@"' >> first.sh
cat first.sh
bash first.sh 404 "monday log.log" access.log
```
```output
status=$1
shift
echo "status $status, then $# files:"
bash args.sh "$@"
status 404, then 2 files:
2 arguments: [monday log.log] [access.log] []
```

That is the shape of logkit's next tool. Given several files, `grep -c`
prints one `FILE:N` line for each; given one file, just the number. `-H`
adds the name in that case too:

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > "monday log.log"
echo "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64" > access.log
grep -c " 404 " "monday log.log" access.log
grep -c " 404 " "monday log.log"
grep -c -H " 404 " "monday log.log"
```
```output
monday log.log:1
access.log:0
1
monday log.log:1
```

<!-- challenge id=c4 objective=5 -->
> **Challenge c4:** Open [`challenges/c4.sh`](challenges/c4.sh) and make it
> print the last N lines of the files after N, its first argument, taken
> together in the order given. With the two logs above,
> `bash challenges/c4.sh 1 access.log "monday log.log"` prints
> `2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153`. Check it
> with `learn check c4`.

## What's next

- **Exercise:** write [`exercise/countall.sh`](exercise/countall.sh),
  logkit's third tool, as its header comment describes:
  `bash exercise/countall.sh 404 access.log "monday log.log"` prints one
  `FILE:N` line for each file. Then run `learn check`.
  [`exercise/notfound.sh`](exercise/notfound.sh) and
  [`exercise/count.sh`](exercise/count.sh) are the finished tools from
  modules 1 and 2; leave them as they are.
- **Quiz:** run `learn quiz`.
- **Recap:** read [`recap.md`](recap.md).

[bashguide-commands#Commands_and_Arguments]: https://mywiki.wooledge.org/BashGuide/CommandsAndArguments#Commands_and_Arguments "BashGuide, Commands and Arguments"
[bashguide-special-characters#Special_characters]: https://mywiki.wooledge.org/BashGuide/SpecialCharacters#Special_characters "BashGuide, Special Characters"
[bashguide-practices#Quoting]: https://mywiki.wooledge.org/BashGuide/Practices#Quoting "BashGuide, Practices: 2. Quoting"
[bashguide-patterns#Glob_Patterns-1]: https://mywiki.wooledge.org/BashGuide/Patterns#Glob_Patterns-1 "BashGuide, Patterns: Glob Patterns"
[tlcl#quoting]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=102 "The Linux Command Line, 7 Seeing the World as the Shell Sees It: Quoting"
[tlcl#double-quotes]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=103 "The Linux Command Line, 7 Seeing the World as the Shell Sees It: Double Quotes"
[tlcl#single-quotes]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=105 "The Linux Command Line, 7 Seeing the World as the Shell Sees It: Single Quotes"
[tlcl#escaping-characters]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=105 "The Linux Command Line, 7 Seeing the World as the Shell Sees It: Escaping Characters"
[tlcl#pathname-expansion]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=96 "The Linux Command Line, 7 Seeing the World as the Shell Sees It: Pathname Expansion"
[tlcl#shift-getting-access-to-many-arguments]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=502 "The Linux Command Line, 32 Positional Parameters: shift – Getting Access to Many Arguments"
[tlcl#handling-positional-parameters-en-masse]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=505 "The Linux Command Line, 32 Positional Parameters: Handling Positional Parameters en Masse"
[bashpitfalls#cp_.24file_.24target]: https://mywiki.wooledge.org/BashPitfalls#cp_.24file_.24target "Bash Pitfalls, 2. cp $file $target"
[bashpitfalls#echo_.24foo]: https://mywiki.wooledge.org/BashPitfalls#echo_.24foo "Bash Pitfalls, 14. echo $foo"
[bashpitfalls#for_arg_in_.24.2A]: https://mywiki.wooledge.org/BashPitfalls#for_arg_in_.24.2A "Bash Pitfalls, 24. for arg in $*"
