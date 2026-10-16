"""Run: python -B -m unittest discover -s scripts/tests -v"""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("collect_evidence", Path(__file__).parents[1] / "collect_evidence.py")
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


@unittest.skipUnless(shutil.which("rg"), "installed ripgrep required")
class SearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = {"include": ["src"], "patterns": ["needle", "literal.*"],
                       "supported_configurations": ["test"], "relevant_files": ["src/main.txt"]}
        (self.root / "src").mkdir()
        (self.root / "src/main.txt").write_text("needle\nliteral.*\nliteralXY\n")

    def test_external_ignore_symlink_is_unknown_without_hashing(self):
        with tempfile.TemporaryDirectory() as outside:
            external = Path(outside) / "ignore"
            external.write_text("src")
            (self.root / ".ignore").symlink_to(external)
            observed = evidence.inventory(self.root, self.config)
            self.assertFalse(observed["complete"])
            self.assertNotIn(".ignore", observed["ancestor_ignore_hashes"])
            self.assertIn("Ignore file resolves outside root: .ignore", observed["problems"])

    def test_nested_external_ignore_prevents_search(self):
        with tempfile.TemporaryDirectory() as outside:
            external = Path(outside) / "ignore"
            external.write_text("*")
            (self.root / "src/nested").mkdir()
            (self.root / "src/nested/.ignore").symlink_to(external)
            # fingerprint's tool-version subprocess uses run/Popen independently.
            # Supply real inventory with a fixed tool identity to isolate search launch.
            snapshot = {"files": {}, "inventory": evidence.inventory(self.root, self.config)}
            with patch.object(evidence, "fingerprint", return_value=snapshot), \
                    patch.object(evidence.subprocess, "Popen") as popen:
                result = evidence.collect(self.root, self.config)
                popen.assert_not_called()
            self.assertFalse(result["complete"])
            self.assertIn("Ignore file resolves outside root: src/nested/.ignore", result["unknown"])

    def test_new_consumer_and_ignore_changes_invalidate(self):
        rg = shutil.which("rg")
        old = evidence.fingerprint(self.root, self.config, rg)
        (self.root / "src/new_consumer.py").write_text("needle")
        current = evidence.fingerprint(self.root, self.config, rg)
        self.assertEqual(old["files"], current["files"])
        self.assertEqual(evidence.freshness(old, current)["status"], "stale")
        (self.root / ".ignore").write_text("src/new_consumer.py")
        latest = evidence.fingerprint(self.root, self.config, rg)
        self.assertEqual(evidence.freshness(current, latest)["status"], "stale")

    def test_inventory_limit_is_unknown(self):
        (self.root / "src/extra").write_text("x")
        self.config["max_inventory_files"] = 1
        result = evidence.collect(self.root, self.config)
        self.assertFalse(result["complete"])
        self.assertIn("Inventory limit exceeded", result["unknown"])
        self.assertEqual(evidence.freshness(result["fingerprint"], result["fingerprint"])["status"], "unknown")

    def test_state_validation_checks_form_not_truth(self):
        valid = {"decision": "eligible", "implementation": "not_applied", "verification": "not_run"}
        self.assertEqual(evidence.validate_states(valid), [])
        self.assertTrue(evidence.validate_states(dict(valid, decision="safe")))
        self.assertTrue(evidence.validate_states(dict(valid, complete=False, unknown=[])))
        self.assertTrue(evidence.validate_states(dict(valid, result="error", unknown=[])))
        self.assertTrue(evidence.validate_states(dict(valid, unknown=["external consumers"])))
        self.assertTrue(evidence.validate_states(dict(valid, verification="passed")))
        self.assertEqual(evidence.validate_states(dict(valid, verification="passed",
                         verification_evidence="recorded command and result")), [])

    def test_batch_equals_repeated_scope(self):
        batched = evidence.collect(self.root, self.config)
        repeated = []
        for pattern in self.config["patterns"]:
            config = dict(self.config, patterns=[pattern])
            repeated.extend(evidence.collect(self.root, config)["matches"])
        def normalize(matches):
            return {(json.dumps(m["path"], sort_keys=True), m["line_number"],
                     json.dumps(m["lines"], sort_keys=True)) for m in matches}
        self.assertEqual(normalize(batched["matches"]), normalize(repeated))

    def test_timeout_is_not_absence(self):
        with patch.object(evidence.subprocess, "Popen") as popen:
            process = popen.return_value
            process.wait.side_effect = [evidence.subprocess.TimeoutExpired("rg", 1), None]
            process.returncode = -9
            with patch.object(evidence, "fingerprint", return_value={"files": {}}):
                result = evidence.collect(self.root, self.config)
            process.kill.assert_called_once()
        self.assertFalse(result["complete"])
        self.assertEqual(result["result"], "error")
        self.assertIn("Search timeout", result["unknown"])

    def test_nonobject_nonfinite_and_nondirectory_rejected(self):
        for config in ([], None, dict(self.config, timeout_seconds=float("nan")),
                       dict(self.config, timeout_seconds=float("inf"))):
            with self.assertRaises(ValueError):
                evidence.collect(self.root, config)
        with self.assertRaises(ValueError):
            evidence.collect(self.root / "src/main.txt", self.config)

    def test_batched_literal_matches(self):
        result = evidence.collect(self.root, self.config)
        self.assertTrue(result["complete"])
        self.assertEqual(result["result"], "matches")
        self.assertEqual(len(result["matches"]), 2)
        self.assertEqual(result["matches"][0]["matched_patterns"], ["needle"])
        self.assertEqual(result["returncode"], 0)
        self.assertEqual(result["decision"], "needs_evidence")

    def test_no_match_is_successful_scoped_scan(self):
        self.config["patterns"] = ["absent"]
        result = evidence.collect(self.root, self.config)
        self.assertEqual(result["returncode"], 1)
        self.assertTrue(result["complete"])
        self.assertEqual(result["result"], "no_matches")

    def test_missing_and_unresolved_not_negative_proof(self):
        self.config["include"].append("missing")
        self.config["unresolved"] = ["external registry"]
        self.config["patterns"] = ["absent"]
        result = evidence.collect(self.root, self.config)
        self.assertFalse(result["complete"])
        self.assertEqual(result["result"], "incomplete")
        self.assertIn("external registry", result["unknown"])
        self.assertIn("Missing included path: missing", result["unknown"])

    def test_targeted_hidden_and_ignored(self):
        (self.root / "src/.registry").write_text("secret_symbol")
        (self.root / "src/.ignore").write_text("generated/\n")
        (self.root / "src/generated").mkdir()
        (self.root / "src/generated/out.txt").write_text("secret_symbol")
        self.config["patterns"] = ["secret_symbol"]
        self.assertEqual(evidence.collect(self.root, self.config)["result"], "no_matches")
        self.config.update(include_hidden=True, include_ignored=True)
        self.assertEqual(len(evidence.collect(self.root, self.config)["matches"]), 2)

    def test_dependencies_remain_excluded(self):
        (self.root / "src/node_modules").mkdir()
        (self.root / "src/node_modules/lib").write_text("dependency_symbol")
        self.config.update(include_hidden=True, include_ignored=True, patterns=["dependency_symbol"])
        self.assertEqual(evidence.collect(self.root, self.config)["result"], "no_matches")

    def test_truncated_output_unknown(self):
        self.config["max_output_bytes"] = 20
        result = evidence.collect(self.root, self.config)
        self.assertTrue(result["truncated"])
        self.assertFalse(result["complete"])
        self.assertNotEqual(result["result"], "no_matches")

    def test_invalid_glob_is_error_not_absence(self):
        self.config["exclude"] = ["["]
        result = evidence.collect(self.root, self.config)
        self.assertEqual(result["returncode"], 2)
        self.assertEqual(result["result"], "error")
        self.assertFalse(result["complete"])

    def test_missing_tool(self):
        with patch.object(evidence.shutil, "which", return_value=None):
            self.assertEqual(evidence.collect(self.root, self.config)["result"], "error")

    def test_safe_literal_flag_like_input(self):
        self.config["patterns"] = ["--help", "$(touch ATTACK)"]
        result = evidence.collect(self.root, self.config)
        self.assertEqual(result["result"], "no_matches")
        self.assertFalse((self.root / "ATTACK").exists())

    def test_outside_root_is_rejected(self):
        self.config["include"] = ["../"]
        with self.assertRaises(ValueError):
            evidence.collect(self.root, self.config)

    def test_fingerprints_invalidate_file_config_tool_oracle(self):
        rg = shutil.which("rg")
        old = evidence.fingerprint(self.root, self.config, rg)
        self.assertEqual(evidence.freshness(old, old)["status"], "unchanged_declared_inputs")
        for field in ("config_sha256", "files", "tool", "oracle_id"):
            modified = dict(old)
            modified[field] = {} if field == "files" else "changed"
            self.assertEqual(evidence.freshness(old, modified)["status"], "stale")
        (self.root / "src/main.txt").unlink()
        current = evidence.fingerprint(self.root, self.config, rg)
        self.assertEqual(evidence.freshness(current, current)["status"], "unknown")

    def test_config_rejects_nonliteral_multiline_pattern(self):
        self.config["patterns"] = ["a\nb"]
        with self.assertRaises(ValueError):
            evidence.collect(self.root, self.config)


if __name__ == "__main__":
    unittest.main()
