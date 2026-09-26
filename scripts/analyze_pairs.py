#!/usr/bin/env python3
"""Summarize paired recovery outcomes from a small CSV file.

Required columns: source_id, condition, delay, no_recovery_success,
recovery_success. The source task, rather than the episode, is the sampling
unit for uncertainty estimates.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from causal_recovery.core import (  # noqa: E402
    bootstrap_cluster_ci,
    classify_outcome,
    paired_effect,
    source_cluster_effects,
    source_cluster_sign_flip_pvalue,
)


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    required = {
        "source_id",
        "condition",
        "delay",
        "no_recovery_success",
        "recovery_success",
    }
    missing = required - set(rows[0]) if rows else required
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    return rows


def summarize(rows: list[dict[str, str]], draws: int, seed: int) -> dict:
    effects = [paired_effect(r["no_recovery_success"], r["recovery_success"]) for r in rows]
    clusters = source_cluster_effects(rows)
    counts = {name: 0 for name in ("rescue", "harm", "stable_success", "stable_failure")}
    for row in rows:
        counts[classify_outcome(row["no_recovery_success"], row["recovery_success"])] += 1
    ci = bootstrap_cluster_ci(clusters, draws=draws, seed=seed)
    return {
        "episodes": len(rows),
        "source_tasks": len(clusters),
        "effect_pp": 100.0 * sum(effects) / len(effects),
        "cluster_bootstrap_95_ci_pp": [100.0 * ci[0], 100.0 * ci[1]],
        "cluster_sign_flip_p": source_cluster_sign_flip_pvalue(
            clusters, draws=max(draws, 100_000), seed=seed
        ),
        "outcomes": counts,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--bootstrap-draws", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260926)
    args = parser.parse_args()
    report = summarize(load_rows(args.input), args.bootstrap_draws, args.seed)
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
