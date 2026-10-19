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
    print(f"Receipt for {order['customer']}")
    print("-" * 32)
    # list the items and add up the subtotal
    subtotal = 0
    for item in order["items"]:
        line_total = item["price"] * item["qty"]
        subtotal += line_total
        print(f"{item['qty']:>3} x {item['name']:<18}{line_total:>8.2f}")
    print("-" * 32)
    # discount: SAVE10 takes 10% off orders of 40.00 or more
    discount = 0
    if order["code"] == "SAVE10" and subtotal >= 40:
        discount = round(subtotal * 0.10, 2)
    # shipping is free from 50.00, counted after the discount
    if subtotal - discount >= 50:
        shipping = 0
    else:
        shipping = 4.95
    # totals
    print(f"{'Subtotal':<24}{subtotal:>8.2f}")
    if discount:
        print(f"{'Discount (SAVE10)':<24}{-discount:>8.2f}")
    print(f"{'Shipping':<24}{shipping:>8.2f}")
    print(f"{'Total':<24}{subtotal - discount + shipping:>8.2f}")
