---
description: Plan a course's modules from its brief and sources, and get the plan approved
argument-hint: <course-name>
---

Write the module plan for `workspace/<course>/` as `outline.yaml`, review it
with the author, and on approval write the module list into `course.yaml`.
The course name comes from `$ARGUMENTS`. The format and rules are in
`spec/README.md` ("outline.yaml"); module size limits are in
`spec/content.md`.

This is the main review point before anything expensive is generated. Work
with the author, not around them.

1. **Read the brief** (`brief.yaml`): the learner, the goals, the project
   style, the constraints.

2. **Read the sources' structure first:**

   ```
   uv run python -m forge.sources list workspace/<course>
   ```

   Then read only the sections that matter for the goals. Large sources don't
   need to be read in full.

3. **Draft the plan:**
   - Pick the concepts the goals need, pitched at the learner. Leave out what
     the goals don't need, and list notable omissions in `left_out` with a
     reason.
   - Group the concepts into modules. A module has 3–5 objectives and must fit
     a lesson of 500–1,200 words, 2–4 challenges and a 5–7 question quiz.
   - Order the modules so nothing is used before it is taught. Each concept
     appears in the `introduces` of one module only.
   - Cite for each module the source sections its lesson will draw on.
   - Cumulative course: write a `scenario` that fits every module naturally,
     and say in each `exercise` what that module adds to it. If no scenario
     fits, tell the author and suggest `independent` instead of forcing one.
   - Independent course: describe each module's exercise on its own.

4. **Write `outline.yaml` and check it:**

   ```
   uv run python -m forge.validate workspace/<course> --outline
   ```

   Fix every problem before showing the plan.

5. **Review with the author:**

   ```
   uv run python -m forge.outline show workspace/<course>
   ```

   Show the output, then point out the decisions worth a second look: the
   module order, anything left out, and modules that may be too big or too
   small. Change the outline as the author asks, check it again, and show it
   again. Repeat until the author approves.

6. **On approval only:**

   ```
   uv run python -m forge.outline approve workspace/<course>
   ```

   This writes the module IDs into `course.yaml`. The next step is
   `/build-module 01`.

Changing the plan later means editing `outline.yaml`, approving it again,
and rebuilding the modules it affects.
