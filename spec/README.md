# re-course spec

**Spec version: 1**

The spec is the contract between the agents that write modules, the validator
that checks them, and the `learn` runtime that serves them. Anything two of
them must agree on is here. Teaching advice and language specifics are not;
they live in skills and agent prompts.

The reference implementation of this spec is the golden example
`examples/python/implement-strings/`.

| File | Contents | Read by |
|---|---|---|
| `README.md` | terms, layouts, `course.yaml`, `brief.yaml`, `module.yaml`, sources, objectives, runtime commands | everyone |
| `content.md` | lesson, runnable examples, citations, challenges, quiz, recap | lesson-writer, fact-checker, reviewer |
| `exercises.md` | starter files, tests, failure messages, solutions, broken variants | test-author, solution-author |
| `exercise-types/<type>.md` | validation rules for one exercise type | test-author, solution-author, validator |
| `schemas/*.json` | machine-checkable structure | validator, runtime |

Markdown is the source of truth for intent, schemas for structure. Change both
together.

## Terms

- **Course:** an ordered list of modules on one subject, in one language.
- **Module:** one lesson with its challenges, exercise, quiz and recap.
- **Part:** something `learn check` can check on its own: a challenge (`c1`,
  `c2`, …) or the `exercise`.
- **Workspace:** `workspace/<course>/`, where a course is generated and
  reviewed. Has everything, including authoring files.
- **Published course:** `shared-workspace/<course>/`, written only by
  `/publish`. Learner files only.

## Course layout

```
<course>/
├── course.yaml          # course metadata, read by the runtime
├── pyproject.toml       # the course's environment; see "Course environment"
├── brief.yaml           # workspace only: the hand-written course brief
├── sources/             # workspace only: ingested sources
│   └── <source-id>.md
└── modules/
    └── <module-id>/     # see "Module layout"
```

## `course.yaml`

```yaml
title: Python Strings
spec_version: 1
language: python
modules:          # module IDs in learning order
  - 01-strings
```

All fields are required. `language` must have a runtime plugin
(`runtime/learn/languages/<language>.py`).

## `brief.yaml`

The input to the generator, written by the course author. Agents treat it as
the source of truth; the validator uses its source IDs.

```yaml
title: Python Strings
spec_version: 1
language: python
learner: >-
  Writes basic Python: variables, print(), if/for, lists, simple functions.
goals:
  - "take strings apart with indexes and slices"
sources:
  - id: pytutorial          # source ID used in citations
    url: https://docs.python.org/3/tutorial/introduction.html
project_style: independent  # or: cumulative (the template's default)
dependencies: []            # packages the course needs, e.g. ["polars>=1.0"]
constraints: ["standard library only"]
```

Each source has an `id` (lowercase letters, digits, hyphens) and either a
`url` or a `path` to a local file, relative to the workspace.

`dependencies` is copied into the course's `pyproject.toml`, which defines the
course's own environment (see "Course environment").

## Course environment

Each course has its own virtual environment, defined by the course's
`pyproject.toml` and managed by uv. It lists the `learn` runtime
(`re-course-learn`), the packages from the brief's `dependencies` and the
Python version. `learn` runs tests, examples and quiz code with that
environment's interpreter, so course packages are always available.

The course's `uv.lock` is committed, so every learner gets the same package
versions. `.venv/` is not.

## Module layout

```
<module-id>/
├── module.yaml
├── lesson.md
├── challenges/          # one file per challenge: <id>.<ext>
├── exercise/            # starter files
├── tests/
├── quiz.yaml
├── recap.md
├── solution/            # workspace only
└── broken/              # workspace only
```

All files and folders are required. `solution/` and `broken/` exist only in
the workspace and are never published.

**Naming:** the module ID is `NN-kebab-case-title`, where `NN` is the
two-digit position in the course (`01-strings`). The folder name equals the
ID. Learners can refer to a module by its number (`learn check 01`).

## `module.yaml`

```yaml
id: 01-strings
title: "Strings: Indexing, Slicing and Methods"
exercise_type: implement
language: python
prerequisites: []                 # module IDs
objectives:
  - "Get single characters from a string with positive and negative indexes"
  - "Take substrings with slices, including omitted and out-of-range bounds"
sources: [pytutorial#text, pystdtypes#string-methods]
checkpoint: checkpoints/03/       # optional; cumulative courses only
```

- `exercise_type` names the file in `exercise-types/` that applies.
- `sources` lists exactly the citation IDs the lesson uses.
- `checkpoint` is not yet specified; see `exercises.md`.

## Objectives

Objectives are numbered from 1 in `module.yaml` order. Everything else refers
to them by number:

- every challenge, quiz question, test and recap point names its
  objective(s);
- every objective is checked by at least one test and asked about in at
  least one quiz question.

## Sources

The ingest step writes one Markdown file per source, `sources/<source-id>.md`:

```markdown
---
id: pytutorial
title: "The Python Tutorial: 3. An Informal Introduction to Python"
url: https://docs.python.org/3/tutorial/introduction.html
version: "3.14"
retrieved: 2026-10-04
license: >-
  © Copyright 2001 Python Software Foundation. Licensed under the Python
  Software Foundation License Version 2.
excerpt: "Section 3.1.2 only"   # optional; present when not the whole source
---

## 3.1.2. Text {#text}

...
```

- Every section that can be cited has a heading ending in `{#<section-id>}`.
- A section includes everything up to the next heading of the same or higher
  level.
- Omitted text inside an excerpt is marked `[…]`.

**Citation IDs** are `<source-id>#<section-id>`. The section ID is the
source's own anchor or section number where it has one (`pytutorial#text`
matches `introduction.html#text`), otherwise a slug of the heading.

## Runtime commands

Lessons refer to these commands; this is what they do.

| Command | Does |
|---|---|
| `learn next` | Shows the current module and which parts still fail. |
| `learn check` | Checks every part of the current module. |
| `learn check <part>` | Checks one part of the current module: `c1`, `exercise`, … |
| `learn check <module> [part]` | Checks another module, or one of its parts. |
| `learn quiz [module]` | Runs a module's quiz in the terminal. |

The **current module** is the first module, in `course.yaml` order, with a
failing test. The runtime keeps no saved state.

`learn check` runs the tests in a temporary copy of the module, without
`solution/` and `broken/`. It exits with 0 when everything checked passes and
1 otherwise.
