"""Validate a course workspace against the spec.

    uv run python -m forge.validate <course> [module ...] [--static]

The validator judges; agents fix what it reports.
"""

from pathlib import Path

from . import core, implement
from .report import Report, Section
from .runner import RunnerError, run_jobs

EXERCISE_TYPES = {"implement": implement}


def validate(course_dir, modules=None, execute=True):
    """Check a course and return a Report. `modules` are IDs or numbers (default:
    all); `execute=False` skips the checks that run code."""
    course_dir = Path(course_dir)
    report = Report(str(course_dir))
    section, course = core.check_course(course_dir)
    report.groups.append(("course", [section]))
    if course is None:
        return report

    for module_id in resolve(course, modules):
        module_dir = course_dir / "modules" / module_id
        if not module_dir.is_dir():
            report.groups.append((module_id, [Section("files", [f"modules/{module_id}/ doesn't exist"])]))
            continue
        sections, module = core.check_module(course, module_dir)
        if module is not None and execute:
            sections += run_checks(module)
        report.groups.append((module_id, sections))
    return report


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


def run_checks(module):
    exercise_type = EXERCISE_TYPES[module.data["exercise_type"]]
    jobs = {**core.jobs(module), **exercise_type.jobs(module)}
    try:
        results = run_jobs(module.course.dir, jobs)
    except RunnerError as error:
        return [Section("running checks", [str(error)])]
    return core.check_results(module, results) + exercise_type.check(module, results)
