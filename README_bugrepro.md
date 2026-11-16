# bugrepro: a bug reproduction agent

Give it a bug report and a repository. A local Qwen3 model (via Ollama) explores
the repo, writes a test that should fail if the bug is real, runs it, and
reports a verdict.

## Setup

```
pip install ollama
ollama pull qwen3
```

## Usage

```
python run_agent.py --target ./test_repo --report bug_reports/bool_priority.txt \
    --max-steps 15 --log-file ./logs/baseline.log
```

| Flag | Meaning |
|---|---|
| `--target` | Repository to work in (default `./`) |
| `--report` | Bug report: a path to a text file, or the report text itself |
| `--max-steps` | Maximum agent loop iterations (default 15) |
| `--log-file` | Also write the full trace to this file |
| `--model` | Ollama model (default `qwen3`) |

The agent writes one file into the target, `repro_test.py`. Reset the target
with Git between runs (`git checkout . && git clean -fd`).

## How it works

1. The model gets four tools: `list_files`, `read_file`, `write_repro_test`,
   `run_repro_test`, plus `report_verdict` to finish.
2. It loops: choose a tool, the harness runs it, the result goes back to the model.
3. The loop ends when the model reports a verdict or `--max-steps` is reached.

Guardrails enforced in code, not just in the prompt:

- All paths must stay inside `--target`.
- The only file the agent can write is `repro_test.py`.
- `REPRODUCED` is accepted only if the last test run really raised an
  `AssertionError`; `NOT_REPRODUCED` only if the last run really passed.
  Otherwise the verdict becomes `INCONCLUSIVE`.
- Tool errors go back to the model as text instead of crashing the agent.
- The bug report and file contents are labeled as untrusted data (prompt
  injection defense, which Josh's archbot lacked).

## Verdicts and exit codes

| Verdict | Exit code | Meaning |
|---|---|---|
| `REPRODUCED` | 0 | The test failed an assertion: bug confirmed |
| `NOT_REPRODUCED` | 1 | The test passed: code behaves correctly |
| `INCONCLUSIVE` | 2 | Vague report, broken test, step limit, or downgraded claim |

## Example reports

- `bug_reports/bool_priority.txt`: a real bug in the testbed (`True` is accepted as a priority)
- `bug_reports/sorting_claim.txt`: not a bug; the expected verdict is `NOT_REPRODUCED`
- `bug_reports/vague.txt`: too vague to test; the expected verdict is `INCONCLUSIVE`

## Known limitations

- The test runs as a normal Python subprocess (10 second timeout) and is **not
  sandboxed**. Only run it against code you trust.
- A wrong expectation in the test can produce a failing assertion that is not a
  real bug (a false positive). The harness checks that the test failed, not that
  the test is right.
