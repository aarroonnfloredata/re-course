---
name: lang-python
description: "How to write Python course material for re-course - starter stubs, challenge and exercise tests (pytest; behaviour tests and structural checks for refactor modules), solutions, broken variants, runnable lesson examples and predict-output quiz code. Use when writing or fixing any of these for a module with `language: python`."
---

# Python course material

This skill covers only what is specific to Python. The rules themselves are
in the spec; read these first:

- `spec/README.md` – layouts, `module.yaml`, objectives
- `spec/exercises.md` – starter files, tests, failure messages, solutions,
  broken variants
- `spec/exercise-types/<type>.md` – the validation rules for the module's
  exercise type
- `spec/content.md` – runnable examples and quiz (for lesson and quiz code)

Reference module: `examples/python/implement-strings/modules/01-strings/`.
When in doubt, do what it does.

## Python version and libraries

- Use the Python version set by the course's `pyproject.toml`
  (`requires-python`); use nothing newer than that version supports.
- Learner code, tests, lesson examples and quiz code may use the standard
  library and the packages in the brief's `dependencies`, nothing else.
  pytest comes with the runtime.

## Starter files

`exercise/` holds one module of functions (e.g. `exercise/text_tools.py`).
Each challenge is `challenges/<id>.py` with one function.

```python
def initials(name):
    """Return the initials of `name`.

    Take the first letter of each word, in uppercase, followed by a dot.
    Words are separated by any amount of whitespace. An empty name gives "".

    Examples:
        initials("ada lovelace")          returns "A.L."
        initials("Grace Brewster Hopper") returns "G.B.H."
    """
    # TODO: write initials()
    raise NotImplementedError
```

- The docstring states the full behaviour, including edge cases. Tests check
  nothing beyond it.
- Write examples as `... returns ...` lines, not `>>>` doctests: nothing runs
  them, and doctest syntax suggests otherwise.
- The stub body is exactly `# TODO: write <name>()` and
  `raise NotImplementedError`. The test helpers turn this into
  "`<name>()` is not written yet."
- A module docstring at the top says what the file is and to run
  `learn check`.

## Tests

### Files

```
tests/
├── conftest.py          # copy from the reference module, unchanged
├── helpers.py           # copy from the reference module, unchanged
├── test_challenges.py   # one test per challenge: test_<id>_<what>
└── test_exercise.py     # the exercise tests
```

`conftest.py` registers the `objective` marker. `helpers.py` provides:

- `load(relative_path)` – imports a learner file by path, relative to the
  module. A file that can't be loaded becomes a failure with a message.
- `check(func, args, expected, kwargs=None, hint=None)` – calls the function
  and fails with the spec's message format unless it returns `expected`.
  Handles the stub's `NotImplementedError` and any other exception.

### Writing a test

```python
import pytest

from helpers import check, load

EXERCISE = "exercise/text_tools.py"


@pytest.mark.objective(1, 4)
@pytest.mark.parametrize(
    "name, expected",
    [
        ("ada lovelace", "A.L."),
        ("plato", "P."),
        ("", ""),
    ],
)
def test_initials(name, expected):
    tools = load(EXERCISE)
    check(tools.initials, (name,), expected)


@pytest.mark.objective(2, 3)
def test_mask_keep():
    tools = load(EXERCISE)
    check(tools.mask, ("1234567890",), "********90", kwargs={"keep": 2})
```

- Every test has `@pytest.mark.objective(...)` with the objective number(s)
  it checks.
- Call `load(...)` inside each test. Never import learner files at the top
  of a test file: one broken file would stop the whole test file from
  loading.
- Use `check(...)` for every result. Don't write bare `assert`: pytest's
  assertion output is not a plain-language message.
- Use `parametrize` for cases of the same behaviour; each case is reported
  on its own.
- An optional `hint=` adds one `Hint:` line to the failure.
- When a function prints instead of returning, prefer changing the exercise
  so it returns. If printing is the point, use pytest's `capsys` fixture and
  fail with `pytest.fail(message, pytrace=False)` in the same message format.
- Tests are deterministic: no randomness, current time, network, or files
  outside pytest's `tmp_path`.

### Challenge checks

One test function per challenge, named `test_<id>_<what>`, in
`test_challenges.py`. A few `check(...)` calls in a row are fine; the first
failure stops the test.

```python
@pytest.mark.objective(1)
def test_c1_last_char():
    c1 = load("challenges/c1.py")
    check(c1.last_char, ("Python",), "n")
    check(c1.last_char, ("a",), "a")
```

## Solutions and broken variants

- A solution file is the starter file with each `# TODO` and
  `raise NotImplementedError` replaced by the implementation. Docstrings stay
  exactly the same.
- Solutions use only what the lesson (or an earlier module) taught: a `for`
  loop rather than a comprehension if comprehensions haven't come up yet.
- A broken variant is a full copy of the solution file with one plausible
  mistake. Its first line, above the module docstring:

  ```python
  # Broken variant: mask() keeps the first `keep` characters instead of the last.
  ```

## Refactor modules

For `exercise_type: refactor`. Read `.claude/skills/exercise-refactor/`
first. Reference module:
`examples/python/refactor-long-method/modules/01-long-method/`.

