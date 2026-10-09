# HideEvolve

HideEvolve is the workspace for a first paper on foundation-model-agent discovery of blind image-watermarking programs.

The study asks whether an agent can discover executable and robust `embed`/`decode` programs more efficiently than strong search baselines under the same total cost. The planned hard task combines geometric desynchronization with regional deletion. The hypothesis is open; negative results remain part of the study.

## Current status

W01 opened early on 2026-10-09. The environment, upstream inventory and DeepSeek connectivity are operational. The initial two bounded ShinkaEvolve searches produced one valid and one invalid candidate; a clean-environment reproduction and two additional seeded host runs have since passed. W01 acceptance is GO with a documented evidence-form deviation: full raw logs and post-run display images substitute for historical desktop screenshots. See `每周实验报告/W01_第一周任务完成与严格验收报告.md`.

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
