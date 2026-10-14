"""HTML page -> Markdown with a {#id} on every heading.

Section IDs come from the page's own anchors, so citations match the page's
URLs (`introduction.html#text` -> `{#text}`).
"""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from markdownify import MarkdownConverter

from .common import Converted, IngestError, SectionIds, slugify

# Tried in order when the source has no `selector`.
MAIN_CANDIDATES = ["main", "[role=main]", "article", "div.body", "#content", "div.content"]
REMOVE = ["script", "style", "noscript", "nav", "footer", "form", "button", "iframe",
          "[role=navigation]", "a.headerlink", ".sphinxsidebar"]
HEADINGS = ["h1", "h2", "h3", "h4", "h5", "h6"]
# Marks a heading's place during conversion; replaced by {#id} afterwards, so
# markdownify never sees (or escapes) the ID.
TOKEN = "ZZANCHOR{}ZZ"


def convert(html, base_url=None, selector=None):
    # html5lib parses like a browser: it closes the <p> tags wikis leave open,
    # where html.parser nests them hundreds deep.
    soup = BeautifulSoup(html, "html5lib")
    title = page_title(soup)
    main, warnings = main_content(soup, selector)
    for pattern in REMOVE:
        for element in main.select(pattern):
            element.decompose()
    if base_url:
        for link in main.find_all("a", href=True):
            link["href"] = urljoin(base_url, link["href"])
        for image in main.find_all("img", src=True):
            image["src"] = urljoin(base_url, image["src"])

    anchors = mark_headings(main)
    converter = MarkdownConverter(heading_style="ATX", bullets="-",
                                  code_language_callback=code_language)
    markdown = converter.convert_soup(main)
    for index, anchor in enumerate(anchors):
        markdown = markdown.replace(TOKEN.format(index), f"{{#{anchor}}}", 1)
    return Converted(title, tidy(markdown), warnings)


def page_title(soup):
    if soup.title and soup.title.get_text(strip=True):
        return soup.title.get_text(" ", strip=True)
    heading = soup.find("h1")
    return heading.get_text(" ", strip=True) if heading else "Untitled"


def main_content(soup, selector):
    if selector:
        found = soup.select_one(selector)
        if found is None:
            raise IngestError(f"selector {selector!r} matches nothing on the page")
        return found, []
    for candidate in MAIN_CANDIDATES:
        found = soup.select_one(candidate)
        if found is not None:
            return found, []
    return soup.body or soup, ["used the whole page (no <main> or <article>); "
                               "if menus or footers got in, set a `selector`"]


def mark_headings(main):
    ids, anchors = SectionIds(), []
    for heading in main.find_all(HEADINGS):
        text = heading.get_text(" ", strip=True)
        anchors.append(ids.take(heading_anchor(heading) or slugify(text)))
        heading.append(" " + TOKEN.format(len(anchors) - 1))
    return anchors


def heading_anchor(heading):
    """The anchor a link to this heading would use, if the page has one."""
    if heading.get("id"):
        return heading["id"]
    inner = heading.find(attrs={"id": True}) or heading.find("a", attrs={"name": True})
    if inner is not None:
        return inner.get("id") or inner.get("name")
    # A section wrapper's id: <section id> (Sphinx), <div class="section" id>
    # (older docutils). Plain container divs don't count.
    parent = heading.parent
    is_section = parent is not None and (
        parent.name == "section" or (parent.name == "div" and "section" in (parent.get("class") or []))
    )
    if is_section and parent.get("id") and parent.find(HEADINGS) is heading:
        return parent["id"]
    previous = heading.find_previous_sibling()
    if previous is not None and previous.name in ("a", "span") \
            and (previous.get("id") or previous.get("name")) and not previous.get_text(strip=True):
        return previous.get("id") or previous.get("name")
    return None


def code_language(element):
    """The language of a <pre> block, from classes like `language-bash` or
    Sphinx's `highlight-python3` on the block or its wrappers."""
    for node in [element, *list(element.parents)[:3]]:
        for name in node.get("class") or []:
            match = re.match(r"(?:language|lang|highlight)-([\w+-]+)$", name)
            if match and match.group(1) not in ("default", "none", "text"):
                return re.sub(r"3$", "", match.group(1))
    return None


def tidy(markdown):
    lines = [line.rstrip() for line in markdown.replace("¶", "").split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"
