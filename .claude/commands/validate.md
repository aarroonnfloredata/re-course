---
description: Validate a course, or some of its modules, against the spec and say what needs fixing
argument-hint: <course-name> [module ...] [--static]
---

Run the validator on a course and explain the result. From `$ARGUMENTS`: the
course name (`workspace/<name>/`; a path such as
`examples/python/implement-strings` also works), optional module numbers or
IDs, and an optional `--static`.

1. **Run it:**

   ```
   uv run python -m forge.validate workspace/<course> [module ...] [--static]
   ```

   `--static` skips the checks that run code and is much faster. Before the
   outline is approved (`course.yaml` has no modules yet), use `--outline`
   instead, which checks only the brief and the outline.

2. **Report:** if there are no problems, say so in one line. Otherwise list
   the problems by module and, for each, who fixes it:

   | Problem in | Fixed by |
   |---|---|
   | `brief.yaml`, `course.yaml`, `pyproject.toml` | the author (`/new-course`, `forge.dependencies`) |
   | `outline.yaml`, or a module not matching it | `/outline` |
   | `sources/`, citations pointing at missing sections | `/ingest` |
   | lesson, quiz, recap, runnable examples, starter files | lesson-writer |
   | tests | test-author |
   | `solution/`, `broken/` | solution-author |
   | a solution failing a test | `/build-module` decides which side is wrong |

3. **Don't fix anything unless the author asks.** To fix a module, use
   `/build-module <course> <module>` and choose "re-check and fix", so the
   test-author and solution-author stay apart.
