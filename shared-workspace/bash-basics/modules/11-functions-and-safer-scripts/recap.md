# Recap: Functions and Safer Scripts

- `name() { commands; }` defines a function, before any call. Inside,
  `$1`, … and `$#` are its own. (objective 1)
- Variables are global unless declared `local` before first being set,
  loop variables too. (objective 1)
- A function gives back output, for `$( )`, and a status: `return N` or
  its last command's. `exit` ends the script. (objective 2)
- `source file` runs a file in the current shell, keeping its functions.
  Load a library with `source "$(dirname "$0")/lib.sh"`. (objective 3)
- `set -e` stops at a failing command, even grep finding nothing; `set -u`
  at an unset variable; `pipefail` fails a pipeline if any command fails.
  (objective 4)
- `set -e` misses commands tested by `if`, `&&`, `||` (functions
  included), `echo "$(cmd)"`, `local n=$(cmd)` and failures mid-pipeline.
  (objective 4)
- Test for expected failures yourself, not via `set -e`; use pipefail
  only where later commands read everything (`sed -n`, not `head`).
  (objective 4)
