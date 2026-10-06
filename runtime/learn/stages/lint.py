"""The lint stage: advice from the language's linter (bash: ShellCheck) on the
learner's files. Advice never decides whether a part passes."""

from .. import languages
from .tests import EXERCISE


def run(module, parts):
    """Advice for the learner files of `parts` (challenge IDs and/or
    "exercise"), or None when the language has no linter."""
    plugin = languages.get(module.language)
    if not hasattr(plugin, "lint"):
        return None
    paths = []
    for part in parts:
        if part == EXERCISE:
            folder = module.path / EXERCISE
            found = sorted(folder.rglob("*")) if folder.is_dir() else []
        else:
            found = sorted((module.path / "challenges").glob(f"{part}.*"))
        paths += [path.relative_to(module.path).as_posix() for path in found if path.is_file()]
    return plugin.lint(module.path, paths)
