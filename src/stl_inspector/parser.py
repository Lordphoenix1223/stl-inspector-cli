from __future__ import annotations

import math
import struct
from pathlib import Path
from typing import Iterable

MAX_FILE_SIZE_BYTES = 64 * 1024 * 1024


def _read_candidate_file(candidate_path: Path) -> bytes:
    if not candidate_path.exists():
        raise ValueError(f"File not found: {candidate_path}")
    if not candidate_path.is_file():
        raise ValueError(f"Not a file: {candidate_path}")

    file_size = candidate_path.stat().st_size
    if file_size == 0:
        raise ValueError("STL file is empty")
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"STL file is larger than the supported limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB"
        )

    return candidate_path.read_bytes()


def _triangle_area(a: tuple[float, float, float], b: tuple[float, float, float], c: tuple[float, float, float]) -> float:
    ab = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    ac = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    cross = (
        ab[1] * ac[2] - ab[2] * ac[1],
        ab[2] * ac[0] - ab[0] * ac[2],
        ab[0] * ac[1] - ab[1] * ac[0],
    )
    return 0.5 * math.sqrt(cross[0] ** 2 + cross[1] ** 2 + cross[2] ** 2)


def _summarize_vertices(vertices: Iterable[tuple[float, float, float]], triangle_count: int, stl_type: str, file_name: str) -> dict[str, object]:
    vertices = list(vertices)
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    min_corner = {"x": min(xs), "y": min(ys), "z": min(zs)}
    max_corner = {"x": max(xs), "y": max(ys), "z": max(zs)}
    centroid = {
        "x": sum(xs) / len(xs),
        "y": sum(ys) / len(ys),
        "z": sum(zs) / len(zs),
    }
    dimensions = {
        "x": max_corner["x"] - min_corner["x"],
        "y": max_corner["y"] - min_corner["y"],
        "z": max_corner["z"] - min_corner["z"],
    }
    area = 0.0
    for index in range(0, len(vertices), 3):
        area += _triangle_area(vertices[index], vertices[index + 1], vertices[index + 2])
    return {
        "file_name": file_name,
        "stl_type": stl_type,
        "triangle_count": triangle_count,
        "vertex_count": len(vertices),
        "units": "assumed_mm",
        "dimensions_mm": dimensions,
        "min_corner_mm": min_corner,
        "max_corner_mm": max_corner,
        "centroid_mm": centroid,
        "surface_area_sq_mm": area,
    }


def _inspect_binary_stl(path: Path, data: bytes) -> dict[str, object]:
    if len(data) < 84:
        raise ValueError("Binary STL header is incomplete")

    triangle_count = struct.unpack_from("<I", data, 80)[0]
    expected_size = 84 + triangle_count * 50
    if len(data) < expected_size:
        raise ValueError(f"Incomplete binary STL: expected at least {expected_size} bytes, found {len(data)}")

    vertices: list[tuple[float, float, float]] = []
    offset = 84
    for _ in range(triangle_count):
        offset += 12  # normal
        for _ in range(3):
            vertex = struct.unpack_from("<fff", data, offset)
            vertices.append(vertex)
            offset += 12
        offset += 2  # attribute byte count

    return _summarize_vertices(vertices, triangle_count, "binary", path.name)


def _inspect_ascii_stl(path: Path) -> dict[str, object]:
    vertices: list[tuple[float, float, float]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("vertex "):
            continue
        parts = stripped.split()
        if len(parts) != 4:
            raise ValueError(f"Malformed vertex line at {line_number}")
        _, x_value, y_value, z_value = parts
        try:
            vertices.append((float(x_value), float(y_value), float(z_value)))
        except ValueError as exc:
            raise ValueError(f"Non-numeric vertex value at line {line_number}") from exc
    if not vertices or len(vertices) % 3 != 0:
        raise ValueError("ASCII STL vertex list is empty or malformed")
    triangle_count = len(vertices) // 3
    return _summarize_vertices(vertices, triangle_count, "ascii", path.name)


def inspect_stl(path: str | Path) -> dict[str, object]:
    stl_path = Path(path)
    data = _read_candidate_file(stl_path)
    looks_ascii = data[:5].lower() == b"solid" and b"\0" not in data[:256]
    if looks_ascii:
        try:
            return _inspect_ascii_stl(stl_path)
        except ValueError:
            # A few binary exporters still write a "solid" prefix.
            pass
    return _inspect_binary_stl(stl_path, data)
