"""Independent finite behavior oracle; imports reviewed fixture code, NOT a sandbox."""
import importlib.util
from pathlib import Path
import sys
import unittest

# Set before any candidate import, including when called without python -B.
sys.dont_write_bytecode = True
ROOT = Path(__file__).parent / "fixtures"


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / name / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Probe:
    def __init__(self, events, fail=None):
        self.events, self.fail = events, fail

    def __getattribute__(self, name):
        if name == "strip":
            object.__getattribute__(self, "events").append("access:strip")
        return object.__getattribute__(self, name)

    def strip(self):
        self.events.append("call:strip")
        if self.fail:
            raise self.fail("probe")
        return Fold(self.events)


class Fold:
    def __init__(self, events):
        self.events = events

    def casefold(self):
        self.events.append("call:casefold")
        return "sentinel"


class ContractChecks(unittest.TestCase):
    def test_dead_leaf_survivor(self):
        app = load("dead_leaf")
        for value, expected in [(0, "current:0"), ("旧", "current:旧"), (None, "current:None"), ("", "current:"), (" x ", "current: x "), ("\x00", "current:\x00")]:
            self.assertEqual(app.render(value=value), expected)
        events = []
        class Value:
            def __str__(self):
                events.append("str")
                return "x"
        self.assertEqual(app.render(Value()), "current:x")
        self.assertEqual(events, ["str"])

    def test_text_and_call_forms(self):
        # Expected outputs are fixed contract examples, not candidate-derived.
        cases = [(" Straße ", "strasse"), ("\u2003Σς\t", "σσ"), (" İ ", "i\u0307"),
                 ("", ""), ("３\x00", "３\x00"), (" \n\t", ""), ("A" * 4096, "a" * 4096)]
        for name in ("live_wrapper", "boundary_wrapper"):
            app = load(name)
            for value, expected in cases:
                with self.subTest(name=name, value=value[:20]):
                    if name == "boundary_wrapper":
                        self.assertEqual(app.render(value, True), expected)
                        self.assertEqual(app.render(value=value, authorized=True), expected)
                    else:
                        self.assertEqual(app.render(value), expected)
                        self.assertEqual(app.render(value=value), expected)

    def test_authorized_access_order_and_count(self):
        for name in ("live_wrapper", "boundary_wrapper"):
            app = load(name)
            events = []
            kwargs = {"authorized": True} if name == "boundary_wrapper" else {}
            self.assertEqual(app.render(Probe(events), **kwargs), "sentinel")
            self.assertEqual(events, ["access:strip", "call:strip", "call:casefold"])
            for error in (AttributeError, ValueError, RuntimeError):
                events = []
                with self.assertRaisesRegex(error, "^probe$"):
                    app.render(Probe(events, error), **kwargs)
                self.assertEqual(events, ["access:strip", "call:strip"])
            with self.assertRaises(AttributeError):
                app.render(None, **kwargs)

    def test_authorization_precedes_processing(self):
        app = load("boundary_wrapper")
        events = []
        class Authorization:
            def __bool__(self):
                events.append("authorization")
                return True
        self.assertEqual(app.render(Probe(events), Authorization()), "sentinel")
        self.assertEqual(events, ["authorization", "access:strip", "call:strip", "call:casefold"])

    def test_denied_never_accesses_input(self):
        app = load("boundary_wrapper")
        for authorized in (False, None, 0):
            events = []
            with self.assertRaisesRegex(PermissionError, "^denied$"):
                app.render(Probe(events, RuntimeError), authorized=authorized)
            self.assertEqual(events, [])
        events = []
        with self.assertRaisesRegex(PermissionError, "^denied$"):
            app.render(Probe(events))
        self.assertEqual(events, [])
        for value in (None, "", "internal:secret"):
            with self.assertRaises(PermissionError):
                app.render(value)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ROOT = Path(sys.argv.pop(1)).resolve()
    unittest.main()
