import re
import unicodedata
from dataclasses import dataclass, field

SECTION_ID = re.compile(r"^[A-Za-z0-9._-]+$")


class IngestError(Exception):
    pass


@dataclass
class Converted:
    """A source turned into Markdown, before the front matter is added."""

    title: str
    markdown: str
    warnings: list[str] = field(default_factory=list)


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"


class SectionIds:
    """Hands out unique section IDs within one source: the wanted ID if it is
    valid and free, otherwise a slug, with -2, -3, … for duplicates."""

    def __init__(self):
        self.used = set()

    def take(self, wanted):
        base = wanted if wanted and SECTION_ID.match(wanted) else slugify(wanted or "")
        candidate, number = base, 2
        while candidate in self.used:
            candidate = f"{base}-{number}"
            number += 1
        self.used.add(candidate)
        return candidate
