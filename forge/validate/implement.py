"""Validation rules for `exercise_type: implement`. See spec/exercise-types/implement.md."""

from .core import job_failed
from .report import Section


def jobs(module):
    found = {"solution": {"kind": "tests", "module": str(module.dir),
                          "overlays": [str(module.dir / "solution")]}}
    for variant in module.variants:
        found[f"broken:{variant}"] = {
            "kind": "tests", "module": str(module.dir),
            "overlays": [str(module.dir / "solution"), str(module.dir / "broken" / variant)],
        }
    return found


def check(module, results):
    section = Section("implement rules")
    starter, solution = results["starter"], results["solution"]
    if job_failed(starter, section) or job_failed(solution, section):
        return [section]

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
    return [section]


def name(result):
    return f"{result['file']}::{result['name']}"
