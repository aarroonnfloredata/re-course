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
