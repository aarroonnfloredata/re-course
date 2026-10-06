import argparse
import sys
from pathlib import Path

from . import ingest
from .common import IngestError


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m forge.ingest",
                                     description="Turn a course's sources into Markdown.")
    parser.add_argument("course", help="the course folder, e.g. workspace/bash-basics")
    parser.add_argument("ids", nargs="*", help="source IDs from brief.yaml (default: all)")
    parser.add_argument("--refresh", action="store_true", help="download pages again")
    args = parser.parse_args(argv)

    if not (Path(args.course) / "brief.yaml").is_file():
        print(f"forge.ingest: no brief.yaml in {args.course}", file=sys.stderr)
        return 2
    try:
        reports = ingest(args.course, args.ids, refresh=args.refresh)
    except IngestError as error:
        print(f"forge.ingest: {error}", file=sys.stderr)
        return 1

    print(f"Ingesting {args.course}\n")
    for report in reports:
        if report.error:
            print(f"✗ {report.id}: {report.error}")
            continue
        print(f"✓ {report.id}: {report.output}, {report.sections} sections, "
              f"{report.words:,} words, {report.code_blocks} code blocks")
        for warning in report.warnings:
            print(f"    ⚠ {warning}")
    return 1 if any(report.error for report in reports) else 0


if __name__ == "__main__":
    sys.exit(main())
