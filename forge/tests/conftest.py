import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "examples/python/implement-strings"


@pytest.fixture
def course(tmp_path):
    """A copy of the golden example. Its runtime path is made absolute, since the
    copy no longer sits inside re-course."""
    target = tmp_path / "course"
    shutil.copytree(GOLDEN, target, ignore=shutil.ignore_patterns("__pycache__", ".venv", "uv.lock"))
    pyproject = target / "pyproject.toml"
    pyproject.write_text(
        pyproject.read_text().replace('"../../../runtime"', f'"{ROOT / "runtime"}"')
    )
    return target


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
