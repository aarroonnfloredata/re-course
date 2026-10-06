import tomllib

import pytest
import yaml
from conftest import edit

from forge import dependencies
from forge.new_course import NewCourseError, create
from forge.validate import validate


def test_create(root):
    course = create("demo", 'Python "Gotchas"', "python", "A short course.", root=root)
    assert course == root / "workspace/demo"
    for name in ["README.md", "pyproject.toml", "brief.yaml", "course.yaml", ".gitignore",
                 "uv.lock", "modules", "sources"]:
        assert (course / name).exists(), name
    assert not (course / ".git").exists()  # nothing inside re-course is its own repository
    for path in course.glob("*.*"):
        if path.is_file():
            assert "{{" not in path.read_text(), path.name
    assert yaml.safe_load((course / "course.yaml").read_text())["title"] == 'Python "Gotchas"'
    project = tomllib.loads((course / "pyproject.toml").read_text())["project"]
    assert project["name"] == "demo"
    assert project["description"] == 'Python "Gotchas": a re-course course'
    assert "A short course." in (course / "README.md").read_text()


@pytest.mark.parametrize(
    "name, language, message",
    [
        ("Demo Course", "python", "use lowercase letters"),
        ("demo", "cobol", "no runtime plugin for 'cobol'; supported: python"),
    ],
)
def test_create_rejects(root, name, language, message):
    with pytest.raises(NewCourseError, match=message):
        create(name, "Title", language, "Summary.", root=root)
    assert list((root / "workspace").iterdir()) == []


def test_create_refuses_an_existing_folder(root):
    (root / "workspace/demo").mkdir()
    with pytest.raises(NewCourseError, match="already exists"):
        create("demo", "Title", "python", "Summary.", root=root)


def test_dependencies_sync(root):
    course = create("demo", "Demo", "python", "Summary.", root=root)
    edit(course / "brief.yaml", "dependencies: []", 'dependencies: ["six"]')
    assert dependencies.sync(course) == ["six"]
    listed = tomllib.loads((course / "pyproject.toml").read_text())["project"]["dependencies"]
    assert listed == ["re-course-learn", "six"]
    assert 'name = "six"' in (course / "uv.lock").read_text()


def test_dependencies_must_be_a_list(root):
    course = create("demo", "Demo", "python", "Summary.", root=root)
    edit(course / "brief.yaml", "dependencies: []", "dependencies: six")
    with pytest.raises(dependencies.DependencyError, match="must be a list"):
        dependencies.sync(course)


def test_validator_flags_unsynced_dependencies(course):
    edit(course / "brief.yaml", "dependencies: []", 'dependencies: ["six"]')
    problems = validate(course, execute=False).problems
    assert any("doesn't list 'six' from brief.yaml" in problem for problem in problems)
