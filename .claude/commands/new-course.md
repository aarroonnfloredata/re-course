---
description: Create a course workspace and fill in its brief with the author
argument-hint: <course-name>
---

Create a new course workspace, `workspace/<name>/`, then fill in its brief
together with the author. The name comes from `$ARGUMENTS` if given.

1. **Ask for what's missing:** the name (lowercase letters, digits and
   hyphens, e.g. `bash-basics`), a title, the language, and one sentence
   describing the course for its README. The language needs a runtime plugin
   in `runtime/learn/languages/`.

2. **Create the workspace:**

   ```
   uv run python -m forge.new_course <name> --title "<title>" --language <language> --summary "<sentence>"
   ```

   If it fails, show the error and stop.

3. **Fill in `workspace/<name>/brief.yaml` with the author.** Field rules are
   in `spec/README.md` ("brief.yaml"). Ask about one field at a time and
   replace every `TODO`:
   - `learner`: who the course is for and what they already know. Push for
     specifics; this decides how high or low the material is pitched.
   - `goals`: what the learner can do after the course.
   - `sources`: what the course is built from. Only use sources the author
     names; never invent one. Give each a short `id` (lowercase letters,
     digits, hyphens) and a `url`, or a `path` relative to the workspace.
     Mention that the author is responsible for the sources' copyright.
   - `project_style`: `cumulative` (the default), where the exercises extend
     one scenario across the course; or `independent`, where each module's
     exercise stands alone (see `spec/exercises.md`). Suggest `independent`
     only when the topics share no natural scenario or modules may be taken
     in any order.
   - `dependencies`: packages beyond the standard library, if any.
   - `constraints`: anything else the course must respect.

4. **If `dependencies` isn't empty**, update the course environment:

   ```
   uv run python -m forge.dependencies workspace/<name>
   ```

5. **Finish:** show the filled-in brief and confirm no `TODO` is left. The
   next step is `/ingest`.

Don't commit anything in the new workspace's git repo.
