"""Create a course workspace from templates/course/.

    uv run python -m forge.new_course <name> --title "..." --language python --summary "..."

Fills in the template's placeholders, runs `git init` in the new folder (only
there; nothing is committed) and creates its uv.lock. The author fills in the
brief afterwards; see .claude/commands/new-course.md.
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .dependencies import DependencyError, lock

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class NewCourseError(Exception):
    pass


def create(name, title, language, summary, root=ROOT):
    """Create root/workspace/<name>/ and return its path."""
    if not NAME.match(name):
        raise NewCourseError(f"{name!r}: use lowercase letters, digits and hyphens, e.g. bash-basics")
    plugins = root / "runtime/learn/languages"
    if not (plugins / f"{language}.py").is_file():
        supported = sorted(path.stem for path in plugins.glob("*.py") if path.stem != "__init__")
        raise NewCourseError(f"no runtime plugin for {language!r}; supported: {', '.join(supported)}")
    for label, value in (("title", title), ("summary", summary)):
        if not value.strip():
            raise NewCourseError(f"the {label} is empty")
    target = root / "workspace" / name
    if target.exists():
        raise NewCourseError(f"workspace/{name} already exists")

    shutil.copytree(root / "templates/course", target)
    try:
        fill_placeholders(target, {"name": name, "title": title, "language": language,
                                   "summary": summary})
        (target / "modules").mkdir()
        (target / "sources").mkdir()
        git_init(target)
        lock(target)
    except (NewCourseError, DependencyError):
        shutil.rmtree(target)
        raise
    return target


def fill_placeholders(folder, values):
    for path in folder.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for key, value in values.items():
            if path.suffix in (".yaml", ".toml"):
                # The template puts these placeholders inside double quotes.
                value = value.replace("\\", "\\\\").replace('"', '\\"')
            text = text.replace("{{" + key + "}}", value)
        path.write_text(text, encoding="utf-8")


def git_init(folder):
    try:
        process = subprocess.run(["git", "init", "-q"], cwd=folder, capture_output=True, text=True)
    except FileNotFoundError:
        raise NewCourseError("git is not installed: https://git-scm.com/downloads") from None
    if process.returncode != 0:
        raise NewCourseError(f"git init failed: {process.stderr.strip()}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m forge.new_course",
                                     description="Create a course workspace from the template.")
    parser.add_argument("name", help="folder name, e.g. bash-basics")
    parser.add_argument("--title", required=True)
    parser.add_argument("--language", required=True)
    parser.add_argument("--summary", required=True, help="one sentence for the course README")
    args = parser.parse_args(argv)
    try:
        target = create(args.name, args.title, args.language, args.summary)
    except NewCourseError as error:
        print(f"forge.new_course: {error}", file=sys.stderr)
        return 1
    print(f"Created {target.relative_to(ROOT)}/. Next: fill in its brief.yaml.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
