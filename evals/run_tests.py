"""Run both regression suites; fail rather than silently accept empty discovery."""
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent


def main():
    success = True
    for relative in ("evals", "scripts/tests"):
        suite = unittest.TestLoader().discover(str(ROOT / relative), pattern="test_*.py")
        count = suite.countTestCases()
        if count == 0:
            raise RuntimeError("No tests discovered in " + relative)
        print(f"{relative}: {count} discovered tests", flush=True)
        success = unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() and success
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
