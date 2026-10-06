import shutil
from pathlib import Path

import pytest

GOLDEN = Path(__file__).resolve().parents[2] / "examples/python/implement-strings"
GOLDEN_MODULE = GOLDEN / "modules/01-strings"
BASH_COURSE = Path(__file__).resolve().parent / "fixtures/bash-course"
BASH_MODULE = BASH_COURSE / "modules/01-greetings"

collect_ignore = ["fixtures"]  # course tests, run by the tests below


def copy_course(source, tmp_path, monkeypatch):
    target = tmp_path / "course"
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", ".venv"))
    monkeypatch.chdir(target)
    return target


@pytest.fixture
def course_dir(tmp_path, monkeypatch):
    """A fresh copy of the golden course, with the working directory inside it."""
    return copy_course(GOLDEN, tmp_path, monkeypatch)


@pytest.fixture
def bash_course_dir(tmp_path, monkeypatch):
    """A fresh copy of the bash fixture course, with the working directory inside it."""
    return copy_course(BASH_COURSE, tmp_path, monkeypatch)


@pytest.fixture
def finish(course_dir):
    """Copy a module's solution over its learner files, as if the learner finished it."""

    def finish_module(module_id="01-strings"):
        module_dir = course_dir / "modules" / module_id
        shutil.copytree(module_dir / "solution", module_dir, dirs_exist_ok=True)

    return finish_module
