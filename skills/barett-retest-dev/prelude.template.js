async (page) => {
const s = page.context();
const BASE = 'https://dev-barett.vdx.vn';
const WS = '__WS__';
const CC_PASSWORD = __CC_PASSWORD__;
if (!s.__cdp || !s.__cdp.isConnected()) s.__cdp = await s.browser().browserType().connectOverCDP(WS, {timeout: 60000});
s.__roles = s.__roles || {};
const ctx0 = s.__cdp.contexts()[0];
if (!s.__tab || s.__tab.isClosed()) {
  s.__tab = ctx0.pages().find(p => p.__ccTest) || await ctx0.newPage();
  s.__tab.__ccTest = true;
}
const t = s.__tab;
const idle = async (p) => { await p.waitForLoadState('networkidle').catch(()=>{}); await p.waitForTimeout(400); };
const h = {};
h.go = async (p, path) => {
  for (let k = 0; k < 4; k++) {
    await p.goto(BASE + path).catch(()=>{}); await idle(p);
    await p.locator('.o_action_manager, .o_offline').first().waitFor({timeout: 20000}).catch(()=>{}); await idle(p);
    if (!(await p.getByText('Bạn đang offline').count())) return;
    await p.waitForTimeout(3000);
  }
  throw new Error('offline after retries: ' + path);
};
h.headerButtons = async (p) => (await p.locator('.o_form_statusbar .o_statusbar_buttons button:visible').allInnerTexts()).map(x => x.trim()).filter(Boolean);
h.cpButtons = async (p) => (await p.locator('.o_control_panel button:visible').allInnerTexts()).map(x => x.trim()).filter(Boolean);
h.status = async (p) => (await p.locator('.o_statusbar_status button.o_arrow_button_current').innerText().catch(()=>null));
h.errors = async (p) => {
  const out = [];
  for (const sel of ['.o_notification_body', '.modal-dialog .modal-body']) for (const e of await p.locator(sel + ':visible').all()) out.push((await e.innerText()).trim().slice(0, 500));
  return out;
};
h.save = async (p) => { const b = p.locator('.o_form_button_save:visible'); if (await b.count()) { await b.first().click(); await idle(p); } };
h.discard = async (p) => { const b = p.locator('.o_form_button_cancel:visible'); if (await b.count()) { await b.first().click(); await idle(p); } };
h.closeDialogs = async (p) => {
  for (let k = 0; k < 4; k++) {
    const m = p.locator('.modal:visible').last();
    if (!(await m.count())) break;
    const stay = m.locator('footer button').filter({hasText: /^(Ở đây|Ok|OK|Đóng|Close)$/});
    if (await stay.count()) await stay.first().click();
    else if (await m.locator('.btn-close').count()) await m.locator('.btn-close').first().click();
    else break;
    await idle(p);
  }
  for (const b of await p.locator('.o_notification_close:visible').all()) await b.click().catch(()=>{});
};
h.errDetail = async (p) => {
  const m = p.locator('.modal:visible').last();
  if (!(await m.count())) return null;
  await m.locator('button, a').filter({hasText: /thông tin kỹ thuật/i}).first().click().catch(()=>{});
  await p.waitForTimeout(500);
  const lines = (await m.innerText()).split('\n').filter(Boolean);
  return lines.slice(-12).join('\n');
};
h.pick = async (p, name, typed, scope, exact) => {
  const root = scope ? p.locator(scope) : p.locator('.o_form_view').first();
  const i = root.locator(`.o_field_widget[name="${name}"] input`).first();
  await i.click(); await i.fill(''); await i.pressSequentially(typed, {delay: 20}); await p.waitForTimeout(1500);
  const items = p.locator('.o-autocomplete--dropdown-item');
  const texts = await items.allInnerTexts();
  const ok = texts.findIndex(x => !/^Tạo|Tìm kiếm thêm|Search More|^Create|Bắt đầu nhập/.test(x.trim()) && (!exact || x.includes(typed)));
  if (ok < 0) { await i.press('Escape'); throw new Error(`no option for ${name} "${typed}": ${JSON.stringify(texts)}`); }
  const picked = texts[ok].trim(); await items.nth(ok).click(); await idle(p); return picked;
};
h.val = async (p, name) => {
  const w = p.locator(`.o_form_view .o_field_widget[name="${name}"]`).first();
  if (!(await w.count())) return null;
  const inp = w.locator('input:not([type=checkbox]), textarea, select');
  if (await inp.count()) return await inp.first().inputValue();
  return (await w.innerText()).trim();
};
h.readonly = async (p, name) => p.locator(`.o_form_view .o_field_widget[name="${name}"]`).first().evaluate(e => e.classList.contains('o_readonly_modifier')).catch(()=>null);
h.as = async (login) => {
  const r = s.__roles[login];
  if (r && !r.page.isClosed()) return r.page;
  if (r) {
    try {
      const p = await r.ctx.newPage(); r.page = p;
      await h.go(p, '/odoo');
      if (!p.url().includes('/web/login')) return p;
    } catch (e) {}
  }
  const ctx = await s.browser().newContext({viewport: {width: 1440, height: 900}});
  const p = await ctx.newPage();
  await p.goto(BASE + '/web/login');
  await p.fill('input[name="login"]', login); await p.fill('input[name="password"]', CC_PASSWORD);
  await Promise.all([p.waitForURL(/\/odoo/, {timeout: 30000}), p.click('form button[type="submit"]')]);
  await idle(p);
  s.__roles[login] = {ctx, page: p};
  return p;
};
h.click = async (p, text, scope = '.o_form_view .o_form_statusbar, .modal:visible') => { await p.locator(scope).locator('button:visible').filter({hasText: text}).first().click(); await idle(p); };
h.idle = idle;
h.invalid = async (p) => p.locator(".o_field_invalid").evaluateAll(es => es.map(e => e.getAttribute("name")));
h.prNew = async (p, typed, qty) => {
  await h.go(p, '/odoo/action-529/new');
  await p.locator('.o_field_widget[name="line_ids"] a').filter({hasText: 'Thêm một dòng'}).first().click(); await idle(p);
  const r = '.o_field_widget[name="line_ids"] .o_selected_row';
  const product = await h.pick(p, 'product_id', typed, r);
  const q = p.locator(`${r} [name="product_qty"] input`); await q.fill(String(qty)); await q.press('Tab'); await idle(p);
  await h.save(p); await p.waitForURL(/action-529\/\d+/, {timeout: 15000}).catch(()=>{});
  return {id: (p.url().match(/action-529\/(\d+)/) || [])[1], name: await h.val(p, 'name'), product, assigned: await h.val(p, 'assigned_to'), errs: await h.errors(p)};
};
h.alertBtns = async (p) => (await p.locator('.o_form_view .alert:visible button:visible').allInnerTexts()).map(x => x.trim());
h.prView = async (login, id) => {
  const q = await h.as(login);
  await h.go(q, `/odoo/action-529/${id}`);
  return {
    status: await h.status(q), header: await h.headerButtons(q), alert: await h.alertBtns(q),
    addLine: await q.locator('.o_field_widget[name="line_ids"] a:visible').filter({hasText: 'Thêm một dòng'}).count(),
    descRO: await h.readonly(q, 'description'), dateRO: await h.readonly(q, 'date_start'),
    gear: await q.locator('.o_cp_action_menus .dropdown-toggle:visible').count(),
    err: await h.errors(q),
  };
};
h.gearItems = async (q) => { const g = q.locator('.o_cp_action_menus .dropdown-toggle:visible').first(); if (!(await g.count())) return null; await g.click(); await idle(q); const items = (await q.locator('.o-dropdown--menu .dropdown-item:visible').allInnerTexts()).map(x => x.trim()); await q.keyboard.press('Escape'); return items; };
s.__h = h; h.s = s; h.t = t; h.BASE = BASE;
return "prelude ok";
}
