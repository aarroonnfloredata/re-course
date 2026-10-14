# Variables, Arguments and Command Substitution

logkit's first tool always reads `access.log` and always looks for status 404.
Real tools take such values from the command line. This module shows
how to keep values in variables, read a script's arguments, and store a
command's output to use later. With them you add a second tool to logkit,
[`exercise/count.sh`](exercise/count.sh), which counts the requests with any
status in any log file.

By the end of this module you can:

1. Assign variables without spaces around `=` and expand them with `$` and
   `${ }`
2. Read a script's arguments with `$1`, `$2`, … and count them with `$#`
3. Capture a command's output in a variable with `$( )`

**How to work through it:** try each example in bash. If an example prints
something different from its output block, type `exit`, start a fresh
`bash` and run the example again.

## Variables

A variable is a name that holds a value. To assign one, write the name, `=`
and the value: `logfile=access.log`. ([bashguide-parameters#Parameters])
A name is made of letters, digits and underscores, and starts with a letter
or an underscore. Names are case-sensitive, so `logfile` and `LOGFILE` are
different variables. ([bashguide-parameters#Special_Parameters_and_Variables])

In Python, `count = 5` makes an `int`. In bash, `count=5` stores the text
`5`: values have no types. To store a value that holds a space, such as
`"logkit report"` below, put it in quotes. ([tlcl#assigning-values-to-variables-and-constants])

To use the value, put a `$` before the name. Before it runs a command, bash
replaces `$logfile` with the value; this is called parameter
expansion. ([bashguide-parameters#Parameters]) The `$` is not part of the
name: it only asks for the expansion. ([bashguide-parameters#Special_Parameters_and_Variables])

```bash run
logfile=access.log
title="logkit report"
echo "$title for $logfile"
```
```output
logkit report for access.log
```

Expansion works inside double quotes, so a variable can be part of a grep
pattern. Below, `" $status "` becomes `" 404 "` before grep
runs. ([bashguide-parameters#Parameters])

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
echo "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404" >> access.log
logfile=access.log
status=404
grep -c " $status " "$logfile"
```
```output
1
```

In a command's arguments, write every expansion in double quotes, like
`"$logfile"` above. Without them, a value with spaces can fall apart into
several words; module 3 shows when that happens. ([bashguide-parameters#Parameters]) ([tlcl#assigning-values-to-variables-and-constants])

Python raises a `NameError` for a name that was never assigned. Bash
doesn't stop: the expansion is empty, and the command runs with whatever is
left. ([tlcl#variables-and-constants]) Below, grep runs twice with the same
pattern, before and after `status` is set. The first time, the pattern is
just two spaces:

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
echo "pattern: [ $status ]"
grep -c " $status " access.log
status=404
echo "pattern: [ $status ]"
grep -c " $status " access.log
```
```output
pattern: [  ]
0
pattern: [ 404 ]
1
```

### No spaces around `=`

Spaces around `=` turn an assignment into a command. Bash splits
`wanted = 404` into three words, runs the first one, `wanted`, as a command,
and passes it `=` and `404` as its arguments. ([bashpitfalls#foo_.3D_bar]) ([bashguide-parameters#Parameters])
And the name you assign to has no `$` in front: `$wanted=404` is wrong as
well. ([bashpitfalls#A.24foo.3Dbar])

```bash run
wanted = 404 2> /dev/null
echo "wanted holds [$wanted]"
wanted=404
echo "wanted holds [$wanted]"
```
```output
wanted holds []
wanted holds [404]
```

There is no command called `wanted`, so the first line failed with an error
like `wanted: command not found`. ([bashguide-parameters#Special_Parameters_and_Variables])

`wanted= 404` and `wanted =404` are wrong too. ([bashpitfalls#foo_.3D_bar])
When another word follows an assignment, bash runs that word as a command,
and the variable doesn't keep the value. So `wanted= 404` runs a command
called `404`, and `heading=logkit report` runs `report`. The `1` below is
grep finding bash's error message in `errors.txt`:

```bash run
heading=logkit echo "bash ran echo"
echo "heading holds [$heading]"
heading=logkit report 2> errors.txt
grep -c "report: command not found" errors.txt
echo "heading holds [$heading]"
```
```output
bash ran echo
heading holds []
1
heading holds []
```

### Where a name ends: `${ }`

After a `$`, bash reads letters, digits and underscores as part of the name.
In `$day_backup` the name is `day_backup`, a different variable, which is
empty. Braces mark where the name ends: `${day}_backup`. ([tlcl#assigning-values-to-variables-and-constants])
A `.` can't be part of a name, so `$day.log` needs no
braces. ([bashguide-parameters#Special_Parameters_and_Variables])

```bash run
name=access
day=2026-10-06
echo "$name_$day.log"
echo "${name}_$day.log"
```
```output
2026-10-06.log
access_2026-10-06.log
```

The first line expanded the empty variable `name_`, then `$day`.

<!-- challenge id=c1 objective=1 -->
> **Challenge c1:** Open [`challenges/c1.sh`](challenges/c1.sh) and make it
> copy `access.log` to `access_2026-10-06.log`, then print
> `saved access.log as access_2026-10-06.log`. The check looks only at that
> result; the practice is in building both names from the variables
> `name=access` and `day=2026-10-06` with `$` and `${ }`. Check it with
> `learn check c1`.

## Arguments

The words after the script's name on the command line are its arguments.
Inside the script, `$1` holds the first one, `$2` the second, and so on; they
are called positional parameters. ([tlcl#accessing-the-command-line]) ([bashguide-io#Command-line_Arguments])
`$#` holds how many there are. ([tlcl#determining-the-number-of-arguments]) ([bashguide-parameters#Special_Parameters_and_Variables])
The script's own name doesn't count: `$1` is Python's `sys.argv[1]`, and
`$#` is `len(sys.argv) - 1`.

```bash run
echo 'echo "log: $1, status: $2, $# arguments"' > args.sh
cat args.sh
bash args.sh access.log 404
bash args.sh monday.log 500 GET
```
```output
echo "log: $1, status: $2, $# arguments"
log: access.log, status: 404, 2 arguments
log: monday.log, status: 500, 3 arguments
```

As `cat args.sh` shows, the single quotes kept `$1`, `$2` and `$#` as they
are, so they ended up in the script; module 3 explains single quotes.

An argument that wasn't given expands to nothing, like a variable that was
never assigned. ([tlcl#accessing-the-command-line])

```bash run
echo 'echo "$# arguments, log: [$1], status: [$2]"' > args.sh
bash args.sh access.log
bash args.sh
```
```output
1 arguments, log: [access.log], status: []
0 arguments, log: [], status: []
```

From the tenth argument on, the number needs braces:
`${10}`. ([bashguide-io#Command-line_Arguments]) ([tlcl#accessing-the-command-line])
Without them, `$10` is `$1` followed by a `0`:

```bash run
echo 'echo "$10 ${10}"' > ten.sh
bash ten.sh a b c d e f g h i j
```
```output
a0 j
```

Copy arguments into named variables at the top of the script, so the rest
reads `$logfile` instead of `$1`. Here, `last.sh` prints the last few
requests of a log; the file and the number of lines come from its
arguments:

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > monday.log
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" >> monday.log
echo "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64" >> monday.log
echo 'logfile=$1' > last.sh
echo 'lines=$2' >> last.sh
echo 'echo "The last $lines requests in $logfile:"' >> last.sh
echo 'tail -n "$lines" "$logfile"' >> last.sh
cat last.sh
bash last.sh monday.log 2
```
```output
logfile=$1
lines=$2
echo "The last $lines requests in $logfile:"
tail -n "$lines" "$logfile"
The last 2 requests in monday.log:
2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153
2026-10-06T10:16:02 203.0.113.5 POST /login 401 64
```

<!-- challenge id=c2 objective=2 -->
> **Challenge c2:** Open [`challenges/c2.sh`](challenges/c2.sh) and make it
> print its second argument, its first and the number of arguments, as
> `STATUS in LOGFILE (N arguments)`: `bash challenges/c2.sh access.log 404`
> prints `404 in access.log (2 arguments)`. Check it with `learn check c2`.

## Capturing output: `$( )`

To store what a command prints, put the command between `$(` and `)` and
assign the result to a variable. ([tlcl#assigning-values-to-variables-and-constants])
This is command substitution: bash runs the command first and uses its
output in place of the `$( )`. Older scripts write it with backquotes, as in
`` count=`grep -c " 404 " access.log` ``, and bash still accepts that
form. ([tlcl#command-substitution])

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
echo "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64" >> access.log
echo "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153" >> access.log
count=$(grep -c " 404 " access.log)
echo "[$count]"
```
```output
[2]
```

grep's output went into the variable, not to the screen. grep printed `2`
and a newline, but the variable holds just `2`: the newline at the end of
the output is dropped. That makes the value easy to use in the middle of a
line. In Python terms, it's like keeping
`subprocess.run(...).stdout.rstrip("\n")`.

Between the parentheses, a pipeline works as well as a single
command. ([tlcl#command-substitution]) Below, only the last 404 request is
stored:

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
echo "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64" >> access.log
echo "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153" >> access.log
latest=$(grep " 404 " access.log | tail -n 1)
echo "latest 404: $latest"
```
```output
latest 404: 2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153
```

After `=`, an expansion needs no double quotes, even when its value has
spaces: the whole value is assigned, as `latest` shows. Text you type with
spaces still needs them. ([tlcl#assigning-values-to-variables-and-constants])
The quotes inside `$( )`, around `" 404 "`, belong
to grep's pattern, not to the assignment. A variable copied with
`copy=$label` keeps all its spaces too:

```bash run
label="logkit   report"
copy=$label
echo "[$copy]"
```
```output
[logkit   report]
```

<!-- challenge id=c3 objective=3 -->
> **Challenge c3:** Open [`challenges/c3.sh`](challenges/c3.sh) and make it
> print how many GET and how many POST requests `access.log` holds, on one
> line: with three GET requests and one POST, it prints `3 GET, 1 POST`.
> Check it with `learn check c3`.

## What's next

- **Exercise:** write [`exercise/count.sh`](exercise/count.sh), logkit's
  second tool, as its header comment describes:
  `bash exercise/count.sh access.log 404` prints a line like
  `access.log: 2 requests with status 404`. Then run `learn check`.
  [`exercise/notfound.sh`](exercise/notfound.sh) is module 1's tool,
  finished; leave it as it is.
- **Quiz:** run `learn quiz`.
- **Recap:** read [`recap.md`](recap.md).

[bashguide-parameters#Parameters]: https://mywiki.wooledge.org/BashGuide/Parameters#Parameters "BashGuide, Parameters"
[bashguide-parameters#Special_Parameters_and_Variables]: https://mywiki.wooledge.org/BashGuide/Parameters#Special_Parameters_and_Variables "BashGuide, Parameters: Special Parameters and Variables"
[bashguide-io#Command-line_Arguments]: https://mywiki.wooledge.org/BashGuide/InputAndOutput#Command-line_Arguments "BashGuide, Input and Output: 1. Command-line Arguments"
[tlcl#variables-and-constants]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=416 "The Linux Command Line, 25 Starting a Project: Variables and Constants"
[tlcl#assigning-values-to-variables-and-constants]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=419 "The Linux Command Line, 25 Starting a Project: Assigning Values to Variables and Constants"
[tlcl#accessing-the-command-line]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=500 "The Linux Command Line, 32 Positional Parameters: Accessing the Command Line"
[tlcl#determining-the-number-of-arguments]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=501 "The Linux Command Line, 32 Positional Parameters: Determining the Number of Arguments"
[tlcl#command-substitution]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=101 "The Linux Command Line, 7 Seeing the World as the Shell Sees It: Command Substitution"
[bashpitfalls#foo_.3D_bar]: https://mywiki.wooledge.org/BashPitfalls#foo_.3D_bar "Bash Pitfalls, 16. foo = bar"
[bashpitfalls#A.24foo.3Dbar]: https://mywiki.wooledge.org/BashPitfalls#A.24foo.3Dbar "Bash Pitfalls, 15. $foo=bar"
