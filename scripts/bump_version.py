#!/usr/bin/env python3
# Keeps the version in lockstep across pyproject and all distribution manifests.
# Usage: bump_version.py 1.0.0   |   bump_version.py --check
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
PYPROJECT = ROOT / "mcp_server" / "pyproject.toml"
JSON_MANIFESTS = {
    ROOT / ".claude-plugin" / "plugin.json": [["version"]],
    ROOT / "server.json": [["version"], ["packages", 0, "version"]],
    ROOT / "mcp_server" / "manifest.json": [["version"]],
    ROOT / "gemini-extension.json": [["version"]],
}
VERSION_LINE = re.compile(r'^version = "(?P<version>[^"]+)"$', re.MULTILINE)


def get_path(data, path):
    for key in path:
        data = data[key]
    return data


def set_path(data, path, value):
    for key in path[:-1]:
        data = data[key]
    data[path[-1]] = value


def collect_versions():
    versions = {str(PYPROJECT): VERSION_LINE.search(PYPROJECT.read_text())["version"]}
    for manifest, paths in JSON_MANIFESTS.items():
        data = json.loads(manifest.read_text())
        for path in paths:
            versions[f"{manifest}:{'.'.join(map(str, path))}"] = get_path(data, path)
    return versions


def check():
    versions = collect_versions()
    if len(set(versions.values())) == 1:
        print(f"All versions agree: {next(iter(versions.values()))}")
        return 0
    for location, found in versions.items():
        print(f"{found}  {location}")
    print("Version mismatch across manifests. Run scripts/bump_version.py <version>.")
    return 1


def bump(new_version):
    PYPROJECT.write_text(
        VERSION_LINE.sub(f'version = "{new_version}"', PYPROJECT.read_text(), count=1)
    )
    for manifest, paths in JSON_MANIFESTS.items():
        data = json.loads(manifest.read_text())
        for path in paths:
            set_path(data, path, new_version)
        manifest.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Bumped all manifests to {new_version}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Bump or check manifest versions")
    parser.add_argument("version", nargs="?", help="New semver, e.g. 1.0.0")
    parser.add_argument("--check", action="store_true", help="Verify versions agree")
    args = parser.parse_args()

    if args.check == bool(args.version):
        parser.error("pass either a version or --check")
    return check() if args.check else bump(args.version)


if __name__ == "__main__":
    sys.exit(main())
