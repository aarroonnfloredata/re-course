#!/usr/bin/env bash
# Challenge c2 – see "Functions" in lesson.md.

# twice WORD: print WORD twice, with a space between.
#
# Examples:
#   twice hi    prints "hi hi"
#   twice 42    prints "42 42"
twice() {
    echo "$1 $1"
}
