"""Publish a course: replace shared-workspace/<course>/ with its learner files.

    uv run python -m forge.publish <course> [--accept-unknown-licenses]

1. The full validator must pass (so every module is built).
2. Sources with an unknown licence that a module cites need the author's
   confirmation: --accept-unknown-licenses.
3. shared-workspace/<course>/ is deleted and the learner files are copied in.
4. Smoke check: no authoring files in the copy, and `learn next` runs there.
5. The course's trial folder is removed.

Git is left to the author; see .claude/commands/publish.md.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import trial
from .validate import validate

ROOT = Path(__file__).resolve().parents[1]
AUTHORING = ["brief.yaml", "outline.yaml", "sources", ".venv"]
PRIVATE_FOLDERS = ["solution", "broken"]


class PublishError(Exception):
    pass


@dataclass
class Published:
    target: Path
    modules: list[str]
    unknown_licenses: dict = field(default_factory=dict)  # source ID -> citing modules
    removed_trial: bool = False


def publish(course_dir, accept_unknown_licenses=False, shared_dir=None):
    course_dir = Path(course_dir)
    shared_dir = Path(shared_dir) if shared_dir else ROOT / "shared-workspace"

    report = validate(course_dir)
    if report.problems:
        raise PublishError("the validator found problems:\n" + "\n".join(report.problems))
    course = yaml.safe_load((course_dir / "course.yaml").read_text(encoding="utf-8"))
    unknown = unknown_licenses(course_dir, course["modules"])
    if unknown and not accept_unknown_licenses:
        listed = "\n".join(f"{source} (cited by {', '.join(modules)})"
                           for source, modules in unknown.items())
        raise PublishError("these sources have an unknown licence; confirm with "
                           f"--accept-unknown-licenses:\n{listed}")

    target = shared_dir / course_dir.name
    if target.exists():
        shutil.rmtree(target)
    trial.copy_learner_files(course_dir, target)
    smoke_check(target)
    removed = trial.remove(course_dir)
    return Published(target, course["modules"], unknown, removed)


def unknown_licenses(course_dir, module_ids):
    """Sources cited by the course's modules whose licence is missing or unknown."""
    cited = {}
    for module_id in module_ids:
        module = yaml.safe_load((course_dir / "modules" / module_id / "module.yaml").read_text())
        for citation in module["sources"]:
            cited.setdefault(citation.split("#", 1)[0], []).append(module_id)
    unknown = {}
    for source_id, modules in sorted(cited.items()):
        text = (course_dir / "sources" / f"{source_id}.md").read_text(encoding="utf-8")
        front = re.match(r"---\n(.*?)\n---\n", text, re.S)
        license_text = str((yaml.safe_load(front.group(1)) or {}).get("license") or "") if front else ""
        if not license_text or license_text.lower().startswith("unknown"):
            unknown[source_id] = sorted(set(modules))
    return unknown


def smoke_check(target):
    leaked = [name for name in AUTHORING if (target / name).exists()]
    leaked += [str(path.relative_to(target)) for name in PRIVATE_FOLDERS
               for path in target.rglob(name) if path.is_dir()]
    if leaked:
        raise PublishError(f"authoring files ended up in {target}: {', '.join(leaked)}")
    # Build the environment outside the published folder, from the lock file as is.
    with tempfile.TemporaryDirectory() as environment:
        process = subprocess.run(
            ["uv", "run", "--quiet", "--locked", "learn", "next"], cwd=target,
            capture_output=True, text=True,
            env={**os.environ, "UV_PROJECT_ENVIRONMENT": environment},
        )
    if process.returncode != 0:
        raise PublishError(f"`learn next` fails in {target}:\n"
                           + (process.stderr or process.stdout).strip())


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m forge.publish",
                                     description="Publish a course to shared-workspace/.")
    parser.add_argument("course", help="the course folder, e.g. workspace/bash-basics")
    parser.add_argument("--accept-unknown-licenses", action="store_true",
                        help="publish even though some cited sources have an unknown licence")
    args = parser.parse_args(argv)
    if not (Path(args.course) / "course.yaml").is_file():
        print(f"forge.publish: no course.yaml in {args.course}", file=sys.stderr)
        return 2
    try:
        published = publish(args.course, args.accept_unknown_licenses)
    except PublishError as error:
        print(f"forge.publish: {error}", file=sys.stderr)
        return 1
    print(f"Published {len(published.modules)} module(s) to {published.target}/.")
    for source, modules in published.unknown_licenses.items():
        print(f"  licence unknown, accepted: {source} (cited by {', '.join(modules)})")
    if published.removed_trial:
        print(f"  removed {trial.trial_dir(args.course)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
