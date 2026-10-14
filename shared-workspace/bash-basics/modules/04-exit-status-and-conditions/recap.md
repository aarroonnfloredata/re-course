# Recap: Exit Status and Conditions

- Exit status 0 means success, anything else failure. It is separate from
  the output: `grep -c` can print `0` and fail. (objective 1)
- `$?` holds the last command's status; save it at once:
  `grep_status=$?`. (objective 1)
- A script exits with its last command's status; `exit 2` ends it at once
  with 2. (objective 1)
- `a && b` runs `b` only when `a` succeeds, `a || b` only when it fails.
  Don't mix them. (objective 2)
- `if cmd; then ...; elif cmd2; then ...; else ...; fi` branches on
  command statuses: `if grep -q " 503 " file; then`. (objective 3)
- `[[ ]]` compares strings with `=` and `!=`, numbers with `-eq`, `-lt`,
  `-gt` (`<` and `>` sort as text), and checks files with `-e`, `-f`, `-d`.
  (objective 4)
- On the right of `=`, an unquoted value is a glob pattern; quote it to
  compare text. (objective 4)
