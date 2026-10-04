"""Helpers shared by this module's tests.

They turn every failure into a plain-language message: what was called, what
was expected, what came back, and an optional hint.
"""

import importlib.util
from pathlib import Path

import pytest

MODULE_DIR = Path(__file__).resolve().parent.parent


def load(relative_path):
    """Import a learner file by path, e.g. load("exercise/text_tools.py")."""
    path = MODULE_DIR / relative_path
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as error:
        pytest.fail(
            f"{relative_path} could not be loaded: {type(error).__name__}: {error}",
            pytrace=False,
        )
    return module


def check(func, args, expected, kwargs=None, hint=None):
    """Fail with a plain-language message unless func(*args, **kwargs)
    returns `expected`."""
    kwargs = kwargs or {}
    shown = [repr(arg) for arg in args]
    shown += [f"{key}={value!r}" for key, value in kwargs.items()]
    call = f"{func.__name__}({', '.join(shown)})"

    try:
        result = func(*args, **kwargs)
    except NotImplementedError:
        pytest.fail(f"{func.__name__}() is not written yet.", pytrace=False)
    except Exception as error:
        message = f"{call} raised {type(error).__name__}: {error}"
    else:
        if result == expected:
            return
        message = f"{call} should return {expected!r}, but returned {result!r}."

    if hint:
        message += f"\nHint: {hint}"
    pytest.fail(message, pytrace=False)
