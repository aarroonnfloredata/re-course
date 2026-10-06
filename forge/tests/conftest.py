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


def edit(path, old, new):
    """Replace the first `old` in a file, failing if it isn't there."""
    text = path.read_text()
    assert old in text, f"{old!r} not found in {path}"
    path.write_text(text.replace(old, new, 1))
