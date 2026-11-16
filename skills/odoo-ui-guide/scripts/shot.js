// Copy into the Playwright MCP output root, then load once per browser session with browser_run_code_unsafe({filename}).
// Installs page.context().__guideShot(page, outPath, marks, opts) which draws numbered red boxes
// over the given elements, takes a viewport screenshot, then removes the overlay.
//
// marks: [{ target, label, pad }]
//   target: CSS / Playwright selector string ("text=Lưu", "button:has-text('Xác nhận')", "div[name=state]")
//           or a function (page) => Locator for role/label based lookups.
//   label:  text of the red tag, conventionally "1 Bấm Xác nhận" (number first).
//   pad:    extra pixels around the element (default 4).
// opts: { tag: "above" | "below" | "right" | "inside", fullPage: false }
// Returns { path, marks: [{label, found, box}] } so missing targets are visible to the caller.
async (page) => {
  const ctx = page.context();
  ctx.__guideShot = async (pg, outPath, marks = [], opts = {}) => {
    const results = [];
    const boxes = [];
    for (const mark of marks) {
      const locator = typeof mark.target === "function" ? mark.target(pg) : pg.locator(mark.target);
      let box = null;
      try {
        const first = locator.first();
        if (await first.isVisible({ timeout: 2000 })) {
          await first.scrollIntoViewIfNeeded({ timeout: 2000 }).catch(() => {});
          box = await first.boundingBox();
        }
      } catch (e) {
        box = null;
      }
      results.push({ label: mark.label, found: !!box, box });
      if (box) boxes.push({ ...box, label: mark.label, pad: mark.pad ?? 4, tag: mark.tag || opts.tag || "above" });
    }
    await pg.evaluate((items) => {
      const layer = document.createElement("div");
      layer.id = "__guide_overlay";
      Object.assign(layer.style, { position: "fixed", inset: "0", pointerEvents: "none", zIndex: "2147483647" });
      for (const it of items) {
        const frame = document.createElement("div");
        Object.assign(frame.style, {
          position: "fixed",
          left: `${it.x - it.pad}px`,
          top: `${it.y - it.pad}px`,
          width: `${it.width + it.pad * 2}px`,
          height: `${it.height + it.pad * 2}px`,
          border: "2px solid #e53935",
          borderRadius: "6px",
          boxSizing: "border-box",
        });
        layer.appendChild(frame);
        if (!it.label) continue;
        const tag = document.createElement("div");
        tag.textContent = it.label;
        Object.assign(tag.style, {
          position: "fixed",
          background: "#e53935",
          color: "#fff",
          font: "bold 11px/1.35 Arial, sans-serif",
          padding: "1px 6px",
          borderRadius: "3px",
          whiteSpace: "nowrap",
        });
        layer.appendChild(tag);
        const tagH = tag.offsetHeight;
        const tagW = tag.offsetWidth;
        let left = it.x - it.pad;
        let top = it.y - it.pad - tagH - 1;
        if (it.tag === "right") {
          left = it.x + it.width + it.pad + 4;
          top = it.y + (it.height - tagH) / 2;
          if (left + tagW > window.innerWidth - 2) {
            left = it.x + it.width + it.pad - tagW;
            top = it.y - it.pad - tagH - 1;
          }
        } else if (it.tag === "below" || top < 0) {
          top = it.y + it.height + it.pad + 1;
        } else if (it.tag === "inside") {
          top = it.y - it.pad + 2;
          left = it.x - it.pad + 2;
        }
        left = Math.max(0, Math.min(left, window.innerWidth - tagW - 2));
        tag.style.left = `${left}px`;
        tag.style.top = `${top}px`;
      }
      document.body.appendChild(layer);
    }, boxes);
    try {
      await pg.screenshot({ path: outPath, fullPage: !!opts.fullPage });
    } finally {
      await pg.evaluate(() => document.getElementById("__guide_overlay")?.remove());
    }
    return { path: outPath, marks: results.map(({ label, found }) => ({ label, found })) };
  };
  // Log in as a given user; handles Odoo 17/18 "Choose a user" screen. baseUrl like http://localhost:8069
  ctx.__guideLogin = async (pg, baseUrl, db, login, password) => {
    await pg.goto(`${baseUrl}/web/session/logout?redirect=/web/login`).catch(() => {});
    await pg.goto(`${baseUrl}/web/login${db ? `?db=${encodeURIComponent(db)}` : ""}`);
    const another = pg.getByText(/Use another user|Sử dụng người dùng khác/).first();
    if (!(await pg.locator("#login").isVisible().catch(() => false)) && (await another.isVisible().catch(() => false))) {
      await another.click();
    }
    await pg.locator("#login").fill(login);
    await pg.locator("#password").fill(password);
    await pg.locator("#password").press("Enter");
    await pg.waitForURL((url) => !url.pathname.startsWith("/web/login"), { timeout: 20000 });
    return pg.url();
  };
  return "guideShot installed";
}
