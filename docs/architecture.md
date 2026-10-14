# Architecture

The Orchestrator owns the loop, the State owns the truth, and agents are stateless advisers.

![Agents and orchestrator](assets/agents-orchestrator-diagram.png)

## Components

| Component | Location | Responsibility |
|-----------|----------|----------------|
| Entry point | `main.py` | CLI, pre-flight Ollama checks and warm-up, run summary, exit codes |
| Document loader | `services/document_loader.py` | Splits the Markdown by `##` sections and serves small slices (default cap 3,500 chars) to each agent; stores a SHA-256 hash so a checkpoint is only resumed against the same document |
| CrewAI runner | `crew/runner.py` | Wraps each agent as a cached CrewAI `Agent`; every call is a single-task `Crew` against `ollama/<model>` (temperature 0.1, 300 s timeout, watchdog +30 s) |
| Agents | `agents/` | Nine specialised agents on a shared `BaseAgent` that builds prompts, appends rejection feedback, extracts JSON and validates it against a Pydantic schema |
| Decision engine | `orchestrator/decisions.py` | Pure function `(state, team, settings) -> next action` |
| Orchestrator | `orchestrator/orchestrator.py` | Main loop, retries, transactional merge, fallbacks, repair, finalisation, execution log |
| Canonical state | `orchestrator/state.py` | `ProjectState` holds every entity; Python generates all IDs (`REQ-`, `EPIC-`, `TASK-`, `SPRINT-`, `RISK-`, `MS-`) |
| Planning logic | `orchestrator/planning.py` | Deterministic sprint scheduler, task assigner, heuristic dependencies |
| Validators | `validators/` | Authoritative deterministic validator (39 rule codes) and an advisory semantic validator |
| Services | `services/` | JSON extraction, atomic JSON store, Ollama health checks, logging, errors, dependency-graph cycle detection, offline mock LLM |
| Project Assistant | `chat.py`, `server.py` | Scoped Q&A over the final plan: CLI, browser page, REST API |

## Planning phases

1. **Understand** - Requirements Analyst, Epic Planner
2. **Plan** - Task Planner, Risk Analyst, Dependency Planner, Priority Planner
3. **Schedule** - Sprint Planner, Python scheduler, Assignment Planner, Python assigner
4. **Validate** - deterministic validator, Python repair, Project Validator (advisory)

## Data model

| Entity | ID format | Main fields |
|--------|-----------|-------------|
| Requirement | `REQ-001` | title, description, priority, kind (functional / non_functional / constraint) |
| Epic | `EPIC-001` | name, description, priority, linked requirement IDs |
| Task | `TASK-001` | title, type, description, estimated hours, priority, epic, status |
| Dependency | - | `task_id`, `depends_on`, type (`blocks`), reason |
| Sprint | `SPRINT-001` | number, goal, task IDs, planned hours, capacity hours |
| Assignment | - | `task_id`, `member_id`, `sprint_id`, reason |
| Risk | `RISK-001` | title, description, likelihood, impact, mitigation, epic IDs |
| Milestone | `MS-001` | name, sprint, week, criteria |

## Reliability for small local models

| Typical model failure | Protection |
|-----------------------|------------|
| JSON wrapped in markdown fences, extra prose, trailing commas, truncation | `extract_json` strips fences, finds the first balanced object, removes trailing commas, repairs truncated output |
| Numbers where strings are expected, synonyms such as "urgent" | Lenient proposal types normalise values; canonical state models are strict (`extra=forbid`) |
| Invented or mixed-up IDs | Python generates all IDs; incoming references are normalised and checked |
| Circular or self-referencing dependencies | Cycle detection on every merge; repair removes the closing edge |
| Assignment to a non-existent member or wrong role | Eligible members are given in the prompt and enforced again in code |
| Timeouts and hangs | 300 s timeout, watchdog, bounded retries, then a per-action fallback |
| Endless loops | Per-action round cap and global iteration cap |
| Resuming against a different document | Checkpoint stores the document hash |
| Half-written files after a crash | Atomic writes (temp file + `os.replace`) |
