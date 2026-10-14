# Functions and Safer Scripts

This module packs steps that logkit's tools repeat into functions in a
library, [`exercise/loglib.sh`](exercise/loglib.sh), and builds logkit's
last tool on it: [`exercise/logkit.sh`](exercise/logkit.sh), one command
that loads the library and stops at the first error.

By the end of this module you can:

1. Define functions that take arguments and keep their variables local
2. Give results back from a function through its output and its return
   status
3. Load functions from another file with `source`
4. Make a script stop on errors with `set -euo pipefail`, and know the cases
   `set -e` misses

**How to work through it:** a function stays defined in your shell, like a
variable, so start a fresh `bash` for each
example. ([bashguide-compound#Functions-1]) Examples that use `exit` or
`set` write a small script and run it with `bash`. Don't type `set -e` at
your prompt: it ends the shell it runs in at a failing command, and there
that shell is yours. ([tlcl#set-e-set-u-and-set-o-pipefail])

## Functions

A function is a block of commands with a name. `name() { commands; }`
stores the block without running it; writing `name` later runs it, like
any command. ([bashguide-compound#Functions-1]) ([tlcl#shell-functions])
Define it before the line that calls it. ([tlcl#shell-functions]) Inside it, `$1`, `$2`, … and `$#` are its
own arguments, not the
script's. ([bashguide-compound#Functions-1]) ([tlcl#using-positional-parameters-with-shell-functions])

```bash run
show_args() {
    echo "$# arguments, first: [$1]"
}
show_args "monday log.log" 404
show_args access.log
show_args
```
```output
2 arguments, first: [monday log.log]
1 arguments, first: [access.log]
0 arguments, first: []
```

### Local variables

A variable set inside a function is global, so a function can overwrite
its caller's. ([bashguide-compound#Functions-1]) ([tlcl#local-variables])
`local name` gives the function its own `name`, seen also by the
functions it calls. After the call, `name` is the caller's again,
unchanged. ([tlcl#local-variables]) Write `local` before
the variable is first set, a `for` loop's variable included. It works only
inside a function:

```bash run
echo "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153" > access.log
status="none yet"
count_global() {
    for status in "$@"; do
        grep -c " $status " access.log
    done
}
count_local() {
    local status count
    for status in "$@"; do
        count=$(grep -c " $status " access.log)
        echo "$status: $count"
    done
}
count_local 404 500
echo "status: $status"
count_global 404 500
echo "status: $status"
local status 2> /dev/null || echo "local outside a function fails"
```
```output
404: 1
500: 0
status: none yet
1
0
status: 500
local outside a function fails
```

With `local`, a function can use `status` without checking the rest of
the script's names. ([tlcl#local-variables])
`local count` and `count=$(...)` are separate lines on purpose: "What
`set -e` misses" shows why.

<!-- challenge id=c1 objective=1 -->
> **Challenge c1:** Open [`challenges/c1.sh`](challenges/c1.sh) and write
> `report_404 LOGFILE...`: for each LOGFILE it prints `LOGFILE: N`, its
> number of 404 requests, with `logfile` and `count` as local variables.
> For the log above, `report_404 access.log access.log` prints
> `access.log: 1` twice. Check it with `learn check c1`.

## Giving results back

A Python function returns a value; a bash function, like a command,
gives back its output, which `$( )` captures, and its exit
status. ([tlcl#shell-functions]) `return` skips the rest of the
function; the caller goes on. ([tlcl#shell-functions]) `return 1` makes
its status 1, the way to
report a failure, with the message on
stderr. ([tlcl#using-positional-parameters-with-shell-functions])
Without `return`, the status is that of the last command it ran:

```bash run
echo "2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0" > access.log
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > clean.log
server_errors() {
    if [[ ! -f $1 ]]; then
        echo "server_errors: no such file: $1" >&2
        return 2
    fi
    grep -c " 5[0-9][0-9] " "$1"
}
n=$(server_errors access.log)
echo "access.log: $n, status $?"
n=$(server_errors clean.log)
echo "clean.log: $n, status $?"
server_errors missing.log 2> /dev/null
echo "missing.log: status $?"
if server_errors access.log > /dev/null; then
    echo "access.log has server errors"
fi
```
```output
access.log: 1, status 0
clean.log: 0, status 1
missing.log: status 2
access.log has server errors
```

`n=$(...)` takes the function's status as its own, so `$?` shows it. A
status says whether something worked; give values back as output.

`exit` inside a function ends the whole script, not just the function:

```bash run
echo 'stop_return() { return 2; }' > stop.sh
echo 'stop_exit() { exit 2; }' >> stop.sh
echo 'stop_return' >> stop.sh
echo 'echo "after return: status $?"' >> stop.sh
echo 'stop_exit' >> stop.sh
echo 'echo "after exit: never printed"' >> stop.sh
bash stop.sh
echo "stop.sh ended with status $?"
```
```output
after return: status 2
stop.sh ended with status 2
```

So `exit` suits a function that reports an error and ends the script,
like the `die` you'll write in loglib.sh, and `return` one whose caller
carries on.

<!-- challenge id=c2 objective=2 -->
> **Challenge c2:** Open [`challenges/c2.sh`](challenges/c2.sh) and write
> `first_error LOGFILE`: it prints the first request with a 4xx or 5xx
> status and returns 0, returns 1 when there is none, and returns 2 with a
> message on stderr when LOGFILE isn't a regular file. For `access.log`
> above, it prints the 503 request. Check it with `learn check c2`.

## Loading functions with `source`

`bash lib.sh` runs a file as a separate program: what it defines is gone
when it ends. `source file`, or `. file`, runs the file's commands in the
current shell instead, so the functions and variables it defines
stay. ([bashguide-sourcing#Sourcing]) Loading a file that holds only
function definitions stores them and runs nothing
else. ([bashguide-compound#Functions-1])

```bash run
echo 'count_5xx() { grep -c " 5[0-9][0-9] " "$1"; }' > lib.sh
echo "2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0" > access.log
bash lib.sh
count_5xx access.log 2> /dev/null || echo "count_5xx isn't defined"
source ./lib.sh
count_5xx access.log
```
```output
count_5xx isn't defined
1
```

`./lib.sh` is lib.sh in the current folder, wherever the script is. `$0` holds the script's path as you ran
it, and `dirname` prints the folder part of a path, so
`"$(dirname "$0")/lib.sh"` is the lib.sh next to the script, from any
folder. Quotes inside `$( )` are separate from those around it, so a
folder name with a space stays whole:

```bash run
mkdir "my tools"
echo 'greet() { echo "hello from lib.sh"; }' > "my tools/lib.sh"
echo 'source ./lib.sh' > "my tools/here.sh"
echo 'greet' >> "my tools/here.sh"
echo 'echo "script: $0, folder: $(dirname "$0")"' > "my tools/main.sh"
echo 'source "$(dirname "$0")/lib.sh"' >> "my tools/main.sh"
echo 'greet' >> "my tools/main.sh"
bash "my tools/here.sh" 2> /dev/null || echo "here.sh: no ./lib.sh in this folder"
bash "my tools/main.sh"
cd "my tools"
bash main.sh
cd ..
```
```output
here.sh: no ./lib.sh in this folder
script: my tools/main.sh, folder: my tools
hello from lib.sh
script: main.sh, folder: .
hello from lib.sh
```

## Stopping at the first error

Under `set -e`, a script ends at the first command that exits with a
status other than 0; bash would otherwise go on. `set -u` ends it on
expanding a variable that was never
set. ([tlcl#set-e-set-u-and-set-o-pipefail]) `set -e` sees only exit
statuses, so it can't tell an error from a "no": grep finding nothing
stops the script too. Its rules also leave gaps, listed in "What
`set -e` misses". ([bashpitfalls#errexit]) `set -eu` turns on both:

```bash run
echo 'set -eu' > strict.sh
echo 'n=$(grep -c " 500 " "$1")' >> strict.sh
echo 'echo "$1: $n requests with status 500"' >> strict.sh
echo "2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0" > server.log
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
bash strict.sh server.log
echo "status: $?"
bash strict.sh access.log
echo "status: $?"
bash strict.sh 2> /dev/null || echo "strict.sh stopped: no \$1"
```
```output
server.log: 1 requests with status 500
status: 0
status: 1
strict.sh stopped: no $1
```

The assignment took grep's status, 1, so `set -e` stopped strict.sh
before its `echo`. Without an argument, `set -u` stopped it at `$1`:
check `$#` before reading `$1`, as
[`exercise/healthcheck.sh`](exercise/healthcheck.sh) does. ShellCheck,
which `learn check` runs, catches misspelt names
better. ([bashpitfalls#nounset])

### What `set -e` misses

`set -e` doesn't stop the script in these cases, one per line of
misses.sh's output:

- A failing command tested by `if`, `&&` or `||`: there, failing is an
  answer. ([tlcl#set-e-set-u-and-set-o-pipefail]) ([bashpitfalls#errexit])
- Any command inside a function that is tested that
  way. ([bashpitfalls#errexit])
- `cmd` in `echo "$(cmd)"`: `set -e` sees only echo's status.
- `cmd` in `local n=$(cmd)`: `local` succeeds whatever `cmd` did, so write
  `local n` and `n=$(cmd)` as two
  commands. ([bashpitfalls#local_var.3D.24.28cmd.29])
- A failure before a pipeline's last command: the pipeline's status is its
  last command's. ([tlcl#set-e-set-u-and-set-o-pipefail]) ([bashpitfalls#pipefail])

```bash run
echo "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512" > access.log
echo 'set -e' > misses.sh
echo 'grep -q " 500 " access.log || echo "grep failed, and set -e went on"' >> misses.sh
echo 'check() { grep -q " 500 " missing.log; echo "check: went on after grep failed"; }' >> misses.sh
echo 'check 2> /dev/null || echo "never printed"' >> misses.sh
echo 'echo "500 requests: $(grep -c " 500 " access.log)"' >> misses.sh
echo 'count_500() { local n=$(grep -c " 500 " access.log); echo "count_500: $n, went on"; }' >> misses.sh
echo 'count_500' >> misses.sh
echo 'cut -d " " -f 2 missing.log 2> /dev/null | sort' >> misses.sh
echo 'echo "the failed pipeline was missed too"' >> misses.sh
bash misses.sh
echo "misses.sh: status $?"
```
```output
grep failed, and set -e went on
check: went on after grep failed
500 requests: 0
count_500: 0, went on
the failed pipeline was missed too
misses.sh: status 0
```

### `pipefail`

With `set -o pipefail`, a pipeline fails when any of its commands
fails. ([bashpitfalls#pipefail]) `set -euo pipefail` adds it to `-e` and
`-u`, so a failure anywhere in a pipeline stops the script:

```bash run
echo 'set -eu' > loose.sh
echo 'ips=$(cut -d " " -f 2 "$1" | sort)' >> loose.sh
echo 'echo "clients: [$ips]"' >> loose.sh
echo 'set -euo pipefail' > strict.sh
echo 'ips=$(cut -d " " -f 2 "$1" | sort)' >> strict.sh
echo 'echo "clients: [$ips]"' >> strict.sh
bash loose.sh missing.log 2> /dev/null
echo "loose.sh: status $?"
bash strict.sh missing.log 2> /dev/null
echo "strict.sh: status $?"
```
```output
clients: []
loose.sh: status 0
strict.sh: status 1
```

The catch: a command can stop reading early, as `grep -q` does at its
first match, and the command writing to it can then fail though nothing
went wrong. Pipefail is safe only when every command after the first reads all
its input. ([bashpitfalls#pipefail]) `head` stops early too: `yes` prints
`y` lines forever, and once `head` has two, the pipeline fails:

```bash run
echo 'set -o pipefail' > early.sh
echo 'yes | head -n 2' >> early.sh
bash early.sh || echo "early.sh failed"
```
```output
y
y
early.sh failed
```

That's why c3 and logkit's `top_clients` keep their first lines with
`sed -n`, not `head`.

Test for the failures you expect in the script's own code instead of
leaving them to `set -e`, and turn pipefail on only around pipelines
where it is safe. ([tlcl#set-e-set-u-and-set-o-pipefail]) ([bashpitfalls#pipefail])
This module turns them on for whole scripts, to practise them; logkit
still checks for a missing file, and its pipelines read to the end.

<!-- challenge id=c3 objective=4 -->
> **Challenge c3:** Open [`challenges/c3.sh`](challenges/c3.sh) and make it
> print LOGFILE's busiest client, as
> `access.log: busiest client 203.0.113.5`, with one pipeline in `$( )`
> under `set -euo pipefail`. For a missing
> LOGFILE, it prints nothing to stdout and exits with cut's status, 1: it
> leaves out a check of LOGFILE to show `set -e` at work, though a real
> tool checks too, as [`exercise/logkit.sh`](exercise/logkit.sh) does.
> Check it with `learn check c3`.

## What's next

- **Exercise:** write the functions in
  [`exercise/loglib.sh`](exercise/loglib.sh), then
  [`exercise/logkit.sh`](exercise/logkit.sh), and run `learn check`.
  [`exercise/notfound.sh`](exercise/notfound.sh),
  [`exercise/count.sh`](exercise/count.sh),
  [`exercise/countall.sh`](exercise/countall.sh),
  [`exercise/healthcheck.sh`](exercise/healthcheck.sh),
  [`exercise/summary.sh`](exercise/summary.sh),
  [`exercise/top.sh`](exercise/top.sh),
  [`exercise/suspicious.sh`](exercise/suspicious.sh),
  [`exercise/anonymize.sh`](exercise/anonymize.sh),
  [`exercise/bytes.sh`](exercise/bytes.sh) and
  [`exercise/scan.sh`](exercise/scan.sh) are the finished tools from
  modules 1 to 10; leave them unchanged.
- **Quiz:** run `learn quiz`.
- **Recap:** read [`recap.md`](recap.md).

[bashguide-compound#Functions-1]: https://mywiki.wooledge.org/BashGuide/CompoundCommands#Functions-1 "BashGuide, Compound Commands: Functions"
[tlcl#shell-functions]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=426 "The Linux Command Line, 26 Top-Down Design: Shell Functions"
[tlcl#local-variables]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=429 "The Linux Command Line, 26 Top-Down Design: Local Variables"
[tlcl#using-positional-parameters-with-shell-functions]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=504 "The Linux Command Line, 32 Positional Parameters: Accessing the Command Line: Using Positional Parameters with Shell Functions"
[bashguide-sourcing#Sourcing]: https://mywiki.wooledge.org/BashGuide/Sourcing#Sourcing "BashGuide, Sourcing"
[tlcl#set-e-set-u-and-set-o-pipefail]: https://downloads.sourceforge.net/project/linuxcommand/TLCL/25.12/TLCL-25.12A.pdf#page=483 "The Linux Command Line, 30 Troubleshooting: Defensive Programming: set -e, set -u, and set -o pipefail"
[bashpitfalls#errexit]: https://mywiki.wooledge.org/BashPitfalls#errexit "Bash Pitfalls, 60.1. errexit"
[bashpitfalls#pipefail]: https://mywiki.wooledge.org/BashPitfalls#pipefail "Bash Pitfalls, 60.2. pipefail"
[bashpitfalls#nounset]: https://mywiki.wooledge.org/BashPitfalls#nounset "Bash Pitfalls, 60.3. nounset"
[bashpitfalls#local_var.3D.24.28cmd.29]: https://mywiki.wooledge.org/BashPitfalls#local_var.3D.24.28cmd.29 "Bash Pitfalls, 27. local var=$(cmd)"
