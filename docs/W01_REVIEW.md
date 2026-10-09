# W01 review

Status: **GO WITH W02 CONSTRAINTS**

Review due: 2026-10-18

## Evidence available

- Local Git repository and GitHub remote configured.
- Hardware and editor audit recorded.
- ShinkaEvolve pinned at `8adc053a2ce4511ad2ac310e004c530a73fb974a`, Apache-2.0.
- Project Python 3.11 environment created; ShinkaEvolve 0.0.7 import and CLI verified.
- Official circle-packing evaluator executed twice with identical valid score `0.9597642169962064`.
- DeepSeek connectivity probe completed: 9 input tokens, 1 output token, 0 retries, 0.932 seconds.
- Bounded ShinkaEvolve run A2 produced a valid candidate with score `1.2793899694857103` at API cost `$0.0008624`.
- Bounded ShinkaEvolve run B produced an invalid candidate with a higher raw score `2.2391574738041835`; the evaluator reported circle overlap and `correct=false` at API cost `$0.0007819`.
- A2 used 2064 input and 2048 output tokens; B used 1841 input and 1872 output tokens. A2 reached the requested output-token cap but produced a valid candidate. The two Shinka-recorded costs total `$0.0016443`, or about CNY `0.01184` at the planning rate of 7.2. These are framework cost records and estimates, not a reconciled DeepSeek invoice.
- The compact cost and run ledgers include generated-program SHA-256 hashes. Full logs and programs are retained locally in ignored `experiments/runs/`; they are not yet a portable public artifact.
- The runs used distinct output directories, but no explicit framework random seed was frozen. Prompt hashes remain pending in the ledger. These smoke runs establish local operability; confirmatory reproducibility still requires frozen seeds and complete prompt artifacts.
- A separate configuration with `max_patch_resamples=0` failed before any LLM request was logged. Its raw failure record is retained; it consumed no observed model tokens.
- ReEvo HEAD was resolved at `6dce18257da5e11db2d138e417a2fffc5c72d05f`, and its official README documents DeepSeek support. It targets combinatorial heuristics and requires a task adapter, so it remains a conditional baseline with a two-workday limit.

## W02 constraints

- Treat evaluator feasibility as a hard gate. A raw score from an invalid candidate cannot enter the best-feasible curve.
- Set `PYTHONUTF8=1` or use an UTF-8 log sink for Windows runs; the upstream emoji console messages otherwise emit GBK logging errors.
- Make DeepSeek model name, embedding setting, proposal cap, retries, and cost conversion explicit in the run manifest.
- Add an application-side pre-call budget check before larger searches. Shinka's `max_api_costs` was set to USD `0.05` in these probes and must not be treated as automatic enforcement of the CNY `500` project ceiling.
- Build the blind extraction and attack-truth isolation tests before adapting the ShinkaEvolve task.

## Decision

W01 passes. Continue to W02 with the constraints above. The result is an engineering gate, not evidence that ShinkaEvolve or DeepSeek is superior for watermarking.
