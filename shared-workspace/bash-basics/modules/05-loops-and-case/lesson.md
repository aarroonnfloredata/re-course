# Loops, Arithmetic and case

Summing up a folder of logs means going through each file and each line
of it, counting and adding up. This module shows how to repeat commands with `for` and
`while`, do arithmetic, and sort values into classes with `case`. With
them you add [`exercise/summary.sh`](exercise/summary.sh) to logkit: it
reports the requests, errors and bytes of every log in a folder.

By the end of this module you can:

1. Loop over the files a glob matches with `for`, and skip a glob that
   matched nothing
2. Read a file line by line, split into fields, with `while read -r`
3. Count and add with `$(( ))` and `(( ))`
4. Choose between patterns with `case`

**How to work through it:** run each example in bash, each in a new empty
folder, and paste it whole: loops span several lines. If an example
prints something other than its output block, a variable from an earlier
one may be in the way: type `exit`, start a fresh `bash` and try again.

## Looping over files with `for`

`for name in words; do commands; done` runs the commands once for each
word, with the variable `name` set to that word. ([tlcl#for-traditional-shell-form])
`do` and `done` mark where the body begins and ends, as `then` and `fi` do
for `if`. ([bashguide-tests#Conditional_Loops_.28while.2C_until_and_for.29])
It is Python's `for name in items:`, with words as the items.

The words can come from a glob. Each name the glob matches becomes one
word, spaces and all. ([bashguide-tests#Conditional_Loops_.28while.2C_until_and_for.29])
Inside the loop, quote `"$file"` as always (inside `[[ ]]` it needs no
quotes, as in module 4). ([bashpitfalls#for_f_in_.24.28ls_.2A.mp3.29])

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
echo "2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153" > "monday log.log"
echo "Look into the 404s." > notes.txt
for status in 404 500; do
    echo "status $status"
done
for file in *.log; do
    echo "found $file:"
    tail -n 1 "$file"
done
```
```output
status 404
status 500
found access.log:
2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
found monday log.log:
2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153
```

### Not `$(ls)`

Don't loop over the output of `ls`. Unquoted, `$(ls *.log)` is split into
words at every space; quoted, it is a single word holding all the
names. ([bashguide-tests#Conditional_Loops_.28while.2C_until_and_for.29]) ([bashpitfalls#for_f_in_.24.28ls_.2A.mp3.29])
Use the glob itself:

```bash run
echo "2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153" > "monday log.log"
for file in $(ls *.log); do
    echo "[$file]"
done
for file in *.log; do
    echo "[$file]"
done
```
```output
[monday]
[log.log]
[monday log.log]
```

### A glob that matches nothing

A glob that matches no file stays as it is, so the loop still runs once,
with the pattern itself in the variable. ([tlcl#for-traditional-shell-form]) ([bashpitfalls#for_f_in_.24.28ls_.2A.mp3.29])
So check that the file exists, and when it doesn't, skip it with
`continue`. ([bashpitfalls#for_f_in_.24.28ls_.2A.mp3.29]) `continue` skips
the rest of the body and goes on with the next
word. ([tlcl#break-and-continue]) ([bashguide-tests#Conditional_Loops_.28while.2C_until_and_for.29])
Run this example in a folder without `.log` files:

```bash run
for file in *.log; do
    echo "without the check: $file"
done
for file in *.log; do
    [[ -e $file ]] || continue
    echo "with the check: $file"
done
```
```output
without the check: *.log
```

For the logs in another folder, quote the variable and keep the glob
outside the quotes, as in module 3. Loops can also be
nested. ([bashguide-tests#Choices_.28case_and_select.29])

```bash run
mkdir logs "old logs"
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > logs/access.log
echo "2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153" > "logs/monday log.log"
for dir in logs "old logs"; do
    for file in "$dir"/*.log; do
        [[ -e $file ]] || continue
        echo "$file"
    done
done
```
```output
logs/access.log
logs/monday log.log
```

<!-- challenge id=c1 objective=1 -->
> **Challenge c1:** Open [`challenges/c1.sh`](challenges/c1.sh) and make it
> print `FILE: N requests with status 404` for each `.log` file in the
> current folder, and nothing when there is none. Count with
> `grep -c " 404 "`, as [`exercise/count.sh`](exercise/count.sh) does.
> For the first example's logs, it prints
> `access.log: 1 requests with status 404` first. Check it with
> `learn check c1`.

## Reading a file line by line

`while` runs a command before each pass of its body, which sits between
`do` and `done`. Status 0 means one more pass; any other status ends the
loop. ([tlcl#while]) ([bashguide-tests#Conditional_Loops_.28while.2C_until_and_for.29])

To read a file, use `read -r` as the command and put `< file` after
`done`. ([tlcl#reading-files-with-loops]) `read` reads one line and
succeeds; at the end of the file it fails, and the loop
ends. ([tlcl#reading-files-with-loops]) Given several names, it puts one
field of the line in each. ([tlcl#reading-files-with-loops]) The last name
gets the rest of the line:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" >> access.log
while read -r time ip method path status bytes; do
    echo "$status $method $path"
done < access.log
while read -r time ip rest; do
    echo "$ip asked: $rest"
done < access.log
```
```output
200 GET /index.html
404 GET /missing.html
203.0.113.5 asked: GET /index.html 200 512
198.51.100.7 asked: GET /missing.html 404 153
```

Name each field you don't need `_`, as you would in Python.

The `<` after `done` gives the whole loop one input, so each `read` takes
the line after the one before. ([tlcl#reading-files-with-loops]) A `<` on
`read` itself opens the file anew each time, so every `read` gets the
first line:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" >> access.log
read -r _ _ _ first _ _ < access.log
read -r _ _ _ second _ _ < access.log
echo "first: $first, second: $second"
```
```output
first: /index.html, second: /index.html
```

Always write `-r`. Without it, `read` drops backslashes, which mangles
paths such as the one in this attack:

```bash run
echo '2026-10-06T10:18:02 192.0.2.44 GET /scripts/..\..\winnt/cmd.exe 404 153' > attack.log
while read _ _ _ path _ _; do
    echo "without -r: $path"
done < attack.log
while read -r _ _ _ path _ _; do
    echo "with -r:    $path"
done < attack.log
```
```output
without -r: /scripts/....winnt/cmd.exe
with -r:    /scripts/..\..\winnt/cmd.exe
```

## Arithmetic

Bash keeps values as text: after `total=512+153`, `total` holds those
seven characters. ([bashguide-compound#Arithmetic_Evaluation]) Arithmetic
expansion, `$(( expression ))`, computes the expression and is replaced by
the result. ([tlcl#arithmetic-expansion]) Inside, variables need no
`$`. ([bashguide-compound#Arithmetic_Evaluation])

```bash run
total=512+153
echo "$total"
echo "$((512 + 153))"
bytes=512
echo "$((bytes * 2))"
```
```output
512+153
665
1024
```

`(( expression ))` is a command: it computes the expression, which can
assign, as in `(( total = total + bytes ))`, or compare with `<`, `>` and
`==`. ([bashguide-compound#Arithmetic_Evaluation]) ([tlcl#designed-for-integers])
Its exit status is 0 when the result is not zero and 1 when it is, so a
true comparison succeeds. ([bashguide-compound#Arithmetic_Evaluation])
Unlike in `[[ ]]`, `>` compares numbers here. ([bashguide-compound#Arithmetic_Evaluation])

To count, add 1 with `count=$((count + 1))`. ([tlcl#while])
`(( count++ ))` does the same in short, like Python's
`count += 1`. ([bashpitfalls#grep_foo_bar_.7C_while_read_-r.3B_do_.28.28count.2B-.2B-.29.29.3B_done])
And `(( total += bytes ))` adds a value:

```bash run
count=0
count=$((count + 1))
(( count++ ))
(( count += 10 ))
echo "count: $count"
(( count > 9 )) && echo "12 is more than 9"
[[ $count > 9 ]] || echo "but as text, 12 sorts before 9"
```
```output
count: 12
12 is more than 9
but as text, 12 sorts before 9
```

### Counting in a loop

Set each counter to 0 just before the `while` loop. When that loop sits
inside a `for` loop over files, this is inside the `for`, so each file's
counts start from 0. With an empty file, `read` fails at once, so the body
never runs. ([tlcl#reading-files-with-loops])
Below, grep finds no 404 request, so `empty.log` ends up empty, and
`requests`, never set, prints as nothing:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
grep " 404 " access.log > empty.log
total=0
while read -r _ _ _ _ _ bytes; do
    (( requests++ ))
    (( total += bytes ))
done < empty.log
echo "[$requests] requests, [$total] bytes"
```
```output
[] requests, [0] bytes
```

With both set to 0, the loop counts the requests and adds up their
bytes:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" >> access.log
echo "2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0" >> access.log
requests=0
total=0
while read -r _ _ _ _ _ bytes; do
    (( requests++ ))
    (( total += bytes ))
done < access.log
echo "$requests requests, $total bytes"
```
```output
3 requests, 665 bytes
```

Don't pipe into a loop that counts. Each command of a pipeline runs in a
subshell, a separate copy of the shell, so a counter the loop raises goes
up only in that copy. ([bashpitfalls#grep_foo_bar_.7C_while_read_-r.3B_do_.28.28count.2B-.2B-.29.29.3B_done]) ([tlcl#reading-files-with-loops])

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > monday.log
echo "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153" >> monday.log
count=0
grep " 404 " monday.log | while read -r line; do
    (( count++ ))
done
echo "after the pipe: $count"
```
```output
after the pipe: 0
```

<!-- challenge id=c2 objective=3 -->
> **Challenge c2:** Open [`challenges/c2.sh`](challenges/c2.sh) and make it
> read LOGFILE line by line and print `LOGFILE: R requests, B bytes`: the
> number of requests and the sum of their bytes. For the counting example's
> `access.log`, it prints `access.log: 3 requests, 665 bytes`. Check it
> with `learn check c2`.

## Choosing with `case`

`case` checks one value against several glob patterns, where `if` would
need an `elif` with `[[ = ]]` for each. ([bashguide-tests#Choices_.28case_and_select.29])
Its form is: ([tlcl#case])

```text
case word in
    pattern) commands ;;
    pattern|pattern) commands ;;
esac
```

A choice may list several patterns, separated by `|`; any one of them
matching is enough. ([tlcl#patterns]) Each pattern is a glob, tested
against the whole word instead of file names: `2[0-9][0-9]` matches `200`
but not `2000`. ([tlcl#patterns]) `;;` ends a choice's commands, which may
take several lines. ([bashguide-tests#Choices_.28case_and_select.29])

```bash run
for status in 200 301 404 503 2000; do
    case "$status" in
        2[0-9][0-9]) echo "$status: success" ;;
        3[0-9][0-9]) echo "$status: redirect" ;;
        4[0-9][0-9]|5[0-9][0-9])
            echo "$status: error"
            ;;
        *) echo "$status: not a status" ;;
    esac
done
```
```output
200: success
301: redirect
404: error
503: error
2000: not a status
```

Once a pattern matches, `case` runs its commands and checks no more
patterns. ([tlcl#patterns]) ([bashguide-tests#Choices_.28case_and_select.29])
`*)` matches any value, so put it last, as the choice for whatever no
other pattern matched. ([tlcl#patterns]) ([bashguide-tests#Choices_.28case_and_select.29])
When a value can match two patterns, put the one for the special case
first. `/errors/404.html` matches both `*.html` and `/errors/*`, and only
the second `case` below gives error pages their own choice:

```bash run
path=/errors/404.html
case "$path" in
    *.html) echo "*.html first: a page" ;;
    /errors/*) echo "*.html first: an error page" ;;
esac
case "$path" in
    /errors/*) echo "/errors/* first: an error page" ;;
    *.html) echo "/errors/* first: a page" ;;
esac
```
```output
*.html first: a page
/errors/* first: an error page
```

In a `while read` loop, `case` and arithmetic count the server errors:

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
echo "2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0" >> access.log
echo "2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0" >> access.log
server_errors=0
while read -r _ _ _ _ status _; do
    case "$status" in
        5[0-9][0-9]) (( server_errors++ )) ;;
    esac
done < access.log
echo "$server_errors server errors"
```
```output
2 server errors
```

<!-- challenge id=c3 objective=4 -->
> **Challenge c3:** Open [`challenges/c3.sh`](challenges/c3.sh) and make it
> print the kind of a request path, its argument: `page` for paths ending
> in `.html` or `/`, `image` for `.png`, `.jpg` and `.gif`, and `other` for
> the rest. `bash challenges/c3.sh /index.html.bak` prints
> `/index.html.bak: other`. Check it with `learn check c3`.

## What's next

- **Exercise:** write [`exercise/summary.sh`](exercise/summary.sh),
  logkit's fifth tool, as its header comment describes, then run
  `learn check`. [`exercise/notfound.sh`](exercise/notfound.sh),
  [`exercise/count.sh`](exercise/count.sh),
  [`exercise/countall.sh`](exercise/countall.sh) and
  [`exercise/healthcheck.sh`](exercise/healthcheck.sh) are the finished
  tools from modules 1 to 4; leave them as they are.
- **Quiz:** run `learn quiz`.
- **Recap:** read [`recap.md`](recap.md).

[bashguide-tests#Conditional_Loops_.28while.2C_until_and_for.29]: https://mywiki.wooledge.org/BashGuide/TestsAndConditionals#Conditional_Loops_.28while.2C_until_and_for.29 "BashGuide, Tests and Conditionals: 5. Conditional Loops (while, until and for)"
[bashguide-tests#Choices_.28case_and_select.29]: https://mywiki.wooledge.org/BashGuide/TestsAndConditionals#Choices_.28case_and_select.29 "BashGuide, Tests and Conditionals: 6. Choices (case and select)"
[bashguide-compound#Arithmetic_Evaluation]: https://mywiki.wooledge.org/BashGuide/CompoundCommands#Arithmetic_Evaluation "BashGuide, Compound Commands: Arithmetic Evaluation"
[tlcl#for-traditional-shell-form]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=517 "The Linux Command Line, 33 Flow Control: Looping with for: for: Traditional Shell Form"
[tlcl#while]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=467 "The Linux Command Line, 29 Flow Control: Looping with while / until: while"
[tlcl#break-and-continue]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=469 "The Linux Command Line, 29 Flow Control: Looping with while / until: break and continue"
[tlcl#reading-files-with-loops]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=475 "The Linux Command Line, 29 Flow Control: Looping with while / until: Reading Files with Loops"
[tlcl#arithmetic-expansion]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=98 "The Linux Command Line, 7 Seeing the World as the Shell Sees It: Arithmetic Expansion"
[tlcl#designed-for-integers]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=446 "The Linux Command Line, 27 Flow Control: Branching with if: (( )) - Designed for Integers"
[tlcl#case]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=493 "The Linux Command Line, 31 Flow Control: Branching with case: case"
[tlcl#patterns]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=495 "The Linux Command Line, 31 Flow Control: Branching with case: Patterns"
[bashpitfalls#for_f_in_.24.28ls_.2A.mp3.29]: https://mywiki.wooledge.org/BashPitfalls#for_f_in_.24.28ls_.2A.mp3.29 "Bash Pitfalls, 1. for f in $(ls *.mp3)"
[bashpitfalls#grep_foo_bar_.7C_while_read_-r.3B_do_.28.28count.2B-.2B-.29.29.3B_done]: https://mywiki.wooledge.org/BashPitfalls#grep_foo_bar_.7C_while_read_-r.3B_do_.28.28count.2B-.2B-.29.29.3B_done "Bash Pitfalls, 8. grep foo bar | while read -r; do ((count++)); done"
