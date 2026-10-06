import subprocess

import pytest
import yaml
from conftest import module, write_outline

from forge import build, outline, trial
from forge.validate import validate


@pytest.fixture
def planned(new_course):
    """A new (cumulative) course with an approved one-module outline."""
    write_outline(new_course, {"scenario": "A to-do list app.",
                               "modules": [module("01-basics", sources=["notes#notes"])]})
    outline.approve(new_course)
    return new_course


# forge.build init


def test_init_writes_module_yaml_from_the_outline(planned):
    target = build.init(planned, "01")
    assert target == planned / "modules/01-basics"
    for folder in build.FOLDERS:
        assert (target / folder).is_dir()
    data = yaml.safe_load((target / "module.yaml").read_text())
    assert data == {
        "id": "01-basics", "title": "01-basics", "exercise_type": "implement",
        "language": "python", "prerequisites": [],
        "objectives": ["Do one thing", "Do another thing", "Do a third thing"],
        "sources": ["notes#notes"],
    }
    found = validate(planned, execute=False).problems
    assert not any("doesn't match outline.yaml" in problem for problem in found)


def test_init_needs_an_approved_module(new_course):
    write_outline(new_course, {"modules": [module("01-basics", sources=["notes#notes"])]})
    with pytest.raises(build.BuildError, match="approve the outline first"):
        build.init(new_course, "01")
    with pytest.raises(build.BuildError, match="no module '02'"):
        build.init(new_course, "02")


def test_init_refuses_an_existing_module_unless_fresh(planned):
    target = build.init(planned, "01-basics")
    (target / "lesson.md").write_text("draft")
    with pytest.raises(build.BuildError, match="already exists; use --fresh"):
        build.init(planned, "01")
    build.init(planned, "01", fresh=True)
    assert not (target / "lesson.md").exists()


# forge.trial


def test_trial_copies_only_the_learner_files(course):
    target = trial.create(course)
    assert target == course.parent / "course-trial"
    module_dir = target / "modules/01-strings"
    for name in ["lesson.md", "module.yaml", "quiz.yaml", "recap.md", "challenges/c1.py",
                 "exercise/text_tools.py", "tests/test_exercise.py"]:
        assert (module_dir / name).is_file(), name
    for name in ["solution", "broken"]:
        assert not (module_dir / name).exists(), name
    for name in ["brief.yaml", "outline.yaml", "sources"]:
        assert not (target / name).exists(), name
    assert (target / "course.yaml").is_file() and (target / "pyproject.toml").is_file()


def test_trial_runs_with_learn(course):
    target = trial.create(course)
    process = subprocess.run(["uv", "run", "--quiet", "learn", "next"], cwd=target,
                             capture_output=True, text=True)
    assert "Next: Strings: Indexing, Slicing and Methods (01-strings)" in process.stdout


def test_trial_refuses_to_overwrite_unless_fresh(course):
    target = trial.create(course)
    answer = target / "modules/01-strings/challenges/c1.py"
    answer.write_text("my answer")
    with pytest.raises(trial.TrialError, match="your work there will be lost"):
        trial.create(course)
    trial.create(course, fresh=True)
    assert answer.read_text() != "my answer"


def test_remove_trial(course):
    trial.create(course)
    assert trial.remove(course) is True
    assert not trial.trial_dir(course).exists()
    assert trial.remove(course) is False
