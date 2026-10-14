# Recap: Loops, Arithmetic and case

- `for file in *.log; do ...; done` runs the body once per matching name,
  spaces and all. Don't loop over `$(ls)`. (objective 1)
- A glob that matches nothing stays as it is: skip it with
  `[[ -e $file ]] || continue`. For another folder, write `"$dir"/*.log`.
  (objective 1)
- `while read -r a b rest; do ...; done < file` reads a line per pass, a
  field per name; the last name gets the rest. Without `-r`, `read` drops
  backslashes. Name unused fields `_`. (objective 2)
- `total=512+153` is text; `$((512 + 153))` computes. `(( count++ ))` adds
  1, `(( total += bytes ))` adds, `(( a > b ))` compares numbers.
  (objective 3)
- Set counters to 0 just before the `while` loop. Don't pipe into a
  counting loop: its assignments are lost. (objective 3)
- `case` runs only the first pattern that matches: special cases first,
  `*)` last. (objective 4)
