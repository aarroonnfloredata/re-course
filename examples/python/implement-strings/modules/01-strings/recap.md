# Recap: Strings

- `s[0]` is the first character and `s[-1]` the last. An index past the end
  is an error. (objective 1)
- `s[start:end]` includes `start` and excludes `end`. A missing start means
  "from the beginning"; a missing end means "to the end". (objective 2)
- Slice bounds past the end are cut down to fit, without an error.
  (objective 2)
- Strings can't be changed. Build a new one with `+`, `*` and slices.
  (objective 3)
- Methods like `upper()` and `strip()` return a new string. Store the result
  or it's lost. (objective 3)
- `split()` splits on any run of whitespace; `split(",")` splits on every
  comma and can return empty strings. (objective 4)
- `"-".join(words)` glues a list of strings together with `-` between them.
  (objective 4)
