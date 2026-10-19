"""Turn the brief's sources into sources/<id>.md: Markdown with front matter and
a {#section-id} on every heading. See spec/README.md ("Sources").

    uv run python -m forge.ingest <course> [source-id ...] [--refresh]

Originals of downloaded pages are kept in sources/raw/ and reused unless
--refresh is given. sources/<id>.md is rewritten on every run: fix problems
through the brief (e.g. a `selector`), not by editing it.
"""

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

from . import html, pdf, text
from .common import IngestError
from .fetch import EXTENSIONS, fetch

SOURCE_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
UNKNOWN_LICENSE = "unknown: check before publishing"
SECTION = re.compile(r"^#{1,6} .*\{#[^}]+\}$", re.M)
FEW_WORDS = 150


@dataclass
class SourceReport:
    id: str
    output: str = ""
    sections: int = 0
    words: int = 0
    code_blocks: int = 0
    warnings: list[str] = field(default_factory=list)
    error: str | None = None


def ingest(course_dir, ids=None, refresh=False, today=None):
    """Ingest every source in the brief, or only those in `ids`."""
    course_dir = Path(course_dir)
    brief = yaml.safe_load((course_dir / "brief.yaml").read_text(encoding="utf-8")) or {}
    sources = [source for source in brief.get("sources") or [] if isinstance(source, dict)]
    known = {source.get("id") for source in sources}
    for wanted in ids or []:
        if wanted not in known:
            raise IngestError(f"no source {wanted!r} in brief.yaml")

    reports = []
    for source in sources:
        if ids and source.get("id") not in ids:
            continue
        report = SourceReport(str(source.get("id")))
        try:
            ingest_source(course_dir, source, report, refresh, today or date.today())
        except IngestError as error:
            report.error = str(error)
        except Exception as error:  # a crash in one source must not stop the others
            report.error = f"unexpected error: {type(error).__name__}: {error}"
        reports.append(report)
    return reports


def ingest_source(course_dir, source, report, refresh, today):
    source_id = source.get("id")
    if not isinstance(source_id, str) or not SOURCE_ID.match(source_id):
        raise IngestError("the id must be lowercase letters, digits and hyphens")
    if "url" in source:
        path, kind = fetch(source["url"], course_dir / "sources/raw", source_id, refresh)
        origin = {"url": source["url"]}
    elif "path" in source:
        path = course_dir / source["path"]
        kind = EXTENSIONS.get(path.suffix.lower())
        if not path.is_file():
            raise IngestError(f"{source['path']}: file not found")
        if kind is None:
            raise IngestError(f"{source['path']}: unsupported file type; "
                              f"use one of {', '.join(sorted(EXTENSIONS))}")
        origin = {"path": source["path"]}
    else:
        raise IngestError("needs a url or a path")

    for field in ("selector", "exclude"):
        if source.get(field) and kind != "html":
            report.warnings.append(f"`{field}` ignored: it only applies to HTML pages")
    converted = convert(path, kind, source.get("url"), source.get("selector"),
                        source.get("exclude") or ())

    front = {"id": source_id, "title": converted.title, **origin, "retrieved": today,
             "license": source.get("license") or UNKNOWN_LICENSE}
    if source.get("restricted") is True:
        front["restricted"] = True
    output = course_dir / "sources" / f"{source_id}.md"
    output.parent.mkdir(exist_ok=True)
    output.write_text(
        "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=1000)
        + "---\n\n" + converted.markdown,
        encoding="utf-8",
    )

    report.output = output.relative_to(course_dir).as_posix()
    report.sections = len(SECTION.findall(converted.markdown))
    report.words = len(converted.markdown.split())
    report.code_blocks = len(re.findall(r"^```", converted.markdown, re.M)) // 2
    report.warnings += converted.warnings
    if report.sections == 0:
        report.warnings.append("no sections found")
    if report.words < FEW_WORDS:
        report.warnings.append(f"very little text ({report.words} words): check the page, "
                               "or set a `selector`")
    if not source.get("license"):
        report.warnings.append("license unknown: add `license` to this source in brief.yaml")


def convert(path, kind, url=None, selector=None, exclude=()):
    if kind == "html":
        return html.convert(path.read_bytes(), base_url=url, selector=selector, exclude=exclude)
    if kind == "pdf":
        return pdf.convert(path)
    return text.convert(path.read_text(encoding="utf-8", errors="replace"), path.stem)
