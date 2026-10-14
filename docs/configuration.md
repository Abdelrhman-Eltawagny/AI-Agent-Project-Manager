# Configuration

## `config/settings.json`

| Setting | Checked-in value | Meaning |
|---------|------------------|---------|
| `ollama_base_url` | `http://localhost:11434` | Ollama server |
| `model` | `qwen2.5:3b` | Ollama model (code default: `qwen2.5:7b-instruct`) |
| `temperature` | 0.1 | Low randomness for structured output |
| `llm_timeout_seconds` | 300 | Timeout per LLM call |
| `health_timeout_seconds` | 5 | Ollama health-check timeout |
| `keep_alive` | `30m` | How long Ollama keeps the model loaded |
| `max_iterations` / `max_action_rounds` / `max_agent_attempts` / `max_repair_rounds` | 80 / 6 / 3 / 2 | Loop guards |
| `max_context_chars` | 3500 | Cap on the document slice sent to an agent |
| `default_duration_weeks` / `sprint_length_weeks` | 4 / 1 | Defaults when the document does not say |
| `utilization_target` | 0.9 | Target role-pool utilisation before falling back to 100 % |
| `max_epics` / `max_tasks_per_epic` / `min_tasks_per_epic` | 8 / 8 / 2 | Plan-size limits |
| `max_risks` / `max_dependencies_per_task` | 10 / 3 | Plan-size limits |
| `min_estimate_hours` / `max_estimate_hours` | 1 / 24 | Accepted task estimate range |
| `type_min_sprint` | `{"qa": 2}` | QA work cannot start before sprint 2 |
| `output_dir` | `outputs` | Where results are written |

## Environment variables

| Variable | Used by | Meaning |
|----------|---------|---------|
| `PM_MODEL` | settings loader, web service | Overrides `model` |
| `PM_OLLAMA_URL` | settings loader, web service | Overrides `ollama_base_url` |
| `PLAN_PATH` | `server.py` | Plan JSON served by the assistant (default `outputs/final_project_plan.json`) |
| `API_KEY` | `server.py`, Compose | Shared key expected in the `x-api-key` header |

CLI flags `--model` and `--output-dir` override the file for a single run.

## Team: `config/team.json`

Each member has `id`, `name`, `role`, `skills` and `capacity_hours_per_sprint`. Roles used by the scheduler: `project_manager`, `backend_developer`, `frontend_developer`, `ui_ux_designer`, `qa_engineer`, `devops_engineer`. The checked-in team has 8 members and 220 h of capacity per one-week sprint.

## Choosing a model

| Model | Use it for | Observed |
|-------|------------|----------|
| `qwen2.5:3b` | Smoke tests, fast iteration | 27 tasks in about 1 minute (resumed run); 1 dependency |
| `qwen2.5:7b` / `7b-instruct` | Real plans | 48 tasks and 30-45 dependencies in 18-59 minutes |
