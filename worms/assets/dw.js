// Darwin's Worms · 导读：共享脚本。注入顶栏、页头、「在全书的线上」、页末导航、页脚；接管分节地图的打勾、词条的「记下」和筛选、本地笔记；
// 首页目录、全书回顾（recap.html）、概念汇总（terms.html）。照 On Borrowed Time 导读的 bt.js 改。
// 页 id 是 DW_PAGES 里的 id（01a、02b…），另有两页主编页：00「开读之前」、vm「达尔文的蚯蚓书」（DW_EXTRA）。节号 §k 是这一篇的第 k 节。
// localStorage 键一律带 dw- 前缀（全站各教程同一个域名）：dw-done-页、dw-sec-页-节号、dw-star-页-词条、dw-note-页-…、dw-theme。
(() => {
  const CH = window.DW_CHAPTERS || [], SECS = window.DW_SECS || {}, PAGES = window.DW_PAGES || [], STAGES = window.DW_STAGES || [];
  const EXTRA = window.DW_EXTRA || {};
  const READY = new Set(window.DW_READY || []);
  const ROOT = document.currentScript.src.replace(/assets\/dw\.js.*$/, "");
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
  const extra = (id) => Object.assign({ id, ch: 0, secs: [], words: 0 }, EXTRA[id] || {});
  const INTRO = extra("00"), VM = extra("vm");
  const ALL = [INTRO];
  for (const p of PAGES) { ALL.push(p); if (VM.after === p.id) ALL.push(VM); }
  const find = (id) => ALL.find((p) => p.id === id);
  const chOf = (p) => CH.find((c) => c.n === p.ch);
  const secsOf = (p) => (SECS[pad(p.ch)] || []).filter((s) => p.secs.includes(s.k));
  const href = (id) => `${ROOT}chapters/${id}.html`;
  const secRange = (p) => (p.secs.length > 1 ? `§${p.secs[0]}–§${p.secs[p.secs.length - 1]}` : `§${p.secs[0]}`);
  const label = (p) => (p.id === "00" ? "开读之前" : p.id === "vm" ? "附：达尔文的蚯蚓书" : `${chOf(p).t} ${secRange(p)}`);
  const title = (p) => (p.t && p.ch ? `${label(p)} · ${p.t}` : label(p));
  const isDone = (id) => LS.get(`dw-done-${id}`) === "1";
  const secDone = (id, k) => LS.get(`dw-sec-${id}-${k}`) === "1";
  const pageId = () => document.body.dataset.page || null;

  const saved = LS.get("dw-theme");
  if (saved) document.documentElement.dataset.theme = saved;
  function themeBtn() {
    return h("button", { class: "btn", "aria-label": "切换深色/浅色", onclick() {
      const dark = document.documentElement.dataset.theme ? document.documentElement.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
      const next = dark ? "light" : "dark";
      document.documentElement.dataset.theme = next; LS.set("dw-theme", next);
    } }, "深/浅");
  }

  function mountChrome() {
    const id = pageId(), p = id && find(id);
    document.body.prepend(h("div", { class: "topbar" }, h("div", { class: "topbar-inner" },
      h("a", { class: "home", href: `${ROOT}index.html` }, "Darwin's Worms · 导读"),
      h("span", { class: "crumb" }, p ? title(p) : ""),
      themeBtn())));
    document.body.append(h("footer", { class: "site-footer" },
      h("a", { href: "https://beian.miit.gov.cn/", target: "_blank", rel: "noopener" }, "京ICP备18057656号-1")));
    if (!p) return;
    const main = document.querySelector("main");
    document.title = `${title(p)} · Darwin's Worms 导读`;
    const c = chOf(p);
    main.prepend(h("div", { class: "chapter-head" },
      h("div", { class: "kicker" }, c ? `${c.t} ${c.en}` : "Darwin's Worms"),
      h("h1", {}, p.t && c ? `${label(p)}　${p.t}` : p.t || label(p)),
      c ? h("ul", { class: "secnames" }, ...secsOf(p).map((s) => h("li", {}, h("span", { class: "k" }, `§${s.k}`), s.t, h("span", { class: "en" }, `　${s.en} …`)))) : null,
      c ? h("div", { class: "badges" }, h("span", { class: "badge" }, `英文约 ${p.words} 词`), h("span", { class: "badge" }, `本篇 ${c.en}`)) : null));
    const order = ALL.map((x) => x.id);
    const i = order.indexOf(id), prev = order[i - 1], next = order[i + 1];
    const done = h("button", { class: "btn" });
    const paint = () => { done.textContent = isDone(id) ? "✓ 已读完这一页" : "标记：这一页读完了"; done.setAttribute("aria-pressed", isDone(id)); };
    done.onclick = () => { LS.set(`dw-done-${id}`, isDone(id) ? null : "1"); paint(); };
    paint();
    main.append(h("div", { class: "chapter-end" }, done, h("div", { class: "nav" },
      prev && READY.has(prev) ? h("a", { class: "btn", href: href(prev) }, `← ${label(find(prev))}`) : null,
      h("a", { class: "btn", href: `${ROOT}index.html` }, "目录"),
      next && READY.has(next) ? h("a", { class: "btn primary", href: href(next) }, `${label(find(next))} →`) : null)));
  }

  // 「读之前」里的 <div class="linehere"></div>：全书的几段（DW_STAGES），这一页所在的那段高亮；下面列这一页每节在线上的作用（DW_SECS 的 line）
  function mountLine() {
    const box = document.querySelector(".linehere"), id = pageId(), p = id && find(id);
    if (!box || !p) return;
    const band = h("ol", { class: "lineband" });
    for (const st of STAGES) {
      band.append(h("li", { class: st.ch.includes(p.ch) ? "here" : "" }, h("b", {}, st.t), h("span", {}, st.ch.map((n) => CH.find((c) => c.n === n).t).join("、"))));
    }
    const list = h("ul", { class: "linesecs" }, ...secsOf(p).filter((s) => s.line).map((s) => h("li", {}, h("span", { class: "k" }, `§${s.k}`), s.line)));
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
      const key = `dw-star-${id}-${text}`;
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

  // 分节地图：每节前面加「读过了」的勾，并链到词条里对应的 #sK
  function wireSecmap() {
    const id = pageId();
    for (const li of document.querySelectorAll(".secmap li[data-sec]")) {
      const k = li.dataset.sec, key = `dw-sec-${id}-${k}`;
      const box = h("input", { type: "checkbox", "aria-label": `第 ${k} 节读过了` });
      box.checked = secDone(id, k); li.classList.toggle("done", box.checked);
      box.onchange = () => { LS.set(key, box.checked ? "1" : null); li.classList.toggle("done", box.checked); };
      li.prepend(box, h("span", { class: "k" }, `§${k}`));
      if (document.getElementById(`s${k}`)) li.append(h("a", { class: "jump", href: `#s${k}` }, "词条 ↓"));
    }
  }
  const secProgress = (p) => {
    const k = p.secs.filter((s) => secDone(p.id, s)).length;
    return k && !isDone(p.id) ? h("span", { class: "sp" }, `　已读 ${k} 节`) : null;
  };

  // 本地笔记：<textarea class="note" data-key="02b-oneline">，输入即存到本机（键 dw-note-02b-oneline）
  function wireNotes() {
    for (const el of document.querySelectorAll("input.note, textarea.note")) {
      const key = `dw-note-${el.dataset.key}`;
      el.value = LS.get(key) || "";
      let tip = null;
      if (el.tagName === "TEXTAREA") { tip = h("div", { class: "note-tip" }, el.value ? "已保存在本机浏览器" : "写下来会自动保存在本机浏览器"); el.after(tip); }
      let t = null;
      el.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => { LS.set(key, el.value.trim() ? el.value : null); if (tip) tip.textContent = "已保存在本机浏览器"; }, 400); });
    }
  }

  // 首页：按原书的篇分块的目录、进度、我的词本
  function mountHome() {
    const toc = document.getElementById("toc");
    if (!toc) return;
    toc.append(item(INTRO));
    for (const c of CH) {
      toc.append(h("li", { class: "blk" }, c.t, h("span", { class: "te" }, `　${c.en}`), c.d ? h("span", { class: "d" }, c.d) : null));
      for (const p of PAGES.filter((x) => x.ch === c.n)) { toc.append(item(p)); if (VM.after === p.id) toc.append(item(VM)); }
    }
    function item(p) {
      const ready = READY.has(p.id), names = p.ch ? secsOf(p).map((s) => s.t).join(" · ") : p.t;
      return h("li", {}, h("a", Object.assign({ class: (isDone(p.id) ? "done " : "") + (ready ? "" : "todo") }, ready ? { href: href(p.id) } : {}),
        h("span", { class: "n" }, isDone(p.id) ? "✓" : p.id === "00" ? "·" : p.id === "vm" ? "附" : secRange(p)),
        h("span", { class: "t" }, p.ch ? p.t || label(p) : label(p), h("span", { class: "te" }, names)),
        h("span", { class: "b" }, ...(!p.ch ? [] : ready ? [h("span", { class: "badge" }, `约 ${p.words} 词`)] : [h("span", { class: "badge" }, "待写")])),
        p.d ? h("span", { class: "d" }, p.d, p.ch ? secProgress(p) : null) : null));
    }
    const doneN = PAGES.filter((p) => isDone(p.id)).length;
    const pr = document.getElementById("progress");
    if (pr) pr.append(h("div", { class: "progress" }, Object.assign(h("i"), { style: `width:${(100 * doneN) / PAGES.length}%` })), h("p", { class: "lede" }, `已读完 ${doneN} / ${PAGES.length} 页`));
    const wb = document.getElementById("wordbook");
    if (wb) {
      const keys = LS.keys("dw-star-").sort();
      if (!keys.length) wb.append(h("p", { class: "lede" }, "还是空的。在各页里点词条右边的「记下」，它们会汇总到这里。"));
      for (const k of keys) {
        const m = k.match(/^dw-star-(\w+?)-(.*)$/); if (!m || !find(m[1])) continue;
        let zh = ""; try { zh = JSON.parse(LS.get(k)).zh; } catch {}
        wb.append(h("div", {}, h("b", {}, m[2]), h("span", {}, zh), h("a", { href: href(m[1]) }, label(find(m[1])))));
      }
    }
  }

  async function fetchPage(id) {
    try { return new DOMParser().parseFromString(await (await fetch(href(id))).text(), "text/html"); } catch { return null; }
  }
  // 全书回顾（recap.html 的 #recap）：读各个已完成页的「精彩回顾」和「本站的总体看法」，按原书顺序汇总
  async function mountRecap() {
    const box = document.getElementById("recap");
    if (!box) return;
    let shown = 0, lastCh = 0;
    for (const p of ALL.filter((x) => x.id !== "00")) {  // vm（达尔文的蚯蚓书）排在 02b 后面，归在达尔文篇下
      if (!READY.has(p.id)) continue;
      const doc = await fetchPage(p.id); if (!doc) continue;
      const line = doc.querySelector(".recall-line"), items = doc.querySelector(".recall"), verdict = doc.querySelector(".verdict");
      if (!items) continue;
      if (p.ch && p.ch !== lastCh) { lastCh = p.ch; const c = chOf(p); box.append(h("h2", { class: "recap-part" }, `${c.t}　${c.en}`)); }
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
  // 概念汇总（terms.html 的 #terms）：读各个已完成页的「先用中文过一遍」里的 .concept，按出现顺序汇总，链回原页
  async function mountTerms() {
    const box = document.getElementById("terms");
    if (!box) return;
    let shown = 0;
    for (const p of PAGES) {
      if (!READY.has(p.id)) continue;
      const doc = await fetchPage(p.id); if (!doc) continue;
      for (const c of doc.querySelectorAll(".concept")) {
        const node = document.importNode(c, true);
        node.querySelector(".use")?.remove();
        node.querySelector("h3 .sec")?.replaceWith(h("a", { class: "sec", href: `${href(p.id)}#${c.id}` }, label(p)));
        box.append(node); shown++;
      }
    }
    if (!shown) box.append(h("p", { class: "lede" }, "还没有写好的页。"));
  }

  document.addEventListener("DOMContentLoaded", () => { mountChrome(); mountLine(); wireSecmap(); wireEntries(); wireNotes(); mountHome(); mountRecap(); mountTerms(); });
  // 跨设备同步：模块在首页仓库里（/_home/sync.js），所有教程站共用。只在线上加载；本地预览要联调时设 localStorage["sync-dev"] = "1"
  // 上线前要把 dw- 加进 sync.js 的 PREFIXES 和 sync_server.py 的 KEY_RE，见 ~/tutorials-deploy/README.md。
  try { if (location.hostname === "t.miaowuao.cn" || localStorage.getItem("sync-dev")) document.head.append(Object.assign(document.createElement("script"), { src: "/_home/sync.js" })); } catch (e) {}
  window.DW = { h, LS, ROOT, href, label, isDone };
})();
