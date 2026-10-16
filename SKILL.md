---
name: reclaim-code-entropy
description: Find, rank, and implement evidence-backed simplifications of dead or abandoned code, duplicate state/APIs, unnecessary abstractions, and over-engineering. Use for repository simplification, deletion candidates, 代码化简、熵回收、清理冗余、收敛抽象 or 去除过度设计. Prove consumers, compatibility and ownership before removing code. Not a general bug or performance audit.
metadata:
  version: "0.3.0"
---

# Reclaim Code Entropy

Treat code entropy as maintenance surface with no current load-bearing reason: extra representations, states, APIs, branches, packages, policies, or tests that the product must keep coherent.

Core rule: a scanner produces candidates; only consumer, ownership, history, and verification evidence justify deletion. Prefer a few proved cuts over a long speculative list. Finding nothing safe to remove is a valid result.

Use the workflow as decision guidance, scaled to the requested scope and impact. Follow governing repository instructions and existing task records; this skill adds simplification-specific reasoning, not a separate approval or scheduling framework.

## Choose The Mode

- For "audit", "find", "review", or "report", inspect only and return ranked candidates. Do not edit.
- For "apply", "remove", "clean up", "simplify", or "refactor", implement the safest requested cuts and verify them.
- Treat removal of a reachable user capability, supported public API, persisted format, or compatibility path as a product decision. Surface the visible tradeoff before changing it unless the user already made that decision explicitly.
- Infer the mode from the whole request and prior authorization, not individual verbs. In apply mode, carry proven cuts through validation without seeking approval again for ordinary in-scope edits. Pause only the candidate requiring an unresolved product decision; continue independent authorized work.

## Scale Evidence To The Cut

Use the least costly evidence sufficient for the affected contract. These are routing examples, not mandatory stages or a numeric risk score:

- **Local, closed-world cut:** a private leaf or pure forwarding layer with bounded callers and no external, durable, security or lifecycle duty. Inspect the relevant definitions and callers, perform a targeted reference check and the smallest decisive behavior/build check. A brief prose record is enough; no mandatory evidence JSON, inventory helper, full suite, telemetry, multi-agent review or recipe traversal.
- **Shared or configuration-sensitive cut:** multiple owners/callers, dynamic registration, generated code, feature variants or a documented performance budget. Add the relevant entry/configuration coverage and affected integration checks; reuse unaffected evidence instead of restarting the entire audit.
- **Boundary-sensitive cut:** public/wire/persisted compatibility, authorization, data loss, asynchronous ownership or resource release. Add independent boundary probes and the applicable compatibility/lifecycle checks. Capability retirement also needs its product decision; stronger tests cannot substitute for it.

Escalate only when inspection exposes a material unknown, an actual obligation, or a failed decisive check. A short diff can be boundary-sensitive; many mechanical edits need not require unrelated checks. Downgrade effort when new evidence closes the affected scope. Stop gathering evidence once the applicable obligation is supported and required repository gates pass; record residual limits without pursuing unrelated possibilities. Never lower a real safety or compatibility obligation to meet a time budget: defer that cut and continue independent eligible work.

## Establish The Contract

1. Read governing instructions and the nearest contract for the affected surface. Consult architecture, decisions, manifests, and test guidance where they bear on a candidate; do not read every repository document by default.
2. Inspect `git status`; preserve unrelated work. Identify generated, vendored, migration, fixture, and public-package paths before classifying code.
3. Trace the affected runtime flow and its reachable consumers, including applicable configuration, registries, injection, events, queues, persistence, processes/workers, and wire protocols.
4. In apply mode, discover the repository's actual narrow and broad verification commands and run a proportional baseline when feasible. A red baseline limits what later checks can prove; record it instead of claiming a regression.

Do not simplify away validation at trust boundaries, authorization, security controls, accessibility basics, data-loss prevention, durable-data compatibility, or cleanup that establishes resource quiescence.

## Survey For Entropy

Start with large or central production surfaces, not only obvious unused symbols. Use repository-native tools first: `rg --files`, `rg`, compiler/linter output, dependency manifests, and `git log`. Run installed dead-code or dependency tools when useful, but treat every result as a lead. Batch related literal searches when that avoids repeated traversal; preserve the same evidence scope. For repeatable scoped collection and invalidation, see [evidence records](references/evidence-records.md) and the optional helper; a bounded local cut does not require a new tracking system.

Honor repository navigation rules, including a configured code graph. For a broad audit, map the requested domains and record inspected areas and coverage gaps; do not stop at the first easy deletion. For a bounded request, follow affected consumers without turning it into a repository-wide audit. Parallelize independent reads when useful; serialize changes and validation sharing an ownership boundary. Delegation follows host and governing task rules.

Look for these candidate classes:

