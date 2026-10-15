"""Evaluator-owned behavior checks. Run against trusted isolated fixture copies."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).parent / "fixtures"
# unittest must not interpret the fixture path as a test selector.
sys.argv[1:] = []


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / name / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ContractChecks(unittest.TestCase):
    def test_dead_leaf_survivor(self):
        app = load("dead_leaf")
        self.assertEqual(app.render(0), "current:0")
        self.assertEqual(app.render("旧"), "current:旧")

    def test_live_wrapper_contract(self):
        app = load("live_wrapper")
        self.assertEqual(app.render(" Straße "), "strasse")
        self.assertEqual(app.render(""), "")
        with self.assertRaises(AttributeError):
            app.render(None)

    def test_boundary_wrapper_contract(self):
        app = load("boundary_wrapper")
        self.assertEqual(app.render(" Straße ", authorized=True), "strasse")
        # None detects evaluation before authorization, not merely a wrong result.
        with self.assertRaises(PermissionError):
            app.render(None)
        with self.assertRaises(PermissionError):
            app.render("public", authorized=False)
        with self.assertRaises(AttributeError):
            app.render(None, authorized=True)


if __name__ == "__main__":
    unittest.main()
