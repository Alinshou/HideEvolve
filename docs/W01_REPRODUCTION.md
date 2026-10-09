# W01 reproduction guide

W01 establishes a working local ShinkaEvolve and DeepSeek workflow. The saved results are summarized in `repro/w01_results.json`. This guide repeats the configuration; API outputs may change between runs.

## Local environment

Open the project root in VSCode. The interpreter is `.venv/python.exe`, a project-local Conda environment using Python 3.11.17. It is not a standard `venv` layout. VSCode settings point to this executable.

For a fresh Windows checkout, create a Python 3.11 environment at `.venv`, install `repro/requirements-lock.txt`, clone ShinkaEvolve into `third_party/ShinkaEvolve`, check out commit `8adc053a2ce4511ad2ac310e004c530a73fb974a`, and install that source with `pip install -e`. ReEvo is inventoried but is not required for the W01 example.

## Repeat the bounded example

Before a paid repeat, reserve a unique run ID and a maximum cost in the ledger. The original runs used one generated proposal with a 2048 output-token cap. The USD 0.05 upstream cap is a soft stopping condition; the CNY 500 project ceiling remains a separate budget policy.

Use PowerShell from the project root. Supply `DEEPSEEK_API_KEY` locally through the process environment. The earlier probes loaded it transiently from the prior local project's ignored `.env`. Never place a key in a command committed to Git.

```powershell
$env:PYTHONUTF8 = '1'
$taskRoot = (Get-Location).Path
$taskLauncher = Join-Path $taskRoot '.venv/Scripts/shinka_launch.exe'
$taskResults = Join-Path $taskRoot 'experiments/runs/w01-repeat-001'
Push-Location (Join-Path $taskRoot 'third_party/ShinkaEvolve')
try {
  & $taskLauncher 'variant@_global_=circle_packing_example' `
    "results_dir=$taskResults" 'run_name=repeat-001' `
    'max_evaluation_jobs=1' 'max_proposal_jobs=1' 'max_db_workers=1' `
    'db_config.num_islands=1' 'evo_config.llm_models=[deepseek-chat]' `
    'evo_config.llm_dynamic_selection=null' 'evo_config.embedding_model=null' `
    'evo_config.num_generations=2' '+evo_config.max_api_costs=0.05' `
    'evo_config.max_patch_attempts=1' 'evo_config.max_patch_resamples=1' `
    'evo_config.llm_kwargs.temperatures=[0]' 'evo_config.llm_kwargs.max_tokens=2048' `
    'evo_config.meta_rec_interval=null' 'evo_config.meta_llm_models=[]'
  if ($LASTEXITCODE -ne 0) { throw "Shinka exited with code $LASTEXITCODE" }
} finally {
  Pop-Location
}
```

## Inspect the result

Inspect `gen_1/results/correct.json` before using `metrics.json`. A high raw score is excluded from feasible comparisons when `correct` is false. Preserve the run directory, including failures, configuration, logs, token records, and generated code; append its summary to the run and cost ledgers.

The two original search directories are `experiments/runs/w01-shinka-deepseek-a2` and `experiments/runs/w01-shinka-deepseek-b`. Their generated-program hashes are in `experiments/run_manifest.csv`. The W01 run directories were retained locally and are ignored by Git.

Before paper experiments, freeze seeds, capture exact prompts and hashes, implement a pre-call budget check, and prepare a portable raw-evidence bundle. The W01 records are preliminary engineering evidence.
