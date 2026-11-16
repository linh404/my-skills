---
name: computer-issues
description: Record, search, and troubleshoot recurring local computer problems using a durable Markdown knowledge base in ~/Documents/computer-issues.
metadata:
  short-description: Save and retrieve computer fixes
---

# Computer Issues

Use this skill when the user asks to save, remember, search, check, or reuse a fix for a local computer problem.

## Storage

Use `~/Documents/computer-issues` as the canonical knowledge base. Store one Markdown file per recurring issue under `issues/`; update a matching file instead of creating duplicates. Keep secrets out of the knowledge base.

Each entry should include:

- exact symptom and affected device/application;
- date and environment;
- diagnostic evidence and the likely root cause;
- exact fix commands or UI steps;
- verification result;
- rollback/recovery notes;
- a clear status such as **Verified fix**, **Workaround**, or **Unverified suggestion**.

## Workflow

1. Search existing entries before troubleshooting, for example:

   ```bash
   grep -RniE 'keyword|device|error' ~/Documents/computer-issues/issues
   ```

2. If a matching verified fix exists, summarize it first and explain any device/session-specific values that must be rediscovered.
3. For a new issue, inspect the machine with read-only diagnostics where possible. Record only evidence actually observed; distinguish inference from confirmation.
4. If the user asks to apply a fix, make the smallest reversible change, verify it, and then update the issue entry. Do not start/restart Docker containers or services unless the user explicitly authorizes that exact action.
5. Use the current local date in new entries and prefer stable names over transient IDs. Hardware/session IDs, PipeWire node IDs, and process IDs may change; document how to rediscover them.
6. When the problem is not yet solved, record attempted steps and mark the entry **Unverified** rather than presenting a guess as fact.

## Existing reference

The first recorded issue is [Bluetooth TWS connected but audio plays through laptop speakers](file:///home/linh/Documents/computer-issues/issues/bluetooth-audio-routed-to-speakers.md). Use it as a model for evidence, routing diagnosis, and verification.
