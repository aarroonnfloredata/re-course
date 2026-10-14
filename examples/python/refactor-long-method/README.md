# Golden example: refactor, long functions

Hand-written reference for the `refactor` exercise type. It shows agents what
a good refactor module looks like and is a test fixture for the validator.

It is laid out as a course workspace with one module:

- `brief.yaml` – course brief (input to the generator)
- `course.yaml` – course metadata the runtime reads
- `outline.yaml` – the approved module plan
- `sources/` – ingested Wikipedia pages (CC BY-SA 4.0) with section IDs
- `modules/01-long-method/` – the module, including `solution/` and `broken/`

`tests/refactoring.py` in the module holds the helpers for behaviour tests and
structural checks; refactor modules copy it unchanged.
