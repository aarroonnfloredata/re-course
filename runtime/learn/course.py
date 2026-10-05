"""Find and load a course: course.yaml, then each module's module.yaml."""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

COURSE_FILE = "course.yaml"
CHALLENGE_MARKER = re.compile(r"<!-- challenge id=(\w+) objective=\d+ -->")


class CourseError(Exception):
    """A problem with the course or the command line, shown to the learner as is."""


@dataclass
class Module:
    id: str
    path: Path
    title: str
    language: str
    challenges: list[str]  # challenge IDs in lesson order


@dataclass
class Course:
    root: Path
    title: str
    modules: list[Module]

    def find_module(self, name):
        """Find a module by its ID or its number, e.g. "01-strings" or "01"."""
        for module in self.modules:
            if name == module.id or module.id.startswith(f"{name}-"):
                return module
        return None


def find_root(start):
    """Return the nearest folder at or above `start` that has a course.yaml."""
    start = Path(start).resolve()
    for folder in [start, *start.parents]:
        if (folder / COURSE_FILE).is_file():
            return folder
    raise CourseError(
        f"No {COURSE_FILE} found in {start} or its parent folders. "
        "Run learn inside a course folder."
    )


def load_course(root):
    root = Path(root)
    data = read_yaml(root / COURSE_FILE)
    modules = [
        load_module(root / "modules" / module_id)
        for module_id in require(data, "modules", root / COURSE_FILE)
    ]
    return Course(root=root, title=require(data, "title", root / COURSE_FILE), modules=modules)


def load_module(path):
    module_file = path / "module.yaml"
    data = read_yaml(module_file)
    lesson = path / "lesson.md"
    lesson_text = lesson.read_text(encoding="utf-8") if lesson.is_file() else ""
    return Module(
        id=require(data, "id", module_file),
        path=path,
        title=require(data, "title", module_file),
        language=require(data, "language", module_file),
        challenges=CHALLENGE_MARKER.findall(lesson_text),
    )


def read_yaml(path):
    try:
        with open(path, encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        raise CourseError(f"Missing file: {path}") from None
    except yaml.YAMLError as error:
        raise CourseError(f"{path} is not valid YAML: {error}") from None


def require(data, key, path):
    if key not in data:
        raise CourseError(f"{path} has no `{key}` field.")
    return data[key]
