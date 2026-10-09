# HideEvolve

HideEvolve is the workspace for a first paper on foundation-model-agent discovery of blind image-watermarking programs.

The study asks whether an agent can discover executable and robust `embed`/`decode` programs more efficiently than strong search baselines under the same total cost. The planned hard task combines geometric desynchronization with regional deletion. The hypothesis is open; negative results remain part of the study.

## Current status

W01 opened early on 2026-10-09 and completed its environment audit, upstream baseline inventory, DeepSeek connectivity probe, and two bounded official ShinkaEvolve searches. One generated candidate was valid and one was invalid. The review permits continuing to W02 with the recorded constraints.

The detailed schedule is in `HideEvolve_V5.pdf`. The feasibility decision is in `docs/FEASIBILITY_ASSESSMENT_V0.md`, and the active checklist is in `docs/W01_EXECUTION.md`.

The W01 reproduction guide is `docs/W01_REPRODUCTION.md`; the compact result summary is `repro/w01_results.json`.

## Repository layout

```text
configs/        Versioned budgets and later experiment protocols
docs/           Feasibility, decisions, weekly reviews, and paper notes
experiments/    Cost probes and compact run manifests
repro/          Hardware, environment, and upstream baseline manifests
third_party/    Local upstream checkouts; ignored unless explicitly vendored
```

Secrets belong in `.env`, which is ignored by Git. Use `.env.example` as the variable-name template.
