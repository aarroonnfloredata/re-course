---
name: lang-python
description: How to write Python course material for re-course - starter stubs, challenge and exercise tests (pytest), solutions, broken variants, runnable lesson examples and predict-output quiz code. Use when writing or fixing any of these for a module with `language: python`.
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

- `learn check` in the workspace shows the learner's view: with the starter
  files, every test fails, each with a plain message.
- The validator (`forge/validate/`) runs the solution and broken-variant
  setups from `spec/exercise-types/<type>.md`, the runnable examples and the
  `predict-output` answers.
