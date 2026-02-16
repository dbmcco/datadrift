from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from datadrift.git_tools import WorkingChanges
from datadrift.globmatch import match_any
from datadrift.specs import DatadriftSpec


@dataclass(frozen=True)
class Finding:
    kind: str
    severity: str
    summary: str
    details: dict[str, Any] | None = None


def compute_data_drift(
    *,
    task_id: str,
    task_title: str,
    description: str,
    spec: DatadriftSpec,
    git_root: str | None,
    changes: WorkingChanges | None,
) -> dict[str, Any]:
    findings: list[Finding] = []

    changed_files: list[str] = []
    if changes:
        changed_files = [
            p
            for p in changes.changed_files
            if not (p.startswith(".workgraph/") or p.startswith(".git/") or match_any(p, spec.ignore))
        ]

    telemetry: dict[str, Any] = {
        "files_changed": len(changed_files),
    }

    if spec.schema != 1:
        findings.append(
            Finding(
                kind="unsupported_schema",
                severity="warn",
                summary=f"Unsupported datadrift schema: {spec.schema} (expected 1)",
            )
        )

    schema_globs = list(spec.migrations or []) + list(spec.schema_files or [])
    if not schema_globs:
        findings.append(
            Finding(
                kind="invalid_data_config",
                severity="warn",
                summary="datadrift migrations[]/schema_files[] are empty; nothing to keep in sync",
            )
        )

    schema_changed = [p for p in changed_files if schema_globs and match_any(p, schema_globs)]
    non_schema_changed = [p for p in changed_files if not (schema_globs and match_any(p, schema_globs))]
    telemetry["schema_files_changed"] = len(schema_changed)
    telemetry["non_schema_files_changed"] = len(non_schema_changed)

    if spec.require_schema_update_when_code_changes and non_schema_changed and not schema_changed and schema_globs:
        findings.append(
            Finding(
                kind="schema_not_updated",
                severity="warn",
                summary="Non-schema files changed but no schema/migration files changed",
                details={
                    "schema_globs": schema_globs,
                    "changed_non_schema": non_schema_changed[:50],
                },
            )
        )

    score = "green"
    if any(f.severity == "warn" for f in findings):
        score = "yellow"
    if any(f.severity == "error" for f in findings):
        score = "red"

    recommendations: list[dict[str, Any]] = []
    for f in findings:
        if f.kind == "schema_not_updated":
            recommendations.append(
                {
                    "priority": "high",
                    "action": "Update schema/migrations for this task (or adjust datadrift globs)",
                    "rationale": "Schema drift produces broken deploys and silent data corruption; keep migrations in lockstep with code.",
                }
            )
        elif f.kind == "invalid_data_config":
            recommendations.append(
                {
                    "priority": "high",
                    "action": "Populate datadrift migrations[] and/or schema_files[]",
                    "rationale": "Datadrift needs an explicit set of schema/migration paths to keep in sync.",
                }
            )
        elif f.kind == "unsupported_schema":
            recommendations.append(
                {
                    "priority": "high",
                    "action": "Set datadrift schema = 1",
                    "rationale": "Only schema v1 is currently supported.",
                }
            )

    seen_actions: set[str] = set()
    recommendations = [r for r in recommendations if not (r["action"] in seen_actions or seen_actions.add(r["action"]))]  # type: ignore[arg-type]

    return {
        "task_id": task_id,
        "task_title": task_title,
        "git_root": git_root,
        "score": score,
        "spec": asdict(spec),
        "telemetry": telemetry,
        "findings": [asdict(f) for f in findings],
        "recommendations": recommendations,
    }

