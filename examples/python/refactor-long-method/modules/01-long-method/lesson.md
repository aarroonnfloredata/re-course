# Long Functions and Extract Method

Most code you change was written by someone else, often long ago, and it
works. This module is about making such code easier to read without breaking
it: spotting a function that has grown too long and splitting it into
well-named pieces, one safe step at a time.

By the end of this module you can:

1. Say what refactoring is: changing code's structure so it behaves the same
   as before
2. Recognise a long function as a code smell: a hint that something may be
   wrong, not a bug
3. Apply Extract Method: move part of a long function into a new, well-named
   function and call it
4. Refactor in small steps, running the tests after each one and undoing a
   step that breaks them

**How to work through it:** read top to bottom and run the examples yourself.
Each challenge names a file in `challenges/` and the command that checks it.
Unlike in other modules, the code you start from already works: your job is
to change its shape, not what it does.

## Refactoring

Refactoring transforms source code into a new form that behaves the same as
before but no longer "smells". ([wiki-refactoring#Motivation]) The point is
code that is easier to read and change: large routines become a set of
concise, well-named, single-purpose methods. ([wiki-refactoring#Benefits])

These two functions are written differently, but for every amount they
return the same result, so the second is a refactoring of the first:

```python run
def shipping(amount):
    if amount >= 50:
        return 0
    else:
        return 4.95


def shipping_refactored(amount):
    if amount >= 50:
        return 0
    return 4.95


for amount in [20, 50, 80]:
    print(shipping(amount), shipping_refactored(amount))
```
```output
4.95 4.95
0 0
0 0
```

Fixing a bug or adding a rule is not refactoring: both change what the code
does. Keep them apart, so that when something breaks you know which change
caused it.

## Long functions are a smell

Refactoring usually starts with noticing a code smell, for example a method
that is very long. ([wiki-refactoring#Motivation]) A smell is a suggestion
that something may be wrong, not evidence that there is already a problem.
([wiki-code-smell#Definition]) Smells are usually not bugs: the code works,
but its design may slow down development or raise the risk of bugs later.
([wiki-code-smell#Definition])

A long function is hard to read because you have to keep all of it in your
head at once. In the exercise, comments such as `# totals` split
`print_receipt()` into parts; each part does one job and could be a function
of its own.

## Extract Method

Extract Method turns part of a larger method into a new method, and it works
the same for functions. ([wiki-refactoring#Transformations]) For a long
routine, you extract one or more smaller ones. ([wiki-refactoring#Motivation])

Here a comment explains what a block does:

```python run
def print_total(prices):
    # add up the prices
    total = 0
    for price in prices:
        total += price
    print(f"Total: {total:.2f}")


print_total([2.5, 4.0])
```
```output
Total: 6.50
```

To extract the block: write a new function named after what the block does,
move the block into it, pass in the values it reads, return the value it
produces, and put a call where the block was.

```python run
def print_total(prices):
    print(f"Total: {sum_of(prices):.2f}")


def sum_of(prices):
    total = 0
    for price in prices:
        total += price
    return total


print_total([2.5, 4.0])
```
```output
Total: 6.50
```

The output is the same, and the comment is gone: the function's name says
what it said. Removing comments that a good name makes unnecessary is part of
the payoff. ([wiki-refactoring#Benefits])

<!-- challenge id=c1 objective=3 -->
> **Challenge c1:** Open [`challenges/c1.py`](challenges/c1.py) and extract
> the block under the comment into `average(scores)`, which returns the
> average. `report()` calls it and prints exactly what it printed before.
> Check it with `learn check c1`.

### Values that change

Be careful when the block changes a variable that the rest of the function
still uses. Assigning to a parameter inside the new function doesn't change
the caller's variable:

```python run
def apply_discount(total, code):
    if code == "HALF":
        total = total / 2


def checkout(total, code):
    apply_discount(total, code)
    return total


print(checkout(16, "HALF"))
```
```output
16
```

The discount is lost. The new function must return the new value, and the
caller must store it:

```python run
def apply_discount(total, code):
    if code == "HALF":
        return total / 2
    return total


def checkout(total, code):
    total = apply_discount(total, code)
    return total


print(checkout(16, "HALF"))
```
```output
8.0
```

<!-- challenge id=c2 objective=3 -->
> **Challenge c2:** Open [`challenges/c2.py`](challenges/c2.py) and extract
> the discount block into `apply_discount(total, code)`, which returns the
> new total. `checkout()` returns exactly what it returned before. Check it
> with `learn check c2`.

## Small steps, tests after each

Automatic tests should be in place before you refactor, to check that the
code still behaves as expected. ([wiki-refactoring#Testing]) Refactoring is
then a cycle: make a small change, run the tests, make the next change. If a
test fails, undo the last change and do it a different way. Many small steps
take the program from where it was to where you want it.
([wiki-refactoring#Testing]) This only works if the tests run quickly.
([wiki-refactoring#Testing])

In the exercise, two kinds of tests work together:

- **Behaviour tests** ([`tests/test_behaviour.py`](tests/test_behaviour.py)) record what
  `print_receipt()` prints today, odd cases included: an empty order still
  pays shipping. They pass before you change anything and must keep passing.
- **Structural checks** ([`tests/test_structure.py`](tests/test_structure.py)) fail until the long
  function is gone: no function longer than 10 lines and no comments inside
  functions.

So `learn check` starts with some tests passing. A failing behaviour test
after a step means that step changed what the code does:

```text
Behaviour changed: before the refactoring, print_receipt({...}) printed:
    ...
    Shipping                    4.95
but now it prints:
    ...
    Shipping                    0.00
```

Undo that step, then extract the same part again more carefully.

## What's next

- **Exercise:** refactor `print_receipt()` in
  [`exercise/receipt.py`](exercise/receipt.py) step by step, running
  `learn check` after each step.
- **Quiz:** run `learn quiz`.
- **Recap:** read [`recap.md`](recap.md).

[wiki-refactoring#Motivation]: https://en.wikipedia.org/wiki/Code_refactoring#Motivation "Code refactoring, Motivation"
[wiki-refactoring#Benefits]: https://en.wikipedia.org/wiki/Code_refactoring#Benefits "Code refactoring, Benefits"
[wiki-refactoring#Testing]: https://en.wikipedia.org/wiki/Code_refactoring#Testing "Code refactoring, Testing"
[wiki-refactoring#Transformations]: https://en.wikipedia.org/wiki/Code_refactoring#Transformations "Code refactoring, Transformations"
[wiki-code-smell#Definition]: https://en.wikipedia.org/wiki/Code_smell#Definition "Code smell, Definition"
