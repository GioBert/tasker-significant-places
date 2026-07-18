#!/usr/bin/env python3
"""Replay synthetic GPS samples through the Significant Places model."""

from __future__ import annotations

import argparse
from pathlib import Path

from significant_places_model import (
    CSV_HEADER,
    SignificantPlacesSimulator,
    load_config,
    load_known_places,
    load_records,
    load_samples,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("samples", type=Path, help="Synthetic TIMESTAMP;LAT;LON;ACCURACY input")
    parser.add_argument("--config", type=Path, default=Path("config/tasker_globals.csv"))
    parser.add_argument("--known-places", type=Path)
    parser.add_argument("--resume-csv", type=Path, help="Optional existing daily CSV used to rebuild state")
    parser.add_argument("--output", type=Path, help="Optional simulated CSV output")
    args = parser.parse_args()

    simulator = SignificantPlacesSimulator(load_config(args.config), load_known_places(args.known_places))
    samples = load_samples(args.samples)
    if args.resume_csv:
        if not samples:
            parser.error("--resume-csv requires at least one sample")
        recovered = simulator.recover_from_records(
            load_records(args.resume_csv), samples[0].timestamp.date().isoformat()
        )
        print(f"recovered={'true' if recovered else 'false'}")
    events: dict[str, int] = {}
    for sample in samples:
        result = simulator.process(sample)
        events[result.event] = events.get(result.event, 0) + 1

    print(f"samples={sum(events.values())} records={len(simulator.records)}")
    for event, count in sorted(events.items()):
        print(f"{event}={count}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        lines = [CSV_HEADER, *(record.to_csv() for record in simulator.records)]
        args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
