# re-course

re-course turns technical sources (documentation, books, wikis) into
hands-on courses that are graded by tests and work in any editor. Each
module has a short lesson with examples to run, small challenges, an
exercise, a quiz and a recap.

Courses are generated here with Claude Code. Learners take them with
`learn`, a small command-line tool with no AI in it.

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/). It also
  provides Python, so nothing else needs installing for Python.
- [git](https://git-scm.com/downloads)
- bash, for bash courses. macOS and Linux come with it.
- [Claude Code](https://docs.claude.com/en/docs/claude-code/setup), with
  your own access. Only needed to build courses, not to take them.

Tested on macOS.

## Install

```
git clone https://github.com/aarroonnfloredata/re-course.git
cd re-course
python3 forge/doctor.py
```

`forge/doctor.py` checks that everything above is installed and that the
environments work. The first run downloads a few packages.

## Take a course

Published courses are in `shared-workspace/`. Inside a course folder:

```
uv run learn next
```

The first run sets up the course's environment. After that, `learn next`
shows where to start, and the course's own README explains how to work
through it.

To try it right away, use the example course:

```
cd examples/python/implement-strings
uv run learn next
```

## Build a course

Start Claude Code inside the `re-course` folder, so its commands are
available:

```
cd re-course
claude
```

Then, for a course called `bash-basics`:

1. **`/new-course bash-basics`** creates `workspace/bash-basics/` and fills
   in its brief with you: who the course is for, the goals, and the sources.
   You are responsible for your sources' licences.
2. **`/ingest bash-basics`** turns each source into Markdown with stable
   section IDs, which lessons cite.
3. **`/outline bash-basics`** plans the modules: what each teaches, its
   sources and its exercise. You review the plan and approve it. This is the
   main review point, so take your time here.
4. **`/build-module bash-basics 01`** builds a module. Agents write the
   lesson, the tests and a reference solution, and a validator checks
   everything. Repeat for each module.
5. **Take each module yourself**, in a copy that leaves the workspace
   untouched:

   ```
   uv run python -m forge.trial workspace/bash-basics
   cd workspace/bash-basics-trial
   uv run learn next
   ```

   Do this if you want to trial a course or module that you intend to publish
   for others. `--fresh` replaces an earlier trial copy, answers included;
   `/publish` removes it.

   If you write a course only for yourself, you do not have to create a trial
   copy of it. You can work directly with the original course files (e.g.
   `workspace/bash-basics`) as these would not get published and shared.

6. **`/publish bash-basics`** copies the course's learner files into
   `shared-workspace/bash-basics/`, ready to commit and share.

`/validate bash-basics` checks a course at any point and says what needs
fixing.

`workspace/` is private: git ignores it. Only what you publish to
`shared-workspace/` goes into the repository.

## What's supported

- **Course languages:** Python & Bash.
- **Exercise type:** implement: the learner writes code from scratch.
- **Sources:** HTML pages, PDFs (best with a table of contents, which
  defines the sections), and local Markdown or text files.

## Adding a language

A language needs a runtime plugin and a skill. Bash is a worked example of
both.

1. **Runtime plugin:** `runtime/learn/languages/<language>.py`, registered in
   `PLUGINS` in that folder's `__init__.py`. The `__init__.py` docstring
   lists what a plugin provides: running tests and snippets, an optional
   linter, and finding stubs for the validator. Tests can stay pytest files,
   as in bash.
2. **Extra packages:** if courses in the language need packages from PyPI
   (bash needs ShellCheck), add an extra named after the language in
   `runtime/pyproject.toml`. New courses then get `re-course-learn[<language>]`.
3. **Skill:** `.claude/skills/lang-<language>/SKILL.md`, covering starter
   files and stubs, tests, solutions, broken variants and runnable examples.
   Start from `lang-python` or `lang-bash`.
4. **Spec:** add the language's stub form to "Starter files" in
   `spec/exercises.md`.
5. **Fixture and tests:** a one-module course in `runtime/tests/fixtures/`
   whose starter fails, solution passes and broken variants are caught;
   runtime tests for the plugin; a generator test that the validator passes
   the fixture.
6. **Setup check:** in `forge/doctor.py`, check any tool the language needs
   from the system, and try the fixture's environment.

## Where things are

| Folder | Contents |
|---|---|
| `spec/` | the rules every course follows |
| `runtime/` | the `learn` tool |
| `forge/` | the generator's helpers: ingest, validate, publish |
| `.claude/` | the Claude Code commands, agents and skills |
| `templates/course/` | the starting point of every new course |
| `examples/` | the example course |
| `workspace/` | your courses in progress (private) |
| `shared-workspace/` | published courses |

## Development

```
uv run pytest                                                         # generator tests
cd runtime && uv run --no-project --with-editable '.[bash]' --with pytest pytest   # runtime tests
```

`CLAUDE.md` holds the rules for Claude Code when working in this repository.
