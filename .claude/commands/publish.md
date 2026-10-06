---
description: Publish a finished course into shared-workspace/ and offer to commit it
argument-hint: <course-name>
---

Publish `workspace/<course>/` into `shared-workspace/<course>/`. The course
name comes from `$ARGUMENTS`.

1. **Publish:**

   ```
   uv run python -m forge.publish workspace/<course>
   ```

   It refuses when the validator finds problems, which includes modules not
   built yet. Then show the problems and who fixes them, as `/validate` does,
   and stop.

2. **Unknown licences:** if it lists sources with an unknown licence, show
   them with the modules that cite them. Remind the author that the lessons
   and quizzes drawn from those sources will be public, and that checking
   this is their responsibility. Only if the author confirms, run it again
   with `--accept-unknown-licenses`. Better still, add the `license` to the
   source in `brief.yaml` and run `/ingest` for it.

3. **Commit, only with the author's OK:** show what changed:

   ```
   git status --short shared-workspace/<course>
   git diff --stat -- shared-workspace/<course>
   ```

   Suggest a message such as `Publish <course>: <title> (<n> modules)`, and
   commit only after the author explicitly agrees:

   ```
   git add shared-workspace/<course>
   git commit -m "<message>"
   ```

   Never push.

`shared-workspace/` is written only by `/publish`: to change a published
course, change the workspace and publish again. `re-course` is the only
repository; never run `git init` anywhere inside it.
