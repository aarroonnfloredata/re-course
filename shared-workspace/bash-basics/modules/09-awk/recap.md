# Recap: Fields and Totals with awk

- `awk 'pattern { action }'` runs the action on lines the pattern
  matches. No pattern: every line; no action: print the line. Use single
  quotes. (objective 1)
- Fields `$1`, `$2`, … are split at runs of spaces and tabs. `$0` is the
  line, `$NF` the last field; `$NF-1` is that field minus 1. (objective 1)
- `print $2, $4` puts a space between; `$2 $4` glues them. `+` only
  adds. (objective 1)
- `$5 >= 400` compares numbers as numbers; `&&` joins comparisons:
  `$3 == "POST" && $5 == 401`. (objective 2)
- `/regexp/` searches the whole line, `$4 ~ /\.php$/` one field.
  (objective 2)
- `{ total += $6 } END { print total + 0 }` adds up, then prints once.
  Variables take no `$`. `+ 0` prints 0 when the action never ran.
  (objective 3)
- Every pattern is tried on every line, so one program keeps several
  totals. (objective 3)
