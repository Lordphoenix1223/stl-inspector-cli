from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .parser import inspect_stl


def _table_row(report: dict[str, object]) -> str:
    dims = report["dimensions_mm"]
    return (
        f"{report['file_name']}\n"
        f"  type: {report['stl_type']}\n"
        f"  triangles: {report['triangle_count']}\n"
        f"  size_mm: {dims['x']:.3f} x {dims['y']:.3f} x {dims['z']:.3f}\n"
        f"  surface_area_sq_mm: {report['surface_area_sq_mm']:.3f}\n"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect STL files and print geometry metadata.")
    parser.add_argument("paths", nargs="+", help="One or more STL files")
    parser.add_argument("--format", choices=["table", "json"], default="table")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        reports = [inspect_stl(Path(path)) for path in args.paths]
    except (OSError, ValueError) as exc:
        print(f"stl-inspector: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        indent = 2 if args.pretty else None
        print(json.dumps(reports if len(reports) > 1 else reports[0], indent=indent))
        return 0

    for report in reports:
        print(_table_row(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
