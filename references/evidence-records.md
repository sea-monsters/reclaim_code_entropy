# Scoped evidence records (optional)

Use this format for consequential negative evidence or repeated searches. A small,
well-understood cut can use a short prose record instead; running a helper is not
an extra acceptance gate. Searches collect facts, not permission to delete.

## Three independent states

- `decision`: `eligible | needs_evidence | requires_decision | rejected`
- `implementation`: `not_applied | applied | reverted`
- `verification`: `passed | failed | unavailable | not_run`

For example, an eligible change may remain unapplied and untested. An applied
change may fail verification and need reverting. `passed` describes the stated
oracle and commands, not proof of complete behavior. Record candidate, change
kind, supported scope, evidence, unresolved obligations, oracle, actual commands
and results alongside these states. The helper initializes states conservatively;
a search alone never promotes a candidate to eligible or verification to passed.

## Optional batched literal search

Requires Python 3.10+ and installed `rg`; adds no packages. From the repository:

```sh
python -B scripts/collect_evidence.py /tmp/search-scope.json --root /path/to/repository > /tmp/search-evidence.json
python -B scripts/collect_evidence.py /tmp/search-scope.json --root /path/to/repository --check /tmp/search-evidence.json
python -B -m unittest discover -s scripts/tests -v
```

Keep outputs outside the search scope. Example configuration (adapt paths before
running; nonexistent paths deliberately make the evidence incomplete):

```json
{
  "include": ["src", "tests", "config/registry.json"],
  "exclude": ["**/build/**"],
  "patterns": ["LegacyAdapter", "legacy.adapter"],
  "include_hidden": false,
  "include_ignored": false,
  "supported_configurations": ["linux/python3.11/default-feature-set"],
  "unresolved": ["external plugin registry has not been inspected"],
  "relevant_files": ["src/adapter.py", ".gitignore", "config/registry.json"],
  "oracle_files": ["tests/test_adapter_contract.py"],
  "oracle_id": "independent contract probe, revision 1",
  "source_revision": "record the actual inspected commit here",
  "worktree_context": "record dirty paths and untracked inputs here",
  "max_inventory_files": 10000,
  "inventory_timeout_seconds": 5,
  "timeout_seconds": 30,
  "max_output_bytes": 1000000
}
```

Patterns are literal, single-line strings, passed as separate `-e` arguments in
one process; each retained matching line includes its literal `matched_patterns`
attribution, including overlapping patterns. There is no shell interpolation or arbitrary extra-argument channel.
Paths are explicit and confined to the root; symlink directory traversal is not
enabled. Binary files are treated as text. `rg` configuration, parent ignore files,
and global ignore files are disabled for reproducibility. Local ignore files still
apply unless explicitly disabled. Default exclusions always cover `.git`,
`node_modules`, `vendor`, and `.venv`; reported exclusions are part of the evidence,
not proof those locations are irrelevant. If one contains a supported consumer,
inspect it separately and retain that obligation rather than claiming absence.

For a discovered hidden registry or ignored generated source, make a separate
small configuration that names that path and enables `include_hidden` and/or
`include_ignored`. Do not blindly run a whole-repository dependency crawl. Explicit
file paths can be searched by rg even when hidden/ignored traversal is disabled.
Explain why the included configurations cover the candidate's actual supported
use. Dynamic dispatch, reflection, packaged entry points, historical data, remote
registries and external consumers need separate evidence; literal search cannot
resolve them automatically.

### Result interpretation

- Raw `rg` exit 0 means matches, 1 means no matches, 2 means a search error
- Helper exit 0 means a completed scan of the declared scope; both matching and
  no-match scans can succeed. Exit 2 means incomplete/error/stale/unknown evidence
- JSON `result` separates `matches`, `no_matches`, `incomplete`, and `error`
- Missing paths/declared inputs, undeclared supported configurations, unresolved
  entries, timeout, stderr diagnostics and truncated/invalid output prevent
  `complete: true`. A partial scan can retain matches without supporting absence
- The timeout bounds the search process; `max_output_bytes` bounds retained stdout
  and stderr separately, not scan volume or temporary disk use. Output is spooled
  to temporary files and removed after reading. For huge scopes, narrow paths;
  this helper is not a disk-quota manager or untrusted-code sandbox
- `complete` means only that the declared scan completed with retained output and
  no declared unknowns. It never means all consumers have been enumerated

### Invalidation and reuse

Record the actual repository revision and dirty/untracked worktree context in
`source_revision` and `worktree_context` (caller supplied; the helper does not verify
Git provenance). Refresh them after any relevant change.

The fingerprint records the complete configuration, declared relevant file and
oracle hashes, `oracle_id`, and rg executable/version. `--check` compares these
without rerunning searches. Changes make evidence stale; missing declared inputs
make it unknown. The collector also compares declared inputs before/after a scan.
Recheck the affected evidence after changes to relevant source, generated inputs,
configurations, tool or oracle. Include relevant local ignore files explicitly for byte-level change detection,
including nested ignore files (ancestor ignore hashes are also captured).

A bounded conservative file inventory includes hidden and ignored files under the
included paths, pruning default dependency directories. It records names, sizes and
mtime nanoseconds, plus ancestor local ignore-file hashes. New or removed consumers
inside this domain invalidate a prior record even if the target hash is unchanged.
Symlink files/directories in the inventoried domain are unresolved, and ancestor
ignore files resolving outside the root are not hashed and make evidence unknown.
Inventory limits (`max_inventory_files`, default 10000; `inventory_timeout_seconds`,
default 5) or read failures produce unknown evidence. Inventory scans run before and
after collection and during freshness checks; this overhead is optional because the
helper itself is optional. Inventory may conservatively invalidate unrelated edits.

The helper does not discover the complete dependency set, follow symlink directories,
or create an atomic snapshot. Metadata is not a content hash: declare relevant
source, config and oracle files for byte-level hashing, including generated inputs.
External consumers and files beyond the included domain still require discovery
refresh. Check repository changes for new exports, plugins, generators and build
configuration that expand the relevant scope. Unchanged inputs never repair an
originally incomplete consumer inventory, and adversarial timestamp preservation is
outside this lightweight helper's guarantees.

Optional record validation (using the same config/root) is available with
`--validate-record /tmp/candidate-record.json`. It checks allowed state values,
rejects `eligible` with declared unknown obligations or explicit search fields
`complete: false` / `result: error|incomplete`, and requires recorded
`verification_evidence` for `passed`. It does not prove that a decision, command,
result or evidence claim is true. Generic candidate records need not contain search
fields; when present, those fields impose the consistency checks above. No global
`success` state is inferred.

Batching saves repeated process setup and traversal, but this repository makes no
end-to-end speed claim. Compare repeated and batched searches with identical scope
and normalized matching lines before reporting measured timing for a real workload.
