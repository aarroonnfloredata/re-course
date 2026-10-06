---
description: Build one module from its outline entry with the agents, validate it, and report
argument-hint: <course-name> <module-number-or-id>
---

Build one module of `workspace/<course>/` with the agents in `.claude/agents/`,
until the validator passes or the retry limit is reached. The course name and
module come from `$ARGUMENTS`; the module can be given by number (`01`).

You orchestrate: start the agents, read the validator's output, and send each
problem to the agent that can fix it. Don't write module files yourself.

**Keep the authors apart.** The test-author never sees `solution/` or
`broken/`; the solution-author never sees `tests/`. When you pass a problem to
either, include only what that side needs, never the other side's code.

## 1. Prepare

- The module must be in `course.yaml` (approved outline), and the sections it
  cites must exist in `sources/`.
- In a cumulative course, the previous module must be built: this module's
  starter files build on its solution.
- If `modules/<id>/` doesn't exist:
  `uv run python -m forge.build init workspace/<course> <module>`
- If it exists, ask the author: rebuild from scratch (the same command with
  `--fresh`, which deletes the module), or only re-check and fix it (go to
  step 4).

## 2. Lesson

Start the **lesson-writer** with the course folder and module ID. It writes
the lesson, the challenge and exercise starter files, and the quiz.

## 3. Facts, tests and solution, in parallel

Start these three agents at once (one message, three agent calls), each with
the course folder and module ID:

- **fact-checker**: its report goes to the lesson-writer, which fixes what
  it lists.
- **test-author**
- **solution-author**

If either author reports a gap in the starter documentation, the
lesson-writer fixes the documentation; then tell both authors what changed so
they re-check their files. Do the same whenever a fix changes the starter
documentation.

## 4. Validate and fix

```
uv run python -m forge.validate workspace/<course> <module>
```

Send each problem to the agent that can fix it:

| Problem | Goes to |
|---|---|
| lesson, quiz, recap, runnable examples, starter files | lesson-writer |
| a test passes on the starter files; a test without an objective; an objective no test checks | test-author |
| a broken variant no test catches | test-author, with the variant's `Broken variant:` line only |
| a variant that changes nothing, breaks a challenge test, or a unit with no variant | solution-author |
| the solution fails a test | you decide, below |

**When the solution fails a test,** read the failure message and the
starter documentation of that unit, and decide which side is wrong:

- **The test:** tell the test-author "this test expects Y, but the
  documentation says Z", without the solution's code.
- **The solution:** tell the solution-author "for this input the
  documentation says B, yours returns C", without the test's code.
- **The documentation is unclear:** the lesson-writer clarifies it, then
  both authors re-check.

Then validate again. Sending the problems out and validating again is one
**fix round**. A build gets **at most 3 fix rounds** in total, including
those after steps 5 and 6. If problems remain after the third, stop fixing
and report them in step 7.

## 5. Review

Start the **reviewer**. The lesson-writer fixes its findings, except those
that would change what the exercise must do (its starter documentation): ask
the author about those first, since they mean redoing tests and solution.
Validate again; new problems use the remaining fix rounds.

## 6. Recap

Ask the lesson-writer to write `recap.md` from the final lesson, then run the
validator one last time. This final run always happens, even when no fix
rounds are left.

## 7. Report to the author

- The validator's summary.
- Fact-check: what was found and fixed.
- Review: what was fixed, and the findings waiting for the author.
- Anything still unresolved, with the validator's messages.
- How to take the module as a learner, without touching the workspace:

  ```
  uv run python -m forge.trial workspace/<course>
  cd workspace/<course>-trial && uv run learn next
  ```

  (`--fresh` replaces an earlier trial copy; `/publish` removes it.)