1. **Unconsumed surface**: public methods, exports, events, config keys, hooks, packages, registry notifications, or protocol fields with no production consumer.
2. **Mirrored fact**: two events, caches, summaries, state stores, snapshots, or adapters record the same truth and must be synchronized.
3. **Speculative generality**: unset knobs, fixed feature flags, unused fallbacks, one-implementation interfaces, abandoned stubs, or extension points with no owner.
4. **Extra route or layer**: multiple front doors to one behavior, forwarding-only wrappers, pass-through packages, or helpers that obscure a single caller.
5. **Lifecycle duplication**: several flags, sentinels, promises, queues, or controllers represent one transition such as ready, stopped, settled, flushed, or disposed.
6. **Misplaced defense**: copies, freezes, validators, rollback paths, or hostile-object tests protect a same-process typed handoff rather than an actual trust or ownership boundary.
7. **Hand-rolled infrastructure**: local parsers, retry loops, globbing, framing, diffing, or data structures already covered by the standard library, native platform, or an installed dependency.
8. **Support-only residue**: tests or docs are the only consumers; duplicate expected outputs; obsolete inventories; demo/test packages that impose runtime or publishing cost.
9. **Added-then-abandoned residue**: implementation disappeared but flags, schemas, docs, tests, compatibility branches, or decision notes still describe it.

When cycles or dynamic exports matter, trace reachability from the supported runtime roots, not caller counts: a mutually recursive island can be unreachable while a registry-only plugin remains live. Distinguish production roots from test/project roots and unresolved external consumers. Use an existing compiler, build graph or language-aware transform when it adds relevant evidence; do not install new infrastructure by default.

Do not confuse duplication with necessary independence. Separate backends, adapters, representations, or lifecycle mechanisms may intentionally test a contract or protect distinct owners.

For invariant checks, ask whether observations arise independently and can disagree. Self-confirming checks are leads, not proof of redundancy; retain checks spanning independent producers or mutable stores. Treat comments and documentation as maintenance surface too, preserving local contracts and rationale while removing restatements.

## Prove Or Reject A Candidate

For each exact symbol, behavior, or artifact:

1. Search its symbol, file path, package name, config key, event/wire string, and alternate call syntax across the whole repository.
2. Classify every hit:
   - **Production**: runtime source, shipped configuration, real entrypoints, migrations, operational scripts.
   - **Non-production**: tests, docs, comments, snapshots, generated expected output.
   - **Ambiguous**: examples, fixtures, plugins, reflection, registries, lazy imports, code generation, externally consumed exports. Inspect before classifying.
3. Inspect callers and callees, not only search counts. Check dynamic loading, stringly typed dispatch, routes, plugin manifests, DI containers, serialization, environment-keyed lookup, and external package contracts.
4. Inspect relevant history and decisions when the rationale is unclear or the removal affects an established contract. Ask what problem created the surface, whether it still exists, and what evidence beats the original rationale. Missing history increases uncertainty; it is not evidence of obsolescence.
5. Draw ownership for asynchronous or stateful code. Map each state flag, disposer, cancellation path, readiness promise, and terminal outcome to a distinct owner or transition.
6. State what capability or behavior the deletion gives up, even if the answer is "none observable".
7. Estimate net reduction: code, tests dedicated only to that code, docs, config, generated artifacts, dependencies, and concepts removed minus replacement glue and migrations added.
8. Name the smallest check that would fail if the simplification were wrong.

State decision-relevant evidence scope: revision and relevant worktree changes, supported configurations, included/excluded paths, and applicable external-consumer boundaries. Failed or truncated searches, missing/generated sources, stale indexes, incomplete pagination, and unavailable consumer evidence are unknowns, not zero matches. Resolve material gaps before claiming absence. Telemetry establishes only its observed window and environments, not the end of a support obligation.

Classify the cut before deciding:

- **Unreachable deletion**: a supported consumer or material unresolved reachability path blocks deletion. A proven private, closed-world leaf does not require production telemetry or an irrelevant external-consumer survey.
- **Contract-preserving simplification**: existing consumers are expected; preserve their affected supported observable contract, ownership, and compatibility obligations without claiming whole-program equivalence. A short wrapper may own authorization, transactions, error translation, or resource lifetime.
- **Capability/compatibility retirement**: settle the authorized product decision and required migration before applying; lack of observed use alone does not authorize retirement.

Mark candidates **eligible**, **needs evidence**, **requires decision**, or **rejected**. Only eligible cuts enter implementation ranking. Benefit or confidence cannot offset unresolved safety or compatibility obligations. Keep a candidate when current rationale still applies, complexity is merely relocated, or the change is too small or out of scope. A blocked candidate does not block independent proven cuts or evidence gathering.

Keep decision, implementation, and verification separate: `eligible` is not `applied` or `passed`. Track only enough evidence to support the decision. Use this compact record for substantial candidates; combine fields for simple ones:

```text
[kind / risk] candidate
decision: eligible | needs_evidence | requires_decision | rejected
implementation: not_applied | applied | reverted
verification: passed | failed | unavailable | not_run
evidence: revision and scope; exact locations; consumers/ownership/rationale; material unknowns
cut: artifacts and concepts removed minus replacement and migration cost
tradeoff: surviving contract; any capability or compatibility lost
verify: independent baseline oracle; decisive check and result; net reduction
```

