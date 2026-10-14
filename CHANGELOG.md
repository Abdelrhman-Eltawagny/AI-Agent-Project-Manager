# Changelog

All notable changes to this project are documented here.

## [1.0.0] - 2026-10

### Added
- Nine specialised agents: Requirements Analyst, Epic Planner, Task Planner, Dependency Planner, Priority Planner, Risk Analyst, Sprint Planner, Team Assignment Planner, Project Validator.
- State-driven Orchestrator with transactional merging, retry-with-feedback, per-step fallbacks, loop guards and checkpoint/resume.
- Deterministic sprint scheduler, task assigner, heuristic dependency generator and 39-rule validator with automatic repair.
- Project Assistant (CLI, web page, REST API) with a three-layer scope guard.
- Dockerfile and production Docker Compose file (Ollama + web app).
- Offline mock LLM and 29 test cases.
- Documentation, diagrams, charts and example outputs for two sample projects.
