---
name: lang-bash
description: "How to write bash course material for re-course - starter scripts and functions, challenge and exercise tests (pytest running bash), solutions, broken variants, runnable lesson examples and predict-output quiz code. Use when writing or fixing any of these for a module with `language: bash`."
---

# Bash course material

This skill covers only what is specific to bash. The rules themselves are
in the spec; read these first:

- `spec/README.md` – layouts, `module.yaml`, objectives
- `spec/exercises.md` – starter files, tests, failure messages, solutions,
  broken variants
- `spec/exercise-types/<type>.md` – the validation rules for the module's
  exercise type
- `spec/content.md` – runnable examples and quiz (for lesson and quiz code)

Reference files:

- `examples/python/implement-strings/modules/01-strings/`: the golden
  module. Its lesson, quiz and recap show what good looks like.
- `runtime/tests/fixtures/bash-course/modules/01-greetings/`: a bash test
  fixture. Its starter files, tests, solution and broken variants show the
  bash form. It is not a teaching example: its lesson is padding.

## Bash version and tools

Courses target bash 3.2, the version macOS ships. Learners use the tools on
their own machine: BSD versions on macOS, GNU versions on Linux.

**Not in bash 3.2.** Don't use these anywhere:

- `declare -A` (associative arrays): use two plain arrays, or a
  `while read` loop over lines.
- `mapfile`, `readarray`: use `while IFS= read -r line; do ...; done < file`.
- `${var,,}`, `${var^^}`: use `tr '[:upper:]' '[:lower:]'`.
- `**` (`shopt -s globstar`): use `find`.
- `{1..10..2}`, `{01..10}`: use `seq`.
- `${array[-1]}`: use `${array[${#array[@]}-1]}`.
- `&>>` and the `|&` pipe: use `>> file 2>&1` and `2>&1 |`.
- `;&` and `;;&` in `case`: write separate patterns.
- `declare -n`, `declare -l`, `coproc`, `$BASHPID`, `${var@Q}`: leave out.

**Differences between macOS and Linux tools.** Use only options both
versions have, and only output both versions print the same way:

- `sed -i`: BSD needs `-i ''`, GNU doesn't. Write to a new file, then `mv`.
- `\+` and `\?` in `sed` or `grep` patterns, and `grep -P`: GNU only. Use
  `sed -E` and `grep -E`.
- `wc -l` and `wc -w`: macOS pads the number with spaces. Use
  `wc -l < file | tr -d ' '`.
- `uniq -c`: the padding width differs. Use `uniq -c | awk '{print $1, $2}'`.
- `sort` on mixed case or punctuation: the order depends on the locale. Use
  data in one case, or teach `LC_ALL=C sort` explicitly.
- `xargs` with empty input: GNU runs the command once anyway, BSD doesn't.
  Make sure the input isn't empty.
- `date -d`, `stat`, `find -printf`, `head -n -N`, `tac`, `readlink -f`,
  `md5sum`: GNU only or different on macOS. Leave them out.
- Other tools' error messages and exit statuses differ (`ls missing` exits
  with 1 on macOS and 2 on Linux). Print your own messages with `echo`.
- `awk`: macOS has the original awk. Use only POSIX features (no `gensub`,
  `asort`, ...).

**Before the first exercise.** Make sure the course tells the learner to
run examples in bash (their terminal may start another shell, such as zsh
on macOS), and what exit status 0 means: starter files state exit statuses
from the first module on.

## Starter files

Every `.sh` file starts with `#!/usr/bin/env bash`. Learners and tests run
scripts as `bash <file>`, so files don't need to be executable.

### Scripts

A script is one unit. Its header comment documents everything the tests
check: arguments, what it prints, what goes to stderr, exit statuses, files
it reads and writes, and examples. Then the stub, exactly:

```bash
#!/usr/bin/env bash
# greet.sh: greet a guest and add them to the guest list.
#
# Usage: bash exercise/greet.sh NAME
#
# Print "Hello, NAME!", add NAME as a new line at the end of guests.txt in
# the current folder (creating the file if needed) and exit with status 0.
#
# Without a NAME, print "usage: greet.sh NAME" to stderr, leave guests.txt
# alone and exit with status 2.
#
# Examples:
#   bash exercise/greet.sh Ada   prints "Hello, Ada!" and adds Ada to guests.txt
#   bash exercise/greet.sh       prints "usage: greet.sh NAME" to stderr, exits with 2
#
# Write it so that `learn check` passes.

# TODO: write greet.sh
echo "greet.sh is not written yet." >&2
exit 1
```

### Functions

A function file holds only functions and comments: tests load it with
`source`, so any other command would run then. Each function is a unit,
documented in the comment above it:

```bash
# shout TEXT: print TEXT followed by "!", keeping its spaces as they are.
#
# Examples:
#   shout hello          prints "hello!"
#   shout "good  day"    prints "good  day!"
shout() {
    # TODO: write shout()
    echo "shout() is not written yet." >&2
    return 1
}
```

- Write functions as `name() {`, with the closing `}` alone at the start of
  a line. No `function` keyword: the validator finds units by this form.
- The stub is exactly the `# TODO` line, the `echo "<unit> is not written
  yet." >&2` line and `exit 1` (script) or `return 1` (function). `<unit>` is
  the file name for a script and `name()` for a function. The test helpers
  turn that line into the failure message.
- Documentation states exact text for everything printed, errors included:
  tests compare whole lines.
- Write examples as `... prints ...` lines.
- A challenge is `challenges/<id>.sh`: one script or one function, starting
  with `# Challenge c1 – see "<section>" in lesson.md.`
- Stubs give no ShellCheck advice. A challenge about a mistake ShellCheck
  reports (e.g. a missing quote) may show it.

