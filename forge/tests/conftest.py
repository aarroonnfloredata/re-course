import re
import shutil
from pathlib import Path

import pytest
import yaml

from forge.new_course import create

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "examples/python/implement-strings"
BASH_FIXTURE = ROOT / "runtime/tests/fixtures/bash-course"


def copy_course(source, tmp_path):
    """Copy a course. Its runtime path is made absolute, since the copy no
    longer sits inside re-course."""
    target = tmp_path / "course"
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", ".venv", "uv.lock"))
    pyproject = target / "pyproject.toml"
    pyproject.write_text(re.sub(r'path = "[^"]*"', f'path = "{ROOT / "runtime"}"',
                                pyproject.read_text()))
    return target


@pytest.fixture
def course(tmp_path):
    """A copy of the golden example."""
    return copy_course(GOLDEN, tmp_path)


@pytest.fixture
def bash_course(tmp_path):
    """A copy of the runtime's bash fixture course."""
    return copy_course(BASH_FIXTURE, tmp_path)


@pytest.fixture
def root(tmp_path):
    """A minimal copy of re-course: the template, the real runtime and an empty workspace."""
    shutil.copytree(ROOT / "templates", tmp_path / "templates")
    (tmp_path / "runtime").symlink_to(ROOT / "runtime")
    (tmp_path / "workspace").mkdir()
    return tmp_path


def edit(path, old, new):
    """Replace the first `old` in a file, failing if it isn't there."""
    text = path.read_text()
    assert old in text, f"{old!r} not found in {path}"
    path.write_text(text.replace(old, new, 1))


OBJECTIVES = ["Do one thing", "Do another thing", "Do a third thing"]


def module(module_id, **fields):
    entry = {"id": module_id, "title": module_id, "exercise_type": "implement",
             "introduces": [module_id], "objectives": OBJECTIVES, "prerequisites": [],
             "sources": ["pytutorial#text"], "exercise": "Write a function."}
    entry.update(fields)
    return entry


def write_outline(course, plan):
    (course / "outline.yaml").write_text(yaml.safe_dump(plan, sort_keys=False))


@pytest.fixture
def new_course(root):
    """A course straight from /new-course, with a brief and one ingested source."""
    course = create("demo", "Demo", "python", "A demo.", root=root)
    brief = yaml.safe_load((course / "brief.yaml").read_text())
    brief["sources"] = [{"id": "notes", "path": "notes.md"}]
    (course / "brief.yaml").write_text(yaml.safe_dump(brief))
    (course / "sources/notes.md").write_text(
        "---\nid: notes\ntitle: Notes\n---\n\n# Notes {#notes}\n\nIntro text.\n\n"
        "## Loops {#loops}\n\nfor and while.\n")
    return course
