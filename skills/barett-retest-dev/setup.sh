#!/bin/bash
# Render the Playwright prelude with the live CDP endpoint of the user's Chrome.
set -e
PORT_FILE="$HOME/.config/google-chrome/DevToolsActivePort"
OUT_DIR="$HOME/.cache/playwright-mcp-output/cc"
[ -f "$PORT_FILE" ] || { echo "NO_DEVTOOLS_PORT: bật remote debugging ở chrome://inspect/#remote-debugging"; exit 1; }
WS="ws://localhost:$(sed -n 1p "$PORT_FILE")$(sed -n 2p "$PORT_FILE")"
curl -s --max-time 2 "http://localhost:$(sed -n 1p "$PORT_FILE")/json/version" >/dev/null 2>&1 || echo "WARN: port không trả /json/version (bình thường với chrome://inspect mode), vẫn thử connect"
[ -n "$BARETT_CC_PASSWORD" ] || { echo "NO_CC_PASSWORD: đặt biến môi trường BARETT_CC_PASSWORD (mật khẩu chung của các user cc_*)"; exit 1; }
mkdir -p "$OUT_DIR"
WS="$WS" python3 -I - "$(dirname "$0")/prelude.template.js" "$OUT_DIR/prelude.js" <<'PY'
import json, os, sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
s = s.replace("__WS__", os.environ["WS"]).replace("__CC_PASSWORD__", json.dumps(os.environ["BARETT_CC_PASSWORD"]))
open(dst, "w", encoding="utf-8").write(s)
PY
echo "$OUT_DIR/prelude.js  ->  $WS"
