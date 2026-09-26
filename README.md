# Causal Evaluation of Recovery in LLM Agents

Minimal public utilities for evaluating recovery decisions in long-horizon LLM agents.

The repository contains the analysis layer for matched no-recovery/recovery outcomes and a lightweight Causal Intervention Router (CIR) decision rule. Model checkpoints, benchmark data, raw trajectories, and private execution infrastructure are not included.

## Contents

- `src/causal_recovery/core.py`: paired outcome labels, source-task cluster bootstrap, and source-level sign-flip testing.
- `src/causal_recovery/cir.py`: frozen CIR scoring and refresh decision rule.
- `scripts/analyze_pairs.py`: summarize paired outcomes from a CSV file.
- `scripts/route_recovery.py`: apply CIR to pre-intervention prediction features.
- `tests/test_core.py`: basic unit tests for the public utilities.

## Input format

`analyze_pairs.py` expects a UTF-8 CSV with these columns:

```text
source_id,condition,delay,no_recovery_success,recovery_success
```

Each row represents one paired episode. Source-task identifiers are used as the uncertainty-resampling unit.

## Usage

```bash
python3 scripts/analyze_pairs.py \
  --input path/to/paired_outcomes.csv \
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
