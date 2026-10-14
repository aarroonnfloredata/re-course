# Recap: Scripts, Pipes and Redirection

- A script is commands in a file, run with `bash request.sh`. A `#`
  starting a word begins a comment. (objective 1)
- `>` sends stdout to a file, emptying it first, even if the command fails.
  `>>` adds to the end. (objective 2)
- `<` fills a command's stdin from a file. (objective 2)
- Error messages go to stderr, so `>` doesn't catch them. `2> file` saves
  them; `2> /dev/null` throws them away. (objective 3)
- Send your own errors to stderr with `echo "..." >&2`. For both streams in
  one file, write `> all.txt 2>&1`, in that order. (objective 3)
- `|` connects one command's stdout to the next command's stdin; errors
  still reach the screen. (objective 4)
- `grep pattern file` prints matching lines, `grep -c` counts them, and
  `head -n N` and `tail -n N` keep the first or last N lines. Quote patterns
  with spaces: `" 404 "`. (objective 4)
