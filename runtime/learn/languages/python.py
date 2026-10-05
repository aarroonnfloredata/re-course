"""Python courses: tests run with pytest, snippets with the current interpreter."""

import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from ..results import CheckResult

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
