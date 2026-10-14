import json
import shutil

from conftest import edit

from forge.validate import EXERCISE_TYPES, validate
from forge.validate.__main__ import main
from forge.validate.core import SPEC

MODULE = "modules/01-strings"


def assert_found(problems, *expected):
    for text in expected:
        assert any(text in problem for problem in problems), f"no problem mentions {text!r}:\n" + "\n".join(problems)


def test_golden_example_passes(course):
    assert validate(course).problems == []


def test_exercise_types_agree():
    """spec/exercise-types/, both schemas and the validator know the same types."""
    specs = {path.stem for path in (SPEC / "exercise-types").glob("*.md")}
    module = json.loads((SPEC / "schemas/module.schema.json").read_text())
    outline = json.loads((SPEC / "schemas/outline.schema.json").read_text())
    assert set(module["properties"]["exercise_type"]["enum"]) == specs
    assert set(outline["$defs"]["module"]["properties"]["exercise_type"]["enum"]) == specs
    assert set(EXERCISE_TYPES) == specs


def test_static_problems(course):
    module = course / MODULE
    edit(module / "module.yaml", "id: 01-strings", "id: 01-text")
    edit(module / "lesson.md", "index 0. ([pytutorial#text])", "index 0. ([pytutorial#numbers])")
    edit(module / "lesson.md", "1. Get single characters", "1. Get characters")
    edit(module / "lesson.md", "read [`recap.md`](recap.md)", "read `recap.md`")
    edit(module / "lesson.md", "```output\nR2D2\n```\n", "")
    (module / "challenges/c3.py").unlink()
    edit(module / "quiz.yaml", 'options: ["i", "r", "a"]\n  answer: 1', 'options: ["i", "r", "a"]\n  answer: 3')
    edit(module / "recap.md", "is an error. (objective 1)", "is an error.")
    variant = module / "broken/slugify-keeps-case/exercise/text_tools.py"
    edit(variant, "# Broken variant: ", "# ")
    edit(course / "brief.yaml", "    url: https://docs.python.org/3/library/stdtypes.html",
         "    url: https://docs.python.org/3/library/stdtypes.html\n    restricted: sometimes\n"
         "    exclude: .ad")

    problems = validate(course, execute=False).problems
    assert_found(
        problems,
        "id '01-text' doesn't match the folder name",
        "pytutorial#numbers is cited but not defined",
        "don't match module.yaml sources",
        "has no section {#numbers}",
        "the objectives list doesn't match module.yaml",
        "mentions recap.md without linking it",
        "\"What's next\" doesn't link recap.md",
        "must be followed directly by an output block",
        "challenges/c3.*: missing for challenge c3",
        "solution/challenges/c3.py: there is no learner file",
        "q1: answer 3 is not an option",
        "point doesn't end with (objective N)",
        "no point for objective 1",
        "slugify-keeps-case/exercise/text_tools.py: the first line must be",
        "sources/1: restricted must be true or false",
        "sources/1: exclude must be a list of CSS selectors",
    )


def test_schema_problem(course):
    edit(course / MODULE / "quiz.yaml", 'options: ["ari", "Par", "ar"]', "options: [1, 2, 3]")
    assert_found(validate(course, execute=False).problems, "1 is not of type 'string'")


