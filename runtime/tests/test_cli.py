import yaml

from learn.cli import main


def test_next_points_to_the_first_unfinished_module(course_dir, capsys):
    assert main(["next"]) == 0
    out = capsys.readouterr().out
    assert "Next: Strings: Indexing, Slicing and Methods (01-strings)" in out
    assert "Lesson: modules/01-strings/lesson.md" in out
    assert "✗ c1" in out
    assert "✗ exercise: 0 of 16 tests pass" in out


def test_next_when_everything_passes(course_dir, finish, capsys):
    finish()
    assert main(["next"]) == 0
    assert "Every module passes" in capsys.readouterr().out


def test_check_current_module(course_dir, capsys):
    assert main(["check"]) == 1
    out = capsys.readouterr().out
    assert "initials() is not written yet." in out
    assert "4 of 4 still failing." in out


def test_check_one_challenge(course_dir, capsys):
    assert main(["check", "c1"]) == 1
    out = capsys.readouterr().out
    assert "last_char() is not written yet." in out
    assert "c2" not in out


def test_check_module_and_part(course_dir, finish, capsys):
    finish()
    assert main(["check", "01", "exercise"]) == 0
    out = capsys.readouterr().out
    assert "✓ exercise: 16 of 16 tests pass" in out
    assert "All passing." in out


def test_check_shows_the_hint(course_dir, capsys):
    challenge = course_dir / "modules/01-strings/challenges/c3.py"
    challenge.write_text('def count_words(text):\n    return len(text.split(" "))\n')
    assert main(["check", "c3"]) == 1
    out = capsys.readouterr().out
    assert "count_words('  lots   of   space ') should return 3, but returned 10." in out
    assert "Hint: split() with no argument" in out


def test_a_module_not_built_yet_doesnt_stop_the_ones_before_it(course_dir, finish, capsys):
    course_file = course_dir / "course.yaml"
    data = yaml.safe_load(course_file.read_text())
    data["modules"].append("02-lists")
    course_file.write_text(yaml.safe_dump(data))
    assert main(["next"]) == 0
    assert "Next: Strings: Indexing, Slicing and Methods (01-strings)" in capsys.readouterr().out
    assert main(["check", "01", "c1"]) == 1
    finish()
    assert main(["next"]) == 2
    assert "Missing file" in capsys.readouterr().err


def test_check_unknown_part(course_dir, capsys):
    assert main(["check", "c9"]) == 2
    assert "has no part called 'c9'" in capsys.readouterr().err


def test_outside_a_course(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["next"]) == 2
    assert "No course.yaml found" in capsys.readouterr().err


def test_quiz_all_correct(course_dir, monkeypatch, capsys):
    questions = yaml.safe_load((course_dir / "modules/01-strings/quiz.yaml").read_text())
    replies = iter(str(question["answer"] + 1) for question in questions)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(replies))
    assert main(["quiz", "01"]) == 0
    assert f"Score: {len(questions)} of {len(questions)}" in capsys.readouterr().out


def test_quiz_stopped_with_ctrl_d(course_dir, monkeypatch, capsys):
    def end_of_input(prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", end_of_input)
    assert main(["quiz", "01"]) == 1
    assert "Quiz stopped." in capsys.readouterr().out
