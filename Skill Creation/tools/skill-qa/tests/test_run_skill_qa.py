import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "run_skill_qa.py"
spec = importlib.util.spec_from_file_location("run_skill_qa", MODULE_PATH)
run_skill_qa = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["run_skill_qa"] = run_skill_qa
spec.loader.exec_module(run_skill_qa)


class SkillQaTests(unittest.TestCase):
    def test_parse_skill_md_requires_frontmatter(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "SKILL.md"
            p.write_text("# no frontmatter\n", encoding="utf-8")
            front, body, err = run_skill_qa.parse_skill_md(p)
            self.assertEqual(front, {})
            self.assertIn("Missing YAML frontmatter", err)
            self.assertIn("no frontmatter", body)

    def test_validate_scenarios_schema(self):
        ok, _ = run_skill_qa.validate_scenarios_schema([
            {"prompt": "help with skill", "relevant": True, "keywords": ["skill"]}
        ])
        self.assertTrue(ok)

        bad, msg = run_skill_qa.validate_scenarios_schema([{"prompt": "x"}])
        self.assertFalse(bad)
        self.assertIn("relevant", msg)

    def test_predict_trigger_respects_overlap_threshold(self):
        pred = run_skill_qa.predict_trigger(
            prompt="help with SKILL.md frontmatter",
            name="basic-skill",
            description="Template for skill metadata",
            keywords=["skill", "frontmatter"],
            min_overlap_tokens=2,
        )
        self.assertTrue(pred)

        pred_false = run_skill_qa.predict_trigger(
            prompt="help with SKILL.md frontmatter",
            name="basic-skill",
            description="Template for skill metadata",
            keywords=["frontmatter"],
            min_overlap_tokens=2,
        )
        self.assertFalse(pred_false)

    def test_command_allowlist(self):
        self.assertTrue(run_skill_qa.command_is_allowed("python3 --version", ["python3"]))
        self.assertFalse(run_skill_qa.command_is_allowed("rm -rf /", ["python3", "uv"]))


if __name__ == "__main__":
    unittest.main()
