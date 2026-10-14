# Broken variant: behaviour: shipping_for() is given the subtotal before the discount.
"""Receipts for a small online shop.

This file grew over two years of new rules. It works, but print_receipt()
has become hard to read and to change.

Your task: refactor it with Extract Method, without changing what it does.

- print_receipt(order) stays, with the same name and parameter, and prints
  exactly what it prints now, for every order.
- No function in this file is longer than 10 lines, not counting docstrings,
  blank lines and comments.
- No function in this file has comments inside it: the names of the
  functions you extract say what the comments say now.

Run `learn check`. The behaviour tests pass from the start and must keep
passing after every step; the structural checks pass once the task is done.
"""


def print_receipt(order):
    """Print the receipt for `order`.

    `order` is a dict with "customer" (a name), "items" (a list of dicts with
    "name", "price" and "qty") and "code" (a discount code, or None).
    """
    subtotal = subtotal_of(order["items"])
    discount = discount_for(order["code"], subtotal)
    shipping = shipping_for(subtotal)
    print_header(order["customer"])
    print_items(order["items"])
    print_totals(subtotal, discount, shipping)


def subtotal_of(items):
    total = 0
    for item in items:
        total += item["price"] * item["qty"]
    return total


def discount_for(code, subtotal):
    if code == "SAVE10" and subtotal >= 40:
        return round(subtotal * 0.10, 2)
    return 0


def shipping_for(amount):
    if amount >= 50:
        return 0
    return 4.95


def print_header(customer):
    print(f"Receipt for {customer}")
    print("-" * 32)


def print_items(items):
    for item in items:
        line_total = item["price"] * item["qty"]
        print(f"{item['qty']:>3} x {item['name']:<18}{line_total:>8.2f}")
    print("-" * 32)


def print_totals(subtotal, discount, shipping):
    print(f"{'Subtotal':<24}{subtotal:>8.2f}")
    if discount:
        print(f"{'Discount (SAVE10)':<24}{-discount:>8.2f}")
    print(f"{'Shipping':<24}{shipping:>8.2f}")
    print(f"{'Total':<24}{subtotal - discount + shipping:>8.2f}")
