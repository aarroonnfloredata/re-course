#!/usr/bin/env bash
# Broken variant: count_lines() counts words instead of lines.
# text.sh: two small text functions. Use them with `source exercise/text.sh`.
#
# Write each function so that `learn check` passes.

# shout TEXT: print TEXT followed by "!", keeping its spaces as they are.
#
# Examples:
#   shout hello          prints "hello!"
#   shout "good  day"    prints "good  day!"
shout() {
    echo "$1!"
}

# count_lines: print how many lines it reads from its input, as a bare
# number.
#
# Examples:
#   printf 'a\nb\n' | count_lines   prints 2
#   count_lines < /dev/null          prints 0
count_lines() {
    wc -w | tr -d ' '
}
