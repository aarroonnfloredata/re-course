"""Setup check: is this machine ready to generate courses with re-course?

    python3 forge/doctor.py

Uses only the standard library, so it runs before anything is installed.
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "examples/python/implement-strings"
TIMEOUT = 300  # seconds; the first run of an environment downloads packages

# (name, command, where to get it)
TOOLS = [
    ("uv", "uv", "https://docs.astral.sh/uv/getting-started/installation/"),
    ("git", "git", "https://git-scm.com/downloads"),
    ("Claude Code", "claude", "https://docs.claude.com/en/docs/claude-code/setup"),
]


def main():
    print("re-course setup check\n")
    results = [check_tool(*tool) for tool in TOOLS]
    if shutil.which("uv"):
        results += [check_generator_environment(), check_course_environment()]
    else:
        results.append((False, "environments not checked: they need uv"))

    for ok, detail in results:
        print(f"{'✓' if ok else '✗'} {detail}")
    failed = sum(not ok for ok, _ in results)
    print(f"\n{failed} problem(s) to fix." if failed else "\nEverything is ready.")
    return 1 if failed else 0


def check_tool(name, command, url):
    path = shutil.which(command)
    if path is None:
        return False, f"{name} not found. Install it: {url}"
    ok, output = run([command, "--version"])
    if not ok:
        return False, f"{name}: {path} doesn't run (`{command} --version`: {last_line(output)})"
    return True, f"{name}: {first_line(output)}"


def check_generator_environment():
    ok, output = run(["uv", "run", "--quiet", "python", "-c", "import yaml, jsonschema"])
    name = "generator environment (PyYAML, jsonschema)"
    return ok, name if ok else f"{name}: {last_line(output)}"


def check_course_environment():
    """A course environment needs the learn runtime and pytest; the golden
    example is a course."""
    ok, output = run(["uv", "run", "--quiet", "--project", str(GOLDEN),
                      "python", "-c", "import learn.authoring, pytest"])
    name = "course environment (learn runtime, pytest), tried on the golden example"
    return ok, name if ok else f"{name}: {last_line(output)}"


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
