"""Runtime scoring rule for the Causal Intervention Router."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CIRConfig:
    """Thresholds selected before evaluation on a held-out cohort."""

    error_threshold: float = 0.876
    failure_threshold: float = 0.052
    utility_threshold: float = 0.0
    harm_penalty: float = 2.0
    minimum_delay: int = 1


def recovery_utility(p_no_recovery: float, p_refresh: float, harm_penalty: float = 2.0) -> float:
    """Estimate rescue value minus weighted harm risk."""
    rescue_score = (1.0 - p_no_recovery) * p_refresh
    harm_score = p_no_recovery * (1.0 - p_refresh)
    return rescue_score - harm_penalty * harm_score


def should_refresh(
    p_error: float,
    p_no_recovery: float,
    p_refresh: float,
    delay: int,
    config: CIRConfig = CIRConfig(),
) -> bool:
    """Apply the pre-intervention CIR decision rule at one candidate time."""
    if delay < config.minimum_delay:
        return False
    if p_error < config.error_threshold:
        return False
    if (1.0 - p_no_recovery) < config.failure_threshold:
        return False
    utility = recovery_utility(p_no_recovery, p_refresh, config.harm_penalty)
    return utility >= config.utility_threshold
