import pytest
from conftest import GOLDEN_MODULE

from learn.course import load_course
from learn.stages import tests

BROKEN_VARIANTS = sorted(path.name for path in (GOLDEN_MODULE / "broken").iterdir())


@pytest.fixture
def module(course_dir):
    return load_course(course_dir).modules[0]


def test_starter_fails_every_part(module):
    parts = tests.by_part(tests.run(module), module)
    assert list(parts) == ["c1", "c2", "c3", "exercise"]
    assert not any(tests.all_passed(results) for results in parts.values())


def test_starter_failures_say_what_is_missing(module):
    messages = {result.message for result in tests.run(module)}
    assert "last_char() is not written yet." in messages
    assert "initials() is not written yet." in messages


def test_solution_passes(module):
    results = tests.run(module, overlays=[module.path / "solution"])
    assert results
    assert tests.all_passed(results)


@pytest.mark.parametrize("variant", BROKEN_VARIANTS)
def test_broken_variant_fails_only_the_exercise(module, variant):
    overlays = [module.path / "solution", module.path / "broken" / variant]
    parts = tests.by_part(tests.run(module, overlays=overlays), module)
    assert not tests.all_passed(parts["exercise"])
    assert all(tests.all_passed(parts[challenge]) for challenge in module.challenges)


def test_solution_folder_is_not_copied_into_the_run(module):
    # The learner's run must use the starter files, even in a workspace that
    # still has solution/ next to them.
    assert (module.path / "solution").is_dir()
    assert not tests.all_passed(tests.run(module))
