// 《国富论》导读：共享脚本。注入顶栏、页头、「在全书的哪里」、页末导航、页脚；接管分节地图的打勾和分档、本地笔记；
// 首页目录、全书最短读法（00 页的 #path）、全书回顾（recap.html）、汇总页（terms / today / zh）。照 The Selfish Gene 导读的 sg.js 改。
// 页 id 是 WN_PAGES 里的两位数（01–28），另有主编页 00「开读之前」（WN_EXTRA）。节号 §k 是这一页的第 k 节（本站分的，一页之内连续）。
// 读者主体读杨敬年译本：页头和地图里的篇幅、时间按译本汉字数算（zc），英文词数（w）只作参考。
// localStorage 键一律带 wn- 前缀（全站各教程同一个域名）：wn-done-页、wn-sec-页-节号、wn-note-页-…、wn-theme。
(() => {
  const BOOKS = window.WN_BOOKS || [], CH = window.WN_CHAPTERS || [], SECS = window.WN_SECS || {}, PAGES = window.WN_PAGES || [];
  const EXTRA = window.WN_EXTRA || {};
  const READY = new Set(window.WN_READY || []);
  const ROOT = document.currentScript.src.replace(/assets\/wn\.js.*$/, "");
  const CPM = 300; // 杨译每分钟读多少字：18 世纪的论证文字译成中文，比一般读物慢
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
  const extra = (id) => Object.assign({ id, kind: "extra", chs: [], need: [] }, EXTRA[id] || {});
  const INTRO = extra("00");
  const ALL = [INTRO, ...PAGES];
  const find = (id) => ALL.find((p) => p.id === id);
  const chOf = (key) => CH.find((c) => c.key === key);
  const secsOf = (p) => SECS[p.id] || [];
  const sum = (xs, f) => xs.reduce((a, x) => a + (f(x) || 0), 0);
  const zcOf = (p) => sum(secsOf(p), (s) => s.zc);
  const wOf = (p) => sum(secsOf(p), (s) => s.w);
  const mins = (zc) => Math.max(1, Math.round(zc / CPM / 5) * 5 || Math.round(zc / CPM));
  const round = (n, r) => Math.round(n / r) * r;
  const fmtZ = (zc) => (zc >= 10000 ? `${(zc / 10000).toFixed(1)} 万字` : `${round(zc, 100)} 字`);
  const fmtT = (zc) => { const m = mins(zc); return m >= 60 ? `约 ${(m / 60).toFixed(1).replace(/\.0$/, "")} 小时` : `约 ${m} 分钟`; };
  const TIERS = ["先读", "有空", "可跳过"];
  const href = (id) => `${ROOT}chapters/${id}.html`;
  const bookOf = (p) => (p.chs.length ? +p.chs[p.chs.length - 1].split("-")[0] : -1);
  const chLabel = (p) => {
    const cs = p.chs.map(chOf).filter(Boolean);
    if (!cs.length) return "";
    const real = cs.filter((c) => c.n > 0), bk = BOOKS.find((b) => b.n === bookOf(p));
    const intro = cs.some((c) => c.n === 0) ? (cs[0].book === 0 ? "全书引言" : "引言") : "";
    const nums = real.map((c) => c.n), rng = nums.length > 1 ? `第 ${nums[0]}–${nums[nums.length - 1]} 章` : nums.length ? `第 ${nums[0]} 章` : "";
    return [bk ? bk.t : "", [intro, rng].filter(Boolean).join("、"), p.part || ""].filter(Boolean).join(" · ");
  };
  const label = (p) => (p.id === "00" ? "开读之前" : `${p.id}　${chLabel(p)}`);
  const title = (p) => (p.id === "00" ? `开读之前 · ${p.t || ""}` : `${chLabel(p)} · ${p.t || ""}`);
  const isDone = (id) => LS.get(`wn-done-${id}`) === "1";
  const secDone = (id, k) => LS.get(`wn-sec-${id}-${k}`) === "1";
  const pageId = () => document.body.dataset.page || null;

  const saved = LS.get("wn-theme");
  if (saved) document.documentElement.dataset.theme = saved;
  function themeBtn() {
    return h("button", { class: "btn", "aria-label": "切换深色/浅色", onclick() {
      const dark = document.documentElement.dataset.theme ? document.documentElement.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
      const next = dark ? "light" : "dark";
      document.documentElement.dataset.theme = next; LS.set("wn-theme", next);
    } }, "深/浅");
  }
  const tierTag = (t) => h("span", { class: `tier t-${t}` }, t);

  function mountChrome() {
    const id = pageId(), p = id && find(id);
    document.body.prepend(h("div", { class: "topbar" }, h("div", { class: "topbar-inner" },
      h("a", { class: "home", href: `${ROOT}index.html` }, "国富论 · 导读"),
      h("span", { class: "crumb" }, p ? (p.id === "00" ? "开读之前" : `${p.id} ${p.t || ""}`) : ""),
      themeBtn())));
    document.body.append(h("footer", { class: "site-footer" },
      h("a", { href: "https://beian.miit.gov.cn/", target: "_blank", rel: "noopener" }, "京ICP备18057656号-1")));
    if (!p) return;
    const main = document.querySelector("main");
    document.title = `${p.t || label(p)} · 国富论导读`;
    if (p.id !== "00") {
      const cs = p.chs.map(chOf).filter(Boolean), secs = secsOf(p), core = secs.filter((s) => s.tier === "先读");
      main.prepend(h("div", { class: "chapter-head" },
        h("div", { class: "kicker" }, chLabel(p)),
        h("h1", {}, p.t || label(p)),
        h("ul", { class: "chnames" }, ...cs.map((c) => h("li", {}, h("span", { class: "zh" }, c.n ? `第 ${c.n} 章 ${c.zh}` : c.zh), h("span", { class: "en" }, c.en)))),
        h("div", { class: "badges" },
          h("span", { class: `badge k-${p.kind}` }, p.kind === "core" ? "核心页：讲透" : "轻量页：讲个大概"),
          h("span", { class: "badge" }, `译本约 ${fmtZ(zcOf(p))}，${fmtT(zcOf(p))}`),
          core.length && core.length < secs.length ? h("span", { class: "badge t-先读" }, `只读先读的 ${core.length} 节：${fmtT(sum(core, (s) => s.zc))}`) : null,
          !core.length ? h("span", { class: "badge t-可跳过" }, "这一页没有先读的节") : null,
          p.need.includes("sim") ? h("span", { class: "badge b-sim" }, "有模拟器") : null)));
    }
    const order = ALL.map((x) => x.id);
    const i = order.indexOf(id), prev = order[i - 1], next = order[i + 1];
    const done = h("button", { class: "btn" });
    const paint = () => { done.textContent = isDone(id) ? "✓ 已读完这一页" : "标记：这一页读完了"; done.setAttribute("aria-pressed", isDone(id)); };
    done.onclick = () => { LS.set(`wn-done-${id}`, isDone(id) ? null : "1"); paint(); };
    paint();
    const short = (x) => (x.id === "00" ? "开读之前" : `${x.id} ${x.t || ""}`);
    main.append(h("div", { class: "chapter-end" }, done, h("div", { class: "nav" },
      prev && READY.has(prev) ? h("a", { class: "btn", href: href(prev) }, `← ${short(find(prev))}`) : null,
      h("a", { class: "btn", href: `${ROOT}index.html` }, "目录"),
      next && READY.has(next) ? h("a", { class: "btn primary", href: href(next) }, `${short(find(next))} →`) : null)));
  }

  // 「读之前」里的 <div class="linehere"></div>：全书五卷一条带子，这一页所在的卷高亮；下面列这一页每节的档和作用
  function mountLine() {
    const box = document.querySelector(".linehere"), id = pageId(), p = id && find(id);
    if (!box || !p) return;
    const b = bookOf(p);
    const band = h("ol", { class: "lineband" }, ...BOOKS.filter((x) => x.n > 0).map((x) => h("li", { class: x.n === b ? "here" : "" }, h("b", {}, x.t), h("span", {}, x.s))));
    const list = h("ul", { class: "linesecs" }, ...secsOf(p).map((s) => h("li", {}, h("span", { class: "k" }, `§${s.k}`), tierTag(s.tier), s.line || s.t)));
    box.append(h("p", { class: "cap" }, "全书五卷", READY.has("00") ? h("a", { href: `${href("00")}#map` }, "　看全书地图 →") : null), band, list);
  }

  // 分节地图：每节前面加「读过了」的勾和档；顶上一行写最短读法
  function wireSecmap() {
    const id = pageId(), p = id && find(id), ol = document.querySelector(".secmap");
    if (!ol || !p) return;
    const secs = secsOf(p);
    for (const li of ol.querySelectorAll("li[data-sec]")) {
      const k = li.dataset.sec, key = `wn-sec-${id}-${k}`, s = secs.find((x) => String(x.k) === k);
      const box = h("input", { type: "checkbox", "aria-label": `第 ${k} 节读过了` });
      box.checked = secDone(id, k); li.classList.toggle("done", box.checked);
      box.onchange = () => { LS.set(key, box.checked ? "1" : null); li.classList.toggle("done", box.checked); };
      li.prepend(box, h("span", { class: "k" }, `§${k}`));
      if (s) { li.classList.add(`t-${s.tier}`); li.querySelector("b")?.append(tierTag(s.tier), h("span", { class: "w" }, `约 ${round(s.zc, 100)} 字`)); }
    }
    const by = (t) => secs.filter((s) => s.tier === t);
    ol.before(h("p", { class: "pathline" }, ...TIERS.filter((t) => by(t).length).flatMap((t, i) => [i ? "　" : null, tierTag(t), ` ${by(t).length} 节，${fmtT(sum(by(t), (s) => s.zc))}`])));
  }
  const secProgress = (p) => {
    const k = secsOf(p).filter((s) => secDone(p.id, s.k)).length;
    return k && !isDone(p.id) ? h("span", { class: "sp" }, `　已读 ${k} 节`) : null;
  };

  // 本地笔记：<textarea class="note" data-key="05-oneline">，输入即存到本机（键 wn-note-05-oneline）
  function wireNotes() {
    for (const el of document.querySelectorAll("input.note, textarea.note")) {
      const key = `wn-note-${el.dataset.key}`;
      el.value = LS.get(key) || "";
      let tip = null;
      if (el.tagName === "TEXTAREA") { tip = h("div", { class: "note-tip" }, el.value ? "已保存在本机浏览器" : "写下来会自动保存在本机浏览器"); el.after(tip); }
      let t = null;
      el.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => { LS.set(key, el.value.trim() ? el.value : null); if (tip) tip.textContent = "已保存在本机浏览器"; }, 400); });
    }
  }

  // 首页：按卷分块的目录、进度
  function mountHome() {
    const toc = document.getElementById("toc");
    if (!toc) return;
    toc.append(item(INTRO));
    for (const b of BOOKS) {
      const ps = PAGES.filter((p) => bookOf(p) === b.n || (b.n === 1 && bookOf(p) === 0));
      if (!ps.length) continue;
      toc.append(h("li", { class: "blk stage" }, b.t, h("span", { class: "te" }, `　${b.zh}`), b.d ? h("span", { class: "d" }, b.d) : null));
      for (const p of ps) toc.append(item(p));
    }
    function item(p) {
      const ready = READY.has(p.id), core = secsOf(p).filter((s) => s.tier === "先读");
      return h("li", {}, h("a", Object.assign({ class: (isDone(p.id) ? "done " : "") + (ready ? "" : "todo") + (p.kind === "core" ? " core" : "") }, ready ? { href: href(p.id) } : {}),
        h("span", { class: "n" }, isDone(p.id) ? "✓" : p.id === "00" ? "·" : p.id),
        h("span", { class: "t" }, p.t || label(p), h("span", { class: "te" }, p.id === "00" ? "" : chLabel(p))),
        h("span", { class: "b" }, ...(p.id === "00" ? [] : ready ? [h("span", { class: `badge k-${p.kind}` }, p.kind === "core" ? "核心" : "轻量"), core.length ? h("span", { class: "badge t-先读" }, `先读 ${fmtT(sum(core, (s) => s.zc))}`) : null, p.need.includes("sim") ? h("span", { class: "badge b-sim" }, "模拟器") : null] : [h("span", { class: "badge" }, "待写")])),
        p.d ? h("span", { class: "d" }, p.d, p.id === "00" ? null : secProgress(p)) : null));
    }
    const doneN = PAGES.filter((p) => isDone(p.id)).length;
    const pr = document.getElementById("progress");
    if (pr) pr.append(h("div", { class: "progress" }, Object.assign(h("i"), { style: `width:${(100 * doneN) / PAGES.length}%` })), h("p", { class: "lede" }, `已读完 ${doneN} / ${PAGES.length} 页`));
  }

  // 全书最短读法（00 页和首页的 #path）：所有「先读」的节，按书里的顺序，带杨译里的地标和时间；读过的节打勾
  function mountPath() {
    const box = document.getElementById("path");
    if (!box) return;
    const all = PAGES.flatMap((p) => secsOf(p).map((s) => ({ p, s })));
    const tot = (t) => sum(all.filter((x) => x.s.tier === t), (x) => x.s.zc);
    box.append(h("p", { class: "pathline" }, ...TIERS.flatMap((t, i) => [i ? "　" : null, tierTag(t), ` ${fmtZ(tot(t))}，${fmtT(tot(t))}`])));
    const ol = h("ol", { class: "pathlist" });
    for (const { p, s } of all.filter((x) => x.s.tier === "先读")) {
      const c = chOf(s.ch);
      ol.append(h("li", { class: secDone(p.id, s.k) ? "done" : "" },
        h("span", { class: "where" }, c ? `${BOOKS.find((b) => b.n === c.book).t}${c.n ? ` 第 ${c.n} 章` : c.book ? " 引言" : ""}` : ""),
        h("b", {}, s.t), h("span", { class: "zh" }, `从「${s.zh}」读起`),
        h("span", { class: "w" }, `约 ${round(s.zc, 100)} 字`),
        READY.has(p.id) ? h("a", { href: href(p.id) }, `导读 ${p.id} →`) : h("span", { class: "todo" }, `导读 ${p.id} 待写`)));
    }
    box.append(ol);
  }

  async function fetchPage(id) {
    try { return new DOMParser().parseFromString(await (await fetch(href(id))).text(), "text/html"); } catch { return null; }
  }
  // 全书回顾（recap.html 的 #recap）：读各个已完成页的「精彩回顾」和「本站的总体看法」，按书里的顺序汇总
  async function mountRecap() {
    const box = document.getElementById("recap");
    if (!box) return;
    let shown = 0, lastB = -2;
    for (const p of PAGES) {
      if (!READY.has(p.id)) continue;
      const doc = await fetchPage(p.id); if (!doc) continue;
      const line = doc.querySelector(".recall-line"), items = doc.querySelector(".recall"), verdict = doc.querySelector(".verdict");
      if (!items) continue;
      const b = Math.max(1, bookOf(p));
      if (b !== lastB) { lastB = b; const bk = BOOKS.find((x) => x.n === b); box.append(h("h2", { class: "recap-part" }, `${bk.t}　${bk.zh}`)); }
      for (const a of items.querySelectorAll(".sec")) a.replaceWith(h("a", { class: "sec", href: href(p.id) }, a.textContent));
      box.append(h("section", { class: "recap-ch" },
        h("h3", {}, h("a", { href: href(p.id) }, `${p.id}　${p.t || ""}`)),
        h("p", { class: "lede" }, chLabel(p)),
        line ? document.importNode(line, true) : null, document.importNode(items, true),
        verdict ? document.importNode(verdict, true) : null));
      shown++;
    }
    if (!shown) box.append(h("p", { class: "lede" }, "还没有写好的页。"));
  }
  // 汇总页：terms.html 的 #terms 收各页「先用中文过一遍」的 .concept，#oldwords 收「原典」里的熟词生义；
  // today.html 的 #today 收各页「对照今天」的 .today；zh.html 的 #zherr 收各页「译本勘误」的 .zherr。按书里的顺序，链回原页
  async function mountCollect(boxId, sel, strip) {
    const box = document.getElementById(boxId);
    if (!box) return;
    let shown = 0, lastB = -2;
    const seen = new Set();
    for (const p of PAGES) {
      if (!READY.has(p.id)) continue;
      const doc = await fetchPage(p.id); if (!doc) continue;
      for (const c of doc.querySelectorAll(sel)) {
        if (boxId === "oldwords") {
          const w = c.querySelector("b")?.textContent.trim().toLowerCase();
          if (!w || seen.has(w)) continue;
          seen.add(w);
          box.append(h("li", {}, ...[...document.importNode(c, true).childNodes], h("a", { class: "sec", href: href(p.id) }, p.id)));
          shown++; continue;
        }
        const b = Math.max(1, bookOf(p));
        if (boxId !== "terms" && b !== lastB) { lastB = b; const bk = BOOKS.find((x) => x.n === b); box.append(h("h2", { class: "recap-part" }, `${bk.t}　${bk.zh}`)); }
        const node = document.importNode(c, true);
        if (strip) node.querySelector(strip)?.remove();
        const back = h("a", { class: "sec", href: `${href(p.id)}${c.id ? "#" + c.id : ""}` }, p.id);
        const s = node.querySelector("h3 .sec, h4 .sec");
        s ? s.replaceWith(back) : node.querySelector("h3, h4")?.prepend(back, " ");
        box.append(node); shown++;
      }
    }
    if (!shown) box.append(h(boxId === "oldwords" ? "li" : "p", { class: "lede" }, "还没有写好的页。"));
  }

  document.addEventListener("DOMContentLoaded", () => {
    mountChrome(); mountLine(); wireSecmap(); wireNotes(); mountHome(); mountPath(); mountRecap();
    mountCollect("terms", ".concept", ".use"); mountCollect("oldwords", "ul.oldwords li", null);
    mountCollect("today", ".today", null); mountCollect("zherr", ".zherr", null);
  });
  // 跨设备同步：模块在首页仓库里（/_home/sync.js），所有教程站共用。只在线上加载；本地预览要联调时设 localStorage["sync-dev"] = "1"
  // 上线前要把 wn- 加进 sync.js 的 PREFIXES 和 sync_server.py 的 KEY_RE，见 ~/tutorials-deploy/README.md。
  try { if (location.hostname === "t.miaowuao.cn" || localStorage.getItem("sync-dev")) document.head.append(Object.assign(document.createElement("script"), { src: "/_home/sync.js" })); } catch (e) {}
  window.WN = { h, LS, ROOT, href, label, isDone };
})();
