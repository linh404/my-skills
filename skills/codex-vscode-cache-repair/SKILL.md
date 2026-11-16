---
name: codex-vscode-cache-repair
description: Diagnose and repair Codex's VS Code sidebar when the extension activates but its WebView renderer never becomes ready. Use for profile-specific blank/failed Codex UI, especially when a temporary profile works; do not use for Codex CLI, authentication, or VS Code process-start failures.
---

# Repair Codex WebView cache in VS Code

Use this when VS Code opens and `openai.chatgpt` activates, but the Codex sidebar stays blank or reports a UI error.

## Confirm the failure stage

1. Identify the VS Code build, Codex extension version, active user-data directory, and selected profile. Prefer the running process arguments over assumptions. On Linux the usual user-data directory is `~/.config/Code`; `--user-data-dir` or `--profile` can change the active location.
2. Read the newest `Codex.log` under `<user-data>/logs/<session>/window*/exthost/openai.chatgpt/`. Look for:
   - `Webview renderer did not become ready ... reason=renderer_ready_timeout ... receivedWebviewMessage=false ... stage=renderer` — Codex UI did not complete its renderer handshake.
   - `Initialize received id=1` from `CodexMcpConnection` — the bundled app-server started. If initialization fails, diagnose that separately; cache reset is not the first fix.
3. Check whether the user already confirmed that a temporary profile works. Treat this as evidence of profile-local state, not proof that a particular extension conflicts. If another active extension is suspected, compare a controlled profile with the same active extension set before disabling extensions.
4. Do not change `chatgpt.cliExecutable`, login state, Codex history databases, or workspace state to fix a renderer-only timeout.

## Reset profile caches

Only do this when the user asks to fix/reset the profile, or has approved cache removal. If they asked only for diagnosis, stop before mutation and report the evidence.

1. Confirm the exact user-data directory and that it belongs to the main profile. Close VS Code normally so cache databases are not live. Do not use `kill -9`; if the app will not close cleanly, stop and explain what is still running.
2. Create a dated quarantine directory on the same filesystem. Rename existing generated cache directories into it instead of deleting them immediately. Typical names are:
   - `Cache`, `Code Cache`, `GPUCache`
   - `DawnGraphiteCache`, `DawnWebGPUCache`
   - `Service Worker`, `WebStorage`
   - `CachedData`, `CachedProfilesData`, `CachedConfigurations`
3. Do not remove `User/globalStorage`, `User/workspaceStorage`, `Local Storage`, cookies, or extension installation directories as part of this cache reset. `WebStorage` can contain `IndexedDB`; preserve any `WebStorage/*/IndexedDB` separately or keep the quarantine until recovery is verified.
4. Launch VS Code again with the same executable, user-data directory, profile, and workspace. Do not use a fresh profile as the final repair; the goal is to repair the user's original profile.

## Verify and finish

- Reopen the Codex sidebar in the original profile and inspect that session's `Codex.log`.
- Success is a `client.performance.span` for `app_start` with `renderer_ready`, `home_visible`, and `outcome=success`, with no new `renderer_ready_timeout`. Note the startup time; first load after cache reset can be slower.
- If it still times out, retain the quarantined caches and stop. Collect the new `Codex.log` and VS Code renderer/Developer Tools console errors. Do not expand the reset to history, workspace state, credentials, or all extension storage without new evidence.
- Once startup is verified, remove only quarantined generated caches that are safe to regenerate and that the user asked to clear. Keep any preserved IndexedDB or other non-cache state. Record the exact cache directories reset and the verification result in the user's incident notes when available.

## Reference outcome

In the confirmed incident on Ubuntu/VS Code, Codex's app-server initialized but the main profile timed out waiting for its WebView renderer. Test copies with the same Codex state, workspace state, settings, and active user extensions loaded successfully. After the main profile's cache set was quarantined and VS Code restarted, the original profile logged `renderer_ready`, `home_visible`, and `outcome=success` in about 23 seconds. This narrowed the cause to profile-local cache/startup state; the specific directory was not isolated.
