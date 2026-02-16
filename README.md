# datadrift

`datadrift` is a Speedrift-suite sidecar that detects **schema/migration drift** without hard-blocking development.

It is designed to be orchestrated by `driftdriver` (via `./.workgraph/drifts`).

## Ecosystem Map

This project is part of the Speedrift suite for Workgraph-first drift control.

- Spine: [Workgraph](https://graphwork.github.io/)
- Orchestrator: [driftdriver](https://github.com/dbmcco/driftdriver)
- Baseline lane: [speedrift](https://github.com/dbmcco/speedrift)
- Optional lanes: [specdrift](https://github.com/dbmcco/specdrift), [datadrift](https://github.com/dbmcco/datadrift), [depsdrift](https://github.com/dbmcco/depsdrift), [uxdrift](https://github.com/dbmcco/uxdrift), [therapydrift](https://github.com/dbmcco/therapydrift), [yagnidrift](https://github.com/dbmcco/yagnidrift), [redrift](https://github.com/dbmcco/redrift)

## Task Spec Format

Add a per-task fenced TOML block:

````md
```datadrift
schema = 1

# Paths that represent "data/schema changes" for your project.
migrations = [
  "db/migrations/**",
  "migrations/**",
  "alembic/versions/**",
]
schema_files = [
  "schema.sql",
  "db/schema.sql",
]

# If code changes but none of the above changes, emit an advisory finding.
require_schema_update_when_code_changes = true

# Optional: ignore globs (same ** semantics as specdrift/speedrift).
ignore = [
  "**/*.md",
]
```
````

## Workgraph Integration

From a Workgraph repo (where `driftdriver install` has written wrappers):

```bash
./.workgraph/drifts check --task <id> --write-log --create-followups
```

Standalone (from a repo root):

```bash
datadrift --dir . wg check --task <id> --write-log --create-followups
```

Exit codes:
- `0`: clean
- `3`: findings exist (advisory)
