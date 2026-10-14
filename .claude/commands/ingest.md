---
description: Turn a course's sources into Markdown with section IDs, then review the result
argument-hint: <course-name> [source-id ...]
---

Ingest the sources of `workspace/<course>/` and review the result with the
author. The course name and any source IDs come from `$ARGUMENTS`. The source
format is in `spec/README.md` ("Sources").

1. **Run ingest:**

   ```
   uv run python -m forge.ingest workspace/<course> [source-id ...]
   ```

   Downloaded pages are reused from `sources/raw/`; add `--refresh` only when
   the author wants a fresh copy.

2. **Review each source** that ingested, in `sources/<id>.md`:
   - The headings match the source's own table of contents: none missing,
     none extra. For HTML, compare with the page saved in `sources/raw/`.
   - Code blocks came through whole, with their indentation.
   - No menu, sidebar, footer or cookie text got in.
   - Sections have the anchors the source uses, where it has them.

3. **Fix problems through the brief, never by editing `sources/<id>.md`**,
   since ingest rewrites it:
   - Wrong part of an HTML page picked up: find the element that holds the
     main content in `sources/raw/<id>.html`, suggest a `selector` for it,
     and after the author's OK add it to the source in `brief.yaml`. Then run
     ingest again for that source only.
   - A source that fails to download or convert: show the error. Suggest
     another URL or a local file only if the author has one.
   - `license unknown`: ask the author what the source allows and add
     `license` to it in `brief.yaml`, with `restricted: true` if it limits
     sharing material built from the source. If they don't know, leave it;
     the warning comes back at publishing.

4. **Finish** with a short report per source: sections, words, anything
   still open. The next step is `/outline`.
