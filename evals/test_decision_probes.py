"""Finite reference decision probes, NOT measurements of an agent's decisions.

This deliberately small teaching model makes prerequisite failures explicit.
It neither discovers repository facts nor grants permission to change real code.
"""
import unittest


def deletion_decision(*, consumers=False, unresolved=False, complete=True, stale=False,
             historical=False, retirement=False, authorized=False, migration=False,
             decisive_evidence_check="passed", budget=True):
    # decisive_evidence_check is a PRE-CHANGE prerequisite check, not the
    # orthogonal post-implementation verification field. No implementation
    # status or post-patch test outcome is modeled here.
    # This models deletion/retirement only. Live consumers do NOT forbid
    # contract-preserving internal simplification, which is a separate task.
    if unresolved or not complete or stale or decisive_evidence_check != "passed":
        return "needs_evidence"
    if retirement:
        return "eligible" if authorized and migration else "requires_decision"
    if consumers or historical or not budget:
        return "rejected"
    return "eligible"


class DecisionProbes(unittest.TestCase):
    def test_fixed_evidence_scenarios(self):
        cases = [
            ("external SDK export", {"consumers": True}, "rejected"),
            ("unresolved dynamic registry", {"unresolved": True}, "needs_evidence"),
            ("truncated empty search", {"complete": False}, "needs_evidence"),
            ("old upgrade migration", {"historical": True}, "rejected"),
            ("rollback obligation", {"historical": True}, "rejected"),
            ("runner unavailable", {"decisive_evidence_check": "unavailable"}, "needs_evidence"),
            ("red baseline", {"decisive_evidence_check": "failed"}, "needs_evidence"),
            ("cache read budget exceeded", {"budget": False}, "rejected"),
            ("retirement needs authorization", {"retirement": True, "migration": True}, "requires_decision"),
            ("retirement migration unresolved", {"retirement": True, "authorized": True}, "requires_decision"),
            ("authorized resolved retirement", {"retirement": True, "authorized": True, "migration": True}, "eligible"),
            ("changed dependency invalidates evidence", {"stale": True}, "needs_evidence"),
        ]
        for name, facts, expected in cases:
            with self.subTest(name=name):
                self.assertEqual(deletion_decision(**facts), expected)

    def test_retirement_still_needs_prechange_evidence(self):
        for status in ("failed", "unavailable", "not_run"):
            self.assertEqual(deletion_decision(retirement=True, authorized=True,
                                              migration=True, decisive_evidence_check=status), "needs_evidence")

    def test_reachability_cycles_and_registered_plugin(self):
        graph = {"public": {"plugin"}, "plugin": set(), "dead_a": {"dead_b"}, "dead_b": {"dead_a"}}
        reached, pending = set(), ["public"]
        while pending:
            node = pending.pop()
            if node not in reached:
                reached.add(node)
                pending.extend(graph[node])
        self.assertEqual(set(graph) - reached, {"dead_a", "dead_b"})
        self.assertIn("plugin", reached)
        # Local reference counts alone would miss the dead mutually recursive cycle.
        self.assertTrue(all(any(node in edges for edges in graph.values()) for node in ("dead_a", "dead_b")))


if __name__ == "__main__":
    unittest.main()
