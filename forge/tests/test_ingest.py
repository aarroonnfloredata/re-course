import functools
import http.server
import threading
from datetime import date

import pytest
import yaml
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from forge.ingest import IngestError, html, ingest, pdf, text
from forge.ingest.__main__ import main
from forge.validate import core

PAGE = """<html><head><title>Shell Guide</title></head><body>
<nav><a href="/">Home</a> Menu text</nav>
<div class="body" role="main">
  <section id="quoting"><span id="old-label"></span>
    <h1>Quoting<a class="headerlink" href="#quoting">¶</a></h1>
    <p>Quotes keep <a href="spaces.html">spaces</a>.</p>
    <div class="highlight-bash"><div class="highlight"><pre>echo "a  b"</pre></div></div>
    <h2 id="single">Single quotes</h2><p>Nothing expands.</p>
    <h2><a name="double"></a>Double quotes</h2><p>Variables expand.</p>
    <h2>Escapes &amp; more</h2><p>Backslash.</p>
    <h2>Escapes &amp; more</h2><p>Again.</p>
  </section>
</div>
<footer>Footer text</footer></body></html>"""


# HTML


def test_html_sections_take_the_page_anchors():
    converted = html.convert(PAGE, base_url="https://example.com/guide/quoting.html")
    markdown = converted.markdown
    assert converted.title == "Shell Guide"
    assert "# Quoting {#quoting}" in markdown  # the section's id, not the span's
    assert "## Single quotes {#single}" in markdown
    assert "## Double quotes {#double}" in markdown
    assert "## Escapes & more {#escapes-more}" in markdown
    assert "## Escapes & more {#escapes-more-2}" in markdown
    assert converted.warnings == []


def test_html_keeps_content_and_drops_the_rest():
    markdown = html.convert(PAGE, base_url="https://example.com/guide/quoting.html").markdown
    assert '```bash\necho "a  b"\n```' in markdown
    assert "(https://example.com/guide/spaces.html)" in markdown
    assert "¶" not in markdown
    assert "Menu text" not in markdown
    assert "Footer text" not in markdown


def test_html_selector():
    page = "<body><div id='side'>Side</div><div id='text'><h2>Only this</h2></div></body>"
    markdown = html.convert(page, selector="#text").markdown
    assert markdown == "## Only this {#only-this}\n"


def test_html_selector_that_matches_nothing():
    with pytest.raises(IngestError, match="matches nothing"):
        html.convert(PAGE, selector="#missing")


def test_html_exclude():
    page = ("<body><main><div class='crumbs'>Home</div><h2>Kept</h2>"
            "<div class='ad'>Buy now</div><p>Text</p></main></body>")
    converted = html.convert(page, exclude=[".crumbs", ".ad", ".missing"])
    assert converted.markdown == "## Kept {#kept}\n\nText\n"
    assert converted.warnings == ["exclude '.missing' matches nothing on the page"]


def test_html_without_a_main_element_warns():
    converted = html.convert("<body><h2>Title</h2><p>Text</p></body>")
    assert "used the whole page" in converted.warnings[0]


def test_html_with_unclosed_paragraphs():
    # Wikis leave <p> open; more of them than Python's recursion limit must
    # still convert.
    page = "<body><div id='content'><h2>Pitfalls</h2>" + "<p>Tip.\n" * 1500 + "</div></body>"
    markdown = html.convert(page).markdown
    assert markdown.startswith("## Pitfalls {#pitfalls}\n")
    assert markdown.count("Tip.") == 1500


# Markdown and text


def test_markdown_headings_get_ids():
    source = "# Guide\n\n## Part one\n\n## Kept {#keep}\n\n```\n# not a heading\n```\n"
    converted = text.convert(source, "guide")
    assert converted.title == "Guide"
    assert "## Part one {#part-one}" in converted.markdown
    assert "## Kept {#keep}" in converted.markdown
    assert "\n# not a heading\n" in converted.markdown


def test_text_without_headings_is_one_section():
    converted = text.convert("Just some notes.", "notes")
    assert converted.markdown.startswith("## notes {#notes}\n")
    assert converted.warnings


# PDF


