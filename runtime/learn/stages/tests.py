"""The tests stage: run a module's tests in a throwaway copy of the module."""

import re
import shutil
import tempfile
from pathlib import Path

from .. import languages

# Authoring folders exist in workspaces but never take part in a learner's run.
IGNORED = ("solution", "broken", "__pycache__")
EXERCISE = "exercise"


def run(module, overlays=()):
    """Copy the module to a temp dir, copy each overlay folder over it, run the tests.

    Overlays let the validator and the runtime's own tests swap in
    `solution/` or a `broken/` variant.
    """
    language = languages.get(module.language)
    with tempfile.TemporaryDirectory(prefix="learn-") as tmp:
        workdir = Path(tmp) / module.path.name
        shutil.copytree(module.path, workdir, ignore=shutil.ignore_patterns(*IGNORED))
        for overlay in overlays:
            shutil.copytree(overlay, workdir, dirs_exist_ok=True)
        return language.run_tests(workdir)


def part_of(result):
    """Challenge tests are `test_<id>_*` in test_challenges; the rest belong to the exercise."""
    if result.file == "test_challenges":
        match = re.match(r"test_([a-z0-9]+)_", result.name)
        if match:
            return match.group(1)
    return EXERCISE


def by_part(results, module):
    """Group results by part: the module's challenges in lesson order, then the exercise."""
    parts = {challenge: [] for challenge in module.challenges}
    for result in results:
        parts.setdefault(part_of(result), []).append(result)
    if EXERCISE in parts:
        parts[EXERCISE] = parts.pop(EXERCISE)
    return {part: part_results for part, part_results in parts.items() if part_results}


def all_passed(results):
    return all(result.passed for result in results)
