#!/usr/bin/env python3
"""Create a public Tasker project export from a private full backup."""

from __future__ import annotations

import argparse
import copy
import xml.etree.ElementTree as ET
from pathlib import Path


PUBLIC_TOP_LEVEL_TAGS = {"Project", "Profile", "Task"}


def export_public(source: Path, destination: Path) -> None:
    source_root = ET.parse(source).getroot()
    public_root = ET.Element(source_root.tag, source_root.attrib)
    for child in source_root:
        if child.tag in PUBLIC_TOP_LEVEL_TAGS:
            public_root.append(copy.deepcopy(child))

    counts = {tag: len(public_root.findall(tag)) for tag in PUBLIC_TOP_LEVEL_TAGS}
    if counts != {"Project": 1, "Profile": 1, "Task": 3}:
        raise ValueError(f"unexpected public structure: {counts}")

    ET.indent(public_root, space="  ")
    xml = ET.tostring(public_root, encoding="unicode", short_empty_elements=True)
    destination.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n' + xml + "\n",
        encoding="utf-8",
        newline="\n",
    )

    exported = destination.read_text(encoding="utf-8")
    for forbidden in ("<Setting", "<Variable"):
        if forbidden in exported:
            raise ValueError(f"private element leaked into public export: {forbidden}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="Private full Tasker backup")
    parser.add_argument("destination", type=Path, help="Sanitized project XML")
    args = parser.parse_args()
    export_public(args.source, args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
