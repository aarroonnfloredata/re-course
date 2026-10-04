from dataclasses import dataclass


@dataclass
class CheckResult:
    """The outcome of one test, as reported by a language plugin."""

    file: str  # test file without extension, e.g. "test_exercise"
    name: str  # test name with parameters, e.g. "test_initials[plato-P.]"
    passed: bool
    message: str | None = None  # plain-language failure message