def test_problems_found_by_running_code(course):
    module = course / MODULE
    edit(module / "lesson.md", "```output\nJython\nPython\nhahaha\n```", "```output\nJython\nPython\nhaha\n```")
    edit(module / "quiz.yaml", 'options: ["HELLO", "hello", "Hello"]\n  answer: 1',
         'options: ["HELLO", "hello", "Hello"]\n  answer: 0')
    edit(module / "tests/test_exercise.py",
         '@pytest.mark.objective(2)\n@pytest.mark.parametrize("text"', '@pytest.mark.parametrize("text"')
    with open(module / "tests/test_challenges.py", "a") as tests:
        tests.write("\n\n@pytest.mark.objective(1)\ndef test_c1_always_passes():\n    pass\n")
    solution = (module / "solution/exercise/text_tools.py").read_text()
    (module / "broken/slugify-keeps-case/exercise/text_tools.py").write_text(
        "# Broken variant: identical to the solution\n" + solution)
    shutil.rmtree(module / "broken/mask-keeps-first-characters")

    problems = validate(course).problems
    assert_found(
        problems,
        "but the output block says 'Jython\\nPython\\nhaha\\n'",
        "q4: the code prints 'hello', but the marked answer is 'HELLO'",
        "test_exercise::test_mask_short_text_unchanged: declares no objective",
        "starter: test_challenges::test_c1_always_passes passes, so it checks nothing",
        "broken/slugify-keeps-case: no exercise test catches it",
        "broken/slugify-keeps-case/exercise/text_tools.py: changes no function",
        "no broken variant changes mask",
    )


def test_bash_fixture_passes(bash_course):
    assert validate(bash_course).problems == []


def test_bash_problems(bash_course):
    module = bash_course / "modules/01-greetings"
    edit(module / "solution/exercise/text.sh", 'echo "$1!"', "echo $1!")
    edit(bash_course / "pyproject.toml", '"re-course-learn[bash]"', '"re-course-learn"')
    problems = validate(bash_course).problems
    assert_found(
        problems,
        "pyproject.toml: dependencies must include re-course-learn[bash]",
        "solution/exercise/text.sh:12: Double quote to prevent globbing",
    )


def test_cli(course, capsys):
    assert main([str(course), "--static"]) == 0
    assert "No problems found." in capsys.readouterr().out
    edit(course / MODULE / "recap.md", "(objective 4)", "(objective 9)")
    assert main([str(course), "01", "--static"]) == 1
    assert "objective 9 doesn't exist" in capsys.readouterr().out


def test_cli_without_a_course(tmp_path, capsys):
    assert main([str(tmp_path)]) == 2
    assert "no course.yaml" in capsys.readouterr().err


REFACTOR_MODULE = "modules/01-long-method"


def test_refactor_example_passes(refactor_course):
    assert validate(refactor_course).problems == []


def test_refactor_problems(refactor_course):
    module = refactor_course / REFACTOR_MODULE
    edit(module / "tests/test_structure.py", "@pytest.mark.objective(3)\ndef test_no_comments",
         "@pytest.mark.objective(3)\ndef test_always_passes():\n    pass\n\n\n"
         "@pytest.mark.objective(3)\ndef test_no_comments")
    edit(module / "broken/comments-kept/exercise/receipt.py", "        return 0\n    return 4.95",
         "        return 0\n    return 5.95")
    edit(module / "broken/discount-ignores-threshold/exercise/receipt.py",
         'if code == "SAVE10":', 'if code == "SAVE10" and subtotal >= 39:')
    edit(module / "broken/printing-left-inline/exercise/receipt.py",
         "# Broken variant: smell:", "# Broken variant:")
    problems = validate(refactor_course).problems
    assert_found(
        problems,
        "starter: test_structure::test_always_passes passes, so it checks nothing",
        "but a smell variant must keep the behaviour",
        "broken/discount-ignores-threshold: no behaviour test catches it",
        "broken/printing-left-inline/exercise/receipt.py: the first line must name the kind",
    )


def test_refactor_behaviour_test_must_pass_on_the_starter(refactor_course):
    module = refactor_course / REFACTOR_MODULE
    edit(module / "tests/test_behaviour.py", "Total                      16.95",
         "Total                      17.95")
    assert_found(
        validate(refactor_course).problems,
        "starter: behaviour test test_behaviour::test_print_receipt_prints_the_same"
        "[small-order-pays-shipping] fails, so it pins down something the starter doesn't do",
    )


def test_refactor_needs_both_kinds_of_variant(refactor_course):
    module = refactor_course / REFACTOR_MODULE
    for variant in ("comments-kept", "printing-left-inline"):
        shutil.rmtree(module / "broken" / variant)
    assert_found(validate(refactor_course, execute=False).problems, "broken/: no smell variant")
