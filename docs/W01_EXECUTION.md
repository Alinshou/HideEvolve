# W01 execution checklist

Week: 2026-10-12 to 2026-10-18

Opened early: 2026-10-09

Goal: create a reproducible baseline environment and obtain two independent official ShinkaEvolve example runs.

## Deliverables

- [x] Initialize local Git repository and configure `origin`.
- [x] Record local hardware, editor, Python, Git, and GPU state.
- [x] Record the prior project revision and its reuse boundary.
- [x] Set the DeepSeek project budget ceiling to CNY 500.
- [x] Create an upstream baseline manifest with verification states.
- [x] Clone ShinkaEvolve and pin its exact commit and license.
- [x] Create an isolated Python 3.11 environment from the upstream instructions.
- [x] Run the official circle-packing evaluator twice; both runs returned the same valid score.
- [x] Run the official example twice with distinct run identifiers.
- [x] Record wall time, API model, token use, estimated cost, failures, and output hashes.
- [x] Inspect ReEvo entry points and estimate integration risk.
- [x] Complete `docs/W01_REVIEW.md` with GO, REVISE, or STOP.

## Acceptance rule

W01 passes when the official ShinkaEvolve example can be rerun twice from a pinned commit with complete logs and cost records. If network, dependency, authentication, or platform issues block it, the review must contain a reproducible failure record and a bounded repair plan.

## Remaining reproducibility work

- Prompt hashes and explicit framework seeds were not frozen for the W01 smoke runs. Complete these before paper experiments.
- Full raw run directories are local ignored artifacts; prepare a portable evidence bundle before reporting paper results.

- GitHub access was intermittent on 2026-10-09, then recovered. Each remote operation still needs an explicit exit status and failure record.
- The key is available only in the prior local project's ignored `.env`. It is loaded transiently for W01 and never copied into this repository.
- The official default configuration expects OpenAI embeddings. DeepSeek-only runs must explicitly set `embedding_model: null` and record that protocol change.
