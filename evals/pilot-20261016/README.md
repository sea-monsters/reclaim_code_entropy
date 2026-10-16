# Synthetic pilot evidence — 2026-10-16

These are small diagnostic trials, not a production benchmark. Publishing these
fixtures makes them unsuitable as unseen future holdouts. No comparative efficacy,
error-rate, speed, or long-term maintenance benefit is established.

## Four-condition pilot (before final adaptive-routing change)

One fresh agent per condition, same newly authored task/repository and inherited
hosted model/settings. A had no task-specific skill; B used original `b1edaf0`;
C used v0.2 `cdf5521`; D used a pre-final v0.3 SKILL snapshot. Full hashes are in
`provenance.json`. D predates the final adaptive-evidence section and cannot be
presented as a trial of the exact released version.

All four passed all six independent oracle checks and made the same implementation
cut: removed a private dead function and inlined a private forwarding hop, reducing
`parcel.py` by eight lines. All preserved permission ordering, hidden-manifest
runtime export, a pre-existing user edit, and executable permission. A added six
regression tests (72 net test lines); B/C/D did not persist additional tests.
Independent reruns: A 8/8 repository tests, B/C/D 2/2 each. Full diffs were reviewed.
There was no observed version advantage on this task.

Per-condition patches, outcomes and test logs are in `results/`. Patches exclude
the pre-existing synthetic user edit. The oracle was authored before candidates
ran and withheld from them. Checksums were recorded after early arms and verified
again at completion; this is not signed preregistration. D reported reading only
SKILL.md, not its support files. Later helper fixes were not exercised by D.

Replay a final patch in a fresh directory (requires Python 3.10+ and Git):

```sh
python3 create_arm.py /tmp/entropy-pilot-replay
cd /tmp/entropy-pilot-replay
# Use the absolute path to this published evidence directory:
git apply /path/to/pilot-20261016/results/b.patch
python3 -B -m unittest discover -s tests -v
python3 -B /path/to/pilot-20261016/pilot_oracle.py .
```

Running the oracle before applying a patch intentionally fails structural
completion while passing surviving behavior/protection. `create_arm.py` refuses
to overwrite an existing directory. Review candidate code before oracle imports;
these tools are not an adversarial sandbox.

## Adaptive-routing follow-up (after the added SKILL section)

Two fresh tasks used the later SKILL hash in `adaptive/provenance.json`:

- Private closed-world leaf: removed only the unused function; used targeted
  references and the existing one-test suite. No evidence JSON, inventory helper
  or reference recipes. The agent redundantly ran baseline discovery and the
  equivalent documented command once each; there was no unrelated broad suite
- Lifecycle boundary: replaced derived stored `released` state with a property,
  retaining separate stopping/admission and pending-task ownership. Read the
  lifecycle/mirrored-state recipes and added stop-with-inflight and transition
  checks. Three repository tests pass, including 729 six-operation sequences.
  Independent evaluator also passed all 364 traces of lengths 0–5

`adaptive/` contains starting fixtures, task, patches, results, test logs and the
independent oracle. Replay by copying the appropriate `*-seed` directory, applying
its patch, then running `python3 -B -m unittest test_app -v` and
`python3 -B /path/to/adaptive/adaptive_oracle.py leaf .` (or `boundary`). These
probes were authored from the declared contracts while tasks were active; they
were not preregistered. Full diffs independently reviewed. Sequential finite
traces do not establish concurrency safety or support undocumented direct state
mutation. This demonstrates distinct evidence routes in two examples, not optimal
cost or statistically established skill adherence.

## Limits and complete reporting

- Convenience order, partly overlapping; not randomized; one trial per condition
- Shared hosted model/settings, but exact model ID and cost/tool/token counters
  were not recorded; no timing or cost comparison is reported
- Same-privilege, instruction-separated working directories; no OS-enforced oracle
  protection. Candidates were not given evaluator answers or other arms
- Tiny synthetic cases, not unseen real repository families; no audit-mode agent
  trial, realistic concurrency matrix, or independent follow-on maintenance task
- Historical stdin tests are agent-reported, not independently transcript-verified.
  Stored suites and oracles were independently rerun; arbitrary report honesty
  is not certified
- Reviewer initially ran B's tests and later boundary tests from the parent
  directory, causing import errors; both passed from their required candidate
  directories. These invocation errors are retained here and are not candidate
  regressions. No candidate failures/timeouts were omitted
