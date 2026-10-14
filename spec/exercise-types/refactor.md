# Exercise type: refactor

Applies to modules with `exercise_type: refactor`. The learner improves
working code without changing what it does: the starter files are legacy code
with the smells the module teaches, behaviour tests pin down what that code
does, and structural checks test that the smells are gone.

Example: `examples/python/refactor-long-method/`.

## Starter files

- Working code, not stubs. It reads like real code that grew through
  changing requirements, and it has the smells the module teaches.
- Each exercise file's module docstring states the task:
  - what to refactor;
  - the interface that must stay: the names and signatures other code calls;
  - the targets the structural checks test, as properties ("no function in
    this file is longer than 12 lines");
  - a new requirement to add after the refactoring, if the module has one.
- Tests check only what the starter code does and what the task states.

## Tests

Exercise tests are of two kinds:

- **Behaviour tests**, in the test file named `test_behaviour`: they pin
  down what the starter code does, through the interface that must stay.
  They pass on the starter, on the solution and on every correct
  refactoring.
- **All other exercise tests** (by convention `test_structure`, and
  `test_extension` for a new requirement) fail on the starter and pass on the
  solution:
  - structural checks test the task's targets. They test properties (length,
    complexity, nesting, parameter counts, which function calls which),
    never one particular design, and name only what the task names;
  - tests of a new requirement test it like any new behaviour.

Challenge checks follow the same rules as in `implement`: each fails on the
starter and passes on the solution. A challenge that asks for a small
refactoring checks the structure and the behaviour in its one test.

Failure messages follow `exercises.md`. A behaviour test says that the
behaviour changed: ``Behaviour changed: fine_for(3) returned 0.75 before the
refactoring, but now returns 1.0.`` A structural check names the property and
the target: ``return_item() is 41 lines long; the task asks for no function
longer than 12 lines.``

## Broken variants

Each variant is one plausible refactoring mistake, of one of two kinds. The
kind follows `Broken variant:` in the variant's first line:

- `Broken variant: behaviour: <what is wrong>`: the refactoring changed what
  the code does, e.g. an extracted function drops an edge case, or two
  conditions are merged wrongly.
- `Broken variant: smell: <what is wrong>`: the code still behaves the same,
  but the smell is still there, e.g. the long function still formats the
  receipt itself, or a comment was kept instead of becoming a name.

Every module has at least one variant of each kind.

## Validation rules

The validator runs the module's tests like `learn check` does (a temporary
copy of the module), in these setups:

| Setup | Files copied over the module | Required result |
|---|---|---|
| Starter | none | every behaviour test passes; every other test fails |
| Solution | `solution/` | every test passes |
| Each `behaviour` variant | `solution/`, then `broken/<variant>/` | at least one behaviour test fails, and every challenge test passes |
| Each `smell` variant | `solution/`, then `broken/<variant>/` | every behaviour test passes, at least one other exercise test fails, and every challenge test passes |

- A behaviour test that fails on the starter pins down something the code
  doesn't do.
- Any other test that passes on the starter checks nothing.
- A variant that its kind's tests miss means the tests miss a mistake. The
  tests get fixed, not the variant.