## Tests

Tests are pytest files that run the learner's code with bash.

### Files

```
tests/
├── conftest.py          # copy from the bash fixture, unchanged
├── helpers.py           # copy from the bash fixture, unchanged
├── test_challenges.py   # one test per challenge: test_<id>_<what>
└── test_exercise.py     # the exercise tests
```

`conftest.py` registers the `objective` marker. `helpers.py` runs each
script or function in a new empty folder and provides:

- `run_script(path, *args, stdin="", files=None)` – runs `bash <path>
  <args>`. `path` is relative to the module, e.g. `"exercise/greet.sh"`.
- `call(path, function, *args, stdin="", files=None)` – loads the file with
  `source`, then calls the function. A file that can't be loaded, or has no
  such function, becomes a failure with a message.
- Both take `files`, the folder's files before the run (`{name: text}`), and
  return a `Run` with `stdout`, `stderr`, `status` and `files` (the folder's
  files after the run).
- `check(run, stdout=None, status=0, stderr=None, hint=None)` – fails with
  the spec's message format unless the run printed `stdout` and `stderr`
  (each only if given) and exited with `status`.
- `check_file(run, name, expected, hint=None)` – fails unless the run left
  file `name` holding `expected`.

Output is compared line by line: a missing final newline doesn't count;
spaces do.

### Writing a test

```python
import pytest

from helpers import call, check, check_file, run_script

GREET = "exercise/greet.sh"
TEXT = "exercise/text.sh"


@pytest.mark.objective(1)
@pytest.mark.parametrize("name", ["Ada", "Grace Hopper"])
def test_greet(name):
    check(run_script(GREET, name), stdout=f"Hello, {name}!")


@pytest.mark.objective(3)
def test_greet_adds_the_guest():
    run = run_script(GREET, "Grace", files={"guests.txt": "Ada\n"})
    check(run, stdout="Hello, Grace!")
    check_file(run, "guests.txt", "Ada\nGrace\n", hint="> replaces a file; >> adds to it.")


@pytest.mark.objective(2)
def test_count_lines():
    check(call(TEXT, "count_lines", stdin="one two\nthree\n"), stdout="2")
```

- Every test has `@pytest.mark.objective(...)` with the objective number(s)
  it checks.
- Every result goes through `check(...)` or `check_file(...)`. Don't write
  bare `assert`: its output is not a plain-language message.
- `check` always checks the exit status, 0 by default. Pass `status=` when
  the documentation says the code fails.
- Use `parametrize` for cases of the same behaviour; each case is reported
  on its own.
- An optional `hint=` adds one `Hint:` line to the failure.
- Give input files through `files=` and input through `stdin=`. Code under
  test reads and writes only in its own folder: no absolute paths, `$HOME`,
  `/tmp`, network, current time or random values.
- Aim at bash mistakes: unquoted variables (test with double spaces,
  leading spaces and empty strings), `>` instead of `>>`, `$1` and `$2`
  swapped, a missing or wrong exit status, output on stdout that belongs on
  stderr.

### Challenge checks

One test function per challenge, named `test_<id>_<what>`, in
`test_challenges.py`. A few checks in a row are fine; the first failure
stops the test.

```python
@pytest.mark.objective(1)
def test_c1_counts_arguments():
    check(run_script("challenges/c1.sh", "a", "b", "c"), stdout="3")
    check(run_script("challenges/c1.sh"), stdout="0")
```

## Solutions and broken variants

- A solution file is the starter file with each stub (the `# TODO` line, the
  `echo` line and the `exit 1` or `return 1`) replaced by the code. Comments
  stay exactly the same.
- Solutions use only what the lesson (or an earlier module) taught, and
  give no ShellCheck advice; the validator checks this. Run
  `uv run shellcheck --shell=bash solution/<path>` in the course folder.
- A broken variant is a full copy of the solution file with one plausible
  mistake. Its `Broken variant:` comment goes on line 2, after the `#!`
  line:

  ```bash
  #!/usr/bin/env bash
  # Broken variant: shout() leaves $1 unquoted, so runs of spaces become one.
  ```

## Runnable examples and quiz code

Lesson `bash run` blocks and quiz `code` run on their own with `bash -c`,
in an empty temporary folder, with no input.

- Each block defines everything it uses; nothing carries over from earlier
  blocks. Create the files it needs inside the block:
  `printf 'apple\nbanana\n' > fruit.txt`.
- Set arguments with `set --`: `set -- "a b" c` makes `$1` `a b` and `$#`
  `2`. In `bash -c`, `$0` is `bash`.
- The block must exit with status 0, and its last command decides. `grep`
  without a match, `false` and a failed `[ ... ]` exit with 1. To show a
  failure, print its status: `grep y notes.txt; echo "status: $?"`.
- The output block is stdout only. Text sent to stderr doesn't appear in it.
  Show your own messages, not other tools' error messages, which differ
  between macOS and Linux.
- Only print output that is the same on every run and machine: no times,
  random values, `ls -l` details or paths outside the block's folder.
- Commands the learner runs on their own files (`bash exercise/greet.sh
  Ada`) can't run in the validator. Write them inline, or in a `text` block.

## Checking your work

- Run a snippet with `bash -c '...'`, or a documented example against your
  solution with `bash <path to solution file> ...`. Do it in a new folder
  from `mktemp -d`, so files the code writes stay out of the workspace.
- `uv run learn check` in the course folder shows the learner's view: with
  the starter files, every test fails, each with a plain message.
- The validator (`forge/validate/`) runs the solution and broken-variant
  setups from `spec/exercise-types/<type>.md`, ShellCheck on `solution/`,
  the runnable examples and the `predict-output` answers.
