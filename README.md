# Causal Evaluation of Recovery in LLM Agents

Minimal public utilities and derived experiment results for evaluating recovery decisions in long-horizon LLM agents.

The repository contains the analysis layer for matched no-recovery/recovery outcomes, a lightweight Causal Intervention Router (CIR) decision rule, and sanitized result tables from the main analyses. Model checkpoints, benchmark data, raw trajectories, and private execution infrastructure are not included.

## Contents

- `src/causal_recovery/core.py`: paired outcome labels, source-task cluster bootstrap, and source-level sign-flip testing.
- `src/causal_recovery/cir.py`: frozen CIR scoring and refresh decision rule.
- `scripts/analyze_pairs.py`: summarize paired outcomes from a CSV file.
- `scripts/route_recovery.py`: apply CIR to pre-intervention prediction features.
- `tests/test_core.py`: basic unit tests for the public utilities.
- `data/mechanism_paired_outcomes.csv`: sanitized task-level paired outcomes for the mechanism-control analysis.
- `data/main_delay_effects.csv`, `data/main_intervention_effects.csv`: derived main-experiment summaries.
- `data/qwen8_fitted_cir_decisions.csv`, `data/qwen8_policy_summary.csv`, `data/qwen8_policy_comparisons.csv`: sanitized cross-model policy results.

## Input format

`analyze_pairs.py` expects a UTF-8 CSV with these columns. A ready-to-use example is included at `data/mechanism_paired_outcomes.csv`:

```text
source_id,condition,delay,no_recovery_success,recovery_success
```

Each row represents one paired episode. Source-task identifiers are used as the uncertainty-resampling unit.

## Usage

```bash
python3 scripts/analyze_pairs.py \
  --input data/mechanism_paired_outcomes.csv \
  --output analysis.json
```

For CIR routing, provide a CSV with `p_error`, `p_no_recovery`, `p_refresh`, and `delay`:

```bash
python3 scripts/route_recovery.py \
  --input path/to/features.csv \
  --output routed_features.csv
```

Run the checks with:

```bash
python3 tests/test_core.py -v
```

The public code uses only the Python standard library.
