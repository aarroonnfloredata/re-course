"""Run jobs inside a course's own environment, through the runtime's
`learn.authoring` entry point."""

import json
import subprocess

TIMEOUT = 600  # seconds for all of a module's jobs


class RunnerError(Exception):
    pass


def run_jobs(course_dir, jobs):
    """Run `jobs` (a dict of name -> job) and return a dict of name -> result."""
    names = list(jobs)
    command = ["uv", "run", "--quiet", "--project", str(course_dir),
               "python", "-m", "learn.authoring"]
    try:
        process = subprocess.run(
            command, input=json.dumps([jobs[name] for name in names]),
            capture_output=True, text=True, timeout=TIMEOUT,
        )
    except FileNotFoundError:
        raise RunnerError("uv is not installed: https://docs.astral.sh/uv/") from None
    except subprocess.TimeoutExpired:
        raise RunnerError(f"the course's checks took longer than {TIMEOUT} seconds") from None
    if process.returncode != 0:
        raise RunnerError(
            "could not run checks in the course's environment:\n"
            + (process.stderr or process.stdout).strip()
        )
    return dict(zip(names, json.loads(process.stdout)))
