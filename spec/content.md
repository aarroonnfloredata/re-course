# Content: lesson, challenges, quiz, recap

Spec version: see `README.md`. Example: `examples/python/implement-strings/`.

Everything here is plain Markdown or YAML, so it reads well in any editor and
on GitHub. Tool-only information goes in HTML comments, which viewers hide.

## Lesson (`lesson.md`)

### Structure

In this order:

1. `# <module title>`
2. An introduction of one or two short paragraphs.
3. "By the end of this module you can:" followed by the objectives as a
   numbered list: same objectives, same order as `module.yaml`. Wording may
   only add code formatting.
4. A short "How to work through it" paragraph. It doesn't repeat what the
   course `README.md` already tells the learner: where to run examples and
   the starter stubs.
5. One `##` section per topic, with `###` subsections where needed.
   Challenges sit in the section they practise.
6. `## What's next`, linking the exercise files and `recap.md` and naming
   `learn check` and `learn quiz`.
7. The citation definitions.

**Length:** 500–1,200 words of prose, not counting code blocks and citation
definitions. (The golden lesson has 684. Tune this range with the first
generated course.)

### Runnable examples

Every code block in the course's language is runnable and is followed
directly by its expected output:

````markdown
```python run
word = "Python"
print(word[-1])
```
```output
n
```
````

- The info string is `<language> run`; the output block is `output`.
- Each block runs on its own, in an empty temporary folder, with no state
  from earlier blocks.
- The output block is the exact stdout. The block must exit successfully.
- To show an error, catch it and print it, so the example still runs:

  ````markdown
  ```python run
  try:
      "Python"[42]
  except IndexError as error:
      print("IndexError:", error)
  ```
  ```output
  IndexError: string index out of range
  ```
  ````

- Other fences (e.g. `text`) are allowed for things that are not code.

The validator runs every block and compares its output.

### Citations

Each factual claim is followed by a reference-style link to the source
section it comes from:

```markdown
The first character has index 0. ([pytutorial#text])
```

- The link goes after the sentence's full stop.
- Each ID is defined once, at the end of the lesson, with the section's URL
  and a title:

  ```markdown
  [pytutorial#text]: https://docs.python.org/3/tutorial/introduction.html#text "The Python Tutorial, 3.1.2 Text"
  ```

- Every cited ID exists in `sources/` (see `README.md`), and the set of cited
  IDs equals `sources` in `module.yaml`.
- A claim may go uncited only when a runnable example in the same section
  shows it.
- A short comparison with a language the brief's `learner` already knows
  (`$1` is Python's `sys.argv[1]`) may go uncited. It must be correct, and
  the rest of the sentence still needs its citation or example.

The fact-checker compares each cited claim with the cited section.

### Links to files

Every file the lesson mentions is a relative link from `lesson.md`:
`` [`challenges/c1.py`](challenges/c1.py) ``. Folders are not linked.

## Challenges

A challenge is a short task in the middle of the lesson, completable in a few
minutes. A module has 2–3.

In the lesson, a challenge is an HTML comment followed directly by a
blockquote:

```markdown
<!-- challenge id=c1 objective=1 -->
> **Challenge c1:** Open [`challenges/c1.py`](challenges/c1.py) and finish
> `last_char(word)` so it returns the last character of `word`.
> `last_char("Python")` is `"n"`. Check it with `learn check c1`.
```

- IDs are `c1`, `c2`, … in lesson order. `objective` is one objective number.
- The blockquote starts with `**Challenge <id>:**`, links the file to edit,
  gives at least one example, and ends with "Check it with
  `learn check <id>`."
- It asks only for what the check verifies.
- The learner edits exactly one file: `challenges/<id>.<ext>`. Its check and
  solution are described in `exercises.md`.

## Quiz (`quiz.yaml`)

A list of 5–7 questions:

```yaml
- id: q1
  objective: 1
  type: predict-output
  prompt: What does this print?
  code: |
    city = "Paris"
    print(city[-3])
  options: ["i", "r", "a"]
  answer: 1
  explanation: >-
    Negative indexes count from the end, starting at -1 for the last
    character: -1 is "s", -2 is "i", -3 is "r". "i" is city[3], which ignores
    the minus sign. "a" comes from counting the last character as -0.
```

| Field | Rule |
|---|---|
| `id` | `q1`, `q2`, … in order |
| `objective` | one objective number (counted from 1) |
| `type` | `predict-output`, `spot-the-bug` or `multiple-choice` |
| `prompt` | the question |
| `code` | required for `predict-output` and `spot-the-bug`; optional otherwise |
| `options` | 3–4 different options, all strings (quote numbers: `"3"`, not `3`) |
| `answer` | index into `options`, counted from 0 |
| `explanation` | why the answer is right, addressing the misconceptions behind the wrong options |

- **`predict-output`:** `code` runs on its own, like a runnable example. Its
  stdout, without the final newline, must equal `options[answer]` exactly,
  and no other option may equal it. The validator checks both.
- **`spot-the-bug`:** `code` holds the buggy code; the options are possible
  fixes. Exactly one option fixes it.
- Prefer `predict-output` and `spot-the-bug` over `multiple-choice`, and
  questions about misconceptions over trivia. Every wrong option is a
  plausible misconception.
- The correct answer is not always in the same position.
- The runtime shows text as written, wrapping each line at 79 columns
  without breaking inside "quoted" or `backticked` text. Use `|` to keep
  line breaks.

## Recap (`recap.md`)

```markdown
# Recap: Strings

- `s[0]` is the first character and `s[-1]` the last. An index past the end
  is an error. (objective 1)
```

- `# Recap: <short title>` followed by a bullet list.
- At most 150 words.
- Each point ends with `(objective N)`; every objective appears at least once.
- No material the lesson didn't cover.
