# TTCS Flutter app operation runbook

This is the condensed runbook derived from the TTCS mobile implementation
session on October 8, 2026 and the current repository docs. It applies only to
`/home/linh/Workspace/ttcs`; do not reuse it as a generic Flutter/Android app
runbook. It is an execution guide, not a replacement for the API/domain source.

## 1. Prepare and inspect

```bash
cd /home/linh/Workspace/ttcs
sed -n '1,240p' mobile_app/README.md
sed -n '1,220p' docs/mobile/vuotgio-nckh-mobile-api-plan.md
grep -R "API_BASE_URL\|giang-vien-snapshot\|data-snapshot" -n mobile_app/lib docs/mobile
```

Check the Flutter and Android SDK paths:

```bash
/home/linh/flutter/bin/flutter config --list
cat mobile_app/android/local.properties
/home/linh/flutter/bin/flutter doctor -v
```

If Gradle uses `/usr/lib/android-sdk` while required CMake/tools are under
`/home/linh/android-sdk`, configure Flutter and `local.properties` before
building. Do not paper over a missing SDK/license by claiming a build passed.

## 2. Test and build

```bash
cd /home/linh/Workspace/ttcs/mobile_app
/home/linh/flutter/bin/flutter pub get
/home/linh/flutter/bin/flutter test
/home/linh/flutter/bin/flutter analyze
/home/linh/flutter/bin/flutter build web --release
/home/linh/flutter/bin/flutter build apk --debug
/home/linh/flutter/bin/flutter build apk --release
```

Expected artifacts:

```text
build/web/
build/app/outputs/flutter-apk/app-debug.apk
build/app/outputs/flutter-apk/app-release.apk
```

Use `--dart-define=API_BASE_URL=...` when the target backend is not reachable
through the app's configured default. For a phone attached by USB and a local
backend on port 3000, `adb reverse` lets the app use `http://localhost:3000`.
For LAN testing, use the host's reachable LAN address, e.g.
`http://192.168.1.131:3000`; do not assume that address is stable.

## 3. ADB lifecycle and install

Reset/check ADB when a device was previously connected but disappeared:

```bash
adb kill-server
adb start-server
adb devices -l
```

Stop if the output has no device. Do not claim a device test occurred.

Normal install:

```bash
adb install -r build/app/outputs/flutter-apk/app-debug.apk
```

On MIUI, `INSTALL_FAILED_USER_RESTRICTED` may cancel the direct install even
though USB debugging is connected. Use the observed fallback:

```bash
adb push build/app/outputs/flutter-apk/app-debug.apk \
  /data/local/tmp/ttcs-debug.apk
adb shell pm install -r -g /data/local/tmp/ttcs-debug.apk
```

Confirm installation:

```bash
adb shell pm list packages | grep -F com.example.mobile_app
adb shell dumpsys package com.example.mobile_app \
  | grep -E 'versionCode|versionName|lastUpdateTime'
```

The current artifact still uses package `com.example.mobile_app`; it is not a
production Play Store identity merely because it is a release build.

## 4. Local backend routing

Do not start Docker/DDEV automatically. If an already-running local backend is
authorized for use, route the phone to it:

```bash
adb reverse tcp:3000 tcp:3000
adb reverse --list
```

Start/stop a backend only when the user explicitly requests that exact action.
After testing, remove only the route created here:

```bash
adb reverse --remove tcp:3000
```

## 5. Launch, capture, and inspect

```bash
adb shell am force-stop com.example.mobile_app
adb shell monkey -p com.example.mobile_app \
  -c android.intent.category.LAUNCHER 1
sleep 3
adb logcat -c
adb exec-out screencap -p > /tmp/ttcs-mobile.png
adb shell uiautomator dump /sdcard/window.xml
adb pull /sdcard/window.xml /tmp/ttcs-window.xml
adb logcat -d -v brief '*:S' AndroidRuntime:E flutter:V \
  com.example.mobile_app:V
```

Look for `FATAL EXCEPTION`, Dart `Unhandled Exception`, `RenderFlex overflow`,
`SocketException`, Dio failures, and HTTP `401`, `403`, `404`, `423`, or `500`.
Use `screencap`/`view_image` and UI XML to verify what is actually rendered,
not just what the code appears to promise.

## 6. Device smoke flow

1. Launch/login and verify the signed-in user identity.
2. Confirm the personal scope control contains only `Dự kiến` and `Chính thức`.
3. Select a year and verify projected dashboard data loads.
4. Select `Chính thức` and observe the request/log path. It must use
   `tong-hop/giang-vien-snapshot` for the summary.
5. If the year is not locked, verify the visible
   `YEAR_NOT_LOCKED`/“Chính thức (Snapshot) chưa khả dụng” state and verify
   that projected data is not left displayed as if it were official.
6. Open personal Vượt Giờ detail and NCKH detail; verify read-only records and
   no sensitive raw fields rendered.
7. Open the unit tab (when the account has permission), verify the unit/year/
   scope selectors, backend aggregates, and chart navigation.
8. Select unit `Chính thức`; it must show the lock-required state when no lock
   exists, not silently use projected data.
9. Capture a final screenshot and filtered logcat; record device serial,
   package, artifact path, and exact result.

For UI automation, `uiautomator dump` content descriptions observed in the app
include `Phạm vi dữ liệu`, `Dự kiến`, `Chính thức`, `Xem chi tiết`, and the
summary KPI labels. Prefer these stable semantics over coordinate-only claims;
coordinates are device-specific.

## 7. Backend/API smoke checks

When a local backend is already running, test read-only contracts without
mutating data:

```bash
curl -i http://127.0.0.1:3000/
curl -i -H 'Authorization: Bearer invalid' http://127.0.0.1:3000/api/...
```

With an authorized token/fixture, verify:

- invalid JWT → `401`;
- another lecturer's `MaGV` → `403 MOBILE_SCOPE_FORBIDDEN`;
- ordinary lecturer snapshot list contains only their own `id_User` row;
- faculty user is limited to their own faculty/department;
- privileged roles retain the explicitly documented wider scope;
- an unlocked year → `423`/`YEAR_NOT_LOCKED` or the backend's documented lock
  error.

Never paste real access tokens into logs or commit them.

## 8. API source contract used by the app

| App operation | Endpoint | Source rule |
|---|---|---|
| Personal projected summary | `/v2/vuotgio/tong-hop/data-chuan/:MaGV` | `isDuKien=true` |
| Personal official summary | `/v2/vuotgio/tong-hop/giang-vien-snapshot` | statistics list; select own row; locked year |
| Personal official detail | `/v2/vuotgio/tong-hop/data-snapshot/:MaGV` | SDO detail only |
| Unit projected | `/v2/vuotgio/tong-hop/khoa` | explicit `isDuKien=true` |
| Unit official | `/v2/vuotgio/tong-hop/khoa` | omit `isDuKien`; snapshot; locked year |
| NCKH projected | `/v3/nckh/stats/preview/*` | preview/live |
| NCKH official | `/v3/nckh/stats/*` | approved official live until a true NCKH snapshot exists |

## 9. Cleanup and final report

```bash
adb reverse --remove tcp:3000
adb devices -l
```

Do not stop a backend process unless this workflow started it; if it did, stop
it and say so. Report separately:

- Flutter test/analyze;
- web build/smoke;
- APK debug/release build;
- ADB installation result;
- device UI/API/logcat result;
- known limitations (for example, no locked snapshot for the selected year);
- APK package/signing limitations.
