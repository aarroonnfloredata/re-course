"""Python courses: tests run with pytest, snippets with the current interpreter."""

import ast
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from ..results import CheckResult

EXTENSION = ".py"
TIMEOUT = 60  # seconds for a whole test run


def run_tests(workdir):
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "report.xml"
        command = [
            sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
            f"--junitxml={report}", "tests",
        ]
        try:
            process = subprocess.run(
                command, cwd=workdir, capture_output=True, text=True, timeout=TIMEOUT
            )
        except subprocess.TimeoutExpired:
            return [CheckResult(
                "tests", "timeout", False,
                f"The tests took longer than {TIMEOUT} seconds. "
                "Check your code for a loop that never ends.",
            )]
        if not report.exists():
            output = (process.stdout + process.stderr).strip()
            return [CheckResult("tests", "pytest", False, f"The tests could not run:\n{output}")]
        return parse_report(report)


def parse_report(report):
    results = []
    for case in ET.parse(report).iter("testcase"):
        problem = case.find("failure")
        if problem is None:
            problem = case.find("error")
        message = None
        if problem is not None:
            message = (problem.get("message") or "").removeprefix("Failed: ")
        results.append(CheckResult(
            file=case.get("classname", "").split(".")[-1],
            name=case.get("name", ""),
            passed=problem is None,
            message=message,
        ))
    return results


def run_snippet(code, timeout=10):
    with tempfile.TemporaryDirectory() as tmp:
        return subprocess.run(
            [sys.executable, "-c", code], cwd=tmp, capture_output=True, text=True,
            timeout=timeout,
        )


# Used by the generator's validator only (see learn/authoring.py).


def test_objectives(tests_dir):
    """Map "test_file::test_name" to the numbers in its @pytest.mark.objective(...)."""
    found = {}
    for path in sorted(Path(tests_dir).glob(f"test_*{EXTENSION}")):
        for node in ast.parse(path.read_text(encoding="utf-8")).body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                numbers = []
                for decorator in node.decorator_list:
                    if (isinstance(decorator, ast.Call)
                            and ast.unparse(decorator.func) == "pytest.mark.objective"):
                        numbers += [arg.value for arg in decorator.args
                                    if isinstance(arg, ast.Constant)]
                found[f"{path.stem}::{node.name}"] = numbers
    return found


def stubs(path):
    """Names of the functions in a starter file that still raise NotImplementedError."""
    path = Path(path)
    if path.suffix != EXTENSION:
        return []
    names = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.FunctionDef) and any(
            isinstance(inner, ast.Raise) and inner.exc is not None
            and "NotImplementedError" in ast.unparse(inner.exc)
            for inner in ast.walk(node)
        ):
            names.append(node.name)
    return names


def changed_units(original, changed):
    """Names of the top-level functions that differ between two versions of a file.
    Comments don't count."""

    def functions(path):
        tree = ast.parse(Path(path).read_text(encoding="utf-8"))
        return {node.name: ast.dump(node) for node in tree.body
                if isinstance(node, ast.FunctionDef)}

    if Path(original).suffix != EXTENSION:
        return []
    before, after = functions(original), functions(changed)
    return sorted(name for name in before.keys() | after.keys()
                  if before.get(name) != after.get(name))
