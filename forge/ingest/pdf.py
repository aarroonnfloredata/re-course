"""PDF -> Markdown. The PDF's table of contents (bookmarks) defines the sections.

Section IDs are the section number when the title starts with one ("7.3"),
otherwise a slug of the title. Without a table of contents, each page is a
section.
"""

import re
from pathlib import Path

import pdfplumber
from pdfminer.pdftypes import resolve1
from pdfminer.psparser import PSLiteral
from pdfminer.utils import decode_text

from .common import Converted, SectionIds, slugify

NUMBERED = re.compile(r"^(\d+(?:\.\d+)*)\b")


def convert(path):
    with pdfplumber.open(path) as pdf:
        title = metadata_title(pdf) or Path(path).stem
        pages = [page_text(page) for page in pdf.pages]
        outline = read_outline(pdf)
    if not outline:
        return Converted(title, pages_as_sections(pages),
                         ["the PDF has no table of contents; each page is a section"])
    return Converted(title, outline_sections(pages, outline))


def metadata_title(pdf):
    title = pdf.metadata.get("Title") or ""
    if isinstance(title, bytes):
        title = decode_text(title)
    return title.strip()


def page_text(page):
    """The page's text with its layout kept (so code stays indented), minus the
    page margin and runs of blank lines."""
    lines = [line.rstrip() for line in (page.extract_text(layout=True) or "").split("\n")]
    indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
    margin = min(indents) if indents else 0
    text = "\n".join(line[margin:] for line in lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def read_outline(pdf):
    """[(level, title, page index)] from the PDF's bookmarks; [] if it has none."""
    page_numbers = {page.page_obj.pageid: index for index, page in enumerate(pdf.pages)}
    try:
        entries = list(pdf.doc.get_outlines())
    except Exception:  # pdfminer raises PDFNoOutlines, or errors on broken outlines
        return []
    outline = []
    for level, title, destination, action, _ in entries:
        index = destination_page(pdf.doc, destination, action, page_numbers)
        title = decode_text(title) if isinstance(title, bytes) else str(title or "")
        if index is not None and title.strip():
            outline.append((level, " ".join(title.split()), index))
    return outline


def destination_page(doc, destination, action, page_numbers):
    if destination is None and action is not None:
        action = resolve1(action)
        destination = action.get("D") if isinstance(action, dict) else None
    destination = resolve1(destination)
    if isinstance(destination, (bytes, str, PSLiteral)):  # a named destination
        name = destination.name if isinstance(destination, PSLiteral) else destination
        try:
            destination = resolve1(doc.get_dest(name))
        except Exception:
            return None
    if isinstance(destination, dict):
        destination = resolve1(destination.get("D"))
    if isinstance(destination, list) and destination:
        return page_numbers.get(getattr(destination[0], "objid", None))
    return None


def outline_sections(pages, outline):
    text, starts = "", []
    for page in pages:
        starts.append(len(text))
        text += page + "\n\n"
    starts.append(len(text))

    # Where each section starts: at its title on its page if found, else at
    # the top of its page. Never before the previous section.
    positions, previous = [], 0
    for _, title, index in outline:
        page_start = max(starts[index], previous)
        found = find_line(text, title, page_start, max(starts[index + 1], page_start))
        previous = found if found is not None else page_start
        positions.append(previous)

    ids, parts = SectionIds(), []
    for number, ((level, title, _), start) in enumerate(zip(outline, positions)):
        end = positions[number + 1] if number + 1 < len(positions) else len(text)
        body = drop_first_line_if(text[start:end].strip(), title)
        heading = "#" * min(level + 1, 6)
        match = NUMBERED.match(title)
        section_id = ids.take(match.group(1) if match else slugify(title))
        parts.append(f"{heading} {title} {{#{section_id}}}\n\n{body}".rstrip() + "\n")
    return "\n".join(parts)


def find_line(text, title, start, end):
    """Offset of the start of the line where `title` appears in text[start:end]."""
    pattern = r"\s+".join(re.escape(word) for word in title.split())
    match = re.compile(pattern, re.I).search(text, start, end)
    if match is None:
        return None
    return text.rfind("\n", start, match.start()) + 1 or start


def drop_first_line_if(body, title):
    first, _, rest = body.partition("\n")
    if " ".join(first.split()).lower() == title.lower():
        return rest.strip()
    return body


def pages_as_sections(pages):
    return "\n".join(f"## Page {number} {{#page-{number}}}\n\n{page}\n"
                     for number, page in enumerate(pages, 1))