### Starter files

Working legacy code, no stubs. The module docstring states the task (see the
exercise-refactor skill); the interface functions keep their docstrings,
which describe what they do, not the task.

### Test files

```
tests/
├── conftest.py          # copy from the implement reference module, unchanged
├── helpers.py           # copy from the implement reference module, unchanged
├── refactoring.py       # copy from the refactor reference module, unchanged
├── test_challenges.py   # one test per challenge: test_<id>_<what>
├── test_behaviour.py    # behaviour tests: pass on the starter
└── test_structure.py    # structural checks (and test_extension.py for a new requirement)
```

`refactoring.py` provides, for behaviour tests:

- `keeps(func, args, before, kwargs=None)`: fails with "Behaviour changed:
  … returned X before the refactoring, but now returns Y." unless the call
  still returns `before`.
- `keeps_output(func, args, before, kwargs=None)`: the same for what the
  call prints, shown as indented lines.
- `keeps_raising(func, args, error_type, kwargs=None)`: the call still
  raises `error_type`.

and for structural checks, each failing with a message that names the
property, the value and the target:

- `max_length(path, limit, names=None)`: lines of code in each function's
  body, not counting the docstring, blank lines and comment lines.
- `max_complexity(path, limit, names=None)`: cyclomatic complexity, counted
  the way radon counts it (`if`, `elif`, `for`, `while`, `except`, `with`,
  `assert`, conditional expressions, comprehensions, match cases, each extra
  `and`/`or` operand).
- `max_nesting(path, limit, names=None)`: how deep blocks sit inside each
  other; an `elif` is not a level.
- `max_parameters(path, limit, names=None)`: parameters without `self` and
  `cls`.
- `no_comments(path, names=None)`: no comments inside functions.
- `functions(path)` and `function(path, name)`: the file's functions and
  methods (`"Class.method"`), each with `.length`, `.complexity`,
  `.nesting`, `.parameters`, `.comments`, `.calls` (names it calls),
  `.reassigned` (local names assigned with `=` more than once) and
  `.assigned_parameters`. Use them with `fail(message)` for a target the
  helpers above don't cover.

`names=None` checks every function and method in the file. `path` is
relative to the module, like `load()`.

To measure a file before the module has tests (the smell-author and the
solution-author do this), use the reference module's copy with an absolute
path, in the course folder:

```
uv run python -c "
import sys, pathlib
sys.path.insert(0, '../../examples/python/refactor-long-method/modules/01-long-method/tests')
from refactoring import functions
path = pathlib.Path('modules/<id>/exercise/<file>.py').resolve()
for f in functions(path).values():
    print(f, f.length, f.complexity, f.nesting, len(f.parameters), f.comments)
"
```

```python
@pytest.mark.objective(1, 4)
@pytest.mark.parametrize("order, printed", RECEIPTS)
def test_print_receipt_prints_the_same(order, printed):
    receipt = load(EXERCISE)
    keeps_output(receipt.print_receipt, (order,), printed)


@pytest.mark.objective(2, 3)
def test_no_function_is_longer_than_10_lines():
    max_length(EXERCISE, 10)
```

- Behaviour cases use `pytest.param(..., id="what-it-pins")`, so a failure
  names the behaviour.
- Get every expected value by running the starter in the course's
  environment (`uv run python -c ...`) and copying the result.
- A challenge check uses `check()` from `helpers.py` for the new function,
  `function(...).calls` to see that the old code calls it, then `keeps()` or
  `keeps_output()` for the old behaviour. A missing function is a `fail()`
  with a plain message, not an `AttributeError`.

### Solutions and broken variants

- The solution is the refactored starter file. The module docstring (the
  task) and the interface docstrings stay exactly the same.
- A variant's first line names its kind:

  ```python
  # Broken variant: behaviour: shipping_for() is given the subtotal before the discount.
  # Broken variant: smell: the item lines and totals are still printed inside print_receipt().
  ```

- Check a smell variant against the targets yourself: it must miss one by
  more than a line or two, or it may pass the structural checks.

## Runnable examples and quiz code

Lesson `python run` blocks and quiz `code` run on their own with
`python -c`, in an empty temporary folder.

- Each block defines everything it uses; nothing carries over from earlier
  blocks.
- Show values with `print(...)`. `print` of a list shows its items with
  quotes: `['a', 'b']`.
- To show an error, catch it and print it:

  ```python
  try:
      word[0] = "J"
  except TypeError as error:
      print("TypeError:", error)
  ```

- Only print output that is the same on every run and machine: no sets
  (unordered), object addresses (`<... at 0x...>`), times or random values.
- Exception messages can change between Python versions. Use them only when
  they are the same in every version the course's `requires-python` allows,
  and keep the example short.

## Checking your work

- Run a snippet, or a documented example against your solution, in the
  course's environment: `uv run python -c ...` in the course folder.
- `learn check` in the workspace shows the learner's view: with the starter
  files, every test fails, each with a plain message.
- The validator (`forge/validate/`) runs the solution and broken-variant
  setups from `spec/exercise-types/<type>.md`, the runnable examples and the
  `predict-output` answers.
