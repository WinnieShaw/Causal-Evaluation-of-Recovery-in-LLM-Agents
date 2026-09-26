#!/usr/bin/env python3
"""Apply a frozen CIR configuration to pre-intervention feature rows."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from causal_recovery.cir import CIRConfig, should_refresh  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    config = CIRConfig(**json.loads(args.config.read_text(encoding="utf-8"))) if args.config else CIRConfig()
    with args.input.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    required = {"p_error", "p_no_recovery", "p_refresh", "delay"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"input must contain {sorted(required)}")
    for row in rows:
        row["refresh"] = str(
            int(
                should_refresh(
                    float(row["p_error"]),
                    float(row["p_no_recovery"]),
                    float(row["p_refresh"]),
                    int(row["delay"]),
                    config,
                )
            )
        )
    with args.output.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
