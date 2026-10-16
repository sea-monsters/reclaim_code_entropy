# Parcel output adapter

Supported entrypoints are `parcel.render(value, permitted=False)` and the `export` command in `.runtime/commands.json`. This manifest is read by the host at runtime using importlib; it is not imported by Python modules in this repository. Hidden runtime configuration is shipped. All consumers are in this repository and this documented host dispatch. There are no other external consumers, generated files, or supported Python versions below 3.10.

`render` must reject a false permission value with `PermissionError("blocked")` before interacting with value in any way. On permission, it calls value.strip() once followed by casefold() once and returns that result, propagating errors. Both parameters may be supplied by keyword; permission is optional. `export` accepts only value and is an independent supported public command that prefixes "parcel:" to str(value).

`notes.txt` contains unrelated user work. Preserve it exactly. Preserve executable permissions on `bin/smoke`.

Baseline command: PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
