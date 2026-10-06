import pytest
import yaml
from conftest import edit

from forge import outline
from forge.new_course import create
from forge.validate import validate

OBJECTIVES = ["Do one thing", "Do another thing", "Do a third thing"]


def module(module_id, **fields):
    entry = {"id": module_id, "title": module_id, "exercise_type": "implement",
             "introduces": [module_id], "objectives": OBJECTIVES, "prerequisites": [],
             "sources": ["pytutorial#text"], "exercise": "Write a function."}
    entry.update(fields)
    return entry


def write_outline(course, plan):
    (course / "outline.yaml").write_text(yaml.safe_dump(plan, sort_keys=False))


def problems(course, **options):
    return validate(course, **options).problems


def assert_found(found, *expected):
    for text in expected:
        assert any(text in problem for problem in found), f"no problem mentions {text!r}:\n" + "\n".join(found)


def test_golden_outline_passes(course):
    assert problems(course, outline_only=True) == []


def test_outline_problems(course):
    edit(course / "brief.yaml", "project_style: independent", "project_style: cumulative")
    write_outline(course, {
        "modules": [
            module("01-indexing", introduces=["Indexing"], prerequisites=["02-methods"]),
            module("03-methods", introduces=["indexing"], sources=["pystdtypes#nope"]),
        ],
        "left_out": [{"section": "pytutorial#text", "reason": "not needed"}],
    })
    assert_found(
        problems(course, outline_only=True),
        "01-indexing: prerequisite 02-methods is not an earlier module",
        "03-methods: is module 2, so its ID must start with 02-",
        "03-methods: 'indexing' is already introduced by 01-indexing",
        "pystdtypes#nope: sources/pystdtypes.md has no section {#nope}",
        "left_out pytutorial#text is also used by a module",
        "a cumulative course needs a scenario",
    )


def test_outline_schema(course):
    write_outline(course, {"modules": [module("01-strings", objectives=["Only one"])]})
    assert_found(problems(course, outline_only=True), "objectives: ['Only one'] is too short")


def test_built_module_must_match_the_outline(course):
    edit(course / "outline.yaml", "Get single characters", "Get characters")
    assert_found(problems(course, execute=False), "module.yaml: `objectives` doesn't match outline.yaml")


def test_course_yaml_must_match_the_outline(course):
    plan = yaml.safe_load((course / "outline.yaml").read_text())
    plan["modules"].append(module("02-more", prerequisites=["01-strings"],
                                  sources=["pystdtypes#str.split"]))
    write_outline(course, plan)
    assert_found(problems(course, execute=False), "course.yaml: modules don't match outline.yaml")


@pytest.fixture
def new_course(root):
    """A course straight from /new-course, with a brief and one ingested source."""
    course = create("demo", "Demo", "python", "A demo.", root=root)
    brief = yaml.safe_load((course / "brief.yaml").read_text())
    brief["sources"] = [{"id": "notes", "path": "notes.md"}]
    (course / "brief.yaml").write_text(yaml.safe_dump(brief))
    (course / "sources/notes.md").write_text(
        "---\nid: notes\ntitle: Notes\n---\n\n# Notes {#notes}\n\nIntro text.\n\n"
        "## Loops {#loops}\n\nfor and while.\n")
    return course


def test_approve_writes_the_module_list(new_course):
    assert_found(problems(new_course, execute=False), "course.yaml: modules: no modules yet; run /outline")
    write_outline(new_course, {
        "scenario": "A to-do list app.",
        "modules": [module("01-basics", sources=["notes#notes"]),
                    module("02-loops", sources=["notes#loops"], prerequisites=["01-basics"])],
    })
    assert outline.approve(new_course) == ["01-basics", "02-loops"]
    course_yaml = yaml.safe_load((new_course / "course.yaml").read_text())
    assert course_yaml["modules"] == ["01-basics", "02-loops"]
    assert course_yaml["title"] == "Demo"
    # The plan is fine; what's left is building the modules.
    assert problems(new_course, execute=False) == [
        "module 01-basics is not built yet (no modules/01-basics/); run /build-module 01",
        "module 02-loops is not built yet (no modules/02-loops/); run /build-module 02",
    ]


def test_approve_refuses_an_outline_with_problems(new_course):
    write_outline(new_course, {"modules": [module("02-basics", sources=["notes#notes"])]})
    with pytest.raises(outline.OutlineError, match="must start with 01-"):
        outline.approve(new_course)
    assert yaml.safe_load((new_course / "course.yaml").read_text())["modules"] == []


def test_sections_and_show(new_course, capsys):
    write_outline(new_course, {
        "modules": [module("01-basics", sources=["notes#notes"])],
        "left_out": [{"section": "notes#loops", "reason": "Later."}],
    })
    assert outline.main(["sections", str(new_course)]) == 0
    out = capsys.readouterr().out
    assert "notes (" in out
    assert "#loops  Loops  (3 words)" in out
    assert outline.main(["show", str(new_course)]) == 0
    out = capsys.readouterr().out
    assert "01-basics  01-basics" in out
    assert "  Objectives:  1. Do one thing" in out
    assert "notes#loops: Later." in out
