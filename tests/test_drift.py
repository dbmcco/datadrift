import unittest

from datadrift.drift import compute_data_drift
from datadrift.git_tools import WorkingChanges
from datadrift.specs import DatadriftSpec


class DatadriftTests(unittest.TestCase):
    def test_schema_not_updated(self) -> None:
        spec = DatadriftSpec(
            schema=1,
            migrations=["migrations/**"],
            schema_files=["schema.sql"],
            require_schema_update_when_code_changes=True,
            ignore=[],
        )

        report = compute_data_drift(
            task_id="t1",
            task_title="T1",
            description="",
            spec=spec,
            git_root="/tmp",
            changes=WorkingChanges(changed_files=["src/app.py"]),
        )
        kinds = {f["kind"] for f in report["findings"]}
        self.assertIn("schema_not_updated", kinds)
        self.assertEqual(report["score"], "yellow")

    def test_schema_updated(self) -> None:
        spec = DatadriftSpec(
            schema=1,
            migrations=["migrations/**"],
            schema_files=[],
            require_schema_update_when_code_changes=True,
            ignore=[],
        )

        report = compute_data_drift(
            task_id="t1",
            task_title="T1",
            description="",
            spec=spec,
            git_root="/tmp",
            changes=WorkingChanges(changed_files=["src/app.py", "migrations/001_init.sql"]),
        )
        kinds = {f["kind"] for f in report["findings"]}
        self.assertNotIn("schema_not_updated", kinds)


if __name__ == "__main__":
    unittest.main()

