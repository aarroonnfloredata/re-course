# Exercises: starter files, tests, solutions, broken variants

Spec version: see `README.md`. Example: `examples/python/implement-strings/`.
How to do each of these in a given language is in that language's skill
(`.claude/skills/lang-<language>/`).

## What the learner edits

- **`exercise/`:** the starter files for the module's exercise.
- **`challenges/<id>.<ext>`:** one file per challenge.

The learner never edits `tests/`. Nothing else in the module is meant to
change.

## Starter files

What the starter files hold depends on the exercise type. In `refactor`
exercises they are working legacy code; see `exercise-types/refactor.md`.
Challenges, and the exercise in `implement`, use stubs:

- Each unit the learner writes (a function, a script) is a stub: a `TODO`
  comment and the language's way of saying "not written yet" (Python:
  `raise NotImplementedError`; bash: print `<unit> is not written yet.` to
  stderr and exit or return with status 1).
- The stub's documentation states the full behaviour, including edge cases,
  with examples. Tests check only behaviour stated there.
- A starter file needs only what the lesson (or an earlier module) covered.

**Given code.** An `implement` exercise can also give the learner working
code to read but not change, for example legacy code they write
characterization tests for. The given file's documentation says so. The
units the learner writes are then test functions in a test file next to it:
stubs whose documentation names the case to pin, never the expected result.
The test file's documentation states the rules the checks need (for
example, which call to make and what to assert on). The exercise tests check
the learner's tests: each must pass on the given code and fail on altered
copies of it, each changing behaviour that test pins.

## Tests

### Location and naming

- All tests live in `tests/`. Helper and configuration files may sit next to
  them.
- **Challenge checks** are in the test file named `test_challenges`. The
  tests for challenge `c1` are named `test_c1_<anything>`.
- **Exercise tests** are in any other test file (by convention
  `test_exercise`; `refactor` exercises use `test_behaviour` and
  `test_structure`).
- This naming is how the runtime groups results into parts; see
  `README.md`.

### Rules

- Every test declares the objective(s) it checks (Python:
  `@pytest.mark.objective(1, 4)`).
- Each test loads the learner's file itself. If the file can't be loaded, the
  test fails with a message saying so; it doesn't break the whole run.
- Tests find learner files relative to the `tests/` folder. The runtime runs
  them in a temporary copy of the module, without `solution/` and `broken/`.
- Tests don't use the network or files outside the module copy.
- A whole test run takes less than 60 seconds; the runtime stops it after
  that and reports a possible endless loop.
- Spec v1: all tests are visible to the learner.

### Failure messages (hard requirement)

Every failure tells the learner, in plain language, what was called, what was
expected and what came back:

| Situation | Message |
|---|---|
| Wrong result | ``initials('ada lovelace') should return 'A.L.', but returned 'A.L'.`` |
| Exception | ``initials('  alan   turing ') raised IndexError: string index out of range`` |
| Stub not written yet | ``last_char() is not written yet.`` |
| File can't be loaded | ``exercise/text_tools.py could not be loaded: SyntaxError: …`` |

- Values are shown as the language writes them in code (Python: `repr`), so
  `'2'` and `2` look different.
- Printed output and file contents are shown as indented lines below the
  sentence that introduces them.
- A failure may add one line starting with `Hint:`.
- No stack traces of the test code.

`learn check` shows each distinct message once per part, up to five.

## Solutions

`solution/` mirrors the path of every file in `exercise/` and
`challenges/`; given code is copied unchanged:

```
solution/
├── challenges/c1.py
└── exercise/text_tools.py
```

When the language has a linter (bash: ShellCheck), solution files get no
advice from it.

## Broken variants

Each variant is one plausible learner mistake, used to prove the tests catch
it.

```
broken/
└── <what-is-wrong>/        # kebab-case, e.g. mask-keeps-first-characters
    └── exercise/text_tools.py
```

- A variant holds full copies of only the files it changes. It is applied on
  top of `solution/`.
- Each changed file starts with a comment `Broken variant: <what is wrong>`,
  after the `#!` line if the file has one. `refactor` variants also name
  their kind: `Broken variant: behaviour: …` or `Broken variant: smell: …`.
- `implement`: at least one variant per unit the learner writes in
  `exercise/`. `refactor`: at least one variant of each kind.
  Challenges have no variants.

What a variant must do under the tests depends on the exercise type; see
`exercise-types/`.

## Cumulative projects and checkpoints

The full rules come with the first cumulative course
(`project_style: cumulative`). Already decided:

- **One scenario across the course.** Each module's exercise extends the same
  scenario. For example, a course on Python data types builds a school's
  student catalogue:
  1. strings: join each student's first and last name;
  2. lists: collect the student names in a list;
  3. dictionaries: register each class as a dictionary with its class teacher
     and the list of students from module 2.
- **Code carries over where it makes sense.** A module starts from the code
  built in earlier modules and extends it. In the example, module 3 starts
  with the student list from module 2 already in place.
- **Carried-over code is the reference solution, not the learner's own.** It
  is part of the module's starter files (its checkpoint). Modules don't
  import each other's files: the runtime checks one module at a time in a
  copy of that module alone, and a mistake left in an earlier module must not
  break the next one.
- **Tests check the new work.** Carried-over code is already correct, so a
  test of it alone would pass on the starter files.
- **Refactor courses refactor one area per module.** The starter files are
  the previous module's solution, in which the area this module works on is
  still in its legacy form. Behaviour tests pin down that area.
