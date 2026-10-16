#!/usr/bin/env python3
"""Optional scoped literal-search evidence; no consumer-completeness inference."""
import argparse
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

DEFAULT_EXCLUDES = ["**/.git/**", "**/node_modules/**", "**/vendor/**", "**/.venv/**"]
STATES = {
    "decision": {"eligible", "needs_evidence", "requires_decision", "rejected"},
    "implementation": {"not_applied", "applied", "reverted"},
    "verification": {"passed", "failed", "unavailable", "not_run"},
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def file_digest(path):
    try:
        if not path.is_file():
            return None
        h = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def local_path(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Paths must resolve inside root: " + name)
    return path


def inventory(root, config):
    """Conservative bounded metadata inventory; not a consumer-discovery oracle."""
    entries, problems, ignore_files = {}, [], {}
    deadline = time.monotonic() + config.get("inventory_timeout_seconds", 5)
    limit = config.get("max_inventory_files", 10000)
    pruned = {".git", "node_modules", "vendor", ".venv"}

    def add(path):
        if len(entries) >= limit or time.monotonic() > deadline:
            raise RuntimeError("Inventory limit exceeded")
        if path.is_symlink():
            if path.name in {".gitignore", ".ignore", ".rgignore"} and not path.resolve().is_relative_to(root):
                problems.append("Ignore file resolves outside root: " + str(path.relative_to(root)))
                return
            problems.append("Unresolved symlink in inventory: " + str(path.relative_to(root)))
            return
        stat = path.stat()
        entries[str(path.relative_to(root))] = [stat.st_size, stat.st_mtime_ns]

    def walk_error(error):
        problems.append(str(error))

    try:
        for name in config["include"]:
            path = local_path(root, name)
            ancestor = path if path.is_dir() else path.parent
            while ancestor.is_relative_to(root):
                for filename in (".gitignore", ".ignore", ".rgignore"):
                    candidate = ancestor / filename
                    if not candidate.resolve().is_relative_to(root):
                        problems.append("Ignore file resolves outside root: " + str(candidate.relative_to(root)))
                        continue
                    ignore_files[str(candidate.relative_to(root))] = file_digest(candidate)
                if ancestor == root:
                    break
                ancestor = ancestor.parent
            if path.is_file():
                add(path)
            elif path.is_dir():
                for directory, dirs, files in os.walk(path, followlinks=False, onerror=walk_error):
                    if time.monotonic() > deadline:
                        raise RuntimeError("Inventory time limit exceeded")
                    for dirname in dirs:
                        if dirname not in pruned and (Path(directory) / dirname).is_symlink():
                            problems.append("Unresolved symlink directory: " + str((Path(directory) / dirname).relative_to(root)))
                    dirs[:] = sorted(d for d in dirs if d not in pruned and not (Path(directory) / d).is_symlink())
                    for filename in sorted(files):
                        add(Path(directory) / filename)
            else:
                problems.append("Missing inventory path: " + name)
    except (OSError, RuntimeError) as exc:
        problems.append(str(exc))
    return {"entries": entries, "ancestor_ignore_hashes": ignore_files,
            "complete": not problems, "problems": problems,
            "policy": "Conservative metadata inventory includes hidden/ignored files; prunes default dependency directories"}


def validate_states(record):
    """Check vocabulary and declared blockers only, never business truth."""
    if not isinstance(record, dict):
        return ["Record must be an object"]
    errors = [key + ": invalid state" for key, values in STATES.items()
              if record.get(key) not in values]
    if record.get("decision") == "eligible" and record.get("unknown"):
        errors.append("eligible conflicts with declared unknown obligations")
    if record.get("decision") == "eligible" and (record.get("complete") is False or
            record.get("result") in {"error", "incomplete"}):
        errors.append("eligible conflicts with incomplete/error search evidence")
    if record.get("verification") == "passed" and not record.get("verification_evidence"):
        errors.append("passed requires recorded verification evidence")
    return errors


def fingerprint(root, config, rg):
    """Caller declares relevant files and oracle inputs, not exhaustive consumers."""
    files = config.get("relevant_files", []) + config.get("oracle_files", [])
    hashes = {name: file_digest(local_path(root, name)) for name in files}
    version = None
    if rg:
        try:
            version = subprocess.run([rg, "--version"], capture_output=True,
                                     timeout=5, check=False).stdout.decode(errors="replace")
        except (OSError, subprocess.TimeoutExpired):
            pass
    return {"config_sha256": digest(config), "files": hashes,
            "inventory": inventory(root, config),
            "tool": {"path": rg, "sha256": file_digest(Path(rg)) if rg else None,
                     "version": version},
            "oracle_id": config.get("oracle_id"),
            "coverage_claim": "Declared inputs only; hashes do not prove exhaustive consumers"}


def freshness(old, current):
    changed = [key for key in ("config_sha256", "files", "tool", "oracle_id", "inventory")
               if old.get(key) != current.get(key)]
    missing = [name for name, value in current["files"].items() if value is None]
    missing += current.get("inventory", {}).get("problems", [])
    return {"status": "stale" if changed else "unknown" if missing else "unchanged_declared_inputs",
            "changed": changed, "missing_inputs": missing,
            "note": "Recheck affected evidence after changes; unchanged is not completeness proof"}


def validate(config):
    if not isinstance(config, dict):
        raise ValueError("Configuration must be an object")
    for key in ("include", "patterns"):
        if not isinstance(config.get(key), list) or not config[key] or not all(
                isinstance(x, str) and x and "\x00" not in x and "\n" not in x for x in config[key]):
            raise ValueError(key + " must be a nonempty list of nonempty single-line strings")
    for key in ("exclude", "unresolved", "relevant_files", "oracle_files", "supported_configurations"):
        if key in config and (not isinstance(config[key], list) or
                              not all(isinstance(x, str) and "\x00" not in x for x in config[key])):
            raise ValueError(key + " must be a list of strings")
    for key in ("include_hidden", "include_ignored"):
        if key in config and not isinstance(config[key], bool):
            raise ValueError(key + " must be a boolean")
    for key, default in (("timeout_seconds", 30), ("max_output_bytes", 1000000),
                         ("inventory_timeout_seconds", 5), ("max_inventory_files", 10000)):
        value = config.get(key, default)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(key + " must be positive")
    if not isinstance(config.get("max_inventory_files", 10000), int):
        raise ValueError("max_inventory_files must be an integer")
    if not isinstance(config.get("max_output_bytes", 1000000), int):
        raise ValueError("max_output_bytes must be an integer")


def collect(root, config):
    validate(config)
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Root must be a directory")
    rg = shutil.which("rg")
    baseline = fingerprint(root, config, rg)
    unknown = list(config.get("unresolved", []))
    unknown += baseline.get("inventory", {}).get("problems", [])
    if not config.get("supported_configurations"):
        unknown.append("Supported configurations are undeclared")
    for name, value in baseline["files"].items():
        if value is None:
            unknown.append("Missing/unreadable declared input: " + name)
    paths = []
    for name in config["include"]:
        path = local_path(root, name)
        if path.exists():
            paths.append(str(path))
        else:
            unknown.append("Missing included path: " + name)
    excludes = DEFAULT_EXCLUDES + config.get("exclude", [])
    args = [rg or "rg", "--json", "--fixed-strings", "--text", "--no-config",
            "--no-ignore-global", "--no-ignore-parent"]
    if config.get("include_hidden", False):
        args.append("--hidden")
    if config.get("include_ignored", False):
        args.append("--no-ignore")
    for pattern in config["patterns"]:
        args.extend(["-e", pattern])
    for pattern in excludes:
        args.extend(["--glob", "!" + pattern])
    args.extend(["--"] + paths)
    record = {"schema_version": 1, "decision": "needs_evidence",
              "implementation": "not_applied", "verification": "not_run",
              "root": str(root), "scope": config, "effective_excludes": excludes,
              "ignore_policy": "Local ignore files honored unless include_ignored; global/parent ignore disabled",
              "traversal_policy": "No symlink-directory following; explicit hidden files may be searched; binary files treated as text",
              "argv": args, "fingerprint": baseline, "unknown": unknown,
              "returncode": None, "result": "error", "complete": False,
              "truncated": False, "matches": [], "stderr": "",
              "limits": {"timeout_seconds": config.get("timeout_seconds", 30),
                         "max_output_bytes": config.get("max_output_bytes", 1000000),
                         "output_limit_kind": "retained output, not scan or temporary disk budget"}}
    if any(problem.startswith("Ignore file resolves outside root:") for problem in unknown):
        return record
    if not rg or not paths:
        unknown.append("ripgrep unavailable" if not rg else "No existing included paths")
        return record
    env = dict(os.environ)
    env.pop("RIPGREP_CONFIG_PATH", None)
    # Temporary files prevent unbounded memory capture. Scan time is bounded; disk is not.
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            process = subprocess.Popen(args, cwd=root, env=env, stdout=stdout, stderr=stderr)
            try:
                process.wait(timeout=config.get("timeout_seconds", 30))
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                unknown.append("Search timeout")
            record["returncode"] = process.returncode
        except OSError as exc:
            unknown.append("Search execution error: " + str(exc))
        cap = config.get("max_output_bytes", 1000000)
        stdout.seek(0)
        raw = stdout.read(cap + 1)
        stderr.seek(0)
        errors = stderr.read(cap + 1)
        record["truncated"] = len(raw) > cap or len(errors) > cap
        record["stderr"] = errors[:cap].decode(errors="replace")
        summary_seen = False
        for line in raw[:cap].splitlines():
            try:
                event = json.loads(line)
                if event["type"] == "match":
                    match = event["data"]
                    lines = match["lines"]
                    content = (lines["text"].encode() if "text" in lines
                               else base64.b64decode(lines["bytes"]))
                    match["matched_patterns"] = [p for p in config["patterns"] if p.encode() in content]
                    record["matches"].append(match)
                if event["type"] == "summary":
                    summary_seen = True
            except (ValueError, KeyError):
                unknown.append("Incomplete or invalid ripgrep JSON output")
        completed = record["returncode"] in (0, 1) and summary_seen and not errors
        record["result"] = ("matches" if record["returncode"] == 0 else "no_matches") if completed else "error"
        if record["truncated"]:
            unknown.append("Output exceeded retention limit")
        record["complete"] = completed and not record["truncated"] and not unknown
        if completed and (record["truncated"] or unknown):
            record["result"] = "incomplete"
    after = fingerprint(root, config, rg)
    if after != baseline:
        unknown.append("Declared inputs changed during search")
        record["complete"] = False
        record["result"] = "incomplete"
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--validate-record", type=Path, help="Validate state vocabulary and declared blockers")
    parser.add_argument("--check", type=Path, help="Compare prior JSON fingerprint without running search")
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text())
        validate(config)
        if not args.root.is_dir():
            raise ValueError("Root must be a directory")
        if args.validate_record:
            errors = validate_states(json.loads(args.validate_record.read_text()))
            result = {"valid_record": not errors, "errors": errors, "semantic_truth_verified": False}
            code = 2 if errors else 0
        elif args.check:
            old = json.loads(args.check.read_text())["fingerprint"]
            result = freshness(old, fingerprint(args.root.resolve(strict=True), config, shutil.which("rg")))
            code = 0 if result["status"] == "unchanged_declared_inputs" else 2
        else:
            result = collect(args.root, config)
            code = 0 if result["complete"] else 2
        print(json.dumps(result, indent=2))
        return code
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"result": "error", "complete": False, "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
