from __future__ import annotations

import struct
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from stl_inspector.parser import inspect_stl


ASCII_STL = """solid triangle
facet normal 0 0 1
  outer loop
    vertex 0 0 0
    vertex 1 0 0
    vertex 0 1 0
  endloop
endfacet
endsolid triangle
"""


class InspectStlTests(unittest.TestCase):
    def test_ascii_stl_is_parsed(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "triangle_ascii.stl"
            path.write_text(ASCII_STL, encoding="utf-8")

            report = inspect_stl(path)

        self.assertEqual(report["stl_type"], "ascii")
        self.assertEqual(report["triangle_count"], 1)
        self.assertEqual(report["dimensions_mm"], {"x": 1.0, "y": 1.0, "z": 0.0})

    def test_binary_stl_is_parsed(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "triangle_binary.stl"
            header = b"Binary STL".ljust(80, b" ")
            triangle_count = struct.pack("<I", 1)
            normal = struct.pack("<fff", 0.0, 0.0, 1.0)
            vertices = struct.pack(
                "<fffffffff",
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
            )
            attr = struct.pack("<H", 0)
            path.write_bytes(header + triangle_count + normal + vertices + attr)

            report = inspect_stl(path)

        self.assertEqual(report["stl_type"], "binary")
        self.assertEqual(report["triangle_count"], 1)
        self.assertEqual(report["dimensions_mm"], {"x": 1.0, "y": 1.0, "z": 0.0})

    def test_empty_file_is_rejected(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "empty.stl"
            path.write_bytes(b"")

            with self.assertRaisesRegex(ValueError, "empty"):
                inspect_stl(path)


if __name__ == "__main__":
    unittest.main()
