# Decision log

## 2026-10-09 — Start W01

- Decision: proceed with W01-W04 exploratory validation.
- Model provider: DeepSeek API.
- Total API budget ceiling: CNY 500; revise only with an explicit later decision.
- Primary paper target: a rigorous first paper on agent-based discovery of blind image-watermarking programs.
- Prior workspace: reuse code and engineering lessons only after inventory and attribution; do not treat its exploratory outcomes as new-study evidence.
- Gate: do not develop the proposed joint-mutation module until G1 identifies a reproducible, watermark-specific structural bottleneck.

## 2026-10-09 — W02 engineering start

- Decision: accept W01 as GO with the documented evidence-form differences in `docs/W01_REVIEW.md`; begin W02 early and record the actual date.
- Protocol: freeze exploratory v1 at RGB 256x256, 32-bit payloads, 16-byte keys, PSNR >=35 dB, A0 plus configured A1 attacks. W09/W12 remain the formal attack and preregistration gates.
- Data: exclude the old project's 100 COCO identities and the Stage 7 development-only 1000 identities; freeze D-search 60, D-select 20 and local ignored D-test 1000 with hash anchors.
- Gate: do not start paid watermark Agent searches until W02 contract tests pass and the execution boundary for untrusted generated code is strengthened beyond the current Windows audit hook.
- Result: W02 contract suite passed 7/7; spatial LSB and DCT/QIM smoke baselines completed 6/6 valid no-attack evaluations. These are evaluator engineering results, not method comparisons.
