# Recap: Cutting, Sorting and Counting

- `cut -d ' ' -f 2` prints field 2 of each line; `-f 4,5` and `-f 4-6`
  print several, in the line's order. Without `-d`, `cut` splits at tabs.
  (objective 1)
- Each space separates fields, so two in a row hold an empty one.
  `-c 1-10` picks characters 1 to 10. (objective 1)
- `sort` compares lines as text (`1024` before `64`); `-n` compares
  numbers; `-r` reverses either order. (objective 2)
- `uniq` drops only neighbouring repeats: sort first.
  `sort | uniq -c` counts each line. (objective 3)
- `uniq -c` pads counts with spaces on the left. Read them with
  `while read -r count value`, not `cut`. (objective 4)
- `sort -nr` puts the biggest count first; `head -n N` keeps only the
  first N lines it gets. (objective 4)
- A `while read` loop at the end of a pipe may print, but variables it
  sets are lost. (objective 4)
