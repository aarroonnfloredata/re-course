"""Copy the brief's `dependencies` into the course's pyproject.toml and update
its uv.lock. Run it whenever the brief's dependencies change.

    uv run python -m forge.dependencies <course>
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

RUNTIME = "re-course-learn"
MARKER = "# From brief.yaml `dependencies`; rewritten by forge.dependencies."
BLOCK = re.compile(r"^dependencies = \[\n.*?^\]\n", re.M | re.S)


class DependencyError(Exception):
    pass


def sync(course_dir):
    """Rewrite pyproject.toml's dependencies from the brief, then lock. Returns
    the brief's dependencies."""
    course_dir = Path(course_dir)
    brief = yaml.safe_load((course_dir / "brief.yaml").read_text(encoding="utf-8")) or {}
    wanted = brief.get("dependencies") or []
    if not isinstance(wanted, list) or not all(isinstance(item, str) and item.strip() for item in wanted):
        raise DependencyError('brief.yaml: dependencies must be a list of requirements, '
                              'e.g. ["polars>=1.0"]')

    pyproject = course_dir / "pyproject.toml"
    lines = [f"    {json.dumps(RUNTIME)},\n", f"    {MARKER}\n"]
    lines += [f"    {json.dumps(item)},\n" for item in wanted]
    text, found = BLOCK.subn("dependencies = [\n" + "".join(lines) + "]\n",
                             pyproject.read_text(encoding="utf-8"), count=1)
    if not found:
        raise DependencyError("pyproject.toml: no `dependencies = [` block found")
    pyproject.write_text(text, encoding="utf-8")
    lock(course_dir)
    return wanted


def lock(course_dir):
    try:
        process = subprocess.run(["uv", "lock", "--quiet"], cwd=course_dir,
                                 capture_output=True, text=True)
    except FileNotFoundError:
        raise DependencyError("uv is not installed: https://docs.astral.sh/uv/") from None
    if process.returncode != 0:
        raise DependencyError(f"uv lock failed:\n{(process.stderr or process.stdout).strip()}")


def main(argv=None):
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: python -m forge.dependencies <course>", file=sys.stderr)
        return 2
    try:
        wanted = sync(args[0])
    except (DependencyError, FileNotFoundError) as error:
        print(f"forge.dependencies: {error}", file=sys.stderr)
        return 1
    listed = ", ".join(wanted) if wanted else "none besides the runtime"
    print(f"pyproject.toml and uv.lock updated. Course packages: {listed}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
