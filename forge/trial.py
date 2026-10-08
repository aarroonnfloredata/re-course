"""Copy a course's learner files into a trial folder, to take the course as a
learner without changing the workspace's starter files.

    uv run python -m forge.trial <course> [--fresh]

The copy goes next to the course (`workspace/<course>-trial/`), so it stays
gitignored and finds the runtime the same way. /publish removes it. Its
course.yaml lists only the modules built so far.
"""

import argparse
import shutil
import sys
from pathlib import Path

import yaml

from .outline import write_modules

# What a learner gets; everything else (brief, outline, sources) is authoring only.
LEARNER_FILES = ["course.yaml", "pyproject.toml", "uv.lock", "README.md", ".gitignore",
                 "modules", "checkpoints"]
SKIP = shutil.ignore_patterns("solution", "broken", "__pycache__", ".venv", ".pytest_cache")


class TrialError(Exception):
    pass


def trial_dir(course_dir):
    course_dir = Path(course_dir)
    return course_dir.parent / f"{course_dir.name}-trial"


def copy_learner_files(course_dir, target):
    """Copy only what a learner gets: no solutions, broken variants, brief,
    outline or sources."""
    course_dir, target = Path(course_dir), Path(target)
    target.mkdir(parents=True)
    for name in LEARNER_FILES:
        source = course_dir / name
        if source.is_dir():
            shutil.copytree(source, target / name, ignore=SKIP)
        elif source.is_file():
            shutil.copy2(source, target / name)


def split_modules(course_dir):
    """The module IDs in course.yaml: those built (with a module.yaml), and
    those not built yet."""
    course_dir = Path(course_dir)
    data = yaml.safe_load((course_dir / "course.yaml").read_text(encoding="utf-8")) or {}
    module_ids = data.get("modules") or []
    built = [m for m in module_ids if (course_dir / "modules" / m / "module.yaml").is_file()]
    return built, [m for m in module_ids if m not in built]


def create(course_dir, fresh=False):
    course_dir = Path(course_dir)
    if not (course_dir / "course.yaml").is_file():
        raise TrialError(f"no course.yaml in {course_dir}")
    target = trial_dir(course_dir)
    if target.exists():
        if not fresh:
            raise TrialError(f"{target} already exists; use --fresh to replace it "
                             "(your work there will be lost)")
        shutil.rmtree(target)
    copy_learner_files(course_dir, target)
    built, unbuilt = split_modules(course_dir)
    if unbuilt:  # learn stops at a listed module that doesn't exist
        write_modules(target / "course.yaml", built)
    return target


def remove(course_dir):
    """Delete the course's trial folder, if there is one. Returns whether it existed."""
    target = trial_dir(course_dir)
    if target.exists():
        shutil.rmtree(target)
        return True
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m forge.trial",
                                     description="Copy a course's learner files to try it out.")
    parser.add_argument("course", help="the course folder, e.g. workspace/bash-basics")
    parser.add_argument("--fresh", action="store_true", help="replace an existing trial folder")
    args = parser.parse_args(argv)
    try:
        target = create(args.course, fresh=args.fresh)
    except TrialError as error:
        print(f"forge.trial: {error}", file=sys.stderr)
        return 1
    _, unbuilt = split_modules(args.course)
    if unbuilt:
        print(f"Left out the modules not built yet: {', '.join(unbuilt)}")
    print(f"Created {target}/. Take the course there:\n\n    cd {target} && uv run learn next")
    return 0


if __name__ == "__main__":
    sys.exit(main())
