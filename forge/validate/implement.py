"""Validation rules for `exercise_type: implement`. See spec/exercise-types/implement.md."""

from .core import job_failed
from .report import Section


def static(module):
    return []


def jobs(module):
    found = setups(module)
    for path in module.learner_files:
        if path.startswith("exercise/"):
            found[f"stubs:{path}"] = {"kind": "stubs", "language": module.language,
                                      "file": str(module.dir / path)}
    for variant, paths in module.variants.items():
        for path in paths:
            original = module.dir / "solution" / path
            if path in module.learner_files and original.is_file():
                found[f"changed:{variant}:{path}"] = {
                    "kind": "changed", "language": module.language, "original": str(original),
                    "changed": str(module.dir / "broken" / variant / path),
                }
    return found


def setups(module):
    """The test runs besides the starter: the solution, and each variant on top of it."""
    found = {"solution": {"kind": "tests", "module": str(module.dir),
                          "overlays": [str(module.dir / "solution")]}}
    for variant in module.variants:
        found[f"broken:{variant}"] = {
            "kind": "tests", "module": str(module.dir),
            "overlays": [str(module.dir / "solution"), str(module.dir / "broken" / variant)],
        }
    return found


def check(module, results):
    return [check_rules(module, results), check_units(results)]


def check_rules(module, results):
    section = Section("implement rules")
    starter, solution = results["starter"], results["solution"]
    if job_failed(starter, section) or job_failed(solution, section):
        return section

    for result in starter:
        if result["passed"]:
            section.add(f"starter: {name(result)} passes, so it checks nothing")
    for result in solution:
        if not result["passed"]:
            section.add(f"solution: {name(result)} fails: {result['message']}")

    caught = 0
    for variant in module.variants:
        results_for_variant = results[f"broken:{variant}"]
        if job_failed(results_for_variant, section):
            continue
        failing = [result for result in results_for_variant if not result["passed"]]
        if any(result["part"] == "exercise" for result in failing):
            caught += 1
        else:
            section.add(f"broken/{variant}: no exercise test catches it")
        for result in failing:
            if result["part"] != "exercise":
                section.add(f"broken/{variant}: challenge test {name(result)} fails; "
                            "variants must only break the exercise")

    starter_failing = sum(not result["passed"] for result in starter)
    solution_passing = sum(result["passed"] for result in solution)
    section.note = (f"starter {starter_failing}/{len(starter)} fail, "
                    f"solution {solution_passing}/{len(solution)} pass, "
                    f"{caught}/{len(module.variants)} variants caught")
    return section


def check_units(results):
    """Each unit the learner writes is a stub, every variant changes a unit of
    the solution, and every unit is changed by some variant."""
    section = Section("variant coverage")
    units, changed_by = [], {}
    for job, result in results.items():
        if job.startswith("stubs:") and not job_failed(result, section):
            units += result
        elif job.startswith("changed:") and not job_failed(result, section):
            _, variant, path = job.split(":", 2)
            if not result:
                section.add(f"broken/{variant}/{path}: changes no function or script of "
                            "the solution")
            for unit in result:
                changed_by.setdefault(unit, []).append(variant)
    if not units:
        section.add("exercise/: no stubs found; each unit the learner writes must be a stub")
    for unit in units:
        if unit not in changed_by:
            section.add(f"no broken variant changes {unit}")
    section.note = f"{len(units)} units in exercise/"
    return section


def name(result):
    return f"{result['file']}::{result['name']}"
