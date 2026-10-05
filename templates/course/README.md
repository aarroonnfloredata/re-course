# {{title}}

{{summary}}

A hands-on course made with [re-course](../../README.md): short lessons with
examples to run, small challenges, an exercise checked by tests, a quiz and a
recap per module.

## Setup

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. In this folder, run:

   ```
   uv run learn next
   ```

   The first run creates the course's environment (`.venv/`) with everything
   the course needs. After that, it shows where to start.

The course has to stay inside the `re-course` folder: it uses the `learn`
runtime from there.

## Working through a module

1. Read the lesson; `learn next` shows where it is. Run the examples yourself.
2. Do each challenge when you reach it, and check it with `learn check c1`
   (using the challenge's ID).
3. Write the exercise in the module's `exercise/` folder, then run
   `learn check`.
4. Take the quiz with `learn quiz`.
5. Read the recap.

Once every check in a module passes, `learn next` moves on to the next one.

Edit only the files in `exercise/` and `challenges/`. Never edit `tests/`.

## Commands

| Command | Does |
|---|---|
| `learn next` | Shows the current module and which parts still fail. |
| `learn check` | Checks every part of the current module. |
| `learn check c1` | Checks one challenge, or `learn check exercise` for the exercise. |
| `learn check 02` | Checks another module; `learn check 02 c1` checks one of its parts. |
| `learn quiz` | Takes the current module's quiz; `learn quiz 02` takes another's. |

Run each command as `uv run learn ...`, or activate the environment once per
terminal and then type just `learn ...`:

```
source .venv/bin/activate      # macOS and Linux
.venv\Scripts\activate         # Windows
```
