# W01 review

Status: **GO WITH DOCUMENTED EVIDENCE-FORM DEVIATION AND W02 CONSTRAINTS**

Review due: 2026-10-18

## 2026-10-09 final direct-evidence check

The user asked us to inspect the evidence directly rather than wait for their screenshots. We inspected C/D source logs, `correct.json`, generation-1 SQLite metadata, generated code, and the archive readback. Each run exited 0 and produced a `correct=true` candidate with internally consistent score, tokens, cost and hashes. The screenshot line item is fulfilled through preserved raw logs plus explicitly labeled post-run log display images; live historical desktop screenshots do not exist and are not claimed. This is a documented evidence-form deviation. The missing first-install transcript is addressed by a separate clean-environment installation reproduction, not backdated. W01 engineering and documentary acceptance is GO under these limits. W02 planning may proceed; no watermark method claim is made.

## 2026-10-09 closeout update

Standalone `repro/repo_audit.md` and `docs/REEVO_INTEGRATION_RISK_W01.md` are present. A separately dated clean environment installation reproduction in `repro/install.log` passed with exit code 0, `pip check`, and exact installed package-version comparisons. The original first-install transcript remains missing. Two further official example runs C/D completed in the new environment with distinct host RNG seeds; both generated valid candidates. New framework-estimated API cost is CNY 0.01040, bringing the recorded W01 estimate to about CNY 0.02225. Full portable evidence, stored prompt hashes, logs, code, and SQLite backups were archived in `每周实验报告/W01_完整证据包_20261009.zip` and verified by CRC and hash readback. Log display images are post-run renderings; the final direct-evidence check above records the accepted evidence-form deviation.

## 2026-10-09 strict-schedule initial audit amendment

The original engineering GO below did not establish complete delivery against page 3 of `HideEvolve_V5.pdf`. The original installation log and log screenshots were not found, and standalone repository-audit and ReEvo-risk documents were missing. The detailed weekly report in `每周实验报告/W01_第一周任务完成与严格验收报告.md` now supplies audit and risk content, but does not fabricate the absent historical installation evidence. W01 remains REVISE for strict delivery until gaps are closed or an explicit exception is recorded. Current SQLite records contain prompt fields; their hashes have not yet been organized into the ledger. Missing framework seeds remain a historical limitation.

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

Original engineering decision: GO to W02 with the constraints above. The strict delivery amendment takes precedence over any interpretation that W01 is unconditionally complete. The result is an engineering gate, not evidence that ShinkaEvolve or DeepSeek is superior for watermarking.
