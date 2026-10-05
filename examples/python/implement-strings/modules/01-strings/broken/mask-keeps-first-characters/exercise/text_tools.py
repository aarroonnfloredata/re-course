# Broken variant: mask() keeps the first `keep` characters instead of the last.
"""Text tools: three small functions for tidying up text.

Write each function so that `learn check` passes. Each one needs only what the
lesson covers: indexing, slicing, `+`, `*`, loops and string methods.
"""


def initials(name):
    """Return the initials of `name`.

    Take the first letter of each word, in uppercase, followed by a dot.
    Words are separated by any amount of whitespace. An empty name gives "".

    Examples:
        initials("ada lovelace")          returns "A.L."
        initials("Grace Brewster Hopper") returns "G.B.H."
    """
    result = ""
    for word in name.split():
        result += word[0].upper() + "."
    return result


def slugify(title):
    """Turn `title` into a URL-friendly "slug".

    Lowercase the title and treat every character that is not a letter or a
    digit as a space. Then join the remaining words with single hyphens.

    Examples:
        slugify("Hello, World!") returns "hello-world"
        slugify("Python 3.14")   returns "python-3-14"
    """
    spaced = ""
    for char in title.lower():
        if char.isalnum():
            spaced += char
        else:
            spaced += " "
    return "-".join(spaced.split())


def mask(text, keep=4):
    """Hide all but the last `keep` characters of `text` behind "*".

    If `text` has `keep` characters or fewer, return it unchanged. `keep` is
    always at least 1.

    Examples:
        mask("1234567890")         returns "******7890"
        mask("1234567890", keep=2) returns "********90"
        mask("123")                returns "123"
    """
    hidden = len(text) - keep
    if hidden <= 0:
        return text
    return "*" * hidden + text[:keep]
