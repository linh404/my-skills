---
name: codex-9router-profiles
description: "Keep a local 9Router Codex profile separate from the normal official Codex login. Use when configuring, switching, or checking either path; do not use for general 9Router provider management."
---

# Codex 9router Profiles

Maintain two deliberately separate paths on this machine:

- **Normal Codex:** plain `codex` uses the official Codex login held in `~/.codex/auth.json`. `~/.codex/config.toml` must not select or define the `9router` provider.
- **9Router:** `codex --profile 9router`, or the Bash convenience form `codex --9router`, layers `~/.codex/9router.config.toml` over the base config. It selects `model_provider = "9router"` and authenticates to the local gateway with the profile's static `Authorization` header.

The objective is routing and credential separation, not two OpenAI accounts. Never copy the official-login access, refresh, or ID tokens into 9Router, its dashboard, shell variables, logs, or commands.

## First checks

1. Run `python3 ~/.codex/skills/codex-9router-profiles/scripts/check_split.py`. It checks configuration structure and credential presence only; it never prints credential values or sends a request.
2. Inspect the three files by structure only: `~/.codex/config.toml`, `~/.codex/9router.config.toml`, and `~/.codex/auth.json`. Redact `Authorization`, API keys, and all token values in any output.
3. Check persistent shell files and the current environment for `OPENAI_BASE_URL` and `OPENAI_API_KEY`. They must not be exported globally, because that would silently route plain `codex` through 9Router.

## Configuration rules

- Keep `~/.codex/config.toml` for shared, non-provider settings (trusted projects, MCP servers, TUI preferences) and normal first-party defaults. Do not add `[model_providers.9router]`, `model_provider = "9router"`, or 9Router credentials there.
- Keep the 9Router endpoint, provider, selected gateway model, and static gateway `Authorization` header exclusively in `~/.codex/9router.config.toml`. Use a local `http://127.0.0.1:20128/v1` endpoint unless the user explicitly selects a different trusted endpoint.
- Preserve `~/.codex/auth.json` and mode `0600`. Only run `codex login` or `codex logout` when the user explicitly requests an official-account authentication change.
- Use `codex --profile 9router` when the Bash wrapper is unavailable. The wrapper may remove only its own `--9router` flag; it must pass every other argument through unchanged and reject a simultaneous `--profile` flag.
- Do not implement this split with system-wide `OPENAI_BASE_URL` / `OPENAI_API_KEY` exports. That pattern is appropriate for a router-only workstation, not a workstation that must preserve plain `codex` for the official account.

## Changes and verification

- Before changing provider settings, take a timestamped `0600` backup of the file that will change. Modify only the target profile or only the 9Router-specific keys in the base config.
- Never start, restart, or containerize 9Router on your own. If it is not running, report that its profile is ready but unavailable; explain the exact command and wait for the user to ask before launching it.
- Validate with the checker after every edit. A successful local configuration check does not prove the gateway is running or that its API key is accepted.
- For a non-network smoke test, use `codex --profile 9router --help`; do not send a prompt or probe the gateway without the user's approval.
