#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass
from typing import Optional, Tuple


SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


@dataclass(frozen=True, order=True)
class SemVer:
    major: int
    minor: int
    patch: int

    @staticmethod
    def parse(value: str) -> "SemVer":
        m = SEMVER_RE.match(value.strip())
        if not m:
            raise ValueError(f"Invalid SemVer '{value}'. Expected 'MAJOR.MINOR.PATCH' (e.g. 0.4.0).")
        return SemVer(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def load_toml_from_str(toml_str: str) -> dict:
    try:
        return tomllib.loads(toml_str)
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"Invalid TOML content: {e}") from e


def load_toml_from_path(path: str) -> dict:
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError as e:
        raise ValueError(f"TOML file not found: {path}") from e
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"Invalid TOML in file '{path}': {e}") from e


def extract_version(toml_obj: dict) -> str:
    """
    Canonical source: PEP 621 -> [project].version
    Optional fallback (if you still use Poetry): [tool.poetry].version
    """
    project = toml_obj.get("project") or {}
    v = project.get("version")
    if isinstance(v, str) and v.strip():
        return v.strip()

    tool = toml_obj.get("tool") or {}
    poetry = tool.get("poetry") or {}
    pv = poetry.get("version")
    if isinstance(pv, str) and pv.strip():
        return pv.strip()

    raise ValueError("Version not found. Expected [project].version (or fallback [tool.poetry].version).")


def normalize_pr_type(pr_type: str) -> Tuple[str, bool]:
    """
    Returns: (type, breaking)
    Supports: feat, fix, chore, feat!, fix!, chore!
    Extendable for docs/refactor/test/revert later.
    """
    pr_type = pr_type.strip()
    breaking = pr_type.endswith("!")
    base_type = pr_type[:-1] if breaking else pr_type

    allowed = {"feat", "fix", "chore"}
    if base_type not in allowed:
        raise ValueError(f"Unsupported pr type '{pr_type}'. Allowed: feat, fix, chore (optionally with '!').")
    return base_type, breaking


def expected_bump(base: SemVer, change_type: str, breaking: bool) -> SemVer:
    if breaking:
        return SemVer(base.major + 1, 0, 0)

    if change_type == "feat":
        return SemVer(base.major, base.minor + 1, 0)

    # fix, chore -> patch
    return SemVer(base.major, base.minor, base.patch + 1)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate version bump between base and head pyproject.toml according to PR type."
    )

    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--head-path", help="Path to HEAD pyproject.toml (checked-out working tree).")
    src.add_argument("--head-toml", help="Raw TOML content of HEAD pyproject.toml.")

    src2 = parser.add_mutually_exclusive_group(required=True)
    src2.add_argument("--base-path", help="Path to BASE pyproject.toml (checked-out working tree).")
    src2.add_argument("--base-toml", help="Raw TOML content of BASE pyproject.toml.")

    parser.add_argument(
        "--pr-type",
        required=True,
        help="PR type derived from title: feat|fix|chore (optionally with '!'). Example: feat or feat!",
    )

    args = parser.parse_args()

    try:
        head_obj = load_toml_from_path(args.head_path) if args.head_path else load_toml_from_str(args.head_toml)
        base_obj = load_toml_from_path(args.base_path) if args.base_path else load_toml_from_str(args.base_toml)

        head_v = SemVer.parse(extract_version(head_obj))
        base_v = SemVer.parse(extract_version(base_obj))

        change_type, breaking = normalize_pr_type(args.pr_type)

        expected = expected_bump(base_v, change_type, breaking)

        if head_v == base_v:
            raise ValueError(f"Version was not bumped. base={base_v} head={head_v}")

        if head_v != expected:
            raise ValueError(
                f"Invalid version bump for '{args.pr_type}'. "
                f"Expected base={base_v} -> head={expected}, got head={head_v}."
            )

        print(f"OK: '{args.pr_type}' bump is valid. base={base_v} head={head_v}")
        return 0

    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
