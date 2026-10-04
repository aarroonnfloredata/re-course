# Strings: Indexing, Slicing and Methods

You already use strings for messages and names. This module shows how to take
them apart and tidy them up: pick out single characters, cut out pieces, and
clean text with string methods.

By the end of this module you can:

1. Get single characters from a string with positive and negative indexes
2. Take substrings with slices, including omitted and out-of-range bounds
3. Build new strings instead of changing existing ones, and keep the results
   of string methods
4. Clean, split and join text with `strip()`, `lower()`, `upper()`, `split()`,
   `join()` and `isalnum()`

**How to work through it:** read top to bottom and run the examples yourself.
Each challenge names a file in `challenges/` to edit and the command that
checks it. Some examples use
`try`/`except` to print an error message instead of stopping; you don't need
to write that yourself.

## Indexing

Each character in a string has a position, called its index. The first
character has index 0. ([pytutorial#text])

```python run
word = "Python"
print(word[0])
print(word[5])
```
```output
P
n
```

There is no separate character type: a single character is a string of
length 1. ([pytutorial#text])

Negative indexes count from the right. The last character is `-1`, not `-0`,
because `-0` is the same as `0`. ([pytutorial#text])

```python run
word = "Python"
print(word[-1])
print(word[-2])
```
```output
n
o
```

An index past the end of the string is an error. ([pytutorial#text])

```python run
word = "Python"
try:
    print(word[42])
except IndexError as error:
    print("IndexError:", error)
```
```output
IndexError: string index out of range
```

<!-- challenge id=c1 objective=1 -->
> **Challenge c1:** Open [`challenges/c1.py`](challenges/c1.py) and finish
> `last_char(word)` so it returns the last character of `word`.
> `last_char("Python")` is `"n"`. Check it with `learn check c1`.

## Slicing

A slice takes a piece of a string: `word[start:end]`. The start is included
and the end is excluded, so `word[2:5]` has `5 - 2 = 3`
characters. ([pytutorial#text])

```python run
word = "Python"
print(word[0:2])
print(word[2:5])
```
```output
Py
tho
```

Either bound can be left out. A missing start means "from the beginning"; a
missing end means "to the end". ([pytutorial#text])

```python run
word = "Python"
print(word[:2])
print(word[4:])
print(word[-2:])
```
```output
Py
on
on
```

Because the start is included and the end excluded, `word[:i] + word[i:]` is
always the whole string. ([pytutorial#text])

Slices are forgiving where indexes are not: a bound past the end is cut down
to fit, without an error. ([pytutorial#text])

```python run
word = "Python"
print(word[4:42])
print(word[42:] == "")
```
```output
on
True
```

<!-- challenge id=c2 objective=2 -->
> **Challenge c2:** Open [`challenges/c2.py`](challenges/c2.py) and finish
> `middle(word)` so it returns `word` without its first and last character.
> `middle("Python")` is `"ytho"` and `middle("ab")` is `""`. Check it with
> `learn check c2`.

## Strings can't be changed

Strings are immutable: once created, they can't be changed. Assigning to an
index is an error. ([pytutorial#text])

```python run
word = "Python"
try:
    word[0] = "J"
except TypeError as error:
    print("TypeError:", error)
```
```output
TypeError: 'str' object does not support item assignment
```

To get a different string, build a new one. `+` glues strings together and
`*` repeats them. ([pytutorial#text])

```python run
word = "Python"
print("J" + word[1:])
print(word)
print("ha" * 3)
```
```output
Jython
Python
hahaha
```

String methods follow the same rule: they return a new string and leave the
original alone. ([pystdtypes#string-methods]) If you don't store the result, it
is lost.

```python run
name = "ada"
name.upper()
print(name)
name = name.upper()
print(name)
```
```output
ada
ADA
```

## String methods

Strings have many methods for basic transformations and
searching. ([pytutorial#text]) These are the ones you'll use most for cleaning
up text.

### Changing case

`lower()` and `upper()` return a copy with all letters in lowercase or
uppercase. ([pystdtypes#string-methods])

```python run
print("Hello, World".lower())
print("Hello, World".upper())
```
```output
hello, world
HELLO, WORLD
```

### Removing whitespace

`strip()` returns a copy without whitespace at the start and end. Whitespace
inside the string stays. ([pystdtypes#string-methods])

```python run
print("[" + "   two  words  ".strip() + "]")
```
```output
[two  words]
```

### Splitting and joining

`split()` with no argument splits on any run of whitespace and ignores
whitespace at the start and end, so it never returns empty
strings. ([pystdtypes#string-methods])

```python run
print("  two   words ".split())
```
```output
['two', 'words']
```

With an argument, `split(sep)` splits on every single `sep`. Two separators
next to each other produce an empty string between
them. ([pystdtypes#string-methods])

```python run
print("a,b,,c".split(","))
print("two  words".split(" "))
```
```output
['a', 'b', '', 'c']
['two', '', 'words']
```

`join()` does the opposite of `split()`: it glues a list of strings together,
putting the string it's called on between them. ([pystdtypes#string-methods])

```python run
words = ["two", "words"]
print("-".join(words))
print(" ".join("  two   words ".split()))
```
```output
two-words
two words
```

The second line is a common pattern: split on whitespace, then join with
single spaces, to tidy up spacing.

<!-- challenge id=c3 objective=4 -->
> **Challenge c3:** Open [`challenges/c3.py`](challenges/c3.py) and finish
> `count_words(text)` so it returns the number of words in `text`. Words are
> separated by any amount of whitespace. `count_words("  lots   of   space ")`
> is `3`. Check it with `learn check c3`.

### Checking characters

`isalnum()` returns `True` if every character is a letter or a digit and there
is at least one character. ([pystdtypes#string-methods])

```python run
print("abc123".isalnum())
print("a-b".isalnum())
print("".isalnum())
```
```output
True
False
False
```

Checking one character at a time lets you filter text:

```python run
kept = ""
for char in "R2-D2!":
    if char.isalnum():
        kept += char
print(kept)
```
```output
R2D2
```

## What's next

- **Exercise:** finish the three functions in
  [`exercise/text_tools.py`](exercise/text_tools.py), then run `learn check`.
- **Quiz:** run `learn quiz`.
- **Recap:** read [`recap.md`](recap.md).

[pytutorial#text]: https://docs.python.org/3/tutorial/introduction.html#text "The Python Tutorial, 3.1.2 Text"
[pystdtypes#string-methods]: https://docs.python.org/3/library/stdtypes.html#string-methods "The Python Standard Library, String Methods"
