"""The `learn` command: learn next, learn check, learn quiz."""

import argparse
import sys
import textwrap
from pathlib import Path

from . import quiz
from .course import CourseError, find_root, load_course
from .stages import lint, tests

MAX_MESSAGES = 5  # distinct failure messages shown per part


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        course = load_course(find_root(Path.cwd()))
        return args.command(course, args)
    except CourseError as error:
        print(f"learn: {error}", file=sys.stderr)
        return 2


def build_parser():
    parser = argparse.ArgumentParser(prog="learn", description="Work through a re-course course.")
    commands = parser.add_subparsers(title="commands", dest="name", required=True)

    next_parser = commands.add_parser("next", help="show the next module and what is left in it")
    next_parser.set_defaults(command=cmd_next)

    check_parser = commands.add_parser("check", help="check a module, a challenge or the exercise")
    check_parser.add_argument(
        "target", nargs="*", metavar="module|part",
        help="e.g. `01`, `c1`, `exercise` or `01 c1` (default: the current module)",
    )
    check_parser.set_defaults(command=cmd_check)

    quiz_parser = commands.add_parser("quiz", help="take a module's quiz")
    quiz_parser.add_argument("module", nargs="?", help="default: the current module")
    quiz_parser.set_defaults(command=cmd_quiz)
    return parser


def cmd_next(course, args):
    module, results = current_module(course)
    if module is None:
        print("Every module passes. Nothing left to do.")
        return 0
    print(f"Next: {module.title} ({module.id})")
    print(f"Lesson: {(module.path / 'lesson.md').relative_to(course.root)}\n")
    for part, part_results in tests.by_part(results, module).items():
        print("  " + status_line(part, part_results))
    print("\nRun `learn check` for details.")
    return 0


def cmd_check(course, args):
    target = list(args.target)
    module = course.find_module(target[0]) if target else None
    if module is not None:
        target.pop(0)
    if len(target) > 1:
        raise CourseError(f"Expected a module and a part, got: {' '.join(args.target)}")
    part = target[0] if target else None

    if module is None:
        module, results = current_module(course)
        if module is None:
            print("Every module passes. Nothing left to do.")
            return 0
    else:
        results = tests.run(module)

    parts = tests.by_part(results, module)
    if part is not None:
        if part not in parts:
            raise CourseError(
                f"{module.id} has no part called {part!r}. "
                f"Use a module (e.g. {module.id}) or a part: {', '.join(parts)}."
            )
        parts = {part: parts[part]}

    print(f"Checking {module.title} ({module.id})\n")
    failing = 0
    for name, part_results in parts.items():
        print(status_line(name, part_results))
        messages = list(dict.fromkeys(r.message for r in part_results if not r.passed))
        for message in messages[:MAX_MESSAGES]:
            print(textwrap.indent(message, "    "))
        if len(messages) > MAX_MESSAGES:
            print(f"    ... and {len(messages) - MAX_MESSAGES} more")
        if not tests.all_passed(part_results):
            failing += 1
    print_advice(module, parts)

    if failing:
        print(f"\n{failing} of {len(parts)} still failing.")
        return 1
    print("\nAll passing.")
    return 0


def cmd_quiz(course, args):
    if args.module:
        module = course.find_module(args.module)
        if module is None:
            raise CourseError(f"No module called {args.module!r}.")
    else:
        module, _ = current_module(course)
        if module is None:
            raise CourseError("Every module passes. Name a module, e.g. `learn quiz 01`.")

    questions = quiz.load(module)
    print(f"Quiz: {module.title} ({len(questions)} questions)")
    try:
        score = quiz.run(questions)
    except (EOFError, KeyboardInterrupt):
        print("\nQuiz stopped.")
        return 1
    print(f"\nScore: {score} of {len(questions)}")
    return 0


def print_advice(module, parts):
    """The linter's advice on the checked files, for languages that have one."""
    try:
        advice = lint.run(module, parts)
    except CourseError as error:
        advice = [str(error)]
    if not advice:
        return
    print("\nAdvice (doesn't affect passing):")
    for line in advice[:MAX_MESSAGES]:
        print(f"    {line}")
    if len(advice) > MAX_MESSAGES:
        print(f"    ... and {len(advice) - MAX_MESSAGES} more")


def current_module(course):
    """Return the first module, in course order, with a failing test, and its results."""
    for module in course.modules:
        results = tests.run(module)
        if not tests.all_passed(results):
            return module, results
    return None, None


def status_line(part, results):
    passed = sum(result.passed for result in results)
    mark = "✓" if passed == len(results) else "✗"
    if len(results) == 1:
        return f"{mark} {part}"
    return f"{mark} {part}: {passed} of {len(results)} tests pass"
