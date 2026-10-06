import shutil

import pytest
from conftest import BASH_MODULE

from learn import authoring
from learn.cli import main
from learn.course import load_course
from learn.languages import bash
from learn.stages import tests

BROKEN_VARIANTS = sorted(path.name for path in (BASH_MODULE / "broken").iterdir())


@pytest.fixture
def module(bash_course_dir):
    return load_course(bash_course_dir).modules[0]


def test_run_snippet():
    result = bash.run_snippet('set -- "a b" c\necho "$#"')
    assert result.returncode == 0
    assert result.stdout == "2\n"


def test_snippet_gets_no_input():
    assert bash.run_snippet("cat").stdout == ""


def test_starter_fails_every_part(module):
    results = tests.run(module)
    parts = tests.by_part(results, module)
    assert list(parts) == ["c1", "c2", "exercise"]
    assert not any(tests.all_passed(part_results) for part_results in parts.values())
    messages = {result.message for result in results}
    assert {"c1.sh is not written yet.", "twice() is not written yet.",
            "greet.sh is not written yet.", "shout() is not written yet."} <= messages


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


def test_failure_messages(module):
    shutil.copytree(module.path / "solution", module.path, dirs_exist_ok=True)
    (module.path / "challenges/c2.sh").write_text('twice() {\n    echo "$1 $1"\n')
    (module.path / "challenges/c1.sh").write_text("echo $#\n")
    shutil.copy(module.path / "broken/greet-overwrites-guests/exercise/greet.sh",
                module.path / "exercise/greet.sh")
    shutil.copy(module.path / "broken/shout-splits-words/exercise/text.sh",
                module.path / "exercise/text.sh")
    messages = {result.message for result in tests.run(module) if not result.passed}
    assert messages == {
        "challenges/c2.sh could not be loaded:\n"
        "    challenges/c2.sh: line 3: syntax error: unexpected end of file",
        "guests.txt held:\n    Ada\n"
        "After `bash exercise/greet.sh Grace`, guests.txt should hold:\n    Ada\n    Grace\n"
        "but it holds:\n    Grace\n"
        "Hint: > replaces a file; >> adds to it.",
        "`shout 'good  day'` should print:\n    good  day!\nbut printed:\n    good day!",
    }


def test_missing_function_and_wrong_status(module):
    shutil.copytree(module.path / "solution", module.path, dirs_exist_ok=True)
    (module.path / "challenges/c2.sh").write_text("double() {\n    echo \"$1 $1\"\n}\n")
    shutil.copy(module.path / "broken/greet-exits-zero-without-name/exercise/greet.sh",
                module.path / "exercise/greet.sh")
    messages = {result.message for result in tests.run(module) if not result.passed}
    assert messages == {
        "challenges/c2.sh has no function called twice.",
        "`bash exercise/greet.sh` should exit with status 2, but exited with 0.\n"
        "Hint: $# is the number of arguments; exit sets the status.",
    }


def test_stubs():
    assert bash.stubs(BASH_MODULE / "exercise/greet.sh") == ["greet.sh"]
    assert bash.stubs(BASH_MODULE / "exercise/text.sh") == ["shout", "count_lines"]
    assert bash.stubs(BASH_MODULE / "solution/exercise/text.sh") == []


@pytest.mark.parametrize(
    "variant, file, unit",
    [
        ("greet-exits-zero-without-name", "greet.sh", "greet.sh"),
        ("shout-splits-words", "text.sh", "shout"),
        ("count-lines-counts-words", "text.sh", "count_lines"),
    ],
)
def test_changed_units(variant, file, unit):
    original = BASH_MODULE / "solution/exercise" / file
    changed = BASH_MODULE / "broken" / variant / "exercise" / file
    assert bash.changed_units(original, changed) == [unit]


def test_comments_and_indentation_are_not_changes(tmp_path):
    original = tmp_path / "a/tools.sh"
    changed = tmp_path / "b/tools.sh"
    original.parent.mkdir()
    changed.parent.mkdir()
    original.write_text('#!/usr/bin/env bash\nhi() {\n    echo "hi"\n}\n')
    changed.write_text('#!/usr/bin/env bash\n# Broken variant: none\nhi() {\n  echo "hi"\n}\n')
    assert bash.changed_units(original, changed) == []


def test_lint(module):
    assert bash.lint(module.path, ["solution/exercise/text.sh", "lesson.md"]) == []
    [finding] = bash.lint(module.path, ["broken/shout-splits-words/exercise/text.sh"])
    assert finding.startswith("broken/shout-splits-words/exercise/text.sh:13: Double quote")
    assert finding.endswith("(https://www.shellcheck.net/wiki/SC2086)")


def test_check_shows_advice_without_failing(module, capsys):
    shutil.copytree(module.path / "solution", module.path, dirs_exist_ok=True)
    (module.path / "challenges/c1.sh").write_text('unused=1\necho "$#"\n')
    assert main(["check", "01"]) == 0
    out = capsys.readouterr().out
    assert "All passing." in out
    assert "Advice (doesn't affect passing):\n    challenges/c1.sh:1: unused appears unused" in out


def test_check_one_part_shows_advice_for_its_files_only(module, capsys):
    (module.path / "challenges/c1.sh").write_text('unused=1\necho "$#"\n')
    main(["check", "c2"])
    assert "Advice" not in capsys.readouterr().out


def test_lint_job():
    job = {"kind": "lint", "language": "bash", "folder": str(BASH_MODULE),
           "files": ["solution/exercise/greet.sh"]}
    assert authoring.run_job(job) == []
    assert authoring.run_job({**job, "language": "python"}) is None
