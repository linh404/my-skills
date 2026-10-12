#!/usr/bin/env python3
"""Verify Codex/9Router separation without exposing credentials or using network."""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import tomllib
from pathlib import Path
from urllib.parse import urlparse


def read_toml(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def private_mode(path: Path) -> bool:
    return stat.S_IMODE(path.stat().st_mode) == 0o600


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Codex and 9Router profile separation without printing secrets."
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=Path.home(),
        help="Home directory containing .codex (default: current user's home).",
    )
    args = parser.parse_args()

    codex_home = args.home.expanduser() / ".codex"
    base_path = codex_home / "config.toml"
    profile_path = codex_home / "9router.config.toml"
    auth_path = codex_home / "auth.json"
    errors: list[str] = []
    warnings: list[str] = []

    if not base_path.is_file():
        errors.append(f"missing base config: {base_path}")
        base = {}
    else:
        try:
            base = read_toml(base_path)
        except tomllib.TOMLDecodeError as error:
            errors.append(f"base config is not valid TOML: {error}")
            base = {}

    if base.get("model_provider") == "9router":
        errors.append("plain Codex selects model_provider = 9router")
    if "9router" in base.get("model_providers", {}):
        errors.append("plain Codex defines [model_providers.9router]")
    if base_path.is_file() and not private_mode(base_path):
        warnings.append("base config is not mode 0600")

    if not profile_path.is_file():
        errors.append(f"missing 9Router profile: {profile_path}")
    else:
        try:
            profile = read_toml(profile_path)
        except tomllib.TOMLDecodeError as error:
            errors.append(f"9Router profile is not valid TOML: {error}")
            profile = {}

        provider = profile.get("model_providers", {}).get("9router", {})
        if profile.get("model_provider") != "9router":
            errors.append("9Router profile does not select model_provider = 9router")
        if not isinstance(provider, dict):
            errors.append("9Router profile has no [model_providers.9router] table")
            provider = {}
        base_url = provider.get("base_url")
        parsed = urlparse(base_url) if isinstance(base_url, str) else None
        if not parsed or parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append("9Router profile has no valid provider base_url")
        elif parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            warnings.append("9Router base_url is not loopback; verify the remote gateway is trusted")
        if provider.get("wire_api") != "responses":
            warnings.append("9Router profile does not declare wire_api = responses")
        authorization = provider.get("http_headers", {}).get("Authorization")
        if not isinstance(authorization, str) or not authorization.strip():
            errors.append("9Router profile has no static Authorization header")
        if "auth" in provider:
            errors.append("9Router profile defines provider auth; use only the static Authorization header")
        if not private_mode(profile_path):
            warnings.append("9Router profile is not mode 0600")

    if not auth_path.is_file():
        errors.append(f"missing official Codex auth file: {auth_path}")
    else:
        try:
            auth = json.loads(auth_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"official auth file is not valid JSON: {error}")
            auth = {}
        tokens = auth.get("tokens") if isinstance(auth, dict) else None
        if not isinstance(tokens, dict) or not tokens.get("refresh_token"):
            warnings.append("official Codex login tokens are not present; plain codex may require codex login")
        if not private_mode(auth_path):
            warnings.append("official auth file is not mode 0600")

    for key in ("OPENAI_BASE_URL", "OPENAI_API_KEY"):
        if os.environ.get(key):
            warnings.append(f"current shell exports {key}; it can override the normal Codex route")

    for message in warnings:
        print(f"WARNING: {message}")
    for message in errors:
        print(f"ERROR: {message}")

    if errors:
        print(f"FAIL: {len(errors)} separation error(s), {len(warnings)} warning(s).")
        return 1

    print(f"PASS: normal Codex and 9Router profile are separated ({len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
