# Recap: Finding Files with find and xargs

- `find logs` lists `logs` and everything below it, unsorted.
  (objective 1)
- `-type f` keeps files, `-type d` folders. `-name '*.log'` matches the
  name, not the path; quote the pattern, or bash expands it first.
  (objective 1)
- `-size +1k` means bigger than one kilobyte. `c` counts bytes; no letter
  means 512-byte blocks. `-empty` matches empty files. (objective 1)
- Tests in a row must all be true; `-o` is or, `!` is not. `-and` binds
  tighter than `-o`: group with `\( ... \)`. (objective 2)
- `-exec cmd {} \;` runs `cmd` once per file, `-exec cmd {} +` once for
  all. An action turns off the default `-print`. (objective 3)
- Pass `sh -c` the name after the script, as `"$1"`, never as `{}`
  inside it. (objective 3)
- `xargs` splits at whitespace and trips on quotes.
  `find ... -print0 | xargs -0 cmd` keeps every name whole. (objective 4)
