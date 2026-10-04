"""The terminal quiz runner."""

import re
import textwrap

from .course import CourseError, read_yaml

WIDTH = 79
QUOTED = re.compile(r'"[^"]*"|`[^`]*`')
NO_BREAK = " "  # textwrap only breaks on ASCII whitespace


def load(module):
    path = module.path / "quiz.yaml"
    if not path.is_file():
        raise CourseError(f"{module.id} has no quiz.")
    return read_yaml(path)


def run(questions, ask=None, say=None):
    """Ask each question in turn and return how many were answered correctly."""
    ask = ask or input
    say = say or print
    score = 0
    for number, question in enumerate(questions, 1):
        say(f"\nQuestion {number} of {len(questions)}")
        say(wrap(question["prompt"]))
        if question.get("code"):
            say("")
            say(textwrap.indent(question["code"].rstrip("\n"), "    "))
        say("")
        options = [str(option) for option in question["options"]]
        for index, option in enumerate(options, 1):
            say(f"  {index}) " + option.replace("\n", "\n     "))

        choice = read_choice(len(options), ask, say)
        answer = question["answer"]
        if choice == answer:
            score += 1
            say("✓ Correct.")
        else:
            say(f"✗ Not quite. The answer is {answer + 1}) {options[answer]}")
        say(wrap(question["explanation"]))
    return score


def read_choice(count, ask, say):
    while True:
        reply = ask(f"\nYour answer (1-{count}): ").strip()
        if reply.isdigit() and 1 <= int(reply) <= count:
            return int(reply) - 1
        say(f"Please type a number from 1 to {count}.")


def wrap(text):
    """Wrap each line to WIDTH without breaking inside "quoted" or `code` text,
    where every space can matter."""

    def protect(match):
        return match.group().replace(" ", NO_BREAK)

    lines = [QUOTED.sub(protect, line) for line in text.strip().split("\n")]
    wrapped = "\n".join(textwrap.fill(line, WIDTH) for line in lines)
    return wrapped.replace(NO_BREAK, " ")
