"""Paired outcome summaries and source-task cluster uncertainty.

The public analysis layer deliberately consumes already-collected paired
outcomes. It does not assume access to model checkpoints or environment data.
"""
from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Iterable, Mapping, Sequence


def _as_binary(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)) and value in (0, 1):
        return int(value)
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "success", "won"}:
        return 1
    if text in {"0", "false", "no", "failure", "lost"}:
        return 0
    raise ValueError(f"expected a binary outcome, received {value!r}")


def classify_outcome(no_recovery: int | bool, recovery: int | bool) -> str:
    """Classify a paired binary outcome relative to no recovery."""
    pair = (_as_binary(no_recovery), _as_binary(recovery))
    return {
        (0, 1): "rescue",
        (1, 0): "harm",
        (1, 1): "stable_success",
        (0, 0): "stable_failure",
    }[pair]


def paired_effect(no_recovery: int | bool, recovery: int | bool) -> int:
    """Return the paired causal contrast in percentage-point units before scaling."""
    return _as_binary(recovery) - _as_binary(no_recovery)


def _percentile(values: Sequence[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot compute a percentile of an empty sample")
    position = (len(ordered) - 1) * q
    low, high = math.floor(position), math.ceil(position)
    if low == high:
        return ordered[low]
    weight = position - low
    return ordered[low] * (1.0 - weight) + ordered[high] * weight


def source_cluster_effects(rows: Iterable[Mapping[str, object]]) -> list[float]:
    """Average episode effects within each source task.

    Rows should contain ``source_id``, ``no_recovery_success`` and
    ``recovery_success``. Averaging within source before resampling keeps all
    conditions from a source task in the same bootstrap cluster.
    """
    by_source: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        source = str(row["source_id"])
        by_source[source].append(
            paired_effect(row["no_recovery_success"], row["recovery_success"])
        )
    if not by_source:
        raise ValueError("no paired rows were provided")
    return [sum(values) / len(values) for values in by_source.values()]


def bootstrap_cluster_ci(
    source_effects: Sequence[float], draws: int = 10_000, seed: int = 20260926
) -> tuple[float, float]:
    """Return a percentile 95% CI from source-task cluster bootstrap draws."""
    if not source_effects:
        raise ValueError("source_effects must not be empty")
    if draws < 1:
        raise ValueError("draws must be positive")
    rng = random.Random(seed)
    n = len(source_effects)
    boot = [
        sum(source_effects[rng.randrange(n)] for _ in range(n)) / n
        for _ in range(draws)
    ]
    return _percentile(boot, 0.025), _percentile(boot, 0.975)


def source_cluster_sign_flip_pvalue(
    source_effects: Sequence[float], draws: int = 100_000, seed: int = 20260926
) -> float:
    """Two-sided source-level sign-flip p-value for a paired mean effect."""
    if not source_effects:
        raise ValueError("source_effects must not be empty")
    if draws < 1:
        raise ValueError("draws must be positive")
    observed = abs(sum(source_effects) / len(source_effects))
    rng = random.Random(seed)
    count = 0
    n = len(source_effects)
    for _ in range(draws):
        signed = sum(value if rng.getrandbits(1) else -value for value in source_effects) / n
        count += abs(signed) >= observed
    return (count + 1) / (draws + 1)
