# Recap: Variables, Arguments and Command Substitution

- Assign with `name=value`: no spaces around `=` and no `$` in front.
  `name = value` runs `name` as a command. (objective 1)
- `$name` expands to the value. A variable that was never assigned expands
  to nothing, not an error. (objective 1)
- Write `${name}` when a letter, digit or `_` follows: `$name_old` is the
  variable `name_old`. (objective 1)
- In a command's arguments, quote expansions: `"$logfile"`. (objective 1)
- `$1`, `$2`, … hold a script's arguments and `${10}` the tenth; a missing
  one expands to nothing. `$#` counts them, without the script's name.
  (objective 2)
- `count=$(grep -c " 404 " access.log)` stores a command's output, without
  the newline at its end. The command can be a pipeline. (objective 3)
- After `=`, an expansion needs no quotes; the whole value is assigned.
  (objective 3)
