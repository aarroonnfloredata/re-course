# Recap: Editing Text with sed

- `sed 's/old/new/' file` works on every line and prints the result; the
  file stays as it was. (objective 1)
- `s` replaces the first match on each line; `s/old/new/g` replaces every
  match. Only the search part is a regular expression. (objective 1)
- Any character after `s` is the delimiter: `s|/old/|/new/|`. For
  variables, use double quotes: `"s|$old|$new|"`. (objective 1)
- `sed -E` takes groups without backslashes. `\1` to `\9` reuse them;
  `\10` is group 1 then `0`. Text matched outside a group is dropped.
  (objective 2)
- An address picks lines: `/ 404 /`, `1`, `$`, `2,4`. `d` deletes them;
  `sed -n '2,4p'` prints only them. `p` without `-n` prints them twice.
  (objective 3)
- `> file` onto the file sed reads leaves it empty. Write a new file, or a
  temporary one, then `&& mv` it over the original. (objective 4)
