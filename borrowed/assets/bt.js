// On Borrowed Time · 导读：共享脚本。注入顶栏、页头、「在全书的线上」、页末导航、页脚；接管分节地图的打勾、词条的「记下」和筛选、本地笔记；
// 首页目录、全书回顾（recap.html）、概念汇总（terms.html）。
// 页 id 是 BT_PAGES 里的 id（01a、02b、04…），00 是「开读之前」。节号用原书的：§k 是这一章的第 k 节。
// localStorage 键一律带 bt- 前缀（全站各教程同一个域名）：bt-done-页、bt-sec-页-节号、bt-star-页-词条、bt-note-页-…、bt-theme。
(() => {
  const CH = window.BT_CHAPTERS || [], SECS = window.BT_SECS || {}, PAGES = window.BT_PAGES || [], STAGES = window.BT_STAGES || [];
  const READY = new Set(window.BT_READY || []);
  const ROOT = document.currentScript.src.replace(/assets\/bt\.js.*$/, "");
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
  const INTRO = { id: "00", ch: 0, secs: [], words: 0, t: "这本书、这位作者、这条线", d: "Weinrich 是谁，全书怎么走，读者手上这本电子书的样子" };
  const ALL = [INTRO, ...PAGES];
  const find = (id) => ALL.find((p) => p.id === id);
  const chOf = (p) => CH.find((c) => c.n === p.ch);
  const secsOf = (p) => (SECS[pad(p.ch)] || []).filter((s) => p.secs.includes(s.k));
  const href = (id) => `${ROOT}chapters/${id}.html`;
  const secRange = (p) => (p.ch === 10 ? "" : p.secs.length > 1 ? `§${p.secs[0]}–§${p.secs[p.secs.length - 1]}` : `§${p.secs[0]}`);
  const label = (p) => (p.id === "00" ? "开读之前" : p.ch === 10 ? "尾声" : `第 ${p.ch} 章 ${secRange(p)}`);
  const title = (p) => (p.t ? `${label(p)} · ${p.t}` : label(p));
  const isDone = (id) => LS.get(`bt-done-${id}`) === "1";
  const secDone = (id, k) => LS.get(`bt-sec-${id}-${k}`) === "1";
  const pageId = () => document.body.dataset.page || null;

  const saved = LS.get("bt-theme");
  if (saved) document.documentElement.dataset.theme = saved;
  function themeBtn() {
    return h("button", { class: "btn", "aria-label": "切换深色/浅色", onclick() {
      const dark = document.documentElement.dataset.theme ? document.documentElement.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
      const next = dark ? "light" : "dark";
      document.documentElement.dataset.theme = next; LS.set("bt-theme", next);
    } }, "深/浅");
  }

  function mountChrome() {
    const id = pageId(), p = id && find(id);
    document.body.prepend(h("div", { class: "topbar" }, h("div", { class: "topbar-inner" },
      h("a", { class: "home", href: `${ROOT}index.html` }, "On Borrowed Time · 导读"),
      h("span", { class: "crumb" }, p ? title(p) : ""),
      themeBtn())));
    document.body.append(h("footer", { class: "site-footer" },
      h("a", { href: "https://beian.miit.gov.cn/", target: "_blank", rel: "noopener" }, "京ICP备18057656号-1")));
    if (!p) return;
    const main = document.querySelector("main");
    document.title = `${title(p)} · On Borrowed Time 导读`;
    const c = chOf(p);
    main.prepend(h("div", { class: "chapter-head" },
      h("div", { class: "kicker" }, c ? `第 ${c.n} 章 ${c.en}` : "On Borrowed Time"),
      h("h1", {}, p.t ? `${label(p)}　${p.t}` : label(p)),
      c ? h("ul", { class: "secnames" }, ...secsOf(p).map((s) => h("li", {}, p.ch === 10 ? null : h("span", { class: "k" }, `§${s.k}`), h("span", { class: "en" }, s.en), s.who ? h("span", { class: "who-n" }, ` • ${s.who}`) : null))) : null,
      c ? h("div", { class: "badges" }, h("span", { class: "badge" }, `英文约 ${p.words} 词`), h("span", { class: "badge" }, `本章 ${c.t}`)) : null));
    const order = ALL.map((x) => x.id);
    const i = order.indexOf(id), prev = order[i - 1], next = order[i + 1];
    const done = h("button", { class: "btn" });
    const paint = () => { done.textContent = isDone(id) ? "✓ 已读完这一页" : "标记：这一页读完了"; done.setAttribute("aria-pressed", isDone(id)); };
    done.onclick = () => { LS.set(`bt-done-${id}`, isDone(id) ? null : "1"); paint(); };
    paint();
    const short = (x) => (x.id === "00" ? "开读之前" : label(x));
    main.append(h("div", { class: "chapter-end" }, done, h("div", { class: "nav" },
      prev && READY.has(prev) ? h("a", { class: "btn", href: href(prev) }, `← ${short(find(prev))}`) : null,
      h("a", { class: "btn", href: `${ROOT}index.html` }, "目录"),
      next && READY.has(next) ? h("a", { class: "btn primary", href: href(next) }, `${short(find(next))} →`) : null)));
  }

  // 「读之前」里的 <div class="linehere"></div>：全书的几段（BT_STAGES），这一页所在的那段高亮；下面列这一页每节在线上的作用（BT_SECS 的 line）
  function mountLine() {
    const box = document.querySelector(".linehere"), id = pageId(), p = id && find(id);
    if (!box || !p) return;
    const band = h("ol", { class: "lineband" });
    for (const st of STAGES) {
      const here = st.ch.includes(p.ch);
      band.append(h("li", { class: here ? "here" : "" }, h("b", {}, st.t), h("span", {}, st.ch.map((n) => (n === 10 ? "尾声" : `第 ${n} 章`)).join("、"))));
    }
    const list = h("ul", { class: "linesecs" }, ...secsOf(p).filter((s) => s.line).map((s) =>
      h("li", {}, p.ch === 10 ? null : h("span", { class: "k" }, `§${s.k}`), s.line)));
    box.append(h("p", { class: "cap" }, "全书的线", READY.has("00") ? h("a", { href: `${href("00")}#line` }, "　看全图 →") : null), band, list.children.length ? list : null);
  }

  // 词条：<div class="entry [trap|img]"><div class="en">…</div><div class="loc" data-p="段号">…</div>…</div>
  function wireEntries() {
    const entries = [...document.querySelectorAll(".entry")];
    if (!entries.length) return;
    const id = pageId();
    const first = document.querySelector("h2 + .lede + h3.sec-head, .entry");
    const count = h("span", { class: "count" });
    const mk = (lab, cls) => h("button", { class: "btn", "aria-pressed": String(!cls), onclick(e) {
      document.body.classList.remove("only-traps", "only-starred");
      if (cls) document.body.classList.add(cls);
      bar.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b === e.currentTarget)));
    } }, lab);
    const bar = h("div", { class: "toolbar" }, mk("全部", ""), mk("只看「每个字都认识」", "only-traps"), mk("只看我记下的", "only-starred"), count);
    const ws = [...document.querySelectorAll("h2")].find((x) => x.textContent === "词与短语");
    (ws ? ws.nextElementSibling : first).after(bar, h("p", { class: "empty-note" }, "还没有记下任何词条。回到「全部」，点词条右边的「记下」。"));
    const refresh = () => {
      const k = entries.filter((e) => e.classList.contains("starred")).length;
      document.body.classList.toggle("none-starred", k === 0);
      count.textContent = `共 ${entries.length} 条（含图里的 ${entries.filter((e) => e.classList.contains("img")).length} 条）· 已记下 ${k}`;
    };
    for (const e of entries) {
      const en = e.querySelector(".en"), text = en.textContent.trim();
      const key = `bt-star-${id}-${text}`;
      if (e.classList.contains("trap")) en.append(h("span", { class: "tag" }, "每个字都认识"));
      if (e.classList.contains("img")) en.append(h("span", { class: "tag img" }, "图里的"));
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
      const k = li.dataset.sec, key = `bt-sec-${id}-${k}`;
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

  // 本地笔记：<textarea class="note" data-key="01a-oneline">，输入即存到本机（键 bt-note-01a-oneline）
  function wireNotes() {
    for (const el of document.querySelectorAll("input.note, textarea.note")) {
      const key = `bt-note-${el.dataset.key}`;
      el.value = LS.get(key) || "";
      let tip = null;
      if (el.tagName === "TEXTAREA") { tip = h("div", { class: "note-tip" }, el.value ? "已保存在本机浏览器" : "写下来会自动保存在本机浏览器"); el.after(tip); }
      let t = null;
      el.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => { LS.set(key, el.value.trim() ? el.value : null); if (tip) tip.textContent = "已保存在本机浏览器"; }, 400); });
    }
  }

  // 首页：按原书的章分块的目录、进度、我的词本
  function mountHome() {
    const toc = document.getElementById("toc");
    if (!toc) return;
    toc.append(item(INTRO));
    for (const c of CH) {
      toc.append(h("li", { class: "blk" }, c.n === 10 ? "尾声" : `第 ${c.n} 章　${c.t}`, h("span", { class: "te" }, `　${c.en}`), c.d ? h("span", { class: "d" }, c.d) : null));
      for (const p of PAGES.filter((x) => x.ch === c.n)) toc.append(item(p));
    }
    function item(p) {
      const ready = READY.has(p.id), names = p.id === "00" ? "" : secsOf(p).map((s) => s.who || s.en).join(" · ");
      return h("li", {}, h("a", Object.assign({ class: (isDone(p.id) ? "done " : "") + (ready ? "" : "todo") }, ready ? { href: href(p.id) } : {}),
        h("span", { class: "n" }, isDone(p.id) ? "✓" : p.id === "00" ? "·" : p.ch === 10 ? "尾" : secRange(p)),
        h("span", { class: "t" }, p.t || (p.id === "00" ? "开读之前" : label(p)), h("span", { class: "te" }, p.id === "00" ? p.t : names)),
        h("span", { class: "b" }, ...(p.id === "00" ? [] : ready ? [h("span", { class: "badge" }, `约 ${p.words} 词`)] : [h("span", { class: "badge" }, "待写")])),
        p.d ? h("span", { class: "d" }, p.d, p.id === "00" ? null : secProgress(p)) : null));
    }
    const doneN = PAGES.filter((p) => isDone(p.id)).length;
    const pr = document.getElementById("progress");
    if (pr) pr.append(h("div", { class: "progress" }, Object.assign(h("i"), { style: `width:${(100 * doneN) / PAGES.length}%` })), h("p", { class: "lede" }, `已读完 ${doneN} / ${PAGES.length} 页`));
    const wb = document.getElementById("wordbook");
    if (wb) {
      const keys = LS.keys("bt-star-").sort();
      if (!keys.length) wb.append(h("p", { class: "lede" }, "还是空的。在各页里点词条右边的「记下」，它们会汇总到这里。"));
      for (const k of keys) {
        const m = k.match(/^bt-star-(\w+?)-(.*)$/); if (!m || !find(m[1])) continue;
        let zh = ""; try { zh = JSON.parse(LS.get(k)).zh; } catch {}
        wb.append(h("div", {}, h("b", {}, m[2]), h("span", {}, zh), h("a", { href: href(m[1]) }, label(find(m[1])))));
      }
    }
  }

  async function fetchPage(id) {
    try { return new DOMParser().parseFromString(await (await fetch(href(id))).text(), "text/html"); } catch { return null; }
  }
  // 全书回顾（recap.html 的 #recap）：读各个已完成页的「精彩回顾」，按原书顺序汇总
  async function mountRecap() {
    const box = document.getElementById("recap");
    if (!box) return;
    let shown = 0, lastCh = 0;
    for (const p of PAGES) {
      if (!READY.has(p.id)) continue;
      const doc = await fetchPage(p.id); if (!doc) continue;
      const line = doc.querySelector(".recall-line"), items = doc.querySelector(".recall");
      if (!items) continue;
      if (p.ch !== lastCh) { lastCh = p.ch; const c = chOf(p); box.append(h("h2", { class: "recap-part" }, c.n === 10 ? "尾声" : `第 ${c.n} 章　${c.t}`)); }
      for (const a of items.querySelectorAll(".sec")) a.replaceWith(h("a", { class: "sec", href: href(p.id) }, a.textContent));
      box.append(h("section", { class: "recap-ch" },
        h("h3", {}, h("a", { href: href(p.id) }, title(p))),
        h("p", { class: "lede" }, secsOf(p).map((s) => s.who || s.en).join(" · ")),
        line ? document.importNode(line, true) : null, document.importNode(items, true)));
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
  // 上线前要把 bt- 加进 sync.js 的 PREFIXES 和 sync_server.py 的 KEY_RE，见 ~/tutorials-deploy/README.md。
  try { if (location.hostname === "t.miaowuao.cn" || localStorage.getItem("sync-dev")) document.head.append(Object.assign(document.createElement("script"), { src: "/_home/sync.js" })); } catch (e) {}
  window.BT = { h, LS, ROOT, href, label, isDone };
})();
