# Exit Status and Conditions

Every command reports whether it worked with a number: its exit status.
You will act on it with `&&`, `||`, `if` and tests, then add
[`exercise/healthcheck.sh`](exercise/healthcheck.sh) to logkit, which checks
a log for server errors and reports the result through its exit status.

By the end of this module you can:

1. Read a command's exit status with `$?` and end a script with a chosen
   status using `exit`
2. Run a command only when another succeeds or fails, with `&&` and `||`
3. Branch on a command's success with `if`, using `grep -q` as the condition
4. Compare strings and numbers and check files with `[[ ]]`

**How to work through it:** examples that use `exit` put it in a small
script; don't type `exit` at your prompt.

## Exit status

An exit status is a whole number from 0 to 255: 0 means success, and any
other number means failure. ([tlcl#exit-status]) ([bashguide-tests#Exit_Status-1]) Unlike
Python's 0, which is false, bash's 0 is the good news.

`$?` holds the exit status of the last
command. ([bashguide-tests#Exit_Status-1]) grep succeeds when it finds a
matching line and fails when it finds none. ([bashpitfalls#if_.5Bgrep_foo_myfile.5D])

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
grep -c " 404 " access.log
echo "status: $?"
grep -c " 500 " access.log
echo "status: $?"
```
```output
1
status: 0
0
status: 1
```

What grep prints and its exit status are separate: `grep -c " 500 "`
printed `0` and still failed. `false` always exits with 1 and `true` with
0, without doing anything else. ([tlcl#exit-status])

`$?` changes after every command, `echo` included. To use a status later,
save it in a variable straight away:

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
grep -c " 500 " access.log
echo "status: $?"
echo "status: $?"
grep -c " 500 " access.log
grep_status=$?
echo "grep's status: $grep_status"
```
```output
0
status: 1
status: 0
0
grep's status: 1
```

### Ending a script with `exit`

A script that runs to its end exits with the status of its last command.
`exit` ends it at once: `exit 2` with status 2, and `exit` without a number
with the status of the last command. ([tlcl#file-expressions])

```bash run
echo 'echo "checking $1"' > check.sh
echo 'exit 3' >> check.sh
echo 'echo "never printed"' >> check.sh
cat check.sh
bash check.sh access.log
echo "status: $?"
```
```output
echo "checking $1"
exit 3
echo "never printed"
checking access.log
status: 3
```

When something goes wrong, exit with a status other than 0 and send the
error message to stderr. ([bashguide-tests#Exit_Status-1]) ([tlcl#string-expressions])

<!-- challenge id=c1 objective=1 -->
> **Challenge c1:** Open [`challenges/c1.sh`](challenges/c1.sh) and make it
> run `grep -c " 404 "` on LOGFILE, its argument, then print
> `grep exited with S` and exit with S, grep's status. For a log without
> 404 requests it prints `0` and `grep exited with 1`, and exits with 1.
> Check it with `learn check c1`.

## `&&` and `||`

`cmd1 && cmd2` runs `cmd2` only when `cmd1` succeeds. `cmd1 || cmd2` runs
`cmd2` only when `cmd1` fails. ([tlcl#control-operators-another-way-to-branch]) ([bashguide-tests#Control_Operators_.28.26.26_and_.7C.7C.29])

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
grep " 404 " access.log > notfound.log && echo "saved the 404 requests"
grep " 500 " access.log > server-errors.log && echo "saved the 500 requests"
grep " 500 " access.log > server-errors.log || echo "no 500 requests"
```
```output
saved the 404 requests
no 500 requests
```

`|| exit 1` stops a script when a command
fails. ([tlcl#control-operators-another-way-to-branch]) Here `save.sh` stops
when grep finds nothing:

```bash run
echo 'grep " 404 " "$1" > notfound.log || exit 1' > save.sh
echo 'echo "saved the 404 requests of $1"' >> save.sh
cat save.sh
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > quiet.log
bash save.sh access.log
echo "status: $?"
bash save.sh quiet.log
echo "status: $?"
```
```output
grep " 404 " "$1" > notfound.log || exit 1
echo "saved the 404 requests of $1"
saved the 404 requests of access.log
status: 0
status: 1
```

### `&& ||` is not if/else

`cmd1 && cmd2 || cmd3` looks like "if `cmd1`, then `cmd2`, else `cmd3`".
But `cmd2` has a status too, and when it fails, `cmd3` runs as
well. ([bashpitfalls#cmd1_.26.26_cmd2_.7C.7C_cmd3]) Below, the 500 count
fails, so the message is wrong.

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
grep -c " 404 " access.log && grep -c " 500 " access.log || echo "no 404 requests"
```
```output
1
0
no 404 requests
```

Use `&&` and `||` for simple cases, and don't mix the two in one command:
write an `if` instead. ([bashguide-tests#Control_Operators_.28.26.26_and_.7C.7C.29]) ([bashpitfalls#cmd1_.26.26_cmd2_.7C.7C_cmd3])

<!-- challenge id=c2 objective=2 -->
> **Challenge c2:** Open [`challenges/c2.sh`](challenges/c2.sh) and make it
> save LOGFILE's 500 requests to `server-errors.log`, printing
> `500 requests saved to server-errors.log` only when there were some.
> Then it saves the 404 requests to `notfound.log`, printing
> `no 404 requests in LOGFILE` only when there were none. For `quiet.log`
> from the `save.sh` example, it prints `no 404 requests in quiet.log`.
> Check it with `learn check c2`.

## Branching with `if`

`if` runs a command and checks its exit status. On success it runs the
commands after `then`; otherwise those after `else`, if there is one. `fi`
ends the block. ([bashguide-tests#Conditional_Blocks_.28if.2C_test_and_.5B.5B.29]) ([tlcl#if])
`then` must start a new command: put it on the next line, or after a `;`
on the same line; otherwise it is one more argument to the command before
it. ([bashguide-tests#Conditional_Blocks_.28if.2C_test_and_.5B.5B.29]) ([bashguide-tests#Control_Operators_.28.26.26_and_.7C.7C.29]) ([bashguide-commands#Commands_and_Arguments])
Python's `if` tests a value; bash's tests whether a command
succeeded. ([tlcl#exit-status]) To branch on what grep finds, use grep
itself as the command. ([bashpitfalls#if_.5Bgrep_foo_myfile.5D]) With `-q`
it prints nothing, so only its status counts:

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
echo "2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0" >> access.log
if grep -q " 503 " access.log; then
    echo "access.log has 503 requests"
else
    echo "access.log has no 503 requests"
fi
if grep -q " 404 " access.log; then echo "and 404 requests"; fi
grep -q " 404 " access.log
echo "status: $?"
```
```output
access.log has 503 requests
and 404 requests
status: 0
```

The indentation is only for reading: the second `if` fits on one
line. ([tlcl#if]) ([bashguide-tests#Conditional_Blocks_.28if.2C_test_and_.5B.5B.29]) Don't wrap
grep in `[ ]`: `[` is a command of its own, not part of
`if`. ([bashpitfalls#if_.5Bgrep_foo_myfile.5D])

`elif` adds another condition, like Python's `elif`. ([tlcl#if]) In a grep
pattern, `[0-9]` matches any one
digit. ([tlcl#bracket-expressions-and-character-classes]) So
`" 5[0-9][0-9] "` finds the server errors, statuses 500 to 599. The double
quotes keep the pattern, spaces included, as one argument and stop bash
from expanding the brackets as a glob. ([tlcl#double-quotes])

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
echo "2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0" >> access.log
echo "2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0" >> access.log
echo "2026-10-06T10:17:30 203.0.113.5 GET /about.html 200 512" >> access.log
grep " 5[0-9][0-9] " access.log
if grep -q " 5[0-9][0-9] " access.log; then
    echo "server errors"
elif grep -q " 4[0-9][0-9] " access.log; then
    echo "client errors only"
else
    echo "no errors"
fi
```
```output
2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0
2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0
server errors
```

<!-- challenge id=c3 objective=3 -->
> **Challenge c3:** Open [`challenges/c3.sh`](challenges/c3.sh) and make it
> print `LOGFILE has POST requests` when LOGFILE, its argument, holds at
> least one POST request; otherwise `LOGFILE has only GET requests` when it
> has GET requests, and otherwise `LOGFILE has no requests`. For the
> `access.log` above, it prints `access.log has POST requests`. Check it
> with `learn check c3`.

## Tests with `[[ ]]`

`[[ expression ]]` succeeds when its expression is true, so it works with
`if`, `&&` and `||`. ([tlcl#a-more-modern-version-of-test]) ([bashguide-tests#Conditional_Blocks_.28if.2C_test_and_.5B.5B.29])
`[` (also called `test`) is the older form, a normal command; in bash
scripts, use `[[`. ([bashguide-tests#Conditional_Blocks_.28if.2C_test_and_.5B.5B.29])

### Strings

`=` (or `==`) and `!=` compare strings. `-z` is true for an empty string
and `-n` for a non-empty one. ([tlcl#string-expressions]) Inside `[[ ]]`, a
variable is neither split into words nor expanded as a glob, so `$name` on
the left needs no quotes, even when it is empty or holds spaces or `*`;
quoting does no harm. ([bashpitfalls#A.5B_.24foo_.3D_.22bar.22_.5D])
On the right of `=` or `==`, an unquoted value, `$var` included, is a glob
pattern matched against the left side, not against file names.
Quote it to compare plain text. ([bashguide-tests#Conditional_Blocks_.28if.2C_test_and_.5B.5B.29]) ([tlcl#a-more-modern-version-of-test])

```bash run
name="monday log.log"
pattern="*.log"
blank=""
[[ $name = "monday log.log" ]] && echo "same name"
[[ $name = $pattern ]] && echo "matches the pattern *.log"
[[ $name = "$pattern" ]]
echo "status: $?"
[[ -z $blank ]] && echo "blank is empty"
```
```output
same name
matches the pattern *.log
status: 1
blank is empty
```

Spaces matter. With `status=404` and no spaces around `=`, `$status=500`
is the single word `404=500`, and a single word is true when it isn't
empty. ([tlcl#string-expressions]) Without a space after `[[`, bash runs
`[[404` as a command, which fails: grep counts the "command not found"
message saved in `errors.txt`, the `1`.

```bash run
status=404
[[ $status = 500 ]] || echo "with spaces: not 500"
echo "$status=500"
[[ $status=500 ]] && echo "no spaces: true anyway"
[[$status = 500]] 2> errors.txt
grep -c "404: command not found" errors.txt
```
```output
with spaces: not 500
404=500
no spaces: true anyway
1
```

### Numbers

Compare numbers with `-eq` (equal), `-ne` (not equal), `-lt` (less than),
`-le` (less or equal), `-gt` (greater than) and `-ge` (greater or
equal). ([tlcl#integer-expressions]) Inside `[[ ]]`, `<` and `>` don't
redirect: they compare strings by sort order, so `10` comes before
`9`. ([bashguide-tests#Conditional_Blocks_.28if.2C_test_and_.5B.5B.29]) ([tlcl#string-expressions])

```bash run
count=10
limit=9
[[ $count -gt $limit ]] && echo "-gt: $count is more than $limit"
[[ $count > $limit ]] || echo ">: $count sorts before $limit"
```
```output
-gt: 10 is more than 9
>: 10 sorts before 9
```

A script can check `$#` first and stop with a usage message on stderr.
Below, `2>&1` sends it to stdout only so it shows in the
output. ([tlcl#redirecting-standard-output-and-standard-error-to-one-file])

```bash run
echo 'if [[ $# -ne 1 ]]; then' > last.sh
echo '    echo "usage: last.sh LOGFILE" >&2' >> last.sh
echo '    exit 2' >> last.sh
echo 'fi' >> last.sh
echo 'tail -n 1 "$1"' >> last.sh
cat last.sh
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
bash last.sh access.log
bash last.sh 2>&1
echo "status: $?"
```
```output
if [[ $# -ne 1 ]]; then
    echo "usage: last.sh LOGFILE" >&2
    exit 2
fi
tail -n 1 "$1"
2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
usage: last.sh LOGFILE
status: 2
```

<!-- challenge id=c4 objective=4 -->
> **Challenge c4:** Open [`challenges/c4.sh`](challenges/c4.sh) and make it
> compare the number of 404 requests in LOGFILE with LIMIT, as numbers:
> `bash challenges/c4.sh access.log 9` prints
> `10 requests with status 404: more than 9` and exits with 1 when
> `access.log` has ten; with a LIMIT of 10 it prints
> `10 requests with status 404: OK` and exits with 0. Check it with
> `learn check c4`.

### Files

`-e FILE` is true when FILE exists, `-f FILE` when it is a regular file and
`-d FILE` when it is a folder (directory). ([tlcl#file-expressions]) `!`
turns a test around. ([bashguide-tests#Conditional_Blocks_.28if.2C_test_and_.5B.5B.29])

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
mkdir logs 2> /dev/null
logfile=access.log
[[ -f $logfile ]] && echo "$logfile is a file"
[[ -d logs ]] && echo "logs is a folder"
[[ -f logs ]] || echo "logs is not a regular file"
[[ ! -e missing.log ]] && echo "missing.log doesn't exist"
```
```output
access.log is a file
logs is a folder
logs is not a regular file
missing.log doesn't exist
```

## What's next

- **Exercise:** write [`exercise/healthcheck.sh`](exercise/healthcheck.sh)
  as its header comment describes, then run `learn check`.
  [`exercise/notfound.sh`](exercise/notfound.sh),
  [`exercise/count.sh`](exercise/count.sh) and
  [`exercise/countall.sh`](exercise/countall.sh) are finished; leave them as
  they are.
- **Quiz:** run `learn quiz`.
- **Recap:** read [`recap.md`](recap.md).

[bashguide-tests#Exit_Status-1]: https://mywiki.wooledge.org/BashGuide/TestsAndConditionals#Exit_Status-1 "BashGuide, Tests and Conditionals: 1. Exit Status"
[bashguide-tests#Control_Operators_.28.26.26_and_.7C.7C.29]: https://mywiki.wooledge.org/BashGuide/TestsAndConditionals#Control_Operators_.28.26.26_and_.7C.7C.29 "BashGuide, Tests and Conditionals: 2. Control Operators (&& and ||)"
[bashguide-tests#Conditional_Blocks_.28if.2C_test_and_.5B.5B.29]: https://mywiki.wooledge.org/BashGuide/TestsAndConditionals#Conditional_Blocks_.28if.2C_test_and_.5B.5B.29 "BashGuide, Tests and Conditionals: 4. Conditional Blocks (if, test and [[)"
[tlcl#if]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=436 "The Linux Command Line, 27 Flow Control: Branching with if: if"
[tlcl#exit-status]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=437 "The Linux Command Line, 27 Flow Control: Branching with if: Exit Status"
[tlcl#file-expressions]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=439 "The Linux Command Line, 27 Flow Control: Branching with if: File Expressions"
[tlcl#string-expressions]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=442 "The Linux Command Line, 27 Flow Control: Branching with if: String Expressions"
[tlcl#integer-expressions]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=443 "The Linux Command Line, 27 Flow Control: Branching with if: Integer Expressions"
[tlcl#a-more-modern-version-of-test]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=445 "The Linux Command Line, 27 Flow Control: Branching with if: A More Modern Version of test"
[tlcl#control-operators-another-way-to-branch]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=450 "The Linux Command Line, 27 Flow Control: Branching with if: Control Operators: Another Way to Branch"
[bashpitfalls#if_.5Bgrep_foo_myfile.5D]: https://mywiki.wooledge.org/BashPitfalls#if_.5Bgrep_foo_myfile.5D "Bash Pitfalls, 9. if [grep foo myfile]"
[bashpitfalls#A.5B_.24foo_.3D_.22bar.22_.5D]: https://mywiki.wooledge.org/BashPitfalls#A.5B_.24foo_.3D_.22bar.22_.5D "Bash Pitfalls, 4. [ $foo = “bar” ]"
[bashpitfalls#cmd1_.26.26_cmd2_.7C.7C_cmd3]: https://mywiki.wooledge.org/BashPitfalls#cmd1_.26.26_cmd2_.7C.7C_cmd3 "Bash Pitfalls, 22. cmd1 && cmd2 || cmd3"
[bashguide-commands#Commands_and_Arguments]: https://mywiki.wooledge.org/BashGuide/CommandsAndArguments#Commands_and_Arguments "BashGuide, Commands and Arguments"
[tlcl#bracket-expressions-and-character-classes]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=296 "The Linux Command Line, 19 Regular Expressions: Bracket Expressions and Character Classes"
[tlcl#double-quotes]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=103 "The Linux Command Line, 7 Seeing the World as the Shell Sees It: Double Quotes"
[tlcl#redirecting-standard-output-and-standard-error-to-one-file]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=84 "The Linux Command Line, 6 Redirection: Redirecting Standard Output and Standard Error to One File"