For non-trivial forwarding layers, mirrored state, or lifecycle changes, consult the relevant [proof recipe](references/proof-recipes.md). Use only the affected recipe; do not turn its checklist into mandatory unrelated work.

## Implement A Proven Cut

1. Work in one ownership boundary at a time. Fix the shared source of entropy rather than patching every caller.
2. Delete the obsolete contract end to end: declaration, implementations, branches, tests that exist only for the removed behavior, exports, config, docs, examples, snapshots, generated inventories, and dependency entries.
3. Preserve tests of the surviving observable contract. Tests are evidence, not an untouchable specification and not disposable merely to improve the line count.
4. Collapse mirrored state onto the load-bearing representation. Do not replace two truths with a synchronization wrapper.
5. Prefer deletion, then standard library/native features, then already-installed dependencies. Add a dependency only when it removes more implementation and dedicated testing burden than its glue and supply-chain cost add.
6. Avoid compatibility shims when there is no compatibility obligation. When one exists, keep the path or design an explicit migration instead of silently deleting it.
7. Keep batches reviewable and reversible. Never discard unrelated user changes.

Before a non-trivial live simplification, identify independent evidence of the surviving contract and a matched before/after check where feasible. Control or qualify clocks, randomness, and external responses. Where affected, check input access, side effects, evaluation count and ordering, defaults and public call forms, not just return values or exception types. Record and separate known bugs unless the requested scope includes their repair; verify any explicitly authorized behavior delta against the intended contract. Deleting or weakening a failing test is not proof of equivalence. Remove tests only when their contract is intentionally retired or their surviving obligations are demonstrably covered independently; retain meaningful regressions.

Treat applied migrations, persisted data, and historical compatibility fixtures as potential durable obligations, not dead code solely because current source has no callers. Follow supported upgrade, rollback, and retention policy and check representative old-data behavior before changing an obligation; policy-compliant archival or consolidation remains possible.

Net-negative lines are evidence of a cut, not the goal. A safe simplification may add a small test or migration; a large deletion can still be wrong.

For a library substitution, verify supported runtime versions and uncovered semantics; for a new dependency, also check maintenance and transitive cost. Do not infer equivalent behavior from a matching API name.

For stateful changes, preserve distinct guarantees such as publication/rollback ordering, callback isolation, terminal-result arbitration, worker ownership, and shutdown quiescence. Typed same-process calls alone do not prove that mutation or reentrancy is harmless.

Update owning records when a cut changes their contract, or when record consolidation was requested. Full supersession requires evidence that no behavior or compatibility duty remains; carry forward unique rationale and repair inbound links. Preserve partial decisions and frozen historical evidence under repository retention rules. Do not import another repository's note directories, commands, or archive policy. Audit mode does not authorize adding TODOs or proposal files.

## Validate The Result

After each non-trivial batch:

1. Search again for deleted symbols, strings, paths, and stale documentation.
2. Run the narrowest decisive check, then required gates and broader checks justified by affected consumers, shared contracts, state, or unresolved risk. Reuse applicable evidence; do not run every suite by default. Add a test only when needed to establish the surviving behavior, not to mirror the edit.
3. Re-run any static analyzer that produced the candidate.
4. Run `git diff --check` when Git is available and inspect the complete diff for accidental scope expansion.
5. Compare behavior at public, persisted, wire, and user-visible boundaries. Check existing performance/resource contracts when affected (for example by removing a cache, index, copy, or batch), even without a speedup claim. Measure any claimed performance benefit; do not expand this into a general performance audit.

Choose checks by the affected risk: a private leaf may need only a build and narrow tests; dynamic entrypoints need relevant registry/configuration coverage; public or persisted boundaries need compatibility fixtures; lifecycle changes need cancellation, reentrancy, ordering, and quiescence checks. Start with the cheapest check that could falsify the candidate, not an obligatory full suite.

Record checks as **passed**, **failed**, **unavailable**, or **not run**, distinguishing preexisting baseline failures. Reuse evidence only while its affected code, dependencies, configuration, tool, and oracle assumptions remain valid; refresh the affected closure after later edits. When decisive verification is unavailable, leave contract-sensitive cuts proposed rather than verified. Low-risk local changes may remain reviewable under existing authorization with explicit limits; never report an unrun check as passed.

If verification fails, identify whether the candidate was load-bearing, the implementation was incomplete, or the baseline was already red. Revert only the current batch or repair the proof; do not weaken a meaningful check to force the deletion through.

## Report The Outcome

For an audit, rank eligible candidates by evidence strength, risk, net maintenance reduction, and implementation/verification cost. Keep blocked candidates separate; do not invent a single entropy score. Include rejected or uncertain high-value candidates only when the missing evidence is actionable.

Lead with the result in the user's language. Cite exact file/symbol evidence, distinguish confirmed facts from hypotheses, and state material coverage gaps. Use the repository's existing proposal format only when a durable record is requested or governed; otherwise report inline.

For applied changes, report:

- what contract or duplicate truth was removed;
- files, lines, dependencies, and concepts removed where measurable;
- any user-visible capability or compatibility behavior changed;
- exact validation run and result;
- high-value candidates intentionally kept and why.
