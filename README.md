# Causal Evaluation of Recovery in LLM Agents

This repository contains the research artifacts for **When Harnesses Lose the Signal: Causal Evaluation of Recovery in LLM Agents**.

Large language model agents rely on execution harnesses to deliver observations, maintain interaction history, and recover from failures. A recovery operation can repair a trajectory, but it can also disrupt an execution that would otherwise succeed. Aggregate success rates hide these opposing effects and offer limited guidance about when recovery should be applied.

We study harness recovery as a causal decision problem. Starting from the same execution state and model prefix, we compare matched continuations with and without recovery, separate trajectory-level rescue from harm, and measure how recovery value changes with observation quality and intervention timing.

## Research questions

This project asks:

1. How do stale or missing observations change an agent's subsequent execution and final outcome?
2. When does refreshing the observation rescue a failing trajectory, and when does it harm an otherwise successful one?
3. How does recovery value change as intervention is delayed?
4. Can pre-intervention execution signals support selective recovery without relying on the final outcome?

## Framework

### Controlled observation interventions

We evaluate four observation conditions in long-horizon ALFWorld tasks:

- **Clean:** the agent receives the current environment observation.
- **One-step stale:** the current observation is replaced by the preceding observation.
- **Two-step stale:** an older observation is supplied, allowing the error to persist across a larger state change.
- **Missing:** the current observation content is withheld.

Recovery is evaluated at delays of 0, 1, 2, and 4 environment actions.

### Matched counterfactual continuations

For each eligible task state, the harness constructs two continuations from the same environment state, execution history, model input, and decoding configuration:

- **No recovery:** execution continues without a refresh.
- **Refresh:** the harness queries the environment and appends the returned observation to the model context.

The paired final outcomes produce four trajectory-level categories:

| No recovery | Refresh | Outcome |
|---|---|---|
| Failure | Success | **Rescue** |
| Success | Failure | **Harm** |
| Success | Success | **Stable success** |
| Failure | Failure | **Stable failure** |

This decomposition exposes recovery effects that are hidden by average success alone.

### Causal Intervention Router

The **Causal Intervention Router (CIR)** uses only information available before an intervention. It estimates:

- whether the trajectory has received an erroneous observation;
- the likelihood of success without recovery;
- the likelihood of success after refresh.

CIR combines the predicted rescue value and harm risk, checks candidate intervention times sequentially, and applies at most one refresh per episode. The underlying agent is not retrained.

## Main findings

Our current experiments use a Qwen3-14B ReAct-style agent on ALFWorld, with additional analyses at other model scales.

- Recovery effects are heterogeneous: refresh can rescue and harm different trajectories under the same observation condition.
- Recovery value depends on timing. Delayed recovery does not produce a uniformly monotonic change in recoverability.
- Retaining factual failures weakens the stale-versus-clean contrast, showing why cohort construction matters for causal interpretation.
- Under two-step stale observations at delay 4, eight rescues are shared by full refresh and a content-ablated refresh. Newly returned observation content is therefore not necessary for those shared rescues, although the remaining mechanism is not identified by this comparison alone.
- On 75 held-out prefix-feasible tasks (300 episodes), frozen CIR improves overall success from **70.33% to 73.33%**: a **+3.00 percentage-point** effect with a source-task bootstrap 95% confidence interval of **[0.67, 5.67]**. The policy produces 11 rescues and 2 harms.
- Under two-step stale observations, CIR improves success by **9.33 percentage points** and concentrates most interventions on this condition.
- Cross-model diagnostics indicate that detecting anomalous observations is easier than predicting whether recovery will improve the final outcome. This distinction is central to selective recovery.

All confidence intervals are computed by resampling source tasks so that observation conditions from the same task remain clustered.

## Scope

The current study focuses on controlled observation errors, a fixed refresh operation, and textual ALFWorld tasks. The paired effects identify recovery outcomes for states reached by the evaluation protocol; they should not be interpreted as unconditional effects over all agent tasks or naturally occurring failures.

## Repository status

This is the initial public repository. The reproducibility release is being organized and will include:

- paired-execution and observation-intervention code;
- CIR training and frozen-policy evaluation scripts;
- experiment configurations and cohort manifests;
- source-task-level statistical analysis;
- figure-generation scripts and machine-readable result tables.

Commands and directory-level documentation will be added together with the corresponding artifacts so that the README does not describe files that are not yet available.

## Citation

Citation information will be added with the public paper release.

## Questions

Please use GitHub Issues for questions about the evaluation protocol, released artifacts, or reproducibility.
