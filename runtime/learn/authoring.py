"""Entry point for the generator's validator. Learners never use this.

It runs inside a course's environment, so tests and snippets see the course's
packages:

    uv run --project <course> python -m learn.authoring < jobs.json

stdin is a JSON list of jobs; stdout is a JSON list of their results, in the
same order. A job that fails returns {"error": "<message>"}.

Jobs:
    {"kind": "tests", "module": "<dir>", "overlays": ["<dir>", ...]}
    {"kind": "snippets", "language": "python", "codes": ["<code>", ...]}
    {"kind": "objectives", "module": "<dir>"}
    {"kind": "stubs", "language": "python", "file": "<path>"}
    {"kind": "changed", "language": "python", "original": "<path>", "changed": "<path>"}
"""

import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from . import languages
from .course import load_module
from .stages import tests


def run_job(job):
    kind = job["kind"]
    if kind == "tests":
        module = load_module(Path(job["module"]))
        overlays = [Path(path) for path in job.get("overlays", [])]
        return [dict(asdict(result), part=tests.part_of(result))
                for result in tests.run(module, overlays=overlays)]
    if kind == "snippets":
        plugin = languages.get(job["language"])
        return [run_snippet(plugin, code) for code in job["codes"]]
    if kind == "objectives":
        module = load_module(Path(job["module"]))
        return languages.get(module.language).test_objectives(module.path / "tests")
    if kind == "stubs":
        return languages.get(job["language"]).stubs(Path(job["file"]))
    if kind == "changed":
        plugin = languages.get(job["language"])
        return plugin.changed_units(Path(job["original"]), Path(job["changed"]))
    raise ValueError(f"unknown job kind {kind!r}")


def run_snippet(plugin, code):
    try:
        process = plugin.run_snippet(code)
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "timed out", "returncode": None}
    return {"stdout": process.stdout, "stderr": process.stderr,
            "returncode": process.returncode}


def main():
    results = []
    for job in json.load(sys.stdin):
        try:
            results.append(run_job(job))
        except Exception as error:
            results.append({"error": f"{type(error).__name__}: {error}"})
    json.dump(results, sys.stdout)


if __name__ == "__main__":
    main()
