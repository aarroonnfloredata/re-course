import argparse
import sys
from pathlib import Path

from . import validate
from .report import print_report


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m forge.validate", description="Validate a course workspace against the spec."
    )
    parser.add_argument("course", help="the course folder, e.g. workspace/bash-basics")
    parser.add_argument("modules", nargs="*", help="module IDs or numbers (default: all)")
    parser.add_argument("--static", action="store_true", help="skip the checks that run code")
    parser.add_argument("--outline", action="store_true",
                        help="check only brief.yaml and outline.yaml")
    args = parser.parse_args(argv)

    if not (Path(args.course) / "course.yaml").is_file():
        print(f"forge.validate: no course.yaml in {args.course}", file=sys.stderr)
        return 2
    report = validate(args.course, args.modules, execute=not args.static,
                      outline_only=args.outline)
    print_report(report)
    return 1 if report.problems else 0


if __name__ == "__main__":
    sys.exit(main())
