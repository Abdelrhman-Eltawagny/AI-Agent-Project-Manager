# Contributing

Thanks for your interest in improving AI Agent Project Manager.

## Development setup

```bash
git clone https://github.com/YOUR_USERNAME/ai-agent-project-manager.git
cd ai-agent-project-manager
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make test
```

`make test` first runs `python main.py --test --mock` (which generates `outputs/final_project_plan.json`, needed by the server tests) and then the unit tests. No Ollama or GPU is required.

To try a real model: install [Ollama](https://ollama.com), `ollama pull qwen2.5:7b-instruct`, then `make run DOC=examples/inputs/clinic_project.md`.

## Design rules

1. **Agents propose, Python decides.** An agent returns a typed proposal. It never mutates the project state, generates IDs, schedules work or validates the plan.
2. **Merge on a copy.** Proposals are merged into a deep copy of the state, validated, then committed.
3. **Every agent step needs a failure policy:** fatal, skipped, or a deterministic fallback. See `orchestrator/orchestrator.py`.
4. **Small prompts, strict schemas.** Local 3B-7B models need short context slices and Pydantic-validated output.
5. **Deterministic validation is authoritative.** The semantic (LLM) review stays advisory.

## Adding or changing an agent

A new agent step usually touches:

- `agents/` - the agent class (role, prompt builder, output schema) and its registration in `agents/__init__.py`
- `models/` - the proposal and state models, and any new enum values
- `orchestrator/decisions.py` - when the new action should be chosen
- `orchestrator/orchestrator.py` - how its proposal is merged and what happens when it fails
- `validators/deterministic_validator.py` - rules for any new entity
- `services/mock_llm.py` and `tests/` - a mock response and tests so CI stays offline

## Pull requests

- Keep changes focused and describe the motivation.
- Add or update tests; all tests must pass offline.
- Update `docs/` and the README when behaviour or configuration changes.
- Never commit `.env`, run logs or generated `outputs/`.

## Reporting bugs

Use the bug-report issue template and attach `outputs/run.log` and `outputs/execution_log.json` (remove sensitive data first).
