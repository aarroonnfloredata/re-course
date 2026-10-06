"""Local Markdown or plain-text file -> Markdown with a {#id} on every heading.
Existing {#id}s are kept."""

import re

from .common import Converted, SectionIds, slugify

HEADING = re.compile(r"^(#{1,6})\s+(.*?)(?:\s*\{#([A-Za-z0-9._-]+)\})?\s*$")


def convert(text, name):
    ids, title, lines, in_code = SectionIds(), None, [], False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_code = not in_code
        match = None if in_code else HEADING.match(line)
        if match:
            hashes, heading, anchor = match.groups()
            if title is None and len(hashes) == 1:
                title = heading
            line = f"{hashes} {heading} {{#{ids.take(anchor or slugify(heading))}}}"
        lines.append(line)
    markdown = "\n".join(lines).strip() + "\n"
    if not ids.used:
        return Converted(name, f"## {name} {{#{slugify(name)}}}\n\n{markdown}",
                         ["no headings found; the whole file is one section"])
    return Converted(title or name, markdown)
