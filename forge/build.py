"""Prepare a module for /build-module.

    uv run python -m forge.build init <course> <module> [--fresh]

Creates modules/<id>/ with its empty folders and a module.yaml written from the
module's entry in outline.yaml, so the two can't drift apart. <module> is an
ID or a number (`01`).
"""

import argparse
import shutil
import sys
from pathlib import Path

import yaml

FOLDERS = ["challenges", "exercise", "tests", "solution", "broken"]


class BuildError(Exception):
    pass


def init(course_dir, name, fresh=False):
    course_dir = Path(course_dir)
    outline = read(course_dir / "outline.yaml", "run /outline first")
    course = read(course_dir / "course.yaml", "is this a course folder?")
    matches = [entry for entry in outline.get("modules") or []
               if entry["id"] == name or entry["id"].startswith(f"{name}-")]
    if not matches:
        raise BuildError(f"no module {name!r} in outline.yaml")
    entry = matches[0]
    if entry["id"] not in (course.get("modules") or []):
        raise BuildError(f"{entry['id']} is not in course.yaml; approve the outline first "
                         "(python -m forge.outline approve)")

    target = course_dir / "modules" / entry["id"]
    if target.exists():
        if not fresh:
            raise BuildError(f"modules/{entry['id']}/ already exists; use --fresh to delete "
                             "and rebuild it")
        shutil.rmtree(target)
    for folder in FOLDERS:
        (target / folder).mkdir(parents=True)
    module = {
        "id": entry["id"],
        "title": entry["title"],
        "exercise_type": entry["exercise_type"],
        "language": course["language"],
        "prerequisites": entry["prerequisites"],
        "objectives": entry["objectives"],
        "sources": entry["sources"],
    }
    (target / "module.yaml").write_text(
        yaml.safe_dump(module, sort_keys=False, allow_unicode=True, width=1000), encoding="utf-8")
    return target


def read(path, hint):
    if not path.is_file():
        raise BuildError(f"no {path.name} in {path.parent}; {hint}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m forge.build",
                                     description="Prepare a module for /build-module.")
    parser.add_argument("command", choices=["init"])
    parser.add_argument("course", help="the course folder, e.g. workspace/bash-basics")
    parser.add_argument("module", help="module ID or number, e.g. 01")
    parser.add_argument("--fresh", action="store_true", help="delete an existing module first")
    args = parser.parse_args(argv)
    try:
        target = init(args.course, args.module, fresh=args.fresh)
    except BuildError as error:
        print(f"forge.build: {error}", file=sys.stderr)
        return 1
    print(f"Created {target}/ with module.yaml from outline.yaml.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
