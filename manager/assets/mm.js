// The Making of a Manager · 导读：共享脚本。注入顶栏、页头、「这一页在全书的哪里」、页末导航、页脚；接管分节地图（节名、原书小标题、纸书页码、译本地标、字数、档、打勾）、
// 词条的「记下」和筛选、本地笔记；首页目录、词本、全书最短读法（00 页和首页的 #path）、全书回顾（recap.html）和五个汇总页：
// 概念（terms.html）、情境卡（cases.html）、判断题（drills.html）、今天怎么看（today.html）、译本勘误（zh.html）。
// 照 Impro 导读的 im.js 改，词条照 Uncontrolled 的 uc.js。读者读的是英文纸书（对着繁体译本），所以页头、地图、最短读法都以原书为主：
// 节名旁边是原书的小标题和纸书页码，译本的小標題和开头几个字（在译本电子书里搜它）放在后面。
// 页 id 是 MM_PAGES 里的 id（in 引言，01–10 十章），另有主编页 00「开读之前」（MM_EXTRA）。节号 §k：§0 是一章第一个小标题之前的开头，§k 是第 k 个小标题。
// localStorage 键一律带 mm- 前缀（全站各教程同一个域名）：mm-done-页、mm-sec-页-节号、mm-note-页-…、mm-star-页-词条、mm-theme。
(() => {
  const CH = window.MM_CHAPTERS || [], SECS = window.MM_SECS || {}, PAGES = window.MM_PAGES || [];
  const EXTRA = window.MM_EXTRA || {};
  const READY = new Set(window.MM_READY || []);
  const ROOT = document.currentScript.src.replace(/assets\/mm\.js.*$/, "");
  const WPM = 170; // 读者每分钟读多少英文词：英文浅白，但母语不是英文、要停下来想自己的经历
  const LS = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { v == null || v === "" ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch {} },
    keys(pre) { try { return Object.keys(localStorage).filter((k) => k.startsWith(pre)); } catch { return []; } },
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
  const extra = (id) => Object.assign({ id, ch: -1 }, EXTRA[id] || {});
  const INTRO = extra("00");
  const ALL = [INTRO, ...PAGES];
  const find = (id) => ALL.find((p) => p.id === id);
  const chOf = (p) => CH.find((c) => c.n === p.ch);
  const secsOf = (p) => (p.ch >= 0 ? SECS[pad(p.ch)] || [] : []);
  const words = (p) => sum(secsOf(p), (s) => s.w);
  const pages = (xs) => (xs.length ? `p.${xs[0].pg[0]}–${xs[xs.length - 1].pg[1]}` : "");
  const href = (id) => `${ROOT}chapters/${id}.html`;
  const chName = (c) => (c.n === 0 ? "引言" : `第 ${c.n} 章`);
  const label = (p) => (p.id === "00" ? "开读之前" : chName(chOf(p)));
  const title = (p) => (p.ch >= 0 ? `${label(p)} · ${p.t || chOf(p).en.replace(/^Introduction: /, "")}` : label(p));
  const zhLoc = (s) => h("span", { class: "zhh" }, `译本「${s.zh}」`, s.zs ? h("span", { class: "zs" }, `开头：「${s.zs}」`) : null);
  const isDone = (id) => LS.get(`mm-done-${id}`) === "1";
  const secDone = (id, k) => LS.get(`mm-sec-${id}-${k}`) === "1";
  const pageId = () => document.body.dataset.page || null;

  const saved = LS.get("mm-theme");
  if (saved) document.documentElement.dataset.theme = saved;
  function themeBtn() {
    return h("button", { class: "btn", "aria-label": "切换深色/浅色", onclick() {
      const dark = document.documentElement.dataset.theme ? document.documentElement.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
      const next = dark ? "light" : "dark";
      document.documentElement.dataset.theme = next; LS.set("mm-theme", next);
    } }, "深/浅");
  }

  function mountChrome() {
    const id = pageId(), p = id && find(id);
    document.body.prepend(h("div", { class: "topbar" }, h("div", { class: "topbar-inner" },
      h("a", { class: "home", href: `${ROOT}index.html` }, "Making of a Manager · 导读"),
      h("span", { class: "crumb" }, p ? title(p) : ""),
      themeBtn())));
    document.body.append(h("footer", { class: "site-footer" },
      h("a", { href: "https://beian.miit.gov.cn/", target: "_blank", rel: "noopener" }, "京ICP备18057656号-1")));
    if (!p) return;
    const main = document.querySelector("main");
    document.title = `${title(p)} · The Making of a Manager 导读`;
    const c = chOf(p), secs = secsOf(p);
    const core = secs.filter((s) => s.tier === "先读");
    main.prepend(h("div", { class: "chapter-head" },
      h("div", { class: "kicker" }, c ? `${chName(c)}　${c.en}　译本：${c.t}` : "The Making of a Manager"),
      h("h1", {}, p.ch >= 0 ? `${label(p)}　${p.t || ""}` : p.t || label(p)),
      c && secs.length > 1 ? h("ul", { class: "secnames" }, ...secs.map((s) => h("li", {}, h("span", { class: "k" }, `§${s.k}`), s.t || s.en, h("span", { class: "en" }, `　${s.en}`)))) : null,
      c ? h("div", { class: "badges" },
        h("span", { class: "badge" }, `纸书 ${pages(secs)}`),
        h("span", { class: "badge" }, `英文约 ${fmtW(words(p))}，${fmtT(words(p))}`),
        core.length && core.length < secs.length ? h("span", { class: "badge t-先读" }, `只读「先读」${fmtT(sum(core, (s) => s.w))}`) : null) : null));
    const order = ALL.map((x) => x.id);
    const i = order.indexOf(id), prev = order[i - 1], next = order[i + 1];
    const done = h("button", { class: "btn" });
    const paint = () => { done.textContent = isDone(id) ? "✓ 已读完这一章" : "标记：这一章读完了"; done.setAttribute("aria-pressed", isDone(id)); };
    done.onclick = () => { LS.set(`mm-done-${id}`, isDone(id) ? null : "1"); paint(); };
    paint();
    main.append(h("div", { class: "chapter-end" }, done, h("div", { class: "nav" },
      prev && READY.has(prev) ? h("a", { class: "btn", href: href(prev) }, `← ${label(find(prev))}`) : null,
      h("a", { class: "btn", href: `${ROOT}index.html` }, "目录"),
      next && READY.has(next) ? h("a", { class: "btn primary", href: href(next) }, `${label(find(next))} →`) : null)));
  }

  // 「读之前」里的 <div class="linehere"></div>：全书引言加十章，这一章高亮；下面列这一章每节的档和作用（MM_SECS 的 tier、line）
  function mountLine() {
    const box = document.querySelector(".linehere"), id = pageId(), p = id && find(id);
    if (!box || !p) return;
    const band = h("ol", { class: "lineband" });
    for (const c of CH) band.append(h("li", { class: c.n === p.ch ? "here" : "" }, h("b", {}, c.n === 0 ? "引言" : String(c.n)), h("span", {}, c.t.replace(/^引言：/, ""))));
    const list = h("ul", { class: "linesecs" }, ...secsOf(p).map((s) => h("li", {}, h("span", { class: "k" }, `§${s.k}`), tierTag(s.tier), s.line || s.t)));
    box.append(h("p", { class: "cap" }, "全书：引言和十章", READY.has("00") ? h("a", { href: `${href("00")}#map` }, "　看全书地图 →") : null), band, list.children.length ? list : null);
  }

  // 分节地图：作者只写 <li data-sec="k"><span class="what">…</span></li>，节名、原书小标题、纸书页码、译本地标、字数、档、勾选框都从 MM_SECS 补上
  function wireSecmap() {
    const id = pageId(), p = id && find(id), ol = document.querySelector(".secmap");
    if (!ol || !p) return;
    const secs = secsOf(p);
    for (const li of ol.querySelectorAll("li[data-sec]")) {
      const k = li.dataset.sec, key = `mm-sec-${id}-${k}`, s = secs.find((x) => String(x.k) === k);
      if (!s) continue;
      const box = h("input", { type: "checkbox", "aria-label": `第 ${k} 节读过了` });
      box.checked = secDone(id, k); li.classList.toggle("done", box.checked);
      box.onchange = () => { LS.set(key, box.checked ? "1" : null); li.classList.toggle("done", box.checked); };
      li.prepend(box, h("span", { class: "k" }, `§${k}`), h("b", {}, s.t, tierTag(s.tier), h("span", { class: "w" }, `约 ${Math.round(s.w / 50) * 50} 词`)),
        h("span", { class: "en" }, `纸书 p.${s.pg[0]}${s.pg[1] > s.pg[0] ? "–" + s.pg[1] : ""}　${s.en}`, h("span", { class: "eo" }, `　开头：${s.eo} …`)), zhLoc(s));
      if (s.tier) li.classList.add(`t-${s.tier}`);
    }
    const by = (t) => secs.filter((s) => s.tier === t);
    if (secs.some((s) => s.tier)) ol.before(h("p", { class: "pathline" }, ...TIERS.filter((t) => by(t).length).flatMap((t, i) => [i ? "　" : null, tierTag(t), ` ${by(t).length} 节，${fmtT(sum(by(t), (s) => s.w))}`])));
  }
  const secProgress = (p) => {
    const k = secsOf(p).filter((s) => secDone(p.id, s.k)).length;
    return k && !isDone(p.id) ? h("span", { class: "sp" }, `　已读 ${k} 节`) : null;
  };

  // 词条：<div class="entry [trap]"><div class="en">…</div><div class="loc" data-p="段号">…</div>…</div>。「记下」存 mm-star-页-词条，首页和跨书词本（/_home/words.html）汇总
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
    const ws = [...document.querySelectorAll("h2")].find((x) => x.textContent === "原文里的口语和行话");
    (ws ? ws.nextElementSibling : entries[0]).after(bar, h("p", { class: "empty-note" }, "还没有记下任何词条。回到「全部」，点词条右边的「记下」。"));
    const refresh = () => {
      const k = entries.filter((e) => e.classList.contains("starred")).length;
      document.body.classList.toggle("none-starred", k === 0);
      count.textContent = `共 ${entries.length} 条 · 已记下 ${k}`;
    };
    for (const e of entries) {
      const en = e.querySelector(".en"), text = en.textContent.trim();
      const key = `mm-star-${id}-${text}`;
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

  // 词条和勘误的 .loc 后面补纸书页码（MM_PG：段号 → 这一段开头所在的页）
  function markPages() {
    const id = pageId(), p = id && find(id);
    if (!p || p.ch < 0) return;
    const pg = (window.MM_PG || {})[pad(p.ch)] || [];
    for (const el of document.querySelectorAll(".entry .loc[data-p], .zherr[data-p] p.loc")) {
      const n = pg[+(el.dataset.p || el.closest(".zherr").dataset.p)];
      if (n) el.append(h("span", { class: "pg" }, ` p.${n}`));
    }
  }

  // 本地笔记：<textarea class="note" data-key="04-oneline">，输入即存到本机（键 mm-note-04-oneline）
  function wireNotes() {
    for (const el of document.querySelectorAll("input.note, textarea.note")) {
      const key = `mm-note-${el.dataset.key}`;
      el.value = LS.get(key) || "";
      let tip = null;
      if (el.tagName === "TEXTAREA") { tip = h("div", { class: "note-tip" }, el.value ? "已保存在本机浏览器" : "写下来会自动保存在本机浏览器"); el.after(tip); }
      let t = null;
      el.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => { LS.set(key, el.value.trim() ? el.value : null); if (tip) tip.textContent = "已保存在本机浏览器"; }, 400); });
    }
  }

  // 首页：目录、进度、词本
  function mountHome() {
    const toc = document.getElementById("toc");
    if (!toc) return;
    for (const p of ALL) toc.append(item(p));
    function item(p) {
      const ready = READY.has(p.id), c = chOf(p), secs = secsOf(p);
      const core = secs.filter((s) => s.tier === "先读");
      return h("li", {}, h("a", Object.assign({ class: (isDone(p.id) ? "done " : "") + (ready ? "" : "todo") }, ready ? { href: href(p.id) } : {}),
        h("span", { class: "n" }, isDone(p.id) ? "✓" : p.id === "00" ? "·" : p.id === "in" ? "引" : p.id.replace(/^0/, "")),
        h("span", { class: "t" }, p.ch >= 0 ? p.t || c.t : label(p), h("span", { class: "te" }, c ? `${c.en.replace(/^Introduction: /, "Introduction · ")}　译本：${c.t}` : "")),
        h("span", { class: "b" }, ...(p.ch < 0 ? [] : ready ? [h("span", { class: "badge" }, `纸书 ${pages(secs)}`), core.length ? h("span", { class: "badge t-先读" }, `先读 ${fmtT(sum(core, (s) => s.w))}`) : null] : [h("span", { class: "badge" }, "待写")])),
        p.d ? h("span", { class: "d" }, p.d, p.ch >= 0 ? secProgress(p) : null) : null));
    }
    const doneN = PAGES.filter((p) => isDone(p.id)).length;
    const pr = document.getElementById("progress");
    if (pr) pr.append(h("div", { class: "progress" }, Object.assign(h("i"), { style: `width:${(100 * doneN) / PAGES.length}%` })), h("p", { class: "lede" }, `已读完 ${doneN} / ${PAGES.length} 章`));
    const wb = document.getElementById("wordbook");
    if (wb) {
      const keys = LS.keys("mm-star-").sort();
      if (!keys.length) wb.append(h("p", { class: "lede" }, "还是空的。在各章里点词条右边的「记下」，它们会汇总到这里。"));
      for (const k of keys) {
        const m = k.match(/^mm-star-(\w+?)-(.*)$/); if (!m || !find(m[1])) continue;
        let zh = ""; try { zh = JSON.parse(LS.get(k)).zh; } catch {}
        wb.append(h("div", {}, h("b", {}, m[2]), h("span", {}, zh), h("a", { href: href(m[1]) }, label(find(m[1])))));
      }
    }
  }

  // 全书最短读法（00 页和首页的 #path）：所有「先读」的节，按书里的顺序，带纸书页码、原书小标题和时间；读过的节打勾
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
        h("span", { class: "where" }, `${label(p)} §${s.k}　纸书 p.${s.pg[0]}${s.pg[1] > s.pg[0] ? "–" + s.pg[1] : ""}`),
        h("b", {}, s.t), h("span", { class: "en" }, s.k === 0 && p.ch > 0 ? `开头：${s.eo} …` : s.en),
        h("span", { class: "w" }, `约 ${Math.round(s.w / 50) * 50} 词`),
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
    let shown = 0;
    for (const p of PAGES) {
      if (!READY.has(p.id)) continue;
      const doc = await fetchPage(p.id); if (!doc) continue;
      const line = doc.querySelector(".recall-line"), items = doc.querySelector(".recall"), verdict = doc.querySelector(".verdict");
      if (!items) continue;
      for (const a of items.querySelectorAll(".sec")) a.replaceWith(h("a", { class: "sec", href: href(p.id) }, a.textContent));
      box.append(h("section", { class: "recap-ch" },
        h("h3", {}, h("a", { href: href(p.id) }, title(p))),
        h("p", { class: "lede" }, `${chOf(p).en}　译本：${chOf(p).t}`),
        line ? document.importNode(line, true) : null, document.importNode(items, true),
        verdict ? document.importNode(verdict, true) : null));
      shown++;
    }
    if (!shown) box.append(h("p", { class: "lede" }, "还没有写好的章。"));
  }
  // 汇总页：terms.html 的 #terms 收 .concept；cases.html 的 #cases 收 .case；drills.html 的 #drills 收 .drill；today.html 的 #today 收 .today；zh.html 的 #zherr 收 .zherr。
  // 按原书顺序，链回原页
  async function mountCollect(boxId, sel, strip) {
    const box = document.getElementById(boxId);
    if (!box) return;
    let shown = 0, lastCh = -1;
    for (const p of PAGES) {
      if (!READY.has(p.id)) continue;
      const doc = await fetchPage(p.id); if (!doc) continue;
      for (const c of doc.querySelectorAll(sel)) {
        if (boxId !== "terms" && p.ch !== lastCh) { lastCh = p.ch; box.append(h("h2", { class: "recap-part" }, `${label(p)}　${chOf(p).t}`)); }
        const node = document.importNode(c, true);
        if (strip) node.querySelector(strip)?.remove();
        const back = h("a", { class: "sec", href: `${href(p.id)}${c.id ? "#" + c.id : ""}` }, label(p));
        const s = node.querySelector("h3 .sec, h4 .sec");
        s ? s.replaceWith(back) : node.querySelector("h3, h4")?.prepend(back, " ");
        box.append(node); shown++;
      }
    }
    if (!shown) box.append(h("p", { class: "lede" }, "还没有写好的章。"));
  }

  document.addEventListener("DOMContentLoaded", () => {
    mountChrome(); mountLine(); wireSecmap(); markPages(); wireEntries(); wireNotes(); mountHome(); mountPath(); mountRecap();
    mountCollect("terms", ".concept", ".use"); mountCollect("cases", ".case", null); mountCollect("drills", ".drill", null);
    mountCollect("today", ".today", null); mountCollect("zherr", ".zherr", null);
  });
  // 跨设备同步：模块在首页仓库里（/_home/sync.js），所有教程站共用。只在线上加载；本地预览要联调时设 localStorage["sync-dev"] = "1"
  // 上线前要把 mm- 加进 sync.js 的 PREFIXES 和 sync_server.py 的 KEY_RE，见 ~/tutorials-deploy/README.md。
  try { if (location.hostname === "t.miaowuao.cn" || localStorage.getItem("sync-dev")) document.head.append(Object.assign(document.createElement("script"), { src: "/_home/sync.js" })); } catch (e) {}
  window.MM = { h, LS, ROOT, href, label, isDone };
})();
