// Uncontrolled · 导读：共享脚本。注入顶栏、页头、「在全书的线上」、页末导航、页脚；接管分节地图的打勾和分档、词条的「记下」和筛选、本地笔记；
// 首页目录、全书最短读法（00 页和首页的 #path）、全书回顾（recap.html）、概念汇总（terms.html）、对照今天汇总（today.html）。
// 照 The Selfish Gene 导读的 sg.js 改，分档和最短读法照国富论导读的 wn.js。
// 页 id 是 UC_PAGES 里的 id（in 是导言；01、10a、10b…：一章一页的用两位章号，拆成两页的加 a、b），另有主编页 00「开读之前」（UC_EXTRA）。
// 节号 §k 是这一章的第 k 节，就是原书的第 k 个小标题（导言原书没有小标题，节是本站分的）。
// localStorage 键一律带 uc- 前缀（全站各教程同一个域名）：uc-done-页、uc-sec-页-节号、uc-star-页-词条、uc-note-页-…、uc-theme。
(() => {
  const CH = window.UC_CHAPTERS || [], SECS = window.UC_SECS || {}, PAGES = window.UC_PAGES || [], STAGES = window.UC_STAGES || [];
  const EXTRA = window.UC_EXTRA || {};
  const READY = new Set(window.UC_READY || []);
  const ROOT = document.currentScript.src.replace(/assets\/uc\.js.*$/, "");
  const WPM = 150; // 读者每分钟读多少英文词：母语不是英文、读的是论证，比读小说慢
  const LS = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { v == null || v === "" ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch {} },
    keys(prefix) { try { return Object.keys(localStorage).filter((k) => k.startsWith(prefix)); } catch { return []; } },
  };
  const h = (tag, attrs = {}, ...kids) => {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) k === "class" ? (el.className = v) : k.startsWith("on") ? (el[k] = v) : el.setAttribute(k, v);
    el.append(...kids.filter((x) => x != null));
    return el;
  };
  const pad = (n) => String(n).padStart(2, "0");
  const sum = (xs, f) => xs.reduce((a, x) => a + (f(x) || 0), 0);
  const fmtT = (w) => { const m = Math.max(5, Math.round(w / WPM / 5) * 5); return m >= 60 ? `约 ${(m / 60).toFixed(1).replace(/\.0$/, "")} 小时` : `约 ${m} 分钟`; };
  const fmtW = (w) => (w >= 10000 ? `${(w / 10000).toFixed(1)} 万词` : `${Math.round(w / 100) * 100} 词`);
  const TIERS = ["先读", "有空", "可跳过"];
  const tierTag = (t) => (t ? h("span", { class: `tier t-${t}` }, t) : null);
  const extra = (id) => Object.assign({ id, ch: -1, secs: [], words: 0, need: [] }, EXTRA[id] || {});
  const INTRO = extra("00");
  const ALL = [INTRO, ...PAGES];
  const find = (id) => ALL.find((p) => p.id === id);
  const chOf = (p) => CH.find((c) => c.n === p.ch);
  const secsOf = (p) => (SECS[pad(p.ch)] || []).filter((s) => p.secs.includes(s.k));
  const href = (id) => `${ROOT}chapters/${id}.html`;
  const half = (p) => (/a$/.test(p.id) ? "（上）" : /b$/.test(p.id) ? "（下）" : "");
  const label = (p) => (p.id === "00" ? "开读之前" : p.ch === 0 ? "导言" : `第 ${p.ch} 章${half(p)}`);
  const title = (p) => (p.ch >= 0 ? `${label(p)} · ${p.t || chOf(p).t}` : label(p));
  const chRange = (ns) => (ns.length === 1 ? (ns[0] ? `第 ${ns[0]} 章` : "导言") : `第 ${ns[0]}–${ns[ns.length - 1]} 章`);
  const isDone = (id) => LS.get(`uc-done-${id}`) === "1";
  const secDone = (id, k) => LS.get(`uc-sec-${id}-${k}`) === "1";
  const pageId = () => document.body.dataset.page || null;

  const saved = LS.get("uc-theme");
  if (saved) document.documentElement.dataset.theme = saved;
  function themeBtn() {
    return h("button", { class: "btn", "aria-label": "切换深色/浅色", onclick() {
      const dark = document.documentElement.dataset.theme ? document.documentElement.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
      const next = dark ? "light" : "dark";
      document.documentElement.dataset.theme = next; LS.set("uc-theme", next);
    } }, "深/浅");
  }

  function mountChrome() {
    const id = pageId(), p = id && find(id);
    document.body.prepend(h("div", { class: "topbar" }, h("div", { class: "topbar-inner" },
      h("a", { class: "home", href: `${ROOT}index.html` }, "Uncontrolled · 导读"),
      h("span", { class: "crumb" }, p ? title(p) : ""),
      themeBtn())));
    document.body.append(h("footer", { class: "site-footer" },
      h("a", { href: "https://beian.miit.gov.cn/", target: "_blank", rel: "noopener" }, "京ICP备18057656号-1")));
    if (!p) return;
    const main = document.querySelector("main");
    document.title = `${title(p)} · Uncontrolled 导读`;
    const c = chOf(p);
    const sibs = c ? PAGES.filter((x) => x.ch === c.n) : [];
    const core = secsOf(p).filter((s) => s.tier === "先读");
    main.prepend(h("div", { class: "chapter-head" },
      h("div", { class: "kicker" }, c ? (c.n ? `${c.part}　第 ${c.n} 章 ${c.en}` : "Introduction") : "Uncontrolled"),
      h("h1", {}, p.ch >= 0 ? `${label(p)}　${p.t || c.t}` : p.t || label(p)),
      c ? h("ul", { class: "secnames" }, ...secsOf(p).map((s) => h("li", {}, h("span", { class: "k" }, `§${s.k}`), s.t, h("span", { class: "en" }, `　${s.en} …`)))) : null,
      c ? h("div", { class: "badges" },
        h("span", { class: "badge" }, `英文约 ${p.words} 词，${fmtT(p.words)}`),
        core.length && core.length < secsOf(p).length ? h("span", { class: "badge t-先读" }, `只读「先读」${fmtT(sum(core, (s) => s.w))}`) : null,
        sibs.length > 1 ? h("span", { class: "badge" }, `本章分 ${sibs.length} 页，这是第 ${sibs.indexOf(p) + 1} 页`) : null,
        p.need.includes("sim") ? h("span", { class: "badge b-sim" }, "有模拟器") : null) : null));
    const order = ALL.map((x) => x.id);
    const i = order.indexOf(id), prev = order[i - 1], next = order[i + 1];
    const done = h("button", { class: "btn" });
    const paint = () => { done.textContent = isDone(id) ? "✓ 已读完这一页" : "标记：这一页读完了"; done.setAttribute("aria-pressed", isDone(id)); };
    done.onclick = () => { LS.set(`uc-done-${id}`, isDone(id) ? null : "1"); paint(); };
    paint();
    main.append(h("div", { class: "chapter-end" }, done, h("div", { class: "nav" },
      prev && READY.has(prev) ? h("a", { class: "btn", href: href(prev) }, `← ${label(find(prev))}`) : null,
      h("a", { class: "btn", href: `${ROOT}index.html` }, "目录"),
      next && READY.has(next) ? h("a", { class: "btn primary", href: href(next) }, `${label(find(next))} →`) : null)));
  }

  // 「读之前」里的 <div class="linehere"></div>：全书的几段（UC_STAGES），这一页所在的那段高亮；下面列这一页每节的档和在线上的作用（UC_SECS 的 tier、line）
  function mountLine() {
    const box = document.querySelector(".linehere"), id = pageId(), p = id && find(id);
    if (!box || !p) return;
    const band = h("ol", { class: "lineband" });
    for (const st of STAGES) {
      band.append(h("li", { class: st.ch.includes(p.ch) ? "here" : "" }, h("b", {}, st.t), h("span", {}, chRange(st.ch))));
    }
    const list = h("ul", { class: "linesecs" }, ...secsOf(p).map((s) => h("li", {}, h("span", { class: "k" }, `§${s.k}`), tierTag(s.tier), s.line || s.t)));
    box.append(h("p", { class: "cap" }, "全书的线", READY.has("00") ? h("a", { href: `${href("00")}#line` }, "　看全图 →") : null), band, list.children.length ? list : null);
  }

  // 词条：<div class="entry [trap]"><div class="en">…</div><div class="loc" data-p="段号">…</div>…</div>
  function wireEntries() {
    const entries = [...document.querySelectorAll(".entry")];
    if (!entries.length) return;
    const id = pageId();
    const count = h("span", { class: "count" });
    const mk = (lab, cls) => h("button", { class: "btn", "aria-pressed": String(!cls), onclick(e) {
      document.body.classList.remove("only-traps", "only-starred");
      if (cls) document.body.classList.add(cls);
      bar.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b === e.currentTarget)));
    } }, lab);
    const bar = h("div", { class: "toolbar" }, mk("全部", ""), mk("只看「每个字都认识」", "only-traps"), mk("只看我记下的", "only-starred"), count);
    const ws = [...document.querySelectorAll("h2")].find((x) => x.textContent === "词与短语");
    (ws ? ws.nextElementSibling : entries[0]).after(bar, h("p", { class: "empty-note" }, "还没有记下任何词条。回到「全部」，点词条右边的「记下」。"));
    const refresh = () => {
      const k = entries.filter((e) => e.classList.contains("starred")).length;
      document.body.classList.toggle("none-starred", k === 0);
      count.textContent = `共 ${entries.length} 条 · 已记下 ${k}`;
    };
    for (const e of entries) {
      const en = e.querySelector(".en"), text = en.textContent.trim();
      const key = `uc-star-${id}-${text}`;
      if (e.classList.contains("trap")) en.append(h("span", { class: "tag" }, "每个字都认识"));
      const btn = h("button", { class: "btn star" });
      const paint = () => { btn.textContent = e.classList.contains("starred") ? "已记下" : "记下"; };
      if (LS.get(key)) e.classList.add("starred");
      btn.onclick = () => {
        const on = e.classList.toggle("starred");
        LS.set(key, on ? JSON.stringify({ zh: e.querySelector(".zh")?.textContent.trim() || "" }) : null);
        paint(); refresh();
      };
      paint(); en.after(btn);
    }
    refresh();
  }

  // 分节地图：每节前面加「读过了」的勾和档，链到词条里对应的 #sK；地图上面一行写这一页各档的时间
  function wireSecmap() {
    const id = pageId(), p = id && find(id), ol = document.querySelector(".secmap");
    if (!ol || !p) return;
    const secs = secsOf(p);
    for (const li of ol.querySelectorAll("li[data-sec]")) {
      const k = li.dataset.sec, key = `uc-sec-${id}-${k}`, s = secs.find((x) => String(x.k) === k);
      const box = h("input", { type: "checkbox", "aria-label": `第 ${k} 节读过了` });
      box.checked = secDone(id, k); li.classList.toggle("done", box.checked);
      box.onchange = () => { LS.set(key, box.checked ? "1" : null); li.classList.toggle("done", box.checked); };
      li.prepend(box, h("span", { class: "k" }, `§${k}`));
      if (s && s.tier) { li.classList.add(`t-${s.tier}`); li.querySelector("b .w")?.before(tierTag(s.tier)); }
      if (document.getElementById(`s${k}`)) li.append(h("a", { class: "jump", href: `#s${k}` }, "词条 ↓"));
    }
    const by = (t) => secs.filter((s) => s.tier === t);
    if (secs.some((s) => s.tier)) ol.before(h("p", { class: "pathline" }, ...TIERS.filter((t) => by(t).length).flatMap((t, i) => [i ? "　" : null, tierTag(t), ` ${by(t).length} 节，${fmtT(sum(by(t), (s) => s.w))}`])));
  }
  const secProgress = (p) => {
    const k = p.secs.filter((s) => secDone(p.id, s)).length;
    return k && !isDone(p.id) ? h("span", { class: "sp" }, `　已读 ${k} 节`) : null;
  };

  // 本地笔记：<textarea class="note" data-key="07-oneline">，输入即存到本机（键 uc-note-07-oneline）
  function wireNotes() {
    for (const el of document.querySelectorAll("input.note, textarea.note")) {
      const key = `uc-note-${el.dataset.key}`;
      el.value = LS.get(key) || "";
      let tip = null;
      if (el.tagName === "TEXTAREA") { tip = h("div", { class: "note-tip" }, el.value ? "已保存在本机浏览器" : "写下来会自动保存在本机浏览器"); el.after(tip); }
      let t = null;
      el.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => { LS.set(key, el.value.trim() ? el.value : null); if (tip) tip.textContent = "已保存在本机浏览器"; }, 400); });
    }
  }

  // 首页：按全书的线分段的目录、进度、我的词本
  function mountHome() {
    const toc = document.getElementById("toc");
    if (!toc) return;
    toc.append(item(INTRO));
    for (const st of STAGES) {
      toc.append(h("li", { class: "blk stage" }, st.t));
      for (const c of CH.filter((x) => st.ch.includes(x.n))) {
        toc.append(h("li", { class: "blk" }, c.n ? `第 ${c.n} 章 ${c.t}` : c.t, h("span", { class: "te" }, `　${c.en}`), c.d ? h("span", { class: "d" }, c.d) : null));
        for (const p of PAGES.filter((x) => x.ch === c.n)) toc.append(item(p));
      }
    }
    function item(p) {
      const ready = READY.has(p.id), names = p.ch >= 0 ? secsOf(p).map((s) => s.t).join(" · ") : p.t;
      const core = secsOf(p).filter((s) => s.tier === "先读");
      return h("li", {}, h("a", Object.assign({ class: (isDone(p.id) ? "done " : "") + (ready ? "" : "todo") }, ready ? { href: href(p.id) } : {}),
        h("span", { class: "n" }, isDone(p.id) ? "✓" : p.id === "00" ? "·" : p.ch === 0 ? "导" : `${p.ch}${half(p) ? (half(p) === "（上）" ? "上" : "下") : ""}`),
        h("span", { class: "t" }, p.ch >= 0 ? p.t || label(p) : label(p), h("span", { class: "te" }, names)),
        h("span", { class: "b" }, ...(p.ch < 0 ? [] : ready ? [h("span", { class: "badge" }, `约 ${p.words} 词`), core.length ? h("span", { class: "badge t-先读" }, `先读 ${fmtT(sum(core, (s) => s.w))}`) : null, p.need.includes("sim") ? h("span", { class: "badge b-sim" }, "模拟器") : null] : [h("span", { class: "badge" }, "待写")])),
        p.d ? h("span", { class: "d" }, p.d, p.ch >= 0 ? secProgress(p) : null) : null));
    }
    const doneN = PAGES.filter((p) => isDone(p.id)).length;
    const pr = document.getElementById("progress");
    if (pr) pr.append(h("div", { class: "progress" }, Object.assign(h("i"), { style: `width:${(100 * doneN) / PAGES.length}%` })), h("p", { class: "lede" }, `已读完 ${doneN} / ${PAGES.length} 页`));
    const wb = document.getElementById("wordbook");
    if (wb) {
      const keys = LS.keys("uc-star-").sort();
      if (!keys.length) wb.append(h("p", { class: "lede" }, "还是空的。在各页里点词条右边的「记下」，它们会汇总到这里。"));
      for (const k of keys) {
        const m = k.match(/^uc-star-(\w+?)-(.*)$/); if (!m || !find(m[1])) continue;
        let zh = ""; try { zh = JSON.parse(LS.get(k)).zh; } catch {}
        wb.append(h("div", {}, h("b", {}, m[2]), h("span", {}, zh), h("a", { href: href(m[1]) }, label(find(m[1])))));
      }
    }
  }

  // 全书最短读法（00 页和首页的 #path）：所有「先读」的节，按书里的顺序，带英文开头（在 Kindle 里搜它）和时间；读过的节打勾
  function mountPath() {
    const box = document.getElementById("path");
    if (!box) return;
    const all = PAGES.flatMap((p) => secsOf(p).map((s) => ({ p, s })));
    if (!all.some((x) => x.s.tier)) { box.append(h("p", { class: "lede" }, "各节的分档还没定。")); return; }
    const tot = (t) => sum(all.filter((x) => x.s.tier === t), (x) => x.s.w);
    box.append(h("p", { class: "pathline" }, ...TIERS.flatMap((t, i) => [i ? "　" : null, tierTag(t), ` ${fmtW(tot(t))}，${fmtT(tot(t))}`])));
    const ol = h("ol", { class: "pathlist" });
    for (const { p, s } of all.filter((x) => x.s.tier === "先读")) {
      ol.append(h("li", { class: secDone(p.id, s.k) ? "done" : "" },
        h("span", { class: "where" }, `${p.ch ? `第 ${p.ch} 章` : "导言"} §${s.k}`),
        h("b", {}, s.t), h("span", { class: "en" }, `${s.en} …`),
        h("span", { class: "w" }, `约 ${Math.round(s.w / 100) * 100} 词`),
        READY.has(p.id) ? h("a", { href: href(p.id) }, `导读 →`) : h("span", { class: "todo" }, "导读待写")));
    }
    box.append(ol);
  }

  async function fetchPage(id) {
    try { return new DOMParser().parseFromString(await (await fetch(href(id))).text(), "text/html"); } catch { return null; }
  }
  // 全书回顾（recap.html 的 #recap）：读各个已完成页的「精彩回顾」和「本站的总体看法」，按原书顺序汇总
  async function mountRecap() {
    const box = document.getElementById("recap");
    if (!box) return;
    let shown = 0, lastCh = -1;
    for (const p of PAGES) {
      if (!READY.has(p.id)) continue;
      const doc = await fetchPage(p.id); if (!doc) continue;
      const line = doc.querySelector(".recall-line"), items = doc.querySelector(".recall"), verdict = doc.querySelector(".verdict");
      if (!items) continue;
      if (p.ch !== lastCh) { lastCh = p.ch; const c = chOf(p); box.append(h("h2", { class: "recap-part" }, c.n ? `第 ${c.n} 章 ${c.t}　${c.en}` : `${c.t}　${c.en}`)); }
      for (const a of items.querySelectorAll(".sec")) a.replaceWith(h("a", { class: "sec", href: href(p.id) }, a.textContent));
      box.append(h("section", { class: "recap-ch" },
        h("h3", {}, h("a", { href: href(p.id) }, title(p))),
        h("p", { class: "lede" }, secsOf(p).map((s) => s.t).join(" · ")),
        line ? document.importNode(line, true) : null, document.importNode(items, true),
        verdict ? document.importNode(verdict, true) : null));
      shown++;
    }
    if (!shown) box.append(h("p", { class: "lede" }, "还没有写好的页。"));
  }
  // 汇总页：terms.html 的 #terms 收各页「先用中文过一遍」的 .concept；today.html 的 #today 收各页「对照今天」的 .today。按原书顺序，链回原页
  async function mountCollect(boxId, sel, strip) {
    const box = document.getElementById(boxId);
    if (!box) return;
    let shown = 0, lastCh = -1;
    for (const p of PAGES) {
      if (!READY.has(p.id)) continue;
      const doc = await fetchPage(p.id); if (!doc) continue;
      for (const c of doc.querySelectorAll(sel)) {
        if (boxId !== "terms" && p.ch !== lastCh) { lastCh = p.ch; box.append(h("h2", { class: "recap-part" }, p.ch ? `第 ${p.ch} 章 ${chOf(p).t}` : chOf(p).t)); }
        const node = document.importNode(c, true);
        if (strip) node.querySelector(strip)?.remove();
        const back = h("a", { class: "sec", href: `${href(p.id)}${c.id ? "#" + c.id : ""}` }, label(p));
        const s = node.querySelector("h3 .sec, h4 .sec");
        s ? s.replaceWith(back) : node.querySelector("h3, h4")?.prepend(back, " ");
        box.append(node); shown++;
      }
    }
    if (!shown) box.append(h("p", { class: "lede" }, "还没有写好的页。"));
  }

  document.addEventListener("DOMContentLoaded", () => {
    mountChrome(); mountLine(); wireSecmap(); wireEntries(); wireNotes(); mountHome(); mountPath(); mountRecap();
    mountCollect("terms", ".concept", ".use"); mountCollect("today", ".today", null);
  });
  // 跨设备同步：模块在首页仓库里（/_home/sync.js），所有教程站共用。只在线上加载；本地预览要联调时设 localStorage["sync-dev"] = "1"
  // 上线前要把 uc- 加进 sync.js 的 PREFIXES 和 sync_server.py 的 KEY_RE，见 ~/tutorials-deploy/README.md。
  try { if (location.hostname === "t.miaowuao.cn" || localStorage.getItem("sync-dev")) document.head.append(Object.assign(document.createElement("script"), { src: "/_home/sync.js" })); } catch (e) {}
  window.UC = { h, LS, ROOT, href, label, isDone };
})();
