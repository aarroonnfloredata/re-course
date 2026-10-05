from learn.languages import python


def test_run_snippet():
    result = python.run_snippet('word = "Python"\nprint(word[-1])')
    assert result.returncode == 0
    assert result.stdout == "n\n"


def test_endless_loop_times_out(tmp_path, monkeypatch):
    monkeypatch.setattr(python, "TIMEOUT", 2)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_loop.py").write_text("def test_loop():\n    while True:\n        pass\n")
    [result] = python.run_tests(tmp_path)
    assert not result.passed
    assert "loop that never ends" in result.message
