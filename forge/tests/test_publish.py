import shutil

import pytest
from conftest import GOLDEN, edit

from forge import publish, trial
from forge.publish import PublishError


@pytest.fixture
def workspace_course(root):
    """The golden example as a course in a minimal re-course copy, where the
    runtime is two folders up, as for any workspace course."""
    course = root / "workspace/strings"
    shutil.copytree(GOLDEN, course, ignore=shutil.ignore_patterns("__pycache__", ".venv", "uv.lock"))
    edit(course / "pyproject.toml", '"../../../runtime"', '"../../runtime"')
    return course


def test_publish(workspace_course, root):
    trial.create(workspace_course)
    published = publish.publish(workspace_course, shared_dir=root / "shared-workspace")
    target = root / "shared-workspace/strings"
    assert published.target == target
    assert published.modules == ["01-strings"]
    assert published.removed_trial and not trial.trial_dir(workspace_course).exists()
    for name in ["course.yaml", "pyproject.toml", "uv.lock", "README.md",
                 "modules/01-strings/lesson.md", "modules/01-strings/tests/test_exercise.py"]:
        assert (target / name).exists(), name
    for name in ["brief.yaml", "outline.yaml", "sources", ".venv",
                 "modules/01-strings/solution", "modules/01-strings/broken"]:
        assert not (target / name).exists(), name


def test_validator_problems_block_publishing(workspace_course, root):
    edit(workspace_course / "modules/01-strings/recap.md", "(objective 4)", "(objective 9)")
    with pytest.raises(PublishError, match="objective 9 doesn't exist"):
        publish.publish(workspace_course, shared_dir=root / "shared-workspace")
    assert not (root / "shared-workspace/strings").exists()


def test_unknown_licence_needs_confirmation(workspace_course, root):
    source = workspace_course / "sources/pytutorial.md"
    text = source.read_text()
    start, end = text.index("license:"), text.index("excerpt:")
    # Quoted, as ingest writes it.
    source.write_text(text[:start] + "license: 'unknown: check before publishing'\n" + text[end:])
    with pytest.raises(PublishError, match=r"pytutorial \(cited by 01-strings\)"):
        publish.publish(workspace_course, shared_dir=root / "shared-workspace")
    published = publish.publish(workspace_course, accept_unknown_licenses=True,
                                shared_dir=root / "shared-workspace")
    assert published.unknown_licenses == {"pytutorial": ["01-strings"]}


def test_publishing_again_replaces_the_copy(workspace_course, root):
    shared = root / "shared-workspace"
    publish.publish(workspace_course, shared_dir=shared)
    (shared / "strings/edited-by-hand.txt").write_text("gone after the next publish")
    publish.publish(workspace_course, shared_dir=shared)
    assert not (shared / "strings/edited-by-hand.txt").exists()
