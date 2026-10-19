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
    """Names of the units in a starter file that still raise NotImplementedError
    (see units())."""
    path = Path(path)
    if path.suffix != EXTENSION:
        return []
    return [name for name, node in units(path) if any(
        isinstance(inner, ast.Raise) and inner.exc is not None
        and "NotImplementedError" in ast.unparse(inner.exc)
        for inner in ast.walk(node)
    )]


def changed_units(original, changed):
    """Names of the units that differ between two versions of a file (see
    units()). Comments don't count."""
    if Path(original).suffix != EXTENSION:
        return []
    before = {name: ast.dump(node) for name, node in units(original)}
    after = {name: ast.dump(node) for name, node in units(changed)}
    return sorted(name for name in before.keys() | after.keys()
                  if before.get(name) != after.get(name))


def units(path):
    """(name, node) for each top-level function ("name") and each method of a
    top-level class ("Class.name"). Functions nested inside them belong to
    them."""
    found = []
    for node in ast.parse(Path(path).read_text(encoding="utf-8")).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found.append((node.name, node))
        elif isinstance(node, ast.ClassDef):
            found += [(f"{node.name}.{item.name}", item) for item in node.body
                      if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))]
    return found
