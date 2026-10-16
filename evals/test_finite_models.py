"""Small executable teaching counterexamples, not concurrency proofs."""
import itertools
import unittest


def lifecycle(trace, collapsed=False):
    closing, inflight = False, 0
    released = False
    for action in trace:
        if action == "start" and not closing:
            inflight += 1
        elif action == "stop":
            closing = True
        elif action == "finish" and inflight:
            inflight -= 1
        released = closing if collapsed else closing and inflight == 0
        if released and inflight:
            return False
    return True


def mirrored(trace, collapse_snapshot=False):
    # Published state is a committed snapshot, not a disposable duplicate.
    draft, published = 0, 0
    observations = []
    for action in trace:
        if action == "edit":
            draft += 1
        elif action == "commit":
            published = draft
        elif action == "read":
            observations.append(draft if collapse_snapshot else published)
    return observations


class FiniteModels(unittest.TestCase):
    def test_lifecycle_stop_is_not_drained(self):
        self.assertTrue(lifecycle(["start", "stop"]))
        self.assertFalse(lifecycle(["start", "stop"], collapsed=True))
        for n in range(5):
            for trace in itertools.product(("start", "stop", "finish"), repeat=n):
                self.assertTrue(lifecycle(trace))

    def test_snapshot_is_not_redundant(self):
        self.assertEqual(mirrored(["edit", "read"]), [0])
        self.assertEqual(mirrored(["edit", "read"], True), [1])
        self.assertEqual(mirrored(["edit", "commit", "read"]), [1])

    def test_true_derived_mirror_can_be_removed(self):
        for edits in range(10):
            authority = edits
            cached_derived = authority * 2
            self.assertEqual(cached_derived, authority * 2)


if __name__ == "__main__":
    unittest.main()
