#!/usr/bin/env python3
"""Baseline check for this Home Assistant add-on repository.

There is no package manifest and nothing to compile, so the delivery commands
have to check the things that actually break here: an add-on manifest that
stops parsing or loses a required key, a Dockerfile that is missing or has no
base image, and a shell script with a syntax error. All three ship silently
today and only fail when Supervisor tries to install the add-on.

Uses nothing beyond python3 and bash, because the runner has no linters
installed and a check that cannot run is not a check.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Supervisor refuses an add-on missing any of these.
REQUIRED_KEYS = ("name", "version", "slug", "arch")


def tracked() -> list[str]:
    listed = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return [path for path in listed.stdout.split("\0") if path]


def main() -> int:
    failures: list[str] = []
    paths = tracked()

    manifests = [path for path in paths if Path(path).name in ("config.json", "config.yaml")]
    if not manifests:
        failures.append("no add-on manifest found")

    for path in manifests:
        if path.endswith(".yaml"):
            continue  # Only the JSON form is parsed without a YAML dependency.
        try:
            manifest = json.loads((ROOT / path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            failures.append(f"{path}: {error}")
            continue
        if not isinstance(manifest, dict):
            failures.append(f"{path}: manifest is not an object")
            continue
        for key in REQUIRED_KEYS:
            if key not in manifest:
                failures.append(f"{path}: missing required key '{key}'")
        # An add-on directory without a Dockerfile cannot be built.
        dockerfile = (ROOT / path).parent / "Dockerfile"
        if not dockerfile.is_file():
            failures.append(f"{path}: no Dockerfile beside the manifest")
        elif not any(
            line.strip().upper().startswith("FROM")
            for line in dockerfile.read_text(encoding="utf-8", errors="replace").splitlines()
        ):
            failures.append(f"{dockerfile.relative_to(ROOT)}: no FROM instruction")

    scripts = [path for path in paths if path.endswith(".sh")]
    for path in scripts:
        syntax = subprocess.run(
            ["bash", "-n", str(ROOT / path)], capture_output=True, text=True
        )
        if syntax.returncode != 0:
            first = (syntax.stderr.strip().splitlines() or ["syntax error"])[0]
            failures.append(f"{path}: {first}")

    for failure in failures:
        print(f"addon-check: {failure}", file=sys.stderr)
    if failures:
        return 1
    print(f"addon-check: {len(manifests)} add-ons, {len(scripts)} shell scripts, all valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
