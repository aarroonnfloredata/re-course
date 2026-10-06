"""Helpers for /outline.

    uv run python -m forge.outline sections <course>   # each source's sections
    uv run python -m forge.outline show <course>       # the outline, for review
    uv run python -m forge.outline approve <course>    # check it, write course.yaml modules
"""

import re
import sys
import textwrap
from pathlib import Path

import yaml

from .validate import validate

HEADING = re.compile(r"^(#{1,6}) (.*?) \{#([^}]+)\}\s*$")
WIDTH = 79


class OutlineError(Exception):
    pass


def sections(course_dir):
    """Each source's headings with their IDs and word counts, indented by level."""
    lines = []
    for path in sorted(Path(course_dir, "sources").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        body = text.split("---\n", 2)[2] if text.startswith("---\n") else text
        found, current = [], None
        for line in body.split("\n"):
            match = HEADING.match(line)
            if match:
                current = [len(match.group(1)), match.group(2), match.group(3), 0]
                found.append(current)
            elif current is not None:
                current[3] += len(line.split())
        lines.append(f"{path.stem} ({len(body.split()):,} words)")
        for level, title, section_id, words in found:
            lines.append(f"{'  ' * (level - 1)}  #{section_id}  {title}  ({words:,} words)")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def show(course_dir):
    """The outline as readable text, for the author to review."""
    plan = load(course_dir)
    lines = []
    if plan.get("scenario"):
        lines += wrapped("Scenario: ", plan["scenario"], "") + [""]
    for module in plan["modules"]:
        lines.append(f"{module['id']}  {module['title']}")
        lines += wrapped("  Introduces:  ", ", ".join(module["introduces"]))
        for number, objective in enumerate(module["objectives"], 1):
            label = "  Objectives:  " if number == 1 else " " * 15
            lines += wrapped(label + f"{number}. ", objective)
        if module["prerequisites"]:
            lines += wrapped("  Needs:       ", ", ".join(module["prerequisites"]))
        lines += wrapped("  Sources:     ", ", ".join(module["sources"]))
        lines += wrapped("  Exercise:    ", module["exercise"])
        lines.append("")
    if plan.get("left_out"):
        lines.append("Left out:")
        for item in plan["left_out"]:
            lines += wrapped("  ", f"{item['section']}: {item['reason']}")
    return "\n".join(lines).rstrip() + "\n"


def approve(course_dir):
    """Check the outline and write its module IDs into course.yaml."""
    course_dir = Path(course_dir)
    report = validate(course_dir, outline_only=True)
    if report.problems:
        raise OutlineError("the outline has problems:\n" + "\n".join(report.problems))
    module_ids = [module["id"] for module in load(course_dir)["modules"]]
    write_modules(course_dir / "course.yaml", module_ids)
    return module_ids


def write_modules(path, module_ids):
    """Replace the `modules:` list in course.yaml, keeping everything else."""
    new = ["modules:  # module IDs in learning order; from outline.yaml"]
    new += [f"  - {module_id}" for module_id in module_ids]
    lines, inside, replaced = [], False, False
    for line in path.read_text(encoding="utf-8").split("\n"):
        if line.startswith("modules:"):
            lines += new
            inside = replaced = True
        elif inside and re.match(r"\s*- ", line):
            continue
        else:
            inside = False
            lines.append(line)
    if not replaced:
        lines = [line for line in lines if line] + new + [""]
    path.write_text("\n".join(lines), encoding="utf-8")


def load(course_dir):
    path = Path(course_dir) / "outline.yaml"
    if not path.is_file():
        raise OutlineError(f"no outline.yaml in {course_dir}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def wrapped(label, text, indent=None):
    indent = " " * len(label) if indent is None else indent
    return textwrap.wrap(" ".join(text.split()), WIDTH, initial_indent=label,
                         subsequent_indent=indent, break_on_hyphens=False) or [label.rstrip()]


def main(argv=None):
    args = argv if argv is not None else sys.argv[1:]
    commands = {"sections": sections, "show": show, "approve": approve}
    if len(args) != 2 or args[0] not in commands:
        print("usage: python -m forge.outline {sections|show|approve} <course>", file=sys.stderr)
        return 2
    command, course_dir = args
    try:
        result = commands[command](course_dir)
    except OutlineError as error:
        print(f"forge.outline: {error}", file=sys.stderr)
        return 1
    if command == "approve":
        print(f"Approved: course.yaml now lists {len(result)} module(s): {', '.join(result)}")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
