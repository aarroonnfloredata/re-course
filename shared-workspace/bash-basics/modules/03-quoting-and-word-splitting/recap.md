# Recap: Quoting, Word Splitting and Globs

- Bash splits a line into words at whitespace. An unquoted `$name` or
  `$( )` is split again, at spaces, tabs and newlines, and a resulting word
  with `*`, `?` or `[` is expanded as a glob. (objective 1)
- Double-quote every expansion: `"$logfile"` is one argument, even when
  empty. `$` still expands inside double quotes; splitting and globs don't.
  (objective 2)
- Single quotes keep everything as typed: `'$status'` is `$status`. A
  backslash quotes one character: `\$`, `\"`. (objective 3)
- `*` matches any string, `?` one character and `[...]` one of the listed
  characters. A glob must match the whole name; one that matches nothing
  stays as it is. (objective 4)
- Keep the glob outside the quotes: `"access-$month"-*.log`. (objective 4)
- After `shift`, `$#` is one less and `$1` holds what was the second
  argument. `"$@"` passes the remaining arguments on unchanged; `$@`, `$*`
  and `"$*"` don't. (objective 5)
