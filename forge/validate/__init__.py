"""Validate a course workspace against the spec.

    uv run python -m forge.validate <course> [module ...] [--static | --outline]

The validator judges; agents fix what it reports.
"""

from pathlib import Path

from . import core, implement, outline, refactor
from .report import Report, Section
from .runner import RunnerError, run_jobs

EXERCISE_TYPES = {"implement": implement, "refactor": refactor}


def validate(course_dir, modules=None, execute=True, outline_only=False):
    """Check a course and return a Report. `modules` are IDs or numbers (default:
    all); `execute=False` skips the checks that run code; `outline_only` checks
    just brief.yaml and outline.yaml, for before the outline is approved."""
    course_dir = Path(course_dir)
    report = Report(str(course_dir))
    if outline_only:
        report.groups.append(("course", check_plan(course_dir)))
        return report

    section, course = core.check_course(course_dir)
    sections = [section]
    report.groups.append(("course", sections))
    if course is None:
        return report
    if (course_dir / "outline.yaml").is_file():
        outline_section, plan = outline.check_outline(course_dir, course.source_ids, course.project_style)
        if plan is not None and list(plan) != course.module_ids:
            outline_section.add("course.yaml: modules don't match outline.yaml; approve the "
                                "outline again (python -m forge.outline approve)")
        course.outline = plan
        sections.append(outline_section)

    for module_id in resolve(course, modules):
        module_dir = course_dir / "modules" / module_id
        if not module_dir.is_dir():
            report.groups.append((module_id, [Section("files", [f"modules/{module_id}/ doesn't exist"])]))
            continue
        sections, module = core.check_module(course, module_dir)
        exercise_type = EXERCISE_TYPES.get(module.data["exercise_type"]) if module else None
        if exercise_type is not None:
            sections += exercise_type.static(module)
            if execute:
                sections += run_checks(module, exercise_type)
        report.groups.append((module_id, sections))
    return report


def check_plan(course_dir):
    brief_section = Section("brief.yaml")
    brief = core.load_yaml(course_dir / "brief.yaml", brief_section)
    if not isinstance(brief, dict):
        if brief is not None:
            brief_section.add("brief.yaml: must be a mapping")
        return [brief_section]
    source_ids = core.check_brief(brief, brief_section)
    outline_section, _ = outline.check_outline(course_dir, source_ids, brief.get("project_style"))
    return [brief_section, outline_section]


def resolve(course, names):
    if not names:
        return [module_id for module_id in course.module_ids
                if (course.dir / "modules" / module_id).is_dir()]
    found = []
    for name in names:
        matches = [module_id for module_id in course.module_ids
                   if module_id == name or module_id.startswith(f"{name}-")]
        found.append(matches[0] if matches else name)
    return found


def run_checks(module, exercise_type):
    jobs = {**core.jobs(module), **exercise_type.jobs(module)}
    try:
        results = run_jobs(module.course.dir, jobs)
    except RunnerError as error:
        return [Section("running checks", [str(error)])]
    return core.check_results(module, results) + exercise_type.check(module, results)
