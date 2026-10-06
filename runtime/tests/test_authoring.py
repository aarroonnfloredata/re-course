import io
import json

from learn import authoring
from learn.languages import python


def test_tests_job_reports_parts(course_dir):
    module = course_dir / "modules/01-strings"
    results = authoring.run_job({"kind": "tests", "module": str(module)})
    assert {result["part"] for result in results} == {"c1", "c2", "c3", "exercise"}
    assert not any(result["passed"] for result in results)


def test_tests_job_with_solution_overlay(course_dir):
    module = course_dir / "modules/01-strings"
    job = {"kind": "tests", "module": str(module), "overlays": [str(module / "solution")]}
    assert all(result["passed"] for result in authoring.run_job(job))


def test_snippets_job():
    job = {"kind": "snippets", "language": "python", "codes": ['print("a")', "1/0"]}
    ok, failing = authoring.run_job(job)
    assert ok == {"stdout": "a\n", "stderr": "", "returncode": 0}
    assert failing["returncode"] == 1
    assert "ZeroDivisionError" in failing["stderr"]


def test_objectives_job(course_dir):
    found = authoring.run_job({"kind": "objectives", "module": str(course_dir / "modules/01-strings")})
    assert found["test_exercise::test_initials"] == [1, 4]
    assert found["test_challenges::test_c3_count_words"] == [4]


def test_stubs_and_changed_units(course_dir):
    module = course_dir / "modules/01-strings"
    assert python.stubs(module / "exercise/text_tools.py") == ["initials", "slugify", "mask"]
    assert python.stubs(module / "solution/exercise/text_tools.py") == []
    variant = module / "broken/mask-keeps-first-characters/exercise/text_tools.py"
    assert python.changed_units(module / "solution/exercise/text_tools.py", variant) == ["mask"]


def test_main_reports_a_failing_job_and_continues(monkeypatch, capsys):
    jobs = [{"kind": "nonsense"}, {"kind": "snippets", "language": "python", "codes": ["print(1)"]}]
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(jobs)))
    authoring.main()
    error, snippets = json.loads(capsys.readouterr().out)
    assert "unknown job kind" in error["error"]
    assert snippets[0]["stdout"] == "1\n"
