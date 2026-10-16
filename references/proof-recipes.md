# Three focused proof recipes

Read only the recipe relevant to the candidate. Start with the change kind:
unreachability requires consumer evidence; internal simplification preserves
supported contracts despite consumers; capability retirement requires an authorized
policy decision. These recipes supplement, rather than replace, that distinction.

## Forwarding layer

**Claim:** removing a forwarding hop preserves observable behavior and does not
remove an ownership, security, compatibility or protocol boundary.

Inspect callers and boundary responsibilities. Compare defaults, positional and
keyword calls, argument evaluation order and count, exception types/messages and
translation, authentication order, transaction scope, context propagation, and
resource creation/cleanup lifetime. A single implementation does not prove that an
interface's protected change boundary has no value.

Minimal independent probes:

1. Call with omitted/default arguments and each supported public calling form
2. Use inputs that append to a trace on access; compare the trace, not just return
   values. Repeated reads or earlier evaluation can be observable
3. Use an input that raises on access. An unauthorized call must fail authorization
   with an empty access trace; catching an early access error still violates this
4. Exercise underlying failures and check promised error conversion and cleanup
5. Trace transaction entry/commit/rollback, active context and resource close;
   verify the same operations occur within the same boundary and exactly once

**Reject example:** moving input normalization ahead of authorization and swallowing
its exception can preserve the final exception while leaking input access.
**Safe candidate:** a private pure forwarding hop with no independent responsibilities,
whose public defaults, order, failures and surrounding boundaries remain intact.
Tests should not require retaining the private helper's name or exact syntax.

## Mirrored state

**Claim:** one authoritative representation can replace two maintained copies
without losing an independent write, snapshot, commit phase or performance duty.

Identify the owner and authority of each value, every write path, synchronization
boundaries, persistence format and compatibility consumers. Determine whether the
second value is a derived read, a snapshot, a committed version, or a cache that
satisfies an existing read/latency budget. Similar values need not be equivalent
states. Do not invent a new performance target solely to block a cut.

Minimal independent probes:

1. Exercise writes through each supported entry, including reset and failure paths
2. Hold a snapshot, update the authority, and check whether the snapshot must remain
   unchanged; a getter that reads the latest state can break this contract
3. Simulate failed/partial commit and check visibility before and after commit
4. Count source reads or use the existing performance benchmark to test a cache's
   documented budget, including invalidation, stale reads and resource ownership

**Reject example:** replace a saved transaction snapshot with a live property.
**Safe candidate:** remove an always-derived private copy with no independent writes,
snapshot contract, persistence obligation or measured cache duty. Preserve the
public view and supported aliasing/mutation behavior.

## Lifecycle state

**Claim:** merging lifecycle flags preserves admission, in-flight work and release
conditions across all supported transitions, including exceptional ones.

Distinguish stop requested, no longer accepting work, work still in flight, and
quiescent/resource-releasable. Identify who owns each transition, synchronization
and release action. Equal values on a happy path do not establish equivalence.

A minimal finite-state teaching model:

```python
accepting, inflight, released = True, 0, False
# start work
assert accepting
inflight += 1
# request stop
accepting = False
assert inflight == 1  # stopped admission is not quiescence
assert not released
# finish work
inflight -= 1
assert not accepting and inflight == 0  # now eligible for release
released = True
```

The shortest counterexample to `can_release = not accepting` is `start → stop`.
This sequential model illustrates the obligation; it is not a concurrency proof.
Probe admission racing with stop, stop during active work, task failure/cancellation,
repeated stop, completion order and any supported restart. Use the implementation's
actual synchronization primitive or a controlled scheduler for concurrency tests.
Verify that new work cannot enter after the promised boundary and cleanup cannot
run before the last owner releases its work. Record untested schedules as limits.

**Reject example:** replace `quiescent` with `closing` while tasks retain a resource.
**Safe candidate:** remove a redundant flag only after proving its invariant over
all supported transitions, failure paths and ownership transfers.

## Reporting any recipe

Keep decision, implementation and verification independent. Cite the actual oracle,
commands and failures, and describe what maintenance obligation disappeared.
A passing baseline with no structural change is not completed simplification;
a failed baseline is not evidence that a new failure is harmless. Record remaining
unknowns and invalidate relevant evidence when source, configuration, tool or oracle
changes. Never turn a recipe checklist or matching file hash into safety proof.
