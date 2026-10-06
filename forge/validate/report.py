from dataclasses import dataclass, field

MAX_SHOWN = 10  # problems shown per section


@dataclass
class Section:
    """One group of checks, e.g. "lesson", with the problems it found."""

    title: str
    problems: list[str] = field(default_factory=list)
    note: str = ""  # a short summary of what was checked

    def add(self, problem):
        self.problems.append(problem)

    @property
    def ok(self):
        return not self.problems


@dataclass
class Report:
    course: str
    groups: list[tuple[str, list[Section]]] = field(default_factory=list)

    @property
    def problems(self):
        return [problem for _, sections in self.groups for section in sections
                for problem in section.problems]


def print_report(report):
    print(f"Validating {report.course}\n")
    for title, sections in report.groups:
        print(title)
        for section in sections:
            mark = "✓" if section.ok else "✗"
            line = f"  {mark} {section.title}"
            if section.note:
                line = f"{line:<28}{section.note}"
            print(line)
            for problem in section.problems[:MAX_SHOWN]:
                print(f"      {problem}")
            if len(section.problems) > MAX_SHOWN:
                print(f"      ... and {len(section.problems) - MAX_SHOWN} more")
    count = len(report.problems)
    print(f"\n{count} problem{'s' if count != 1 else ''} found." if count else "\nNo problems found.")
