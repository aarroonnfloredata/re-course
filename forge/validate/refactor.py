"""Validation rules for `exercise_type: refactor`. See spec/exercise-types/refactor.md."""

import re

from .core import first_line, job_failed
from .implement import name, setups
from .report import Section

BEHAVIOUR_FILE = "test_behaviour"
KINDS = ("behaviour", "smell")
KIND = re.compile(r"Broken variant: (\w+):")


def static(module):
    """Each variant names its kind, and the module has a variant of each kind."""
    section = Section("refactor variants")
    found = set(variant_kinds(module, section).values())
    for variant, paths in module.variants.items():
        for path in paths:
            original = module.dir / "solution" / path
            changed = module.dir / "broken" / variant / path
            if original.is_file() and changed.is_file() \
                    and without_first_comment(changed) == original.read_text(encoding="utf-8"):
                section.add(f"broken/{variant}/{path}: the same as the solution apart from its "
                            "'Broken variant:' line")
    for kind in KINDS:
        if module.variants and kind not in found:
            section.add(f"broken/: no {kind} variant; a refactor module needs at least one "
                        f"'Broken variant: {kind}: …'")
    return [section]


def jobs(module):
    return setups(module)


def variant_kinds(module, section):
    """variant -> its kind, or None when its files don't name one kind."""
    kinds = {}
    for variant, paths in module.variants.items():
        named = set()
        for path in paths:
            file = module.dir / "broken" / variant / path
            match = KIND.search(first_line(file)) if file.is_file() else None
            if match is None or match.group(1) not in KINDS:
                section.add(f"broken/{variant}/{path}: the first line must name the kind: "
                            "'Broken variant: behaviour: …' or 'Broken variant: smell: …'")
            else:
                named.add(match.group(1))
        if len(named) > 1:
            section.add(f"broken/{variant}: its files name different kinds")
        kinds[variant] = named.pop() if len(named) == 1 else None
    return kinds


def check(module, results):
    section = Section("refactor rules")
    starter, solution = results["starter"], results["solution"]
    if job_failed(starter, section) or job_failed(solution, section):
        return [section]

    behaviour = [result for result in starter if is_behaviour(result)]
    others = [result for result in starter if result["part"] == "exercise" and not is_behaviour(result)]
    if not behaviour:
        section.add(f"no behaviour tests: tests/{BEHAVIOUR_FILE} pins down what the starter does")
    if not others:
        section.add("no structural checks: exercise tests other than "
                    f"{BEHAVIOUR_FILE} check the task's targets")

    for result in starter:
        if is_behaviour(result) and not result["passed"]:
            section.add(f"starter: behaviour test {name(result)} fails, so it pins down "
                        f"something the starter doesn't do: {result['message']}")
        elif not is_behaviour(result) and result["passed"]:
            section.add(f"starter: {name(result)} passes, so it checks nothing")
    for result in solution:
        if not result["passed"]:
            section.add(f"solution: {name(result)} fails: {result['message']}")

    caught = 0
    for variant, kind in variant_kinds(module, Section("")).items():
        results_for_variant = results[f"broken:{variant}"]
        if kind is None or job_failed(results_for_variant, section):
            continue
        failing = [result for result in results_for_variant if not result["passed"]]
        behaviour_failing = [result for result in failing if is_behaviour(result)]
        others_failing = [result for result in failing
                          if result["part"] == "exercise" and not is_behaviour(result)]
        if kind == "behaviour":
            if behaviour_failing:
                caught += 1
            else:
                section.add(f"broken/{variant}: no behaviour test catches it")
        else:
            for result in behaviour_failing:
                section.add(f"broken/{variant}: behaviour test {name(result)} fails, but a "
                            "smell variant must keep the behaviour")
            if others_failing and not behaviour_failing:
                caught += 1
            elif not others_failing:
                section.add(f"broken/{variant}: no structural check catches it")
        for result in failing:
            if result["part"] != "exercise":
                section.add(f"broken/{variant}: challenge test {name(result)} fails; "
                            "variants must only break the exercise")

    others_failing = sum(not result["passed"] for result in starter if not is_behaviour(result))
    section.note = (f"starter: {sum(r['passed'] for r in behaviour)}/{len(behaviour)} behaviour "
                    f"tests pass, {others_failing}/{len(starter) - len(behaviour)} others fail; "
                    f"solution {sum(r['passed'] for r in solution)}/{len(solution)} pass; "
                    f"{caught}/{len(module.variants)} variants caught")
    return [section]


def without_first_comment(path):
    """A variant's text without its 'Broken variant:' line."""
    lines = path.read_text(encoding="utf-8").split("\n")
    index = 1 if lines[0].startswith("#!") else 0
    if len(lines) > index and "Broken variant:" in lines[index]:
        del lines[index]
    return "\n".join(lines)


def is_behaviour(result):
    return result["file"] == BEHAVIOUR_FILE
