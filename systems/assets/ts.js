// Thinking in Systems · 导读：共享脚本。注入顶栏、页头、「这一页在全书的哪里」、页末导航、页脚；接管分节地图（节名、译本地标、英文开头、字数、档、打勾）、
// 英文词条的「记下」、本地笔记；首页目录、全书最短读法（00 页和首页的 #path）、全书回顾（recap.html）和四个汇总页：概念（terms.html）、情境题（drills.html）、今天怎么看（today.html）、译本勘误（zh.html）；
// 还有给模拟器用的画图函数 TS.chart（见文件末尾）。
// 照 Fooled by Randomness 导读的 fb.js 改（去掉读前 / 读后的分界），情境题汇总照 The Making of a Manager 的 mm.js。
// 读者读的是简体译本《系统之美》电子书，手上的纸书是英文原版：页头、地图以译本为主（译本小标题、这一节在译本里开头的几个字），原书小标题和英文开头放在后面。
// 页 id 是 TS_PAGES 里的 id（in、01a、02b、07…），另有主编页 00「开读之前」（TS_EXTRA）。节号 §k 是这一章的第 k 个小标题（原书和译本一一对应）。
// localStorage 键一律带 ts- 前缀（全站各教程同一个域名）：ts-done-页、ts-sec-页-节号、ts-star-页-词条、ts-note-页-…、ts-theme。
(() => {
  const PARTS = window.TS_PARTS || [], CH = window.TS_CHAPTERS || [], SECS = window.TS_SECS || {}, PAGES = window.TS_PAGES || [];
  const EXTRA = window.TS_EXTRA || {};
  const READY = new Set(window.TS_READY || []);
  const ROOT = document.currentScript.src.replace(/assets\/ts\.js.*$/, "");
  const CPM = 450; // 读者每分钟读多少个译本的汉字
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
  const pad = (n) => String(n).padStart(2, "0");
  const sum = (xs, f) => xs.reduce((a, x) => a + (f(x) || 0), 0);
  const fmtT = (c) => { const m = Math.max(5, Math.round(c / CPM / 5) * 5); return m >= 60 ? `约 ${(m / 60).toFixed(1).replace(/\.0$/, "")} 小时` : `约 ${m} 分钟`; };
  const fmtZ = (c) => (c >= 10000 ? `${(c / 10000).toFixed(1)} 万字` : c < 100 ? "不到 100 字" : `${Math.round(c / 100) * 100} 字`);
  const TIERS = ["先读", "有空", "可跳过"];
  const tierTag = (t) => (t ? h("span", { class: `tier t-${t}` }, t) : null);
  const extra = (id) => Object.assign({ id, ch: -1, secs: [], need: [] }, EXTRA[id] || {});
  const INTRO = extra("00");
  const ALL = [INTRO, ...PAGES];
  const find = (id) => ALL.find((p) => p.id === id);
  const chOf = (p) => CH.find((c) => c.n === p.ch);
  const secsOf = (p) => p.secs.map((k) => (SECS[pad(p.ch)] || []).find((s) => s.k === String(k))).filter(Boolean);
  const zw = (p) => sum(secsOf(p), (s) => s.zw);
  const href = (id) => `${ROOT}chapters/${id}.html`;
  const sibsOf = (p) => PAGES.filter((x) => x.ch === p.ch);
  const chName = (c) => (c.n === 0 ? "前言和引言" : c.n === 8 ? "附录" : `第 ${c.n} 章`);
  const label = (p) => {
    if (p.id === "00") return "开读之前";
    const c = chOf(p), s = sibsOf(p);
    return chName(c) + (s.length > 1 ? `（${s.indexOf(p) + 1}/${s.length}）` : "");
  };
  const title = (p) => (p.ch >= 0 ? `${label(p)} · ${p.t || ""}`.replace(/ · $/, "") : label(p));
  const zhLoc = (s) => h("span", { class: "zhh" }, `译本：${s.zh}`, s.zs ? h("span", { class: "zs" }, `开头：「${s.zs}」`) : null);
  const isDone = (id) => LS.get(`ts-done-${id}`) === "1";
  const secDone = (id, k) => LS.get(`ts-sec-${id}-${k}`) === "1";
  const pageId = () => document.body.dataset.page || null;
  const simN = (p) => (p.need.includes("sim2") ? 2 : p.need.includes("sim") ? 1 : 0);

  const saved = LS.get("ts-theme");
  if (saved) document.documentElement.dataset.theme = saved;
  function themeBtn() {
    return h("button", { class: "btn", "aria-label": "切换深色/浅色", onclick() {
      const dark = document.documentElement.dataset.theme ? document.documentElement.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
      const next = dark ? "light" : "dark";
      document.documentElement.dataset.theme = next; LS.set("ts-theme", next);
    } }, "深/浅");
  }

  function mountChrome() {
    const id = pageId(), p = id && find(id);
    document.body.prepend(h("div", { class: "topbar" }, h("div", { class: "topbar-inner" },
      h("a", { class: "home", href: `${ROOT}index.html` }, "系统之美 · 导读"),
      h("span", { class: "crumb" }, p ? title(p) : ""),
      themeBtn())));
    document.body.append(h("footer", { class: "site-footer" },
      h("a", { href: "https://beian.miit.gov.cn/", target: "_blank", rel: "noopener" }, "京ICP备18057656号-1")));
    if (!p) return;
    const main = document.querySelector("main");
    document.title = `${title(p)} · Thinking in Systems 导读`;
    const c = chOf(p);
    const sibs = c ? sibsOf(p) : [];
    const core = secsOf(p).filter((s) => s.tier === "先读");
    const zhT = c ? c.zh : "";
    main.prepend(h("div", { class: "chapter-head" },
      h("div", { class: "kicker" }, c ? `${chName(c)}　${c.en}` : "Thinking in Systems"),
      h("h1", {}, p.ch >= 0 ? `${label(p)}　${p.t || ""}` : p.t || label(p)),
      c ? h("p", { class: "zhtitle" }, `译本：${zhT}`) : null,
      c ? h("ul", { class: "secnames" }, ...secsOf(p).map((s) => h("li", {}, h("span", { class: "k" }, s.lab), s.t || s.enh, h("span", { class: "en" }, `　译本：${s.zh}`)))) : null,
      c ? h("div", { class: "badges" },
        h("span", { class: "badge" }, `译本约 ${fmtZ(zw(p))}，${fmtT(zw(p))}`),
        core.length && core.length < secsOf(p).length ? h("span", { class: "badge t-先读" }, `只读「先读」${fmtT(sum(core, (s) => s.zw))}`) : null,
        sibs.length > 1 ? h("span", { class: "badge" }, `这一章分 ${sibs.length} 页，这是第 ${sibs.indexOf(p) + 1} 页`) : null,
        simN(p) ? h("span", { class: "badge b-sim" }, simN(p) > 1 ? `有 ${simN(p)} 个模拟器` : "有模拟器") : null) : null));
    const order = ALL.map((x) => x.id);
    const i = order.indexOf(id), prev = order[i - 1], next = order[i + 1];
    const done = h("button", { class: "btn" });
    const paint = () => { done.textContent = isDone(id) ? "✓ 已读完这一页" : "标记：这一页读完了"; done.setAttribute("aria-pressed", isDone(id)); };
    done.onclick = () => { LS.set(`ts-done-${id}`, isDone(id) ? null : "1"); paint(); };
    paint();
    main.append(h("div", { class: "chapter-end" }, done, h("div", { class: "nav" },
      prev && READY.has(prev) ? h("a", { class: "btn", href: href(prev) }, `← ${label(find(prev))}`) : null,
      h("a", { class: "btn", href: `${ROOT}index.html` }, "目录"),
      next && READY.has(next) ? h("a", { class: "btn primary", href: href(next) }, `${label(find(next))} →`) : null)));
  }

  // 「读之前」里的 <div class="linehere"></div>：全书五段（正文前、三部、书后），这一页所在的段高亮并列出它的章；下面列这一页每节的档和作用（TS_SECS 的 tier、line）
  function mountLine() {
    const box = document.querySelector(".linehere"), id = pageId(), p = id && find(id);
    if (!box || !p) return;
    const c = chOf(p);
    const band = h("ol", { class: "lineband" });
    for (const pt of PARTS) band.append(h("li", { class: c && c.part === pt.n ? "here" : "" }, h("b", {}, pt.zh), h("span", {}, pt.en)));
    const chs = c ? CH.filter((x) => x.part === c.part) : [];
    const chl = h("p", { class: "linechs" }, ...chs.flatMap((x, j) => [j ? "　" : null, x.n === c.n ? h("b", {}, `${chName(x)} ${x.t}`) : `${chName(x)} ${x.t}`]));
    const list = h("ul", { class: "linesecs" }, ...secsOf(p).map((s) => h("li", {}, h("span", { class: "k" }, s.lab), tierTag(s.tier), s.line || s.t)));
    box.append(...[h("p", { class: "cap" }, "全书五段", READY.has("00") ? h("a", { href: `${href("00")}#map` }, "　看全书地图 →") : null), band, chs.length > 1 ? chl : null, list.children.length ? list : null].filter((x) => x != null));
  }

  // 分节地图：作者只写 <li data-sec="k"><span class="what">…</span></li>，节名、译本地标、英文开头、字数、档、勾选框都从 TS_SECS 补上
  function wireSecmap() {
    const id = pageId(), p = id && find(id), ol = document.querySelector(".secmap");
    if (!ol || !p) return;
    const secs = secsOf(p);
    for (const li of ol.querySelectorAll("li[data-sec]")) {
      const k = li.dataset.sec, key = `ts-sec-${id}-${k}`, s = secs.find((x) => x.k === k);
      if (!s) continue;
      const box = h("input", { type: "checkbox", "aria-label": `${s.lab} 读过了` });
      box.checked = secDone(id, k); li.classList.toggle("done", box.checked);
      box.onchange = () => { LS.set(key, box.checked ? "1" : null); li.classList.toggle("done", box.checked); };
      li.prepend(box, h("span", { class: "k" }, s.lab), h("b", {}, s.t || s.enh, tierTag(s.tier), h("span", { class: "w" }, `约 ${Math.round(s.zw / 100) * 100} 字`)), zhLoc(s), h("span", { class: "en" }, `原文：${s.enh}　${s.en} …`));
      if (s.tier) li.classList.add(`t-${s.tier}`);
    }
    const by = (t) => secs.filter((s) => s.tier === t);
    if (secs.some((s) => s.tier)) ol.before(h("p", { class: "pathline" }, ...TIERS.filter((t) => by(t).length).flatMap((t, i) => [i ? "　" : null, tierTag(t), ` ${by(t).length} 节，${fmtT(sum(by(t), (s) => s.zw))}`])));
  }
  const secProgress = (p) => {
    const k = p.secs.filter((s) => secDone(p.id, s)).length;
    return k && !isDone(p.id) ? h("span", { class: "sp" }, `　已读 ${k} 节`) : null;
  };

  // 词条：<div class="entry [trap]"><div class="en">…</div><div class="loc" data-p="段号">…</div>…</div>。「记下」存 ts-star-页-词条，首页和跨书词本（/_home/words.html）汇总
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
    const ws = [...document.querySelectorAll("h2")].find((x) => x.textContent === "原文里的词和句");
    (ws ? ws.nextElementSibling : entries[0]).after(bar, h("p", { class: "empty-note" }, "还没有记下任何词条。回到「全部」，点词条右边的「记下」。"));
    const refresh = () => {
      const k = entries.filter((e) => e.classList.contains("starred")).length;
      document.body.classList.toggle("none-starred", k === 0);
      count.textContent = `共 ${entries.length} 条 · 已记下 ${k}`;
    };
    for (const e of entries) {
      const en = e.querySelector(".en"), text = en.textContent.trim();
      const key = `ts-star-${id}-${text}`;
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

  // 本地笔记：<textarea class="note" data-key="01a-oneline">，输入即存到本机（键 ts-note-01a-oneline）
  function wireNotes() {
    for (const el of document.querySelectorAll("input.note, textarea.note")) {
      const key = `ts-note-${el.dataset.key}`;
      el.value = LS.get(key) || "";
      let tip = null;
      if (el.tagName === "TEXTAREA") { tip = h("div", { class: "note-tip" }, el.value ? "已保存在本机浏览器" : "写下来会自动保存在本机浏览器"); el.after(tip); }
      let t = null;
      el.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => { LS.set(key, el.value.trim() ? el.value : null); if (tip) tip.textContent = "已保存在本机浏览器"; }, 400); });
    }
  }

  // 首页：按五段分组的目录、进度
  function mountHome() {
    const toc = document.getElementById("toc");
    if (!toc) return;
    toc.append(item(INTRO));
    for (const pt of PARTS) {
      const ps = PAGES.filter((x) => chOf(x).part === pt.n);
      if (!ps.length) continue;
      toc.append(h("li", { class: "blk" }, pt.zh, h("span", { class: "te" }, `　${pt.en}`)));
      for (const p of ps) toc.append(item(p));
    }
    function item(p) {
      const ready = READY.has(p.id), names = p.ch >= 0 ? secsOf(p).map((s) => s.t || s.enh).join(" · ") : p.t;
      const core = secsOf(p).filter((s) => s.tier === "先读");
      return h("li", {}, h("a", Object.assign({ class: (isDone(p.id) ? "done " : "") + (ready ? "" : "todo") }, ready ? { href: href(p.id) } : {}),
        h("span", { class: "n" }, isDone(p.id) ? "✓" : p.id === "00" ? "·" : p.id === "in" ? "引" : p.id === "08" ? "附" : p.id.replace(/^0/, "")),
        h("span", { class: "t" }, p.ch >= 0 ? `${label(p)}　${p.t || chOf(p).t}` : label(p), h("span", { class: "te" }, names)),
        h("span", { class: "b" }, ...(p.ch < 0 ? [] : ready ? [h("span", { class: "badge" }, `译本约 ${fmtZ(zw(p))}`), core.length ? h("span", { class: "badge t-先读" }, `先读 ${fmtT(sum(core, (s) => s.zw))}`) : null, simN(p) ? h("span", { class: "badge b-sim" }, "模拟器") : null] : [h("span", { class: "badge" }, "待写")])),
        p.d ? h("span", { class: "d" }, p.d, p.ch >= 0 ? secProgress(p) : null) : null));
    }
    const doneN = PAGES.filter((p) => isDone(p.id)).length;
    const pr = document.getElementById("progress");
    if (pr) pr.append(h("div", { class: "progress" }, Object.assign(h("i"), { style: `width:${(100 * doneN) / PAGES.length}%` })), h("p", { class: "lede" }, `已读完 ${doneN} / ${PAGES.length} 页`));
  }

  // 全书最短读法（00 页和首页的 #path）：所有「先读」的节，按书里的顺序，带译本的地标（在译本电子书里搜开头那几个字）和时间；读过的节打勾
  function mountPath() {
    const box = document.getElementById("path");
    if (!box) return;
    const all = PAGES.flatMap((p) => secsOf(p).map((s) => ({ p, s })));
    if (!all.some((x) => x.s.tier)) { box.append(h("p", { class: "lede" }, "各节的分档还没定。")); return; }
    const tot = (t) => sum(all.filter((x) => x.s.tier === t), (x) => x.s.zw);
    box.append(h("p", { class: "pathline" }, ...TIERS.flatMap((t, i) => [i ? "　" : null, tierTag(t), ` ${fmtZ(tot(t))}，${fmtT(tot(t))}`])));
    const ol = h("ol", { class: "pathlist" });
    for (const { p, s } of all.filter((x) => x.s.tier === "先读")) {
      ol.append(h("li", { class: secDone(p.id, s.k) ? "done" : "" },
        h("span", { class: "where" }, `${chName(chOf(p))} ${s.lab}　译本：${s.zh}`),
        h("b", {}, s.t), h("span", { class: "en" }, s.zs ? `译本开头：「${s.zs}」` : `原文：${s.en} …`),
        h("span", { class: "w" }, `约 ${Math.round(s.zw / 100) * 100} 字`),
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
    let shown = 0, lastPart = -1;
    for (const p of PAGES) {
      if (!READY.has(p.id)) continue;
      const doc = await fetchPage(p.id); if (!doc) continue;
      const line = doc.querySelector(".recall-line"), items = doc.querySelector(".recall"), verdict = doc.querySelector(".verdict");
      if (!items) continue;
      const pt = PARTS[chOf(p).part];
      if (pt.n !== lastPart) { lastPart = pt.n; box.append(h("h2", { class: "recap-part" }, `${pt.zh}　${pt.en}`)); }
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
  // 汇总页：terms.html 的 #terms 收 .concept；drills.html 的 #drills 收 .drill；today.html 的 #today 收 .today；zh.html 的 #zherr 收 .zherr。按原书顺序，链回原页
  async function mountCollect(boxId, sel, strip) {
    const box = document.getElementById(boxId);
    if (!box) return;
    let shown = 0, last = null;
    for (const p of PAGES) {
      if (!READY.has(p.id)) continue;
      const doc = await fetchPage(p.id); if (!doc) continue;
      for (const c of doc.querySelectorAll(sel)) {
        if (boxId !== "terms" && p.id !== last) { last = p.id; box.append(h("h2", { class: "recap-part" }, title(p))); }
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


  // 模拟器画曲线：TS.chart(el, opts) 把 el 的内容换成一张折线图（SVG，viewBox 宽取容器宽，320–640，手机上字不缩小；颜色走 style.css 的 --c1…--c6，深浅主题都清楚）。
  //   opts.series：[{ name: "库存", data: [y0, y1, …], c: 1, dash: false }]，data 的下标就是时间步（第 0 步是初值），c 是 1–6 的颜色号。
  //   opts.xlabel / opts.ylabel：轴名（中文，带单位，如「天」「辆」）；opts.dt：一步多长（默认 1），横轴刻度按 i*dt 标；
  //   opts.ymin / opts.ymax：纵轴范围（不给就按数据取，ymin 默认 0）；opts.marks：[{ x: 25, label: "需求 +10%" }] 竖虚线标记；
  //   opts.hlines：[{ y: 18, label: "设定 18°C" }] 横虚线；opts.height：画面高（默认按宽度定，220 起）。
  //   返回 { svg, y(v), x(i) }，要在图上再画点什么可以用。
  function chart(el, o) {
    const W = Math.round(Math.max(320, Math.min(640, el.clientWidth || 640))), H = o.height || Math.max(220, Math.round(W * 0.44)), L = W < 480 ? 44 : 56, R = 14, T = 26, B = 40;   // 画布宽跟着容器（320–640），手机上字不缩小
    const ser = (o.series || []).filter((s) => s && s.data && s.data.length);
    const n = Math.max(1, ...ser.map((s) => s.data.length - 1)), dt = o.dt || 1;
    const vals = ser.flatMap((s) => s.data).filter((v) => Number.isFinite(v));
    let lo = o.ymin != null ? o.ymin : Math.min(0, ...vals), hi = o.ymax != null ? o.ymax : Math.max(lo + 1, ...vals);
    if (o.ymax == null) hi = lo + (hi - lo) * 1.08;
    const step = niceStep((hi - lo) / 5); if (o.ymax == null) hi = Math.ceil(hi / step) * step;
    const x = (i) => L + ((W - L - R) * i) / n, y = (v) => T + (H - T - B) * (1 - (Math.min(hi, Math.max(lo, v)) - lo) / (hi - lo || 1));
    const NS = "http://www.w3.org/2000/svg";
    const S = (tag, a = {}, txt) => { const e = document.createElementNS(NS, tag); for (const k in a) e.setAttribute(k, a[k]); if (txt != null) e.textContent = txt; return e; };
    const svg = S("svg", { class: "diagram chart", viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": o.title || ser.map((s) => s.name).join("、") });
    for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) {
      svg.append(S("line", { x1: L, x2: W - R, y1: y(v), y2: y(v), class: "grid" }), S("text", { x: L - 6, y: y(v) + 4, "text-anchor": "end", class: "t-m" }, fmtN(v)));
    }
    const xs = niceStep((n * dt) / (W < 480 ? 4 : 6));
    for (let t = 0; t <= n * dt + 1e-9; t += xs) svg.append(S("text", { x: x(t / dt), y: H - B + 16, "text-anchor": "middle", class: "t-m" }, fmtN(t)));
    svg.append(S("line", { x1: L, x2: L, y1: T, y2: H - B, class: "ln" }), S("line", { x1: L, x2: W - R, y1: H - B, y2: H - B, class: "ln" }));
    if (o.xlabel) svg.append(S("text", { x: W - R, y: H - 6, "text-anchor": "end", class: "t-m" }, o.xlabel));
    if (o.ylabel) svg.append(S("text", { x: 4, y: 13, class: "t-m" }, o.ylabel));
    for (const m of o.hlines || []) svg.append(S("line", { x1: L, x2: W - R, y1: y(m.y), y2: y(m.y), class: "ln-d" }), m.label ? S("text", { x: W - R - 4, y: y(m.y) - 5, "text-anchor": "end", class: "t-m" }, m.label) : null);
    for (const m of o.marks || []) svg.append(S("line", { x1: x(m.x / dt), x2: x(m.x / dt), y1: T, y2: H - B, class: "ln-d" }), m.label ? S("text", { x: x(m.x / dt) + 4, y: x(m.x / dt) - L < 90 ? T + 14 : 13, class: "t-m" }, m.label) : null);   // 标记靠左时放进图里，免得和纵轴名叠在一行
    for (const s of ser) {
      const d = s.data.map((v, i) => (Number.isFinite(v) ? `${i ? "L" : "M"}${x(i).toFixed(1)},${y(v).toFixed(1)}` : "")).join("");
      svg.append(S("path", { d, class: `ln s${s.c || 1}${s.dash ? " dash" : ""}`, "stroke-width": 2.5 }));
    }
    const lg = document.createElement("div"); lg.className = "chart-legend";
    for (const s of ser) lg.append(h("span", {}, h("i", { class: `k${s.c || 1}${s.dash ? " dash" : ""}` }), s.name));
    el.replaceChildren(svg, ser.length > 1 ? lg : "");
    return { svg, x, y };
  }
  function niceStep(r) { const p = Math.pow(10, Math.floor(Math.log10(r || 1))), f = r / p; return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * p; }
  function fmtN(v) { const a = Math.abs(v); return a >= 1e4 ? `${+(v / 1e4).toFixed(1)}万` : a >= 100 || Number.isInteger(v) ? String(Math.round(v)) : String(+v.toFixed(2)); }

  document.addEventListener("DOMContentLoaded", () => {
    mountChrome(); mountLine(); wireSecmap(); wireEntries(); wireNotes(); mountHome(); mountPath(); mountRecap();
    mountCollect("terms", ".concept", ".use"); mountCollect("drills", ".drill", null); mountCollect("today", ".today", null); mountCollect("zherr", ".zherr", null);
  });
  // 跨设备同步：模块在首页仓库里（/_home/sync.js），所有教程站共用。只在线上加载；本地预览要联调时设 localStorage["sync-dev"] = "1"
  // 上线前要把 ts- 加进 sync.js 的 PREFIXES 和 sync_server.py 的 KEY_RE，见 ~/tutorials-deploy/README.md。
  try { if (location.hostname === "t.miaowuao.cn" || localStorage.getItem("sync-dev")) document.head.append(Object.assign(document.createElement("script"), { src: "/_home/sync.js" })); } catch (e) {}
  window.TS = { h, LS, ROOT, href, label, isDone, chart, fmtN };
})();
