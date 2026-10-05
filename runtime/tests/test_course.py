import pytest

from learn.course import CourseError, find_root, load_course


def test_find_root_from_a_subfolder(course_dir):
    assert find_root(course_dir / "modules/01-strings/exercise") == course_dir.resolve()


def test_find_root_outside_a_course(tmp_path):
    with pytest.raises(CourseError, match="No course.yaml found"):
        find_root(tmp_path)


def test_load_course(course_dir):
    course = load_course(course_dir)
    assert course.title == "Python Strings"
    assert [module.id for module in course.modules] == ["01-strings"]
    module = course.modules[0]
    assert module.language == "python"
    assert module.challenges == ["c1", "c2", "c3"]


def test_find_module_by_id_or_number(course_dir):
    course = load_course(course_dir)
    assert course.find_module("01-strings").id == "01-strings"
    assert course.find_module("01").id == "01-strings"
    assert course.find_module("02") is None


def test_missing_module_file(course_dir):
    (course_dir / "modules/01-strings/module.yaml").unlink()
    with pytest.raises(CourseError, match="Missing file"):
        load_course(course_dir)
