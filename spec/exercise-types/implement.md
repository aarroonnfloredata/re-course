# Exercise type: implement

Applies to modules with `exercise_type: implement`. The learner writes code
from scratch: the starter files are stubs, and the tests check the finished
behaviour.

Example: `examples/python/implement-strings/`.

## Validation rules

The validator runs the module's tests like `learn check` does (a temporary
copy of the module), in three setups:

| Setup | Files copied over the module | Required result |
|---|---|---|
| Starter | none | **every** test fails |
| Solution | `solution/` | every test passes |
| Each broken variant | `solution/`, then `broken/<variant>/` | at least one exercise test fails, and every challenge test passes |

- A test that passes on the starter checks nothing, so every test must fail
  there.
- A broken variant that passes every test means a mistake the tests miss.
  The tests get fixed, not the variant.
- Challenge tests must still pass with a broken variant, because variants
  only change exercise files.
