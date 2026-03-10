import tempfile
import unittest
from pathlib import Path
import importlib.util
import sys
import json

MODULE_PATH = Path(__file__).resolve().parents[1] / "aggregate_reports.py"
spec = importlib.util.spec_from_file_location("aggregate_reports", MODULE_PATH)
aggregate_reports = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["aggregate_reports"] = aggregate_reports
spec.loader.exec_module(aggregate_reports)


class AggregateReportsTests(unittest.TestCase):
    def test_load_and_write_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "reports"
            run_dir = root / "basic-skill" / "20260101-000000"
            run_dir.mkdir(parents=True)
            (run_dir / "metrics.json").write_text(
                json.dumps(
                    {
                        "skill": "basic-skill",
                        "timestamp_utc": "2026-01-01T00:00:00Z",
                        "qa_passed": True,
                        "checks_passed": 10,
                        "checks_total": 10,
                    }
                ),
                encoding="utf-8",
            )

            rows = aggregate_reports.load_metrics(root)
            self.assertEqual(len(rows), 1)
            out_dir = root / "_meta"
            aggregate_reports.write_csv(out_dir / "metrics.csv", rows)
            aggregate_reports.write_summary(out_dir / "summary.md", rows)

            self.assertTrue((out_dir / "metrics.csv").exists())
            self.assertTrue((out_dir / "summary.md").exists())
            summary = (out_dir / "summary.md").read_text(encoding="utf-8")
            self.assertIn("Pass rate", summary)


if __name__ == "__main__":
    unittest.main()
