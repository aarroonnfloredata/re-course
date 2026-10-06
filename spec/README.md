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
├── outline.yaml         # workspace only: the module plan
├── sources/             # workspace only: ingested sources
│   ├── <source-id>.md
│   └── raw/             # downloaded originals, reused by ingest
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
    license: "PSF License Version 2"   # optional
    selector: "div.body"               # optional; HTML pages only
project_style: independent  # or: cumulative (the template's default)
dependencies: []            # packages the course needs, e.g. ["polars>=1.0"]
constraints: ["standard library only"]
```

Each source has an `id` (lowercase letters, digits, hyphens) and either a
`url` or a `path` to a local file, relative to the workspace. One source is
one page or one file; a site with many pages is listed as several sources.

Optional per source:

- `license`: what the source allows. Copied into the ingested file; without
  it, ingest writes "unknown: check before publishing".
- `selector`: a CSS selector for the page's main content, for when ingest's
  automatic choice picks up menus or footers.

`dependencies` is copied into the course's `pyproject.toml`, which defines the
course's own environment (see "Course environment").

## `outline.yaml`

The module plan, written by `/outline` from the brief and the sources, and
approved by the course author before any module is built.

```yaml
scenario: >-                      # cumulative courses only
  A log analyzer for a small web server, growing module by module.
modules:
  - id: 01-pipes-and-redirection
    title: Pipes and Redirection
    exercise_type: implement
    introduces: [pipes, output redirection, stderr]
    objectives:                   # 3–5
      - "Connect commands with |"
      - "Send output and errors to files"
      - "Keep errors apart from normal output"
    prerequisites: []
    sources: [tlcl#6.1, tlcl#6.2]
    exercise: >-
      Count the error lines in access.log and save them to errors.txt.
left_out:                         # optional
  - section: tlcl#6.5
    reason: "tee: not needed for the goals"
```

- Modules are in learning order and numbered by position (`01-`, `02-`, …).
- `prerequisites` are earlier modules only.
- `introduces` lists the concepts a module teaches first; each concept is
  introduced by one module only.
- Every cited section, in `sources` and `left_out`, exists in `sources/`. A
  section is either used or left out, not both.
- A cumulative course has a `scenario`, and each module's `exercise` says
  what it adds to it.
- Approving the outline (`uv run python -m forge.outline approve <course>`)
  writes the module IDs into `course.yaml`. `/build-module` creates each
  `module.yaml` from its outline entry.

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
objectives:                       # 3–5
  - "Get single characters from a string with positive and negative indexes"
  - "Take substrings with slices, including omitted and out-of-range bounds"
  - "Build new strings instead of changing existing ones, and keep the results of string methods"
sources: [pytutorial#text, pystdtypes#string-methods]
checkpoint: checkpoints/03/       # optional; cumulative courses only
```

- `exercise_type` names the file in `exercise-types/` that applies.
- A module has 3–5 objectives.
- `sources` lists exactly the citation IDs the lesson uses.
- `id`, `title`, `exercise_type`, `prerequisites`, `objectives` and `sources`
  match the module's entry in `outline.yaml`.
- `checkpoint` is not yet specified; see `exercises.md`.

## Objectives

Objectives are numbered from 1 in `module.yaml` order. Everything else refers
to them by number:

- every challenge, quiz question, test and recap point names its
  objective(s);
- every objective is checked by at least one test and asked about in at
  least one quiz question.

## Sources

Ingest (`uv run python -m forge.ingest <course>`) writes one Markdown file per
source, `sources/<source-id>.md`, and keeps downloaded originals in
`sources/raw/`. Supported: HTML pages, PDFs, and local Markdown or text files.

```markdown
---
id: pytutorial
title: 3. An Informal Introduction to Python — Python 3.14.8 documentation
url: https://docs.python.org/3/tutorial/introduction.html   # or: path
retrieved: 2026-10-06
license: PSF License Version 2
---

## 3.1.2. Text {#text}

...
```

- Ingest writes `id`, `title`, `url` or `path`, `retrieved` and `license`.
  A hand-made file may add `version`, and `excerpt` when it holds only part
  of the source; omitted text is then marked `[…]`.
- Every section that can be cited has a heading ending in `{#<section-id>}`.
- A section includes everything up to the next heading of the same or higher
  level.
- Ingest rewrites the file on every run. Fix problems through the brief
  (e.g. a `selector`), not by editing the file.

**Citation IDs** are `<source-id>#<section-id>`. Ingest takes the section ID
from the source itself, so it stays the same between runs:

- **HTML:** the heading's anchor: its own `id`, an anchor inside it, the `id`
  of the section that wraps it, or an empty anchor just before it
  (`pytutorial#text` matches `introduction.html#text`).
- **PDF:** the PDF's table of contents. The ID is the section number when the
  title starts with one (`7.3`); without a table of contents, each page is a
  section (`page-12`).
- **Markdown:** an existing `{#id}`.
- Otherwise a slug of the heading. Duplicates get `-2`, `-3`, ….

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
