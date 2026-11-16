# Barett Chrome DevTools MCP connection

Use this procedure before opening or acting in Odoo. It is part of the
browser-first acceptance workflow and applies to one test run at a time.

## Required connection shape

- Start exactly one `chrome-devtools-mcp` bridge for the run.
- Use the bridge's `--isolated` mode so it creates a fresh temporary
  `--user-data-dir`; do not attach to the user's normal Chrome profile.
- Keep the same bridge, browser process, and temporary profile for the entire
  run. Do not start a second bridge for the same run.
- Keep Chrome headful for acceptance work unless the criterion explicitly
  permits another mode. Record the generated temporary profile path and the
  bridge log path in the run notes, but never record cookies, tokens, or
  credentials.

## Start the bridge

Run the MCP server as a long-lived stdio process in a session that remains
available for the test:

```bash
npx -y chrome-devtools-mcp@latest \
  --isolated \
  --no-usage-statistics \
  --logFile /tmp/barett-chrome-devtools-mcp-<run-id>.log
```

The command should create a path similar to
`/tmp/puppeteer_dev_chrome_profile-<random>`. Do not replace `--isolated` with
`--autoConnect`, the user's normal `--user-data-dir`, or a fixed stale profile.
Those modes can attach the wrong browser or reuse another test's state.

Before starting, preserve the current graphical environment (`DISPLAY` and,
when present, `XAUTHORITY`). If the bridge reports a missing X server or stale
Xauthority, inspect the environment and bridge log, then restart only this
MCP session with the current values. Do not launch Docker, restart Odoo, or
patch a `DevToolsActivePort` file.

## Verify the MCP handshake

Do not treat a running `npx` process as a successful connection. Complete the
MCP lifecycle through the MCP client:

1. Send `initialize` with the client's protocol version and client info.
2. Wait for the response naming the server `chrome_devtools`.
3. Send `notifications/initialized`.
4. Call `tools/list` and confirm browser tools such as `list_pages`,
   `new_page`, `navigate_page`, `take_snapshot`, `click`, `fill`, and
   `press_key` are available.
5. Call read-only `list_pages`; a fresh connection normally reports
   `about:blank`.

If the MCP host requests `roots/list`, answer it promptly with the permitted
workspace roots (an empty list is sufficient when no filesystem roots are
needed). A timeout at this stage is a failed handshake, not a connected run.

## Snapshot preflight and one-session retry

After the handshake, prove that the browser can return the accessibility tree
before starting the acceptance workflow:

1. Call read-only `list_pages`; the isolated browser should expose
   `about:blank`.
2. Call `take_snapshot` on that page. Continue only after it returns a
   `RootWebArea` snapshot.
3. Navigate that same page to `http://localhost:8069/odoo` and call
   `take_snapshot` again. The login snapshot should expose `Email`, `Password`,
   and `Log in` (or their rendered equivalent).
4. Record the snapshot result, temporary profile path, and bridge log path in
   the run record. This preflight is a connection check, not acceptance
   evidence for the issue under test.

If `take_snapshot` times out or the bridge stops responding:

- Capture the exact error and bridge log path.
- Stop only the affected MCP session and start one replacement bridge with
  the current `DISPLAY`/`XAUTHORITY`, a new `--isolated` temporary profile,
  and a new log path. Do not run two bridges for the same run or reuse the
  stuck profile.
- Repeat the three preflight steps once. If the replacement returns both
  snapshots, continue the test with that replacement connection and record
  the retry. If it fails again, classify the run as `BLOCKED`.
- Do not substitute direct CDP, RPC/JSON-RPC, direct HTTP, Android MCP, or the
  user's existing Chrome profile for acceptance actions unless the user
  explicitly authorizes that alternate path and the run records the deviation.

## Use and record the connection

- Use only this MCP/browser profile for navigation, snapshots, DOM/a11y
  inspection, clicks, fills, keyboard input, and exploratory dialog closure.
- Open the requested Odoo or IssueList page with `new_page` only after the
  handshake and after checking the workflow archive.
- Record the bridge/profile evidence in the immutable run record. The
  `chrome_profile` field should identify it as a fresh, isolated, non-headless
  MCP profile.
- If the bridge cannot complete the handshake, record the exact error and
  classify the test `BLOCKED`; do not substitute Android MCP, RPC/JSON-RPC,
  direct HTTP requests, or the user's existing Chrome session for acceptance
  actions.

## End of run

Close only the pages created for the run when the workflow requires it. Stop
the bridge/session after the run unless the surrounding test orchestration
explicitly keeps it for the same run; the temporary profile is disposable and
must not be reused by a later run.
