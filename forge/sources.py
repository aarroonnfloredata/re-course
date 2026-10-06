"""Read ingested sources by section, so agents don't have to read whole files.

    uv run python -m forge.sources list <course>              # every source's sections
    uv run python -m forge.sources show <course> <citation>   # one section, e.g. pytutorial#text
"""

import re
import sys
from pathlib import Path

HEADING = re.compile(r"^(#{1,6}) (.*?) \{#([^}]+)\}\s*$")


class SourceError(Exception):
    pass


def body(path):
    text = path.read_text(encoding="utf-8")
    return text.split("---\n", 2)[2] if text.startswith("---\n") else text


def list_sections(course_dir):
    """Each source's headings with their IDs and word counts, indented by level."""
    lines = []
    for path in sorted(Path(course_dir, "sources").glob("*.md")):
        text = body(path)
        found, current = [], None
        for line in text.split("\n"):
            match = HEADING.match(line)
            if match:
                current = [len(match.group(1)), match.group(2), match.group(3), 0]
                found.append(current)
            elif current is not None:
                current[3] += len(line.split())
        lines.append(f"{path.stem} ({len(text.split()):,} words)")
        for level, title, section_id, words in found:
            lines.append(f"{'  ' * (level - 1)}  #{section_id}  {title}  ({words:,} words)")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def show_section(course_dir, citation):
    """The text of one section: its heading up to the next heading of the same
    or a higher level."""
    if "#" not in citation:
        raise SourceError(f"{citation!r} is not a citation ID like pytutorial#text")
    source_id, section_id = citation.split("#", 1)
    path = Path(course_dir, "sources", f"{source_id}.md")
    if not path.is_file():
        raise SourceError(f"no sources/{source_id}.md")
    lines, level, found = body(path).split("\n"), None, []
    for line in lines:
        match = HEADING.match(line)
        if level is None:
            if match and match.group(3) == section_id:
                level = len(match.group(1))
                found.append(line)
        elif match and len(match.group(1)) <= level:
            break
        else:
            found.append(line)
    if level is None:
        raise SourceError(f"sources/{source_id}.md has no section {{#{section_id}}}")
    return "\n".join(found).rstrip() + "\n"


def main(argv=None):
    args = argv if argv is not None else sys.argv[1:]
    try:
        if len(args) == 2 and args[0] == "list":
            print(list_sections(args[1]), end="")
        elif len(args) == 3 and args[0] == "show":
            print(show_section(args[1], args[2]), end="")
        else:
            print("usage: python -m forge.sources list <course>\n"
                  "       python -m forge.sources show <course> <citation>", file=sys.stderr)
            return 2
    except SourceError as error:
        print(f"forge.sources: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
