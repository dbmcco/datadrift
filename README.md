# datadrift

`datadrift` is a Speedrift-suite sidecar that detects **schema/migration drift** without hard-blocking development.

It is designed to be orchestrated by `driftdriver` (via `./.workgraph/rifts`).

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

# Optional: ignore globs (same ** semantics as specrift/speedrift).
ignore = [
  "**/*.md",
]
```
````

## Workgraph Integration

From a Workgraph repo (where `driftdriver install` has written wrappers):

```bash
./.workgraph/rifts check --task <id> --write-log --create-followups
```

Standalone (from a repo root):

```bash
datadrift --dir . wg check --task <id> --write-log --create-followups
```

Exit codes:
- `0`: clean
- `3`: findings exist (advisory)

