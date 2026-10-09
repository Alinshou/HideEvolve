# HideEvolve feasibility assessment V0

Date: 2026-10-09

Decision: **GO for W01-W04 exploratory validation**

## Paper question

Under a fixed total search cost, can a foundation-model agent discover executable blind image-watermarking programs with higher feasible-candidate discovery efficiency and stronger robustness than general program-evolution baselines?

The main evidence must compare the original ShinkaEvolve baseline with the proposed mechanism under matched seeds, evaluator access, candidate budget, and total token/currency cost. ReEvo is a secondary independent search baseline if its official implementation can be reproduced within the declared integration limit.

## Evidence supporting feasibility

1. The prior `Foundation Model Agent` workspace already demonstrated an auditable DCT/QIM evaluator, search baselines, DeepSeek proposal loop, and three completed 32-evaluation agent trajectories.
2. That prior work retained failures and found no established agent advantage. This gives HideEvolve a tested engineering base and a real unresolved scientific question.
3. The local machine is adequate for evaluator development and pilot experiments: Intel i7-14650HX, 16 GB RAM, NVIDIA RTX 5070 Laptop GPU with 8 GB VRAM, and about 418 GB free disk at audit time.
4. The DeepSeek budget ceiling is CNY 500. Earlier narrow-grid exploratory agent runs were inexpensive, so W01-W03 pilots are affordable. Program-generation prompts may be much larger; W01 must measure actual token and retry costs before formal budgets are frozen.

## Main risks and controls

| Risk | Current assessment | Control or decision gate |
|---|---|---|
| Novelty is too close to generic program evolution | Medium-high | G1 requires a concrete watermark-specific structural failure and literature/implementation comparison. |
| Generated programs are invalid or violate blind extraction | High | W02 contract tests isolate image, message, attack truth, and random seed from `decode`. Invalid proposals remain in the denominator. |
| 8 GB VRAM limits learned watermark baselines | Medium | Start with official inference weights and small batches; record CPU/GPU fallback and do not make training a requirement. |
| Search cost exceeds CNY 500 | Medium | Meter every DeepSeek call and use phase caps in `configs/budget_v0.yaml`; run a cost probe before multi-seed pilots. |
| Formal sample size is too expensive | Medium-high | Use pilot variance and effect size at W12. The prior workspace found that 400 images missed a strict precision target and 600 passed its tested grid; this informs planning but does not freeze the new study size. |
| Upstream repositories or weights are unavailable | Medium | Pin commit SHAs and licenses when accessible; preserve connection failures and enforce the two-day limit for conditional baselines. |
| New mechanism only improves syntax validity | High | Compare B0, B1, and M. G2 requires improvement in feasible robust quality or discovery efficiency, not only legal-code rate. |

## Scope decision

The project is feasible as a first-paper attempt if the contribution is framed around search efficiency and structural program discovery. Acceptance is not predictable at W01. The plan has publishable fallback outcomes: a careful negative comparison, evaluator/protocol contribution, or a narrower empirical study, provided the evidence is complete and the claims match it.

W01 passed with constraints documented in `docs/W01_REVIEW.md`. G1 remains binding: failure to reproduce the original framework or identify a watermark-specific structural bottleneck triggers revision before developing the proposed module.
