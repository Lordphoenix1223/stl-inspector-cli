# STL Inspector CLI

A small Python CLI for inspecting STL files and printing useful geometry metadata without needing a slicer open.

## What It Does

- detects ASCII vs binary STL
- counts triangles
- computes bounding box and dimensions
- computes surface area
- reports centroid and min/max corners
- prints either JSON or a terminal table

This is meant for quick validation when you want answers like:

- "Did this export come out the right size?"
- "Which part is bigger than I thought?"
- "Did I just generate a weirdly tiny coupon by mistake?"

## Install

```bash
python -m pip install -e .
```

## Run Tests

```bash
python -m unittest discover -s tests
```

## Usage

```bash
stl-inspector part_a.stl
stl-inspector part_a.stl part_b.stl --format json
stl-inspector part_a.stl --pretty
```

## Example Output

```json
{
  "file_name": "bench_mechanism_v3_base.stl",
  "stl_type": "ascii",
  "triangle_count": 820,
  "dimensions_mm": {
    "x": 92.0,
    "y": 38.0,
    "z": 22.0
  }
}
```

Full sample reports:

- [sample_reports/bench_mechanism_v3_base.json](./sample_reports/bench_mechanism_v3_base.json)
- [sample_reports/bench_mechanism_v3_carriage.json](./sample_reports/bench_mechanism_v3_carriage.json)
- [sample_reports/bench_mechanism_v3_m3_test_block.json](./sample_reports/bench_mechanism_v3_m3_test_block.json)

## Why I Built It

I wanted something faster and scriptable than bouncing between OpenSCAD and a slicer every time I needed basic geometry facts.

## Repo Layout

```text
stl-inspector-cli/
├── README.md
├── pyproject.toml
├── src/stl_inspector/
│   ├── __init__.py
│   ├── cli.py
│   └── parser.py
├── sample_reports/
│   ├── bench_mechanism_v3_base.json
│   ├── bench_mechanism_v3_carriage.json
│   └── bench_mechanism_v3_m3_test_block.json
├── tests/
│   └── test_parser.py
```

## Current Limitations

- Units are reported as millimeters by convention; STL does not carry units.
- The CLI focuses on geometry summary data, not mesh repair.
- Extremely large files are rejected on purpose instead of being streamed loosely.
