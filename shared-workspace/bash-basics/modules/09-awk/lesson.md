# Fields and Totals with awk

cut picks fields, grep picks lines, and a `while read` loop adds up
numbers. awk does all three in one small program: it reads its input a
line at a time, and for each line runs the actions whose patterns
match. ([wikipedia-awk#Structure_of_AWK_programs]) In this module you add
[`exercise/bytes.sh`](exercise/bytes.sh) to logkit: it adds up the bytes
a server sent, for all requests and for the failed ones.

By the end of this module you can:

1. Print chosen fields of each line with awk's `$1`, `$2`, … and `$NF`
2. Select lines with a comparison or a regular expression as the pattern
3. Add up values across lines and print the total in an `END` block

**How to work through it:** awk programs go in single quotes, like grep
patterns and sed commands; the first section shows why. Paste each
example whole: some programs span several lines.

## Patterns and actions

An awk program is a series of pattern-action pairs, each written
`pattern { action }`. awk splits its input into records, by default one
per line, and tests each record against each pattern in turn. When a
pattern is true, its action runs. ([wikipedia-awk#Structure_of_AWK_programs])

Either half can be left out. Without a pattern, the action runs for every
line; without an action, awk prints the line. That is sed's structure:
an address, then a command. ([wikipedia-awk#Structure_of_AWK_programs])
But awk doesn't print every line; it prints only when a `print` runs or a
pattern has no action.

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" >> access.log
echo "pattern only:"
awk '/ 404 /' access.log
echo "action only:"
awk '{ print $4 }' access.log
echo "both:"
awk '/ 404 / { print $4 }' access.log
```
```output
pattern only:
2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
action only:
/index.html
/missing.html
both:
/missing.html
```

`$4` is the fourth field. awk's fields look like bash's arguments `$1`,
`$2`, …, and in double quotes bash expands them before awk starts. At
the prompt, as in a script run without arguments, `$2` is empty, so the
second awk below gets `{ print  }` and prints the whole line:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
awk '{ print $2 }' access.log
awk "{ print $2 }" access.log
```
```output
203.0.113.5
2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512
```

## Fields

awk splits each line into fields: `$1` is the first, `$2` the second, and
so on, and `$0` is the whole line. ([wikipedia-awk#Built-in_variables])
`print` alone prints `$0`, `print $2, $4` prints two fields with a single
space between them, and every `print` ends its output with a
newline. ([wikipedia-awk#The_print_command])

Leave out the comma and the values are glued together: two values next
to each other make one string. Text of your own goes in double
quotes. ([wikipedia-awk#Variables_and_syntax]) Unlike Python's, awk's `+`
doesn't join strings: there is no operator for that, and `+` turns both
sides into numbers, so the text is lost. ([wikipedia-awk#Sum_last_word])

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
awk '{ print $2, $4 }' access.log
awk '{ print $2 $4 }' access.log
awk '{ print $2 " asked for " $4 }' access.log
awk '{ print "bytes: " + $6 }' access.log
```
```output
198.51.100.7 /missing.html
198.51.100.7/missing.html
198.51.100.7 asked for /missing.html
153
```

### Runs of spaces

By default, fields are separated by white space: any run of spaces and
tabs. ([wikipedia-awk#Built-in_variables]) So two spaces in a row don't
make an empty field as with `cut -d ' '`: awk splits like Python's
`line.split()`. Spaces at the start of a line are skipped too, as in the
padded counts of `uniq -c`:

```bash run
echo "GET  /index.html" > spaced.txt
echo "cut: [$(cut -d ' ' -f 2 spaced.txt)]"
echo "awk: [$(awk '{ print $2 }' spaced.txt)]"
echo "   3 203.0.113.5" > counts.txt
echo "  12 198.51.100.7" >> counts.txt
awk '{ print $2, $1 }' counts.txt
```
```output
cut: []
awk: [/index.html]
203.0.113.5 3
198.51.100.7 12
```

<!-- challenge id=c1 objective=1 -->
> **Challenge c1:** Open [`challenges/c1.sh`](challenges/c1.sh) and make it
> print the client IP and the path of each request in LOGFILE, its first
> argument. The log lines up its columns with extra spaces:
> `2026-10-06T10:15:40 198.51.100.7  GET  /missing.html  404  153`
> becomes `198.51.100.7 /missing.html`. Check it with `learn check c1`.

### The last field

`NF` holds the number of fields in the current line, so `$NF` is the last
field and `$(NF-1)` the one before it. ([wikipedia-awk#Built-in_variables])
That works however many fields each line has. awk applies `$` before
any other operator, so `$NF-1` is the last field minus 1; for the field
before the last, write the parentheses. ([wikipedia-awk#Sum_last_word])
Below, the second line has lost its bytes:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404" >> access.log
awk '{ print NF, $NF, $(NF-1) }' access.log
awk '{ print $NF-1 }' access.log
```
```output
6 512 200
5 404 /missing.html
511
403
```

## Choosing lines

A pattern is usually an expression: a comparison such as `$5 == 404`, or
a regular expression between slashes. ([wikipedia-awk#Structure_of_AWK_programs])

### Comparisons

Logical operators join several comparisons into one
pattern. ([wikipedia-awk#Structure_of_AWK_programs]) The example below
uses `>=`, `>` and `==`, which mean what they mean in Python, and `&&`,
which is Python's `and`. Text goes in double quotes, as in
`$3 == "POST"`. ([wikipedia-awk#Variables_and_syntax]) Fields that hold
numbers compare as numbers: below, 512 is not more than 1000, although
as text it sorts after it.

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" >> access.log
echo "2026-10-06T10:16:02 192.0.2.44 POST /login 401 64" >> access.log
echo "2026-10-06T10:16:48 192.0.2.44 GET /logo.png 200 1024" >> access.log
echo "status 400 or more:"
awk '$5 >= 400 { print $4, $5 }' access.log
echo "more than 1000 bytes:"
awk '$6 > 1000 { print $4, $6 }' access.log
echo "failed logins:"
awk '$3 == "POST" && $5 == 401 { print $2 }' access.log
```
```output
status 400 or more:
/missing.html 404
/login 401
more than 1000 bytes:
/logo.png 1024
failed logins:
192.0.2.44
```

A comparison on a field, like `$5 >= 400`, looks only at the status,
never at a 404 in a path or in the bytes.

### Regular expressions

A regular expression on its own, `/regexp/`, is matched against the whole
line. The `~` operator matches it against any string, such as one field:
`$4 ~ /\.php$/`. ([wikipedia-awk#Structure_of_AWK_programs]) Inside the
slashes, `$` is the end anchor, as in grep; outside them it picks a
field. A log line ends with the bytes, so `/\.php$/` never matches
one. awk reads `|` and `( )` as `grep -E` does, without backslashes:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:16:02 192.0.2.44 GET /wp-login.php 404 153" >> access.log
echo "2026-10-06T10:17:03 198.51.100.7 GET /.env 404 153" >> access.log
echo "whole line:"
awk '/\.php$/' access.log
echo "field 4:"
awk '$4 ~ /\.(php|env)$/ { print $4, $5 }' access.log
```
```output
whole line:
field 4:
/wp-login.php 404
/.env 404
```

<!-- challenge id=c2 objective=2 -->
> **Challenge c2:** Open [`challenges/c2.sh`](challenges/c2.sh) and make it
> print the path of every missing image in LOGFILE: the requests with
> status 404 whose path ends in `.png`, `.jpg` or `.gif`. A 404 request
> for `/img/logo.png` prints `/img/logo.png`; one for `/img/logo.png.bak`
> prints nothing. Check it with `learn check c2`.

## Adding up with END

awk has variables of its own. Unlike in bash, there is no `$` in front:
`$` picks a field by its number, so `$total` is the field whose number is
the value of `total`. ([wikipedia-awk#Sum_last_word])

A variable you never assigned is both 0 and the empty string, so a total
needs no `total = 0` to start. `total += $6` adds a field to a
total. ([wikipedia-awk#Variables_and_syntax])

Two special patterns run their action outside the loop over the lines:
`BEGIN` before the first line is read and `END` after the
last. ([wikipedia-awk#Structure_of_AWK_programs]) So add up in an action
that runs for every line, and print the total in an END block,
`END { ... }`. ([wikipedia-awk#Sum_last_word])

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" >> access.log
awk '{ total += $6 } END { print total }' access.log
awk '{ total += $6 } END { print "[" $total "]" }' access.log
```
```output
665
[]
```

`$total` is field 665, which is empty.

With no lines to read, the action never runs, `total` is never assigned,
and `print total` prints an empty line. Adding 0 turns it into a number,
so `print total + 0` prints `0`. ([wikipedia-awk#Sum_last_word]) With
no file name, awk reads standard input, like grep and sed. Below, grep
finds no 500 request, so awk reads nothing:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
grep " 500 " access.log | awk '{ total += $6 } END { print "[" total "]" }'
grep " 500 " access.log | awk '{ total += $6 } END { print total + 0 }'
```
```output
[]
0
```

<!-- challenge id=c3 objective=3 -->
> **Challenge c3:** Open [`challenges/c3.sh`](challenges/c3.sh) and make it
> print the total bytes of all requests in LOGFILE, as one number: `1689`
> for requests of 512, 153 and 1024 bytes, and `0` for an empty file.
> Check it with `learn check c3`.

### Several totals in one program

awk tests every line against every pattern and runs the action of each
one that is true. ([wikipedia-awk#Structure_of_AWK_programs]) Unlike
`case`, a line that matched one pattern goes on to the next, so one
program can keep several totals. Print each with `+ 0`, in case its
action never ran. A program can span several lines inside the single
quotes; on one line, `;` separates two statements. `++` adds 1, as in bash's `(( count++ ))`.

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" >> access.log
echo "2026-10-06T10:16:02 192.0.2.44 POST /login 401 64" >> access.log
awk '
{ requests++ }
$5 == 404 { notfound++ }
$5 >= 500 { servererrors++ }
END { print "requests:", requests + 0; print "404:", notfound + 0; print "5xx:", servererrors + 0 }
' access.log
```
```output
requests: 3
404: 1
5xx: 0
```

## What's next

- **Exercise:** write [`exercise/bytes.sh`](exercise/bytes.sh), logkit's
  ninth tool, then run `learn check`.
  [`exercise/notfound.sh`](exercise/notfound.sh),
  [`exercise/count.sh`](exercise/count.sh),
  [`exercise/countall.sh`](exercise/countall.sh),
  [`exercise/healthcheck.sh`](exercise/healthcheck.sh),
  [`exercise/summary.sh`](exercise/summary.sh),
  [`exercise/top.sh`](exercise/top.sh),
  [`exercise/suspicious.sh`](exercise/suspicious.sh) and
  [`exercise/anonymize.sh`](exercise/anonymize.sh) are the finished tools
  from modules 1 to 8; leave them unchanged.
- **Quiz:** run `learn quiz`.
- **Recap:** read [`recap.md`](recap.md).

[wikipedia-awk#Structure_of_AWK_programs]: https://en.wikipedia.org/wiki/AWK#Structure_of_AWK_programs "Wikipedia, AWK: Structure of AWK programs"
[wikipedia-awk#The_print_command]: https://en.wikipedia.org/wiki/AWK#The_print_command "Wikipedia, AWK: The print command"
[wikipedia-awk#Built-in_variables]: https://en.wikipedia.org/wiki/AWK#Built-in_variables "Wikipedia, AWK: Built-in variables"
[wikipedia-awk#Variables_and_syntax]: https://en.wikipedia.org/wiki/AWK#Variables_and_syntax "Wikipedia, AWK: Variables and syntax"
[wikipedia-awk#Sum_last_word]: https://en.wikipedia.org/wiki/AWK#Sum_last_word "Wikipedia, AWK: Sum last word"
