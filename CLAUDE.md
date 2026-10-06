# re-course

Generates hands-on, test-graded courses from technical sources. Courses are
generated here with Claude Code; learners take them with the `learn` runtime,
which is plain Python with no AI.

## Read first

- `spec/README.md`: the contract for every course file. Read it before
  writing or changing any course material; it says which other spec files
  apply.
- `.claude/skills/lang-<language>/`: how to write that language's material.
- `examples/python/implement-strings/`: the reference course. When in doubt,
  do what it does.

## Layout

- `spec/`: the spec and JSON schemas
- `runtime/`: the `learn` command
- `forge/`: deterministic generator helpers (ingest, validate)
- `templates/course/`: copied into every new course
- `examples/`: golden examples, one per exercise type
- `workspace/<course>/`: courses being generated; gitignored and private
- `shared-workspace/<course>/`: published courses, committed to `re-course`,
  written only by `/publish`

## Quality bar

- Tests are the product. Every test fails on the starter files, passes on the
  solution, and together they catch every broken variant.
- Every failure message says in plain language what was expected and what
  came back.
- Every factual claim cites a source section. Every runnable example and
  `predict-output` answer matches what the code really prints.
- Test authors and solution authors never see each other's work.
- The validator judges; agents fix what it reports.
- When a course has a problem, fix the generator (spec, skills, agents), then
  regenerate.

## Rules

- Nothing course-specific goes in `.claude/`; it belongs in the course's
  `brief.yaml` or workspace.
- Keep `re-course` working from a fresh clone: no absolute paths.
- Never write to `shared-workspace/` except through `/publish`.
- Run course code inside the course's environment: `uv run ...` in the
  course folder.

## Commands

- Setup check: `python3 forge/doctor.py`
- New course: `/new-course <name>`
- Ingest sources: `/ingest <name>` (runs `uv run python -m forge.ingest <course folder>`)
- Plan modules: `/outline <name>` (uses `uv run python -m forge.outline show|approve <course folder>`)
- Build a module: `/build-module <name> <module>` (uses `uv run python -m forge.build init ...`)
- Take a course as a learner: `uv run python -m forge.trial <course folder>`, then
  `cd <course folder>-trial && uv run learn next`
- Publish a course: `/publish <name>` (uses `uv run python -m forge.publish <course folder>`)
- Read sources by section: `uv run python -m forge.sources list <course folder>`,
  `uv run python -m forge.sources show <course folder> <source-id#section-id>`
- After changing a brief's `dependencies`: `uv run python -m forge.dependencies <course folder>`
- Validate a course: `/validate <name> [module ...]`, or
  `uv run python -m forge.validate <course folder> [module ...]`
  (`--static` skips the checks that run code; `--outline` checks only the
  brief and outline)
- Generator tests: `uv run pytest`
- Runtime tests: `cd runtime && uv run --no-project --with-editable . --with pytest pytest`
- Try a course: `cd <course folder> && uv run learn next`
