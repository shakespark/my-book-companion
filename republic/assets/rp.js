// 理想国 · 对照导读：共享脚本。注入顶栏（含全文的「中文 / 英文 / 对照」开关）、页头（这一卷的几页、页内跳转、接着读）、页末导航、页脚（备案号、全文的底本和许可）；
// 接管全文块（tools/gen_text.py 生成的 article.fulltext）：显示模式、点开的小注、记下读到哪一节；本地笔记；首页目录和进度；全书回顾（recap.html）。
// 照 Thinking in Systems 导读的 ts.js 改：去掉了分节地图、英文词条和词本、译本勘误、最短读法、四个汇总页、模拟器画图。
// 页 id 是 RP_PAGES 里的 id（01a…），另有主编页 00「开读之前」（RP_EXTRA）。节号是斯特方码（327a），全文里每节的锚点是 #s327a。
// localStorage 键一律带 rp- 前缀（全站各教程同一个域名）：rp-done-页、rp-pos-页（读到哪一节）、rp-mode-wide / rp-mode-narrow（全文显示模式，宽屏和手机各记各的）、rp-note-页-…、rp-theme。
(() => {
  const BOOKS = window.RP_BOOKS || [], PAGES = window.RP_PAGES || [], EXTRA = window.RP_EXTRA || {};
  const READY = new Set(window.RP_READY || []);
  const ROOT = document.currentScript.src.replace(/assets\/rp\.js.*$/, "");
  const CPM = 400; // 读者每分钟读多少个汉字（对话体全文，比导读慢一点）
  const WPM = 200; // 只有英文时：每分钟多少个英文词
  const MODES = [["zh", "中文"], ["en", "英文"], ["both", "对照"]];
  const LS = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { v == null || v === "" ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch {} },
  };
  const h = (tag, attrs = {}, ...kids) => {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) k === "class" ? (el.className = v) : k.startsWith("on") ? (el[k] = v) : el.setAttribute(k, v);
    el.append(...kids.filter((x) => x != null));
    return el;
  };
  const fmtT = (min) => { const m = Math.max(5, Math.round(min / 5) * 5); return m >= 60 ? `约 ${(m / 60).toFixed(1).replace(/\.0$/, "")} 小时` : `约 ${m} 分钟`; };
  const minutes = (p) => (p.zw ? p.zw / CPM : (p.w || 0) / WPM);
  const extra = (id) => Object.assign({ id, book: 0, from: "", to: "" }, EXTRA[id] || {});
  const INTRO = extra("00");
  const ALL = [INTRO, ...PAGES];
  const find = (id) => ALL.find((p) => p.id === id);
  const bookOf = (p) => BOOKS.find((b) => b.n === p.book);
  const sibsOf = (p) => PAGES.filter((x) => x.book === p.book);
  const href = (id) => `${ROOT}chapters/${id}.html`;
  const label = (p) => {
    if (!p.book) return p.t || "开读之前";
    const b = bookOf(p), s = sibsOf(p);
    return (b ? b.zh : `第 ${p.book} 卷`) + (s.length > 1 ? `（${s.indexOf(p) + 1}/${s.length}）` : "");
  };
  const title = (p) => (p.book ? `${label(p)} · ${p.t || `${p.from}–${p.to}`}` : label(p));
  const isDone = (id) => LS.get(`rp-done-${id}`) === "1";
  const pageId = () => document.body.dataset.page || null;
  const art = () => document.querySelector("article.fulltext");

  const saved = LS.get("rp-theme");
  if (saved) document.documentElement.dataset.theme = saved;
  function themeBtn() {
    return h("button", { class: "btn", "aria-label": "切换深色/浅色", onclick() {
      const dark = document.documentElement.dataset.theme ? document.documentElement.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
      const next = dark ? "light" : "dark";
      document.documentElement.dataset.theme = next; LS.set("rp-theme", next);
    } }, "深/浅");
  }

  // ---------- 全文的显示模式：宽屏默认对照，手机默认只看中文；读者选过就照他选的（宽屏、手机各记各的） ----------
  const WIDE = matchMedia("(min-width: 1000px)");
  const modeKey = () => `rp-mode-${WIDE.matches ? "wide" : "narrow"}`;
  const hasZh = () => art()?.dataset.zh === "1";
  function curMode() {
    if (!hasZh()) return "en";
    const m = LS.get(modeKey());
    return MODES.some(([k]) => k === m) ? m : WIDE.matches ? "both" : "zh";
  }
  function topSection() {
    for (const s of document.querySelectorAll(".st")) if (s.getBoundingClientRect().bottom > 70) return s;
    return null;
  }
  function applyMode(m, save) {
    const a = art(); if (!a) return;
    const keep = topSection(), y0 = keep && keep.getBoundingClientRect().top;   // 换模式后版面变长变短，让眼前这一节留在原处
    a.classList.remove("m-zh", "m-en", "m-both"); a.classList.add(`m-${m}`);
    if (save) LS.set(modeKey(), m);
    for (const b of document.querySelectorAll(".modesw button")) b.setAttribute("aria-pressed", String(b.dataset.mode === m));
    if (save && keep && keep.getBoundingClientRect().top < window.innerHeight) window.scrollBy(0, keep.getBoundingClientRect().top - y0);
  }
  const modeSwitch = () => h("div", { class: "modesw", role: "group", "aria-label": "全文显示：中文、英文或对照" },
    ...MODES.map(([k, lab]) => h("button", { class: "btn", type: "button", "data-mode": k, "aria-pressed": "false", onclick() { applyMode(k, true); } }, lab)));

  function wireText() {
    const a = art(); if (!a) return;
    const id = pageId();
    const bar = a.querySelector(".ft-bar");
    if (bar && hasZh()) bar.append(h("span", {}, "显示："), modeSwitch(), h("span", {}, WIDE.matches ? "（宽屏默认对照）" : "（手机默认只看中文，英文点「英文」或「对照」）"));
    applyMode(curMode(), false);
    WIDE.addEventListener("change", () => applyMode(curMode(), false));
    // 小注：按钮的 aria-controls 指向这一节下面的 p.fn-t；中英两边同号的按钮一起变
    a.addEventListener("click", (e) => {
      const b = e.target.closest("button.fn"); if (!b) return;
      const t = document.getElementById(b.getAttribute("aria-controls")); if (!t) return;
      t.hidden = !t.hidden;
      for (const x of a.querySelectorAll(`button.fn[aria-controls="${b.getAttribute("aria-controls")}"]`)) x.setAttribute("aria-expanded", String(!t.hidden));
    });
    // 读到哪一节：滚动停下后记下屏幕顶上那一节
    let timer = null;
    window.addEventListener("scroll", () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const s = topSection(), r = a.getBoundingClientRect();
        if (!s || r.top > 0 || r.bottom < 100) return;
        LS.set(`rp-pos-${id}`, s.id === `s${a.dataset.from}` ? null : s.id.slice(1));
      }, 400);
    }, { passive: true });
  }

  function mountChrome() {
    const id = pageId(), p = id && find(id), a = art();
    document.body.prepend(h("div", { class: "topbar" }, h("div", { class: "topbar-inner" },
      h("a", { class: "home", href: `${ROOT}index.html` }, "理想国 · 对照导读"),
      h("span", { class: "crumb" }, p ? title(p) : ""),
      a && hasZh() ? modeSwitch() : null,
      themeBtn())));
    document.body.append(h("footer", { class: "site-footer" },
      h("a", { href: "https://beian.miit.gov.cn/", target: "_blank", rel: "noopener" }, "京ICP备18057656号-1"),
      a ? h("span", { class: "credit" }, "全文：英译 Shorey、希腊文 Burnet，取自 ", h("a", { href: "https://www.perseus.tufts.edu/", rel: "noopener" }, "Perseus Digital Library"),
        "，按 CC BY-SA 4.0 使用；中文是本站新译，同样按 CC BY-SA 4.0 放出。", h("a", { href: "#ft-credit" }, "详细")) : null));
    if (!p) return;
    const main = document.querySelector("main");
    document.title = `${title(p)} · 理想国对照导读`;
    const b = p.book ? bookOf(p) : null, sibs = p.book ? sibsOf(p) : [];
    const pos = LS.get(`rp-pos-${id}`);
    const jumps = [];
    for (const x of main.querySelectorAll("h2[id]")) {
      const k = x.textContent.split("：")[0];
      if (!jumps.some((j) => j[0] === k)) jumps.push([k, x.id]);
    }
    main.prepend(h("div", { class: "chapter-head" },
      h("div", { class: "kicker" }, b ? `${b.zh}　斯特方码 ${p.from}–${p.to}` : "柏拉图《理想国》"),
      h("h1", {}, p.book ? `${label(p)}　${p.t || `${p.from}–${p.to}`}` : p.t || label(p)),
      p.book ? h("div", { class: "badges" },
        h("span", { class: "badge" }, `全文 ${p.n} 节`),
        h("span", { class: "badge" }, p.zw ? `中文约 ${Math.round(p.zw / 100) * 100} 字，${fmtT(minutes(p))}` : `英文约 ${Math.round((p.w || 0) / 100) * 100} 词，中文在译`),
        pos && a && document.getElementById(`s${pos}`) ? h("span", { class: "badge resume" }, h("a", { href: `#s${pos}` }, `上次读到 ${pos}，接着读 →`)) : null) : null,
      sibs.length > 1 ? h("ol", { class: "pageband", "aria-label": `${b ? b.zh : ""}的几页` }, ...sibs.map((x) => h("li", { class: x === p ? "here" : "" },
        x !== p && READY.has(x.id) ? h("a", { href: href(x.id) }, `${x.from}–${x.to}${x.t ? " " + x.t : ""}`) : `${x.from}–${x.to}${x.t ? " " + x.t : ""}`))) : null,
      jumps.length > 1 ? h("nav", { class: "pagenav", "aria-label": "跳到" }, ...jumps.map(([k, hid]) => h("a", { href: `#${hid}` }, k))) : null));
    const order = ALL.map((x) => x.id);
    const i = order.indexOf(id), prev = order[i - 1], next = order[i + 1];
    const done = h("button", { class: "btn" });
    const paint = () => { done.textContent = isDone(id) ? "✓ 已读完这一页" : "标记：这一页读完了"; done.setAttribute("aria-pressed", isDone(id)); };
    done.onclick = () => { LS.set(`rp-done-${id}`, isDone(id) ? null : "1"); paint(); };
    paint();
    main.append(h("div", { class: "chapter-end" }, done, h("div", { class: "nav" },
      prev && READY.has(prev) ? h("a", { class: "btn", href: href(prev) }, `← ${label(find(prev))}`) : null,
      h("a", { class: "btn", href: `${ROOT}index.html` }, "目录"),
      next && READY.has(next) ? h("a", { class: "btn primary", href: href(next) }, `${label(find(next))} →`) : null)));
  }

  // 本地笔记：<textarea class="note" data-key="01a-oneline">，输入即存到本机（键 rp-note-01a-oneline）
  function wireNotes() {
    for (const el of document.querySelectorAll("input.note, textarea.note")) {
      const key = `rp-note-${el.dataset.key}`;
      el.value = LS.get(key) || "";
      let tip = null;
      if (el.tagName === "TEXTAREA") { tip = h("div", { class: "note-tip" }, el.value ? "已保存在本机浏览器" : "写下来会自动保存在本机浏览器"); el.after(tip); }
      let t = null;
      el.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => { LS.set(key, el.value.trim() ? el.value : null); if (tip) tip.textContent = "已保存在本机浏览器"; }, 400); });
    }
  }

  // 首页：按卷分组的目录、进度
  function mountHome() {
    const toc = document.getElementById("toc");
    if (!toc) return;
    toc.append(item(INTRO));
    for (const b of BOOKS) {
      const ps = PAGES.filter((x) => x.book === b.n);
      if (!ps.length) continue;
      toc.append(h("li", { class: "blk" }, b.zh, h("span", { class: "te" }, `　斯特方码 ${b.from}–${b.to}`)));
      for (const p of ps) toc.append(item(p));
    }
    function item(p) {
      const ready = READY.has(p.id), pos = LS.get(`rp-pos-${p.id}`);
      return h("li", {}, h("a", Object.assign({ class: (isDone(p.id) ? "done " : "") + (ready ? "" : "todo") }, ready ? { href: href(p.id) } : {}),
        h("span", { class: "n" }, isDone(p.id) ? "✓" : p.id === "00" ? "·" : p.id.replace(/^0/, "")),
        h("span", { class: "t" }, p.book ? `${label(p)}　${p.t || "（待定）"}` : label(p), p.book ? h("span", { class: "te" }, `${p.from}–${p.to}`) : null),
        h("span", { class: "b" }, ...(!p.book ? [] : ready ? [h("span", { class: "badge" }, p.zw ? `中文约 ${Math.round(p.zw / 100) * 100} 字` : "中文在译"), h("span", { class: "badge" }, fmtT(minutes(p)))] : [h("span", { class: "badge" }, "待写")])),
        p.d || (pos && !isDone(p.id)) ? h("span", { class: "d" }, p.d || "", pos && !isDone(p.id) ? h("span", { class: "sp" }, `　读到 ${pos}`) : null) : null));
    }
    const doneN = PAGES.filter((p) => isDone(p.id)).length;
    const pr = document.getElementById("progress");
    if (pr) pr.append(h("div", { class: "progress" }, Object.assign(h("i"), { style: `width:${(100 * doneN) / (PAGES.length || 1)}%` })), h("p", { class: "lede" }, `已读完 ${doneN} / ${PAGES.length} 页`));
  }

  async function fetchPage(id) {
    try { return new DOMParser().parseFromString(await (await fetch(href(id))).text(), "text/html"); } catch { return null; }
  }
  // 全书回顾（recap.html 的 #recap）：读各个已完成页的「精彩回顾」和「本站的总体看法」，按书的顺序汇总；页内的节号链接改成链回那一页
  async function mountRecap() {
    const box = document.getElementById("recap");
    if (!box || /^H\d$/.test(box.tagName)) return;   // 章节页的「精彩回顾」标题也叫 #recap，只在 recap.html 上汇总
    let shown = 0, lastBook = -1;
    for (const p of PAGES) {
      if (!READY.has(p.id)) continue;
      const doc = await fetchPage(p.id); if (!doc) continue;
      const line = doc.querySelector(".recall-line"), items = doc.querySelector(".recall"), verdict = doc.querySelector(".verdict");
      if (!items) continue;
      if (p.book !== lastBook) { lastBook = p.book; const b = bookOf(p); box.append(h("h2", { class: "recap-part" }, b ? `${b.zh}　${b.from}–${b.to}` : `第 ${p.book} 卷`)); }
      for (const x of [line, items, verdict]) for (const a of x ? x.querySelectorAll('a[href^="#"]') : []) a.setAttribute("href", href(p.id) + a.getAttribute("href"));
      box.append(h("section", { class: "recap-ch" },
        h("h3", {}, h("a", { href: href(p.id) }, title(p))),
        line ? document.importNode(line, true) : null, document.importNode(items, true),
        verdict ? document.importNode(verdict, true) : null));
      shown++;
    }
    if (!shown) box.append(h("p", { class: "lede" }, "还没有写好的页。"));
  }

  document.addEventListener("DOMContentLoaded", () => {
    mountChrome(); wireText(); wireNotes(); mountHome(); mountRecap();
  });
  // 跨设备同步：模块在首页仓库里（/_home/sync.js），所有教程站共用。只在线上加载；本地预览要联调时设 localStorage["sync-dev"] = "1"
  // 上线前要把 rp- 加进 sync.js 的 PREFIXES 和 sync_server.py 的 KEY_RE，见 ~/tutorials-deploy/README.md。
  try { if (location.hostname === "t.miaowuao.cn" || localStorage.getItem("sync-dev")) document.head.append(Object.assign(document.createElement("script"), { src: "/_home/sync.js" })); } catch (e) {}
  window.RP = { h, LS, ROOT, href, label, isDone };
})();
