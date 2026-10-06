"""Setup check: is this machine ready to generate courses with re-course?

    python3 forge/doctor.py

Uses only the standard library, so it runs before anything is installed.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "examples/python/implement-strings"
BASH_FIXTURE = ROOT / "runtime/tests/fixtures/bash-course"
BASH_TARGET = "3.2"  # the bash macOS ships; bash courses target it
TIMEOUT = 300  # seconds; the first run of an environment downloads packages
OK, WARNING, PROBLEM = "✓", "!", "✗"  # only problems fail the check

# (name, command, where to get it)
TOOLS = [
    ("uv", "uv", "https://docs.astral.sh/uv/getting-started/installation/"),
    ("git", "git", "https://git-scm.com/downloads"),
    ("Claude Code", "claude", "https://docs.claude.com/en/docs/claude-code/setup"),
]


def main():
    print("re-course setup check\n")
    results = [check_tool(*tool) for tool in TOOLS] + [check_bash()]
    if shutil.which("uv"):
        results += [check_generator_environment(), check_course_environment(),
                    check_bash_course_environment()]
    else:
        results.append((PROBLEM, "environments not checked: they need uv"))

    for mark, detail in results:
        print(f"{mark} {detail}")
    failed = sum(mark == PROBLEM for mark, _ in results)
    print(f"\n{failed} problem(s) to fix." if failed else "\nEverything is ready.")
    return 1 if failed else 0


def check_tool(name, command, url):
    path = shutil.which(command)
    if path is None:
        return PROBLEM, f"{name} not found. Install it: {url}"
    ok, output = run([command, "--version"])
    if not ok:
        return PROBLEM, f"{name}: {path} doesn't run (`{command} --version`: {last_line(output)})"
    return OK, f"{name}: {first_line(output)}"


def check_bash():
    """bash runs the examples of bash courses. With a bash other than 3.2 first
    on PATH, the validator can't catch features that 3.2 lacks."""
    mark, detail = check_tool("bash", "bash", "https://www.gnu.org/software/bash/")
    version = re.search(r"version (\d+\.\d+)", detail)
    if mark == OK and (version is None or version.group(1) != BASH_TARGET):
        return WARNING, (f"{detail}\n  Bash courses target bash {BASH_TARGET}, as macOS ships "
                         f"it. The validator runs their examples with this bash, so it won't "
                         f"catch features that {BASH_TARGET} lacks.")
    return mark, detail


def check_generator_environment():
    ok, output = run(["uv", "run", "--quiet", "python", "-c", "import yaml, jsonschema"])
    return environment(ok, output, "generator environment (PyYAML, jsonschema)")


def check_course_environment():
    """A course environment needs the learn runtime and pytest; the golden
    example is a course."""
    ok, output = run(["uv", "run", "--quiet", "--project", str(GOLDEN),
                      "python", "-c", "import learn.authoring, pytest"])
    return environment(ok, output, "course environment (learn runtime, pytest), "
                                   "tried on the golden example")


def check_bash_course_environment():
    """A bash course environment adds ShellCheck (re-course-learn[bash]); the
    runtime's bash fixture is a bash course."""
    ok, output = run(["uv", "run", "--quiet", "--project", str(BASH_FIXTURE),
                      "shellcheck", "--version"])
    return environment(ok, output, "bash course environment (ShellCheck), "
                                   "tried on the bash fixture")


def environment(ok, output, name):
    return (OK, name) if ok else (PROBLEM, f"{name}: {last_line(output)}")


def run(command):
    try:
        process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                 timeout=TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as error:
        return False, str(error)
    return process.returncode == 0, (process.stdout + process.stderr).strip()


def first_line(text):
    return text.split("\n")[0] if text else ""


def last_line(text):
    return text.split("\n")[-1] if text else "no output"


if __name__ == "__main__":
    sys.exit(main())