def make_pdf(path, outline=True):
    document = FPDF()
    document.set_title("Shell Book")

    def write(line_text, font="Helvetica", size=12):
        document.set_font(font, size=size)
        document.multi_cell(0, 7, line_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    document.add_page()
    if outline:
        document.start_section("1 Getting started")
    write("1 Getting started\nThe shell reads commands.")
    if outline:
        document.start_section("1.1 First steps", level=1)
    write("1.1 First steps\nType a command and press Enter.")
    write('for f in *; do\n    echo "$f"\ndone', font="Courier", size=11)
    document.add_page()
    if outline:
        document.start_section("2 Quoting")
    write("2 Quoting\nQuotes keep spaces.")
    document.output(str(path))
    return path


def test_pdf_sections_follow_its_table_of_contents(tmp_path):
    converted = pdf.convert(make_pdf(tmp_path / "book.pdf"))
    markdown = converted.markdown
    assert converted.title == "Shell Book"
    assert converted.warnings == []
    parts = markdown.split("\n## ")
    assert markdown.startswith("## 1 Getting started {#1}\n\nThe shell reads commands.")
    assert "### 1.1 First steps {#1.1}\n\nType a command and press Enter." in markdown
    assert parts[-1].startswith("2 Quoting {#2}\n\nQuotes keep spaces.")
    echo = next(line for line in markdown.split("\n") if "echo" in line)
    assert echo.startswith("  "), "code indentation was lost"


def test_pdf_without_a_table_of_contents(tmp_path):
    converted = pdf.convert(make_pdf(tmp_path / "book.pdf", outline=False))
    assert converted.markdown.startswith("## Page 1 {#page-1}")
    assert "## Page 2 {#page-2}" in converted.markdown
    assert "no table of contents" in converted.warnings[0]


# Whole runs


@pytest.fixture
def site(tmp_path):
    """A local web server, so downloads are tested without the internet."""
    root = tmp_path / "site"
    root.mkdir()
    handler = functools.partial(QuietHandler, directory=str(root))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield root, f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@pytest.fixture
def course(tmp_path, site):
    site_root, base = site
    (site_root / "page.html").write_text(PAGE)
    course = tmp_path / "course"
    (course / "files").mkdir(parents=True)
    make_pdf(course / "files/book.pdf")
    (course / "files/notes.md").write_text("# Notes\n\n## Tips\n\nUse quotes.\n")
    brief = {"sources": [
        {"id": "guide", "url": f"{base}/page.html", "license": "CC BY 4.0"},
        {"id": "book", "path": "files/book.pdf", "restricted": True},
        {"id": "notes", "path": "files/notes.md"},
    ]}
    (course / "brief.yaml").write_text(yaml.safe_dump(brief))
    return course


def front_matter(path):
    return yaml.safe_load(path.read_text().split("---\n")[1])


def test_ingest_writes_every_source(course, site):
    reports = ingest(course, today=date(2026, 1, 2))
    assert [report.error for report in reports] == [None, None, None]
    guide = front_matter(course / "sources/guide.md")
    assert guide == {"id": "guide", "title": "Shell Guide", "url": f"{site[1]}/page.html",
                     "retrieved": date(2026, 1, 2), "license": "CC BY 4.0"}
    book_front = front_matter(course / "sources/book.md")
    assert book_front["license"] == "unknown: check before publishing"
    assert book_front["restricted"] is True
    assert front_matter(course / "sources/notes.md")["path"] == "files/notes.md"
    assert (course / "sources/raw/guide.html").is_file()
    book = next(report for report in reports if report.id == "book")
    assert book.sections == 3
    assert any("license unknown" in warning for warning in book.warnings)


def test_ingested_sections_can_be_cited(course):
    ingest(course)
    found = core.Course(course, "python", [], {"guide", "book"})
    assert core.source_problem(found, "guide", "single") is None
    assert core.source_problem(found, "book", "1.1") is None
    assert "no section" in core.source_problem(found, "guide", "missing")


def test_downloads_are_reused_until_refresh(course, site):
    ingest(course, ["guide"])
    (site[0] / "page.html").write_text(PAGE.replace("Single quotes", "Apostrophes"))
    ingest(course, ["guide"])
    assert "Single quotes" in (course / "sources/guide.md").read_text()
    ingest(course, ["guide"], refresh=True)
    assert "Apostrophes" in (course / "sources/guide.md").read_text()


def test_unknown_source_id(course):
    with pytest.raises(IngestError, match="no source 'nope'"):
        ingest(course, ["nope"])


def test_failed_download_is_reported(course):
    brief = yaml.safe_load((course / "brief.yaml").read_text())
    brief["sources"].append({"id": "gone", "url": "http://127.0.0.1:9/missing.html"})
    (course / "brief.yaml").write_text(yaml.safe_dump(brief))
    gone = ingest(course, ["gone"])[0]
    assert "could not download" in gone.error


def test_crash_in_one_source_does_not_stop_the_others(course, monkeypatch, capsys):
    def crash(*args, **kwargs):
        raise RecursionError("maximum recursion depth exceeded")

    monkeypatch.setattr(html, "convert", crash)
    assert main([str(course)]) == 1
    out = capsys.readouterr().out
    assert "✗ guide: unexpected error: RecursionError: maximum recursion depth exceeded" in out
    assert "✓ book: sources/book.md" in out
    assert "✓ notes: sources/notes.md" in out


def test_cli(course, capsys):
    assert main([str(course)]) == 0
    out = capsys.readouterr().out
    assert "✓ guide: sources/guide.md, 5 sections" in out
    assert "⚠ license unknown" in out
