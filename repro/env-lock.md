# W01 environment lock draft

Captured: 2026-10-09

| Component | Observed value | Status |
|---|---|---|
| OS | Windows 11 10.0.26200, x64 | recorded |
| VS Code | 1.140.0 | recorded |
| Python | 3.11.17, project `.venv` | created from the official ShinkaEvolve recommendation |
| Git | 2.53.0.windows.2 | recorded |
| GPU | RTX 5070 Laptop, 8151 MiB, driver 592.27 | recorded |
| Docker | unavailable on PATH | optional until upstream requirements are known |
| DeepSeek key | loaded transiently from the prior local `.env` | never copied or logged |
| ShinkaEvolve SHA | `8adc053a2ce4511ad2ac310e004c530a73fb974a` | installed editable; import and CLI verified |
| ReEvo SHA | `6dce18257da5e11db2d138e417a2fffc5c72d05f` | remote HEAD verified; integration pending |

The global Anaconda environment is not the experiment environment. ShinkaEvolve 0.0.7 and its resolved dependencies are installed in the project-local Python 3.11 environment. The W01 package snapshot is in `repro/requirements-lock.txt`; later study stages must pin their own updated environments.

Prior engineering source: local `Foundation Model Agent` repository at commit `5093a8f0aed925f8e06c92591fdb1aa9a626fabb` (2026-10-08). Reuse requires an explicit file inventory and must preserve provenance.
