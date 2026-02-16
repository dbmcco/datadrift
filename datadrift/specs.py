from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from typing import Any

FENCE_INFO = "datadrift"

_FENCE_RE = re.compile(
    r"```(?P<info>datadrift)\s*\n(?P<body>.*?)\n```",
    re.DOTALL,
)


def extract_datadrift_spec(description: str) -> str | None:
    m = _FENCE_RE.search(description or "")
    if not m:
        return None
    return m.group("body").strip()


def parse_datadrift_spec(text: str) -> dict[str, Any]:
    data = tomllib.loads(text)
    if not isinstance(data, dict):
        raise ValueError("datadrift block must parse to a TOML table/object.")
    return data


@dataclass(frozen=True)
class DatadriftSpec:
    schema: int
    migrations: list[str]
    schema_files: list[str]
    require_schema_update_when_code_changes: bool
    ignore: list[str]

    @staticmethod
    def from_raw(raw: dict[str, Any]) -> "DatadriftSpec":
        schema = int(raw.get("schema", 1))

        migrations_raw = raw.get("migrations", [])
        schema_files_raw = raw.get("schema_files", [])

        migrations = [str(x) for x in (migrations_raw or [])] if isinstance(migrations_raw, list) else []
        schema_files = [str(x) for x in (schema_files_raw or [])] if isinstance(schema_files_raw, list) else []

        require = bool(raw.get("require_schema_update_when_code_changes", True))

        ignore_raw = raw.get("ignore", [])
        ignore = [str(x) for x in (ignore_raw or [])] if isinstance(ignore_raw, list) else []

        return DatadriftSpec(
            schema=schema,
            migrations=migrations,
            schema_files=schema_files,
            require_schema_update_when_code_changes=require,
            ignore=ignore,
        )

