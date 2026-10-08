---
name: ttcs-flutter-device-testing
description: Build, install, and verify only the TTCS Flutter mobile app in /home/linh/Workspace/ttcs on web and real Android devices, including ADB, local-backend routing, TTCS scope/API smoke tests, logs, and artifact checks. Do not use for other Flutter or Android apps.
---

# TTCS Flutter device testing

Use this skill only for the operational workflow of the TTCS mobile app in
`/home/linh/Workspace/ttcs`. It is not a general Flutter, Android, or Codex
app-testing skill. Read the project-specific runbook in
[`references/ttcs-runbook.md`](references/ttcs-runbook.md) when executing a
build, installing an APK, testing a physical device, or checking the two data
scopes.

## First read

From `/home/linh/Workspace/ttcs`, inspect these before changing behavior:

- `mobile_app/README.md`
- `docs/mobile/vuotgio-nckh-flutter.md`
- `docs/mobile/vuotgio-nckh-mobile-api-plan.md`
- `mobile_app/lib/services/api_client.dart`
- `mobile_app/lib/services/auth_repository.dart`
- `mobile_app/lib/services/statistics_repository.dart`
- `mobile_app/lib/main.dart`

Treat the repository source and current API docs as authoritative. Do not infer
that an old APK or an old chat result represents the current source.

## Non-negotiable app contract

- The UI has exactly two data scopes: `projected` (`Dự kiến`) and `official`
  (`Chính thức`). Never add a `snapshot` UI option.
- `official` Vượt Giờ requires a locked academic year and reads the snapshot
  through the statistics endpoint:
  `/v2/vuotgio/tong-hop/giang-vien-snapshot`.
- The personal summary endpoint returns a list; select the authenticated
  user's `id_User` row. Do not substitute
  `/v2/vuotgio/tong-hop/data-snapshot/:MaGV` for the summary.
- `data-snapshot/:MaGV` is only the official personal detail/SDO endpoint.
- Projected personal data uses `data-chuan/:MaGV?isDuKien=true`.
- Projected unit data uses `/tong-hop/khoa?isDuKien=true`; official unit data
  omits `isDuKien` and reads the locked snapshot.
- NCKH currently has live official statistics endpoints but no independent
  snapshot endpoint. Never label live NCKH data as snapshot unless the backend
  contract has actually changed.

## Safety and permissions

- Do not start, restart, recreate, or alter Docker/DDEV services without the
  user's explicit approval. Read-only inspection is allowed.
- Do not mutate or delete production/database snapshot data during app tests.
- A real-device claim requires `adb devices -l` to show a device. If no device
  is listed, report that device testing did not happen.
- Stop or clean up only processes and ADB routing started by this workflow;
  report any process that was already running.

## Required validation

For source changes, run the relevant checks and report exact results:

```bash
cd /home/linh/Workspace/ttcs/mobile_app
/home/linh/flutter/bin/flutter test
/home/linh/flutter/bin/flutter analyze
```

Build only after checking `mobile_app/android/local.properties` points to an
available SDK (in this environment, `/home/linh/android-sdk`) and Flutter SDK
(`/home/linh/flutter`). Verify artifact timestamps and paths after every build.

For the complete device/install/log/UI procedure, use the linked runbook rather
than improvising a destructive command sequence.

## Report honestly

Separate these results:

1. static/unit checks;
2. web build/smoke checks;
3. APK build checks;
4. physical-device checks (install, launch, UI, logcat, API behavior).

Mention known environment/business limitations, such as a year without a lock
record correctly returning `YEAR_NOT_LOCKED`. Do not call that a mobile bug or
silently fall back from `official` to `projected`.
