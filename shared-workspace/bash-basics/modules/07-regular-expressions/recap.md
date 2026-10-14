# Recap: Regular Expressions with grep

- Single quotes pass `\.` and `$` to grep as typed. (objective 1)
- `.` is any one character, `\.` a real dot. `^` anchors to the start of a
  line, `$` to its end. (objective 1)
- `[45]` is one listed character, `[0-9]` one from a range, `[^2]` any but
  2, `[[:digit:]]` one digit. (objective 1)
- `?` makes the element before it optional; `*` repeats it zero or more
  times, `+` one or more, `{n,m}` n to m times. Any text is `.*`.
  (objective 2)
- Unescaped, `?`, `+`, `{ }`, `|` and `( )` are plain text without `-E`.
  (objective 2)
- Unanchored, `[0-9]{3}` also matches inside longer numbers.
  (objective 2)
- `|` splits the whole pattern; parentheses limit it:
  `' (GET|HEAD) /x'`. A quantifier after a group repeats it.
  (objective 3)
- `-v` prints non-matching lines; `-c` counts the lines grep would print,
  with `-v` the non-matching ones; `-i` ignores case. (objective 4)
