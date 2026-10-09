# HideEvolve research rules

These rules apply to the whole repository.

## Research integrity

- Treat the core claim as a hypothesis. Retain negative and null results.
- Keep exploratory development separate from confirmatory experiments.
- Freeze data, attacks, metrics, prompts, seeds, budgets, and selection rules before confirmatory runs.
- Count invalid, duplicate, crashed, and timed-out candidates under the declared budget rule.
- Preserve raw run records as append-only evidence. Corrections create a new run or protocol version.
- Record code revision, configuration, random seeds, model identifier, prompts, token use, cost, runtime, failures, and dataset manifest for every paper result.
- Do not commit API keys, private data, raw third-party datasets, model weights, or large generated outputs.
- Verify references, repositories, licenses, and model availability before citing or running them.

## Engineering discipline

- Build and test the evaluator before relying on agent search results.
- Compare methods under both candidate-count and total-cost views.
- Use configuration files for experiments and keep public interfaces documented.
- Add tests for scientific invariants such as blind extraction, payload recovery, attack determinism, and failure accounting.
- Keep DeepSeek spending within `configs/budget_v0.yaml`. A paid run must have a named run ID and an estimated maximum cost.

## Study boundary

- The first paper studies whether a foundation-model agent can discover executable blind image-watermarking programs more efficiently than strong search baselines under equal cost.
- The initial hard task combines geometric desynchronization with regional deletion.
- The previous DCT/QIM project is prior engineering evidence. Its exploratory outcomes are not new HideEvolve paper results.
