---
id: pystdtypes
title: "The Python Standard Library: Built-in Types"
url: https://docs.python.org/3/library/stdtypes.html
version: "3.14"
retrieved: 2026-10-04
license: >-
  © Copyright 2001 Python Software Foundation. Licensed under the Python
  Software Foundation License Version 2. Code examples are additionally
  licensed under the Zero Clause BSD License.
excerpt: >-
  Introduction of "Text Sequence Type — str"; introduction of "String Methods"
  and the six methods the golden module uses. Omissions are marked […].
---

## Text Sequence Type — str {#textseq}

Textual data in Python is handled with `str` objects, or *strings*. Strings
are immutable sequences of Unicode code points. String literals are written in
a variety of ways:

- Single quotes: `'allows embedded "double" quotes'`
- Double quotes: `"allows embedded 'single' quotes"`
- Triple quoted: `'''Three single quotes'''`, `"""Three double quotes"""`

Triple quoted strings may span multiple lines - all associated whitespace will
be included in the string literal.

String literals that are part of a single expression and have only whitespace
between them will be implicitly converted to a single string literal. That is,
`("spam " "eggs") == "spam eggs"`.

See String and Bytes literals for more about the various forms of string
literal, including supported escape sequences, and the `r` ("raw") prefix that
disables most escape sequence processing.

Strings may also be created from other objects using the `str` constructor.

Since there is no separate "character" type, indexing a string produces
strings of length 1. That is, for a non-empty string *s*, `s[0] == s[0:1]`.

There is also no mutable string type, but `str.join()` or `io.StringIO` can be
used to efficiently construct strings from multiple fragments.

[…]

### String Methods {#string-methods}

Strings implement all of the common sequence operations, along with the
additional methods described below.

Strings also support two styles of string formatting, one providing a large
degree of flexibility and customization (see `str.format()`, Format string
syntax and Custom string formatting) and the other based on C `printf` style
formatting that handles a narrower range of types and is slightly harder to use
correctly, but is often faster for the cases it can handle (printf-style String
Formatting).

The Text Processing Services section of the standard library covers a number
of other modules that provide various text related utilities (including
regular expression support in the `re` module).

[…]

#### str.isalnum() {#str.isalnum}

Return `True` if all characters in the string are alphanumeric and there is at
least one character, `False` otherwise. A character `c` is alphanumeric if one
of the following returns `True`: `c.isalpha()`, `c.isdecimal()`,
`c.isdigit()`, or `c.isnumeric()`. For example:

```pycon
>>> 'abc123'.isalnum()
True
>>> 'abc123!@#'.isalnum()
False
>>> ''.isalnum()
False
>>> ' '.isalnum()
False
```

[…]

#### str.join(iterable, /) {#str.join}

Return a string which is the concatenation of the strings in *iterable*. A
`TypeError` will be raised if there are any non-string values in *iterable*,
including `bytes` objects. The separator between elements is the string
providing this method. For example:

```pycon
>>> ', '.join(['spam', 'spam', 'spam'])
'spam, spam, spam'
>>> '-'.join('Python')
'P-y-t-h-o-n'
```

See also `split()`.

[…]

#### str.lower() {#str.lower}

Return a copy of the string with all the cased characters converted to
lowercase. For example:

```pycon
>>> 'Lower Method Example'.lower()
'lower method example'
```

The lowercasing algorithm used is described in section 3.13 'Default Case
Folding' of the Unicode Standard.

[…]

#### str.split(sep=None, maxsplit=-1) {#str.split}

Return a list of the words in the string, using *sep* as the delimiter string.
If *maxsplit* is given, at most *maxsplit* splits are done (thus, the list will
have at most `maxsplit+1` elements). If *maxsplit* is not specified or `-1`,
then there is no limit on the number of splits (all possible splits are made).

If *sep* is given, consecutive delimiters are not grouped together and are
deemed to delimit empty strings (for example, `'1,,2'.split(',')` returns
`['1', '', '2']`). The *sep* argument may consist of multiple characters as a
single delimiter (to split with multiple delimiters, use `re.split()`).
Splitting an empty string with a specified separator returns `['']`.

For example:

```pycon
>>> '1,2,3'.split(',')
['1', '2', '3']
>>> '1,2,3'.split(',', maxsplit=1)
['1', '2,3']
>>> '1,2,,3,'.split(',')
['1', '2', '', '3', '']
>>> '1<>2<>3<4'.split('<>')
['1', '2', '3<4']
```

If *sep* is not specified or is `None`, a different splitting algorithm is
applied: runs of consecutive whitespace are regarded as a single separator,
and the result will contain no empty strings at the start or end if the string
has leading or trailing whitespace. Consequently, splitting an empty string or
a string consisting of just whitespace with a `None` separator returns `[]`.

For example:

```pycon
>>> '1 2 3'.split()
['1', '2', '3']
>>> '1 2 3'.split(maxsplit=1)
['1', '2 3']
>>> '   1   2   3   '.split()
['1', '2', '3']
```

If *sep* is not specified or is `None` and *maxsplit* is `0`, only leading
runs of consecutive whitespace are considered.

For example:

```pycon
>>> "".split(None, 0)
[]
>>> "   ".split(None, 0)
[]
>>> "   foo   ".split(maxsplit=0)
['foo   ']
```

See also `join()` and `rsplit()`.

[…]

#### str.strip(chars=None, /) {#str.strip}

Return a copy of the string with the leading and trailing characters removed.
The *chars* argument is a string specifying the set of characters to be
removed. If omitted or `None`, the *chars* argument defaults to removing
whitespace. The *chars* argument is not a prefix or suffix; rather, all
combinations of its values are stripped.

Whitespace characters are defined by `str.isspace()`.

For example:

```pycon
>>> '   spacious   '.strip()
'spacious'
>>> 'www.example.com'.strip('cmowz.')
'example'
```

The outermost leading and trailing *chars* argument values are stripped from
the string. Characters are removed from the leading end until reaching a
string character that is not contained in the set of characters in *chars*. A
similar action takes place on the trailing end.

For example:

```pycon
>>> comment_string = '#....... Section 3.2.1 Issue #32 .......'
>>> comment_string.strip('.#! ')
'Section 3.2.1 Issue #32'
```

See also `rstrip()`.

[…]

#### str.upper() {#str.upper}

Return a copy of the string with all the cased characters converted to
uppercase. Note that `s.upper().isupper()` might be `False` if `s` contains
uncased characters or if the Unicode category of the resulting character(s) is
not "Lu" (Letter, uppercase), but e.g. "Lt" (Letter, titlecase).

The uppercasing algorithm used is described in section 3.13 'Default Case
Folding' of the Unicode Standard.

[…]
