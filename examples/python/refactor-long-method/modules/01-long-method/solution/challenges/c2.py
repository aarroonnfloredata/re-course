"""Challenge c2 – see "Values that change" in lesson.md.

Move the block under the comment into a new function
apply_discount(total, code) that returns the new total, and call it from
checkout(). checkout() keeps returning exactly what it returns now.
"""


def checkout(prices, code):
    """Return what to pay for `prices` with the discount `code`.

    "HALF" halves the total; "MINUS5" takes 5 off, but never below 0. Any
    other code changes nothing. The result is rounded to 2 decimals.

    checkout([10, 6], "HALF") returns 8.0.
    """
    total = sum(prices)
    total = apply_discount(total, code)
    return round(total, 2)


def apply_discount(total, code):
    if code == "HALF":
        return total / 2
    if code == "MINUS5":
        return max(total - 5, 0)
    return total
