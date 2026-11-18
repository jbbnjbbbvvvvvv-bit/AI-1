"""Behavioral safeguards; fixtures are temporary Skills, no CAD inputs are opened."""
import importlib.util
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("maintain_lessons", Path(__file__).resolve().parents[1] / "scripts/maintain_lessons.py")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class LessonTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "heritage-cad-workflow"
        self.root.mkdir()
        for name in set(m.ROUTES.values()) | {m.VERIFIED, m.PENDING, "CHANGELOG.md"}:
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text("# Fixture\n", encoding="utf-8")
        (self.root / m.INDEX).write_text("[]\n", encoding="utf-8")
        self.outside = Path(self.tmp.name) / "original.dxf"
        self.outside.write_bytes(b"PROTECTED CAD CONTENT")
        self.proposal = {
            "id": "test-safe-lesson", "date": "2026-11-18", "topic": "geometry",
            "status": "VERIFIED", "review": "clear", "validation_passed": True,
            "task_type": "测试夹具", "problem": "端点不连续", "cause": "连接遗漏",
            "evidence": "夹具中存在可复现断点", "solution": "同源接点统一约束",
            "validation": "独立断点反例及正确案例均已检验", "rule": "只连接已确认同源的接点。",
        }

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}

    def commit(self, proposal):
        changes, result = m.build(self.root, proposal)
        m.transact(self.root, changes, commit=True)
        return result

    def test_verified_routes_rule_and_ledger(self):
        result = self.commit(self.proposal)
        self.assertEqual(result["status"], "VERIFIED")
        self.assertIn(self.proposal["rule"], (self.root / m.ROUTES["geometry"]).read_text(encoding="utf-8"))
        self.assertIn("test-safe-lesson", (self.root / m.VERIFIED).read_text(encoding="utf-8"))
        self.assertNotIn("test-safe-lesson", (self.root / m.PENDING).read_text(encoding="utf-8"))

    def test_dry_run_changes_nothing(self):
        before = self.snapshot()
        changes, _ = m.build(self.root, self.proposal)
        m.transact(self.root, changes)
        self.assertEqual(before, self.snapshot())

    def test_each_topic_routes_only_to_its_reference(self):
        for topic, route in m.ROUTES.items():
            with self.subTest(topic=topic):
                rule = "特定主题测试规则 " + topic
                p = {**self.proposal, "id": "routing-lesson-" + topic, "topic": topic, "rule": rule}
                self.commit(p)
                for other in set(m.ROUTES.values()):
                    text = (self.root / other).read_text(encoding="utf-8")
                    self.assertEqual(rule in text, route == other)

    def test_duplicate_task_does_not_write(self):
        self.commit(self.proposal)
        before = self.snapshot()
        changes, result = m.build(self.root, self.proposal)
        self.assertFalse(changes)
        self.assertEqual(result["status"], "UNCHANGED")
        self.assertEqual(before, self.snapshot())

    def test_normalized_duplicate_with_new_id(self):
        self.commit(self.proposal)
        p = {**self.proposal, "id": "second-task-lesson", "problem": "端点 不连续。"}
        changes, result = m.build(self.root, p)
        self.assertFalse(changes)
        self.assertEqual(result["existing_id"], self.proposal["id"])

    def test_candidate_has_no_execution_effect(self):
        p = {**self.proposal, "status": "CANDIDATE"}
        p.pop("rule")
        before = (self.root / m.ROUTES["geometry"]).read_bytes()
        self.commit(p)
        self.assertEqual(before, (self.root / m.ROUTES["geometry"]).read_bytes())
        self.assertNotIn("test-safe-lesson", (self.root / m.VERIFIED).read_text(encoding="utf-8"))

    def test_candidate_rule_is_rejected(self):
        with self.assertRaises(ValueError):
            m.build(self.root, {**self.proposal, "status": "CANDIDATE"})

    def test_candidate_code_change_is_rejected(self):
        p = {**self.proposal, "status": "CANDIDATE", "patches": {"scripts/tool.py": "pass\n"}}
        p.pop("rule")
        with self.assertRaises(ValueError):
            m.build(self.root, p)

    def test_rejected_method_is_not_formal_rule(self):
        p = {**self.proposal, "status": "REJECTED"}
        p.pop("rule")
        self.commit(p)
        self.assertIn("REJECTED", (self.root / m.PENDING).read_text(encoding="utf-8"))
        self.assertNotIn("test-safe-lesson", (self.root / m.VERIFIED).read_text(encoding="utf-8"))

    def test_verified_requires_validation(self):
        with self.assertRaises(ValueError):
            m.build(self.root, {**self.proposal, "validation_passed": False})

    def test_conflict_is_quarantined(self):
        p = {**self.proposal, "review": "conflict"}
        p.pop("rule")
        self.assertEqual(self.commit(p)["status"], "CANDIDATE")
        self.assertNotIn("test-safe-lesson", (self.root / m.VERIFIED).read_text(encoding="utf-8"))

    def test_candidate_promotion_needs_evidence_gate(self):
        p = {**self.proposal, "status": "CANDIDATE"}
        p.pop("rule")
        self.commit(p)
        with self.assertRaises(ValueError):
            self.commit({**self.proposal, "validation_passed": False})
        self.commit(self.proposal)
        self.assertNotIn("test-safe-lesson", (self.root / m.PENDING).read_text(encoding="utf-8"))
        self.assertEqual(m.read_index(self.root)[0]["status"], "VERIFIED")

    def test_private_path_and_secret_refused(self):
        for value in ("C:/Users/Someone/private/file.txt", "Bearer secretvalue123456789012345"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                m.build(self.root, {**self.proposal, "evidence": value})

    def test_scope_escape_and_cad_write_refused(self):
        for name in ("../original.dxf", "original.dxf", "agents/openai.yaml", "../../AGENTS.md", "scripts/../x.py", "C:/other/file.md"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                m.build(self.root, {**self.proposal, "patches": {name: "bad"}})
        self.assertEqual(self.outside.read_bytes(), b"PROTECTED CAD CONTENT")

    def test_broken_reference_refused_before_writing(self):
        before = self.snapshot()
        changes, _ = m.build(self.root, {**self.proposal, "patches": {"references/geometry-constraints.md": "[bad](missing.md)\n"}})
        with self.assertRaises(ValueError):
            m.transact(self.root, changes, commit=True)
        self.assertEqual(before, self.snapshot())

    def test_invalid_code_refused_before_writing(self):
        before = self.snapshot()
        with self.assertRaises(SyntaxError):
            m.transact(self.root, {"scripts/tool.py": b"def broken(\n"}, commit=True)
        self.assertEqual(before, self.snapshot())

    def test_code_without_related_tests_refused(self):
        with self.assertRaises(ValueError):
            m.transact(self.root, {"scripts/tool.py": b"x = 1\n"}, commit=True)
        self.assertFalse((self.root / "scripts/tool.py").exists())

    def test_write_failure_rolls_back_previous_files(self):
        before = self.snapshot()
        changes, _ = m.build(self.root, self.proposal)
        replace = m.os.replace
        calls = 0
        def fail_second(src, dest):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected IO failure")
            return replace(src, dest)
        with patch.object(m.os, "replace", side_effect=fail_second), self.assertRaises(OSError):
            m.transact(self.root, changes, commit=True)
        self.assertEqual(before, self.snapshot())

    def test_post_write_validation_failure_rolls_back(self):
        before = self.snapshot()
        changes, _ = m.build(self.root, self.proposal)
        validate = m.validate_tree
        def fail_actual(root, *args):
            if root.resolve() == self.root.resolve():
                raise ValueError("injected final validation failure")
            return validate(root, *args)
        with patch.object(m, "validate_tree", side_effect=fail_actual), self.assertRaises(ValueError):
            m.transact(self.root, changes, commit=True)
        self.assertEqual(before, self.snapshot())

    def test_concurrent_edit_refused(self):
        changes, _ = m.build(self.root, self.proposal)
        before = self.snapshot()
        (self.root / "CHANGELOG.md").write_text("external edit", encoding="utf-8")
        with self.assertRaises(ValueError):
            m.transact(self.root, changes, commit=True, expected=before)
        self.assertEqual((self.root / "CHANGELOG.md").read_text(encoding="utf-8"), "external edit")

    def test_existing_lock_blocks_commit(self):
        changes, _ = m.build(self.root, self.proposal)
        (self.root / ".maintenance.lock").write_text("other process", encoding="utf-8")
        before = self.snapshot()
        with self.assertRaises(FileExistsError):
            m.transact(self.root, changes, commit=True)
        self.assertEqual(before, self.snapshot())

    def test_validator_reads_chinese_utf8_in_windows_locale(self):
        (self.root / "SKILL.md").write_text("# 历史建筑雕花\n", encoding="utf-8")
        validator = Path(self.tmp.name) / "validator.py"
        validator.write_text("from pathlib import Path\nimport sys\ns = (Path(sys.argv[1]) / 'SKILL.md').read_text()\nassert '\u96d5\u82b1' in s\n", encoding="utf-8")
        m.validate_tree(self.root, validator)

    def test_code_with_passing_related_test_can_commit(self):
        changes = {
            "scripts/tool.py": b"def twice(x):\n    return x * 2\n",
            "tests/test_tool.py": b"import unittest\nfrom scripts.tool import twice\nclass TestTool(unittest.TestCase):\n    def test_twice(self):\n        self.assertEqual(twice(3), 6)\n",
        }
        m.transact(self.root, changes, commit=True)
        self.assertTrue((self.root / "scripts/tool.py").is_file())

    def test_cli_failed_update_records_candidate_and_preserves_rules(self):
        proposal = {**self.proposal, "patches": {"scripts/tool.py": "def broken(\n"}}
        proposal_path = Path(self.tmp.name) / "proposal.json"
        proposal_path.write_text(json.dumps(proposal, ensure_ascii=False), encoding="utf-8")
        validator = Path(self.tmp.name) / "validator.py"
        validator.write_text("pass\n", encoding="utf-8")
        formal = (self.root / m.ROUTES["geometry"]).read_bytes()
        args = ["maintain", "--skill-root", str(self.root), "--proposal", str(proposal_path), "--skill-validator", str(validator), "--commit"]
        output = io.StringIO()
        with patch.object(sys, "argv", args), contextlib.redirect_stdout(output):
            code = m.main()
        self.assertEqual(code, 1)
        self.assertTrue(json.loads(output.getvalue())["failure_recorded"])
        self.assertEqual(formal, (self.root / m.ROUTES["geometry"]).read_bytes())
        self.assertFalse((self.root / "scripts/tool.py").exists())
        self.assertEqual(m.read_index(self.root)[0]["status"], "CANDIDATE")


if __name__ == "__main__":
    unittest.main()
