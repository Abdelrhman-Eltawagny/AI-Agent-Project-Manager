# Validation and Repair

Validation runs at two stages: *partial* after every merge (catches inconsistent state early) and *final* (adds completeness checks and a serialisation round-trip).

## Rule categories (39 codes)

| Category | Codes |
|----------|-------|
| Identity and schema | `DUPLICATE_ID`, `MISSING_ID`, `BAD_ID_FORMAT`, `MISSING_FIELD`, `INVALID_ENUM`, `INVALID_STATUS`, `SCHEMA_ROUNDTRIP` |
| References | `INVALID_REFERENCE`, `INVALID_SPRINT_REF`, `INVALID_ASSIGNMENT_TASK`, `INVALID_ASSIGNMENT_MEMBER`, `INVALID_DEPENDENCY_REF` |
| Dependencies | `SELF_DEPENDENCY`, `DUPLICATE_DEPENDENCY`, `CIRCULAR_DEPENDENCY`, `DEPENDENCY_ORDER` |
| Estimates and priorities | `INVALID_ESTIMATE`, `INVALID_PRIORITY`, `MISSING_PRIORITY`, `DUPLICATE_PRIORITY`, `PRIORITY_MISMATCH` |
| Sprints and capacity | `SPRINT_COUNT`, `BAD_SPRINT_COUNT`, `EMPTY_SPRINT`, `TASK_NOT_IN_SPRINT`, `TASK_IN_MULTIPLE_SPRINTS`, `SPRINT_CAPACITY`, `ROLE_CAPACITY`, `PLANNED_HOURS_MISMATCH` |
| Assignments | `TASK_NOT_ASSIGNED`, `DUPLICATE_ASSIGNMENT`, `ROLE_MISMATCH`, `ASSIGNMENT_SPRINT_MISMATCH`, `MEMBER_OVERLOAD` |
| Completeness | `EPIC_WITHOUT_TASKS`, `EPIC_TOO_FEW_TASKS`, `REQUIREMENT_UNCOVERED`, `EMPTY_SECTION`, `MISSING_PROJECT` |

Errors block completion; warnings (for example `REQUIREMENT_UNCOVERED`) are reported in `validation.json` but do not.

## Automatic repair

When final validation fails, `repair_plan` maps error codes to fixes **without an LLM**:

- **Dependency errors:** invalid, self-referencing and duplicate edges are dropped; cycles are broken by removing the closing edge; sprints are re-scheduled.
- **Sprint or capacity errors:** deterministic re-planning and full re-assignment.
- **Epic with too few tasks:** the epic is re-queued for the Task Planner, and dependency analysis is re-queued.
- **Priority errors:** priorities are rebuilt from defaults.
- **Assignment errors:** invalid assignments are dropped and rebuilt.

After two unsuccessful repair rounds the run ends as `failed_validation` rather than shipping an unverified plan.

## Semantic review

The Project Validator agent reviews a digest of each sprint and returns `pass` or `concerns` with up to 5 notes. The notes are stored in `validation.json` but never change the pass/fail result.
