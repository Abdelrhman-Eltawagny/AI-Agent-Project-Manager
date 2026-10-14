# Orchestrator

A single loop: **inspect state -> decide next action -> select agent -> run agent -> validate output -> merge into canonical state (transactionally) -> consistency check -> retry / repair -> repeat.**

## Decision priority

`decide_next_action` (in `orchestrator/decisions.py`) walks this checklist in order and returns the first action whose precondition is unmet. Satisfied steps are skipped.

| Order | Condition | Action (agent) |
|-------|-----------|----------------|
| 1 | No project facts yet | `analyze_project` (Requirements Analyst) |
| 2 | Requirements missing | `extract_requirements` (Requirements Analyst) |
| 3 | Requirements exist but no epics | `create_epics` (Epic Planner) |
| 4 | An epic has fewer than 2 tasks | `create_tasks`, one call per epic (Task Planner) |
| 5 | A team role has no matching task type | `create_tasks` in gap mode (Task Planner) |
| 6 | Risks not analysed | `detect_risks` (Risk Analyst) |
| 7 | More than one task and no dependency analysis | `create_dependencies` (Dependency Planner) |
| 8 | Tasks without priority | `set_priorities` (Priority Planner) |
| 9 | Tasks not scheduled, or a sprint has unassigned tasks | `plan_sprints` / `assign_tasks` |
| 10 | State changed since last validation | `validate_plan` (Python) |
| 11 | Validation failed and repair budget remains | `repair_plan` (Python) |
| 12 | Validation passed, no semantic review yet | `semantic_review` (Project Validator) |
| 13 | Everything complete | `generate_summary` -> finalise |

## Safe state updates

- Every proposal is merged into a **deep copy** of the state and run through the deterministic validator (*partial* stage). It is committed and checkpointed only if the merge succeeds and the consistency check passes.
- A rejected proposal (schema violation, unknown reference, inconsistent state) triggers a new call with the exact rejection reason appended to the prompt, up to **3 attempts**.
- Timeouts and transient LLM errors are retried; an unreachable Ollama server or a missing model aborts immediately with an actionable message.
- Each commit increments a state **revision** and writes `state_checkpoint.json` atomically, which enables `--resume`.

## Failure policy per action

| Action | After 3 failed attempts |
|--------|-------------------------|
| `analyze_project`, `extract_requirements`, `create_epics` | **Fatal**: run stops |
| `create_tasks` | Marked skipped; the repair loop re-queues under-filled epics later |
| `detect_risks` | Marked skipped |
| `create_dependencies` | Heuristic dependencies generated in Python, priorities recomputed |
| `set_priorities` | Task-level defaults |
| `plan_sprints` | Python-only planning with the goals and hints already known |
| `assign_tasks` | Deterministic assignment (least-loaded eligible member) |
| `semantic_review` | Marked skipped; does not affect completion |

## Loop guards

| Guard | Setting | Value |
|-------|---------|-------|
| Max loop iterations | `max_iterations` | 80 |
| Max times the same action is selected | `max_action_rounds` | 6 |
| Attempts per agent call | `max_agent_attempts` | 3 |
| Repair rounds after failed validation | `max_repair_rounds` | 2 |
| LLM timeout per call | `llm_timeout_seconds` | 300 s (+30 s watchdog) |

## Completion

A plan is marked `complete` only if the final validation passes **and** the validated revision equals the current revision. Otherwise the status is `failed_validation` and `draft_project_plan.json` is written instead of `final_project_plan.json`.

## Checkpoint and resume

`python main.py --doc <same document> --resume` continues from `outputs/state_checkpoint.json`. The document hash is checked first; a different document aborts the resume.
