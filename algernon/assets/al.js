// Flowers for Algernon · 导读：共享脚本。注入顶栏、页头、页末导航、页脚；读前 / 读后分界；分节地图的打勾、词条的「记下」和筛选、本地笔记；
// 查理的文字曲线、记忆拼图、全书回顾（这三样都只揭开到读者标记读完的页）；首页目录。
// 页 id 见 chapters.js：00 是「开读之前」，01、07、09…17b 是小说页，m1–m7 是回忆录页，nv 是中篇和长篇对照。
// localStorage 键一律带 al- 前缀（全站各教程同一个域名）：al-done-页、al-after-页、al-sec-页-节号、al-star-页-词条、al-note-页-…、al-curve-指标、al-theme。
(() => {
  const PAGES = window.AL_PAGES || [], MPARTS = window.AL_MEMOIR_PARTS || [], READY = new Set(window.AL_READY || []);
  const ROOT = document.currentScript.src.replace(/assets\/al\.js.*$/, "");
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
  const SVGNS = "http://www.w3.org/2000/svg";
  const s = (tag, attrs = {}, text) => {
    const el = document.createElementNS(SVGNS, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
    if (text != null) el.textContent = text;
    return el;
  };
  const INTRO = { id: "00", kind: "intro", t: "这本书、这个人、这两本书", d: "作者是谁，中篇和长篇，查理的世界，怎么用本站" };
  const ALL = [INTRO, ...PAGES];
  const byId = (id) => ALL.find((x) => x.id === id);
  const order = (id) => ALL.findIndex((x) => x.id === id);
  const href = (id) => `${ROOT}chapters/${id}.html`;
  const isDone = (id) => LS.get(`al-done-${id}`) === "1";
  const secDone = (id, k) => LS.get(`al-sec-${id}-${k}`) === "1";
  const range = (a) => (a.length > 1 ? `${a[0]}–${a[a.length - 1]}` : `${a[0]}`);
  const label = (c) => c.kind === "novel" ? `报告 ${range(c.r)}` + (c.id.match(/[a-z]$/) ? `（${{ a: "一", b: "二", c: "三" }[c.id.slice(-1)]}）` : "")
    : c.kind === "memoir" ? `回忆录 ${c.ch.includes(24) ? `第 ${c.ch[0]}–23 章和后记` : `第 ${range(c.ch)} 章`}`
    : c.kind === "intro" ? "开读之前" : c.t;
  const title = (c) => (c.t && c.kind !== "extra" && c.kind !== "intro" ? `${label(c)} · ${c.t}` : label(c));
  // 小说读到哪：读者标记读完的小说页里最靠后的那一页（跨页汇总的东西只揭开到这里）
  const novel = PAGES.filter((c) => c.kind === "novel");
  const reachedIdx = () => novel.reduce((m, c, i) => (isDone(c.id) ? i : m), -1);

  const saved = LS.get("al-theme");
  if (saved) document.documentElement.dataset.theme = saved;
  function themeBtn() {
    return h("button", { class: "btn", "aria-label": "切换深色/浅色", onclick() {
      const dark = document.documentElement.dataset.theme ? document.documentElement.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
      const next = dark ? "light" : "dark";
      document.documentElement.dataset.theme = next; LS.set("al-theme", next);
    } }, "深/浅");
  }
  const badges = (c) => [
    c.kind === "memoir" ? h("span", { class: "badge k-memoir" }, "回忆录") : null,
    c.words ? h("span", { class: "badge" }, `英文约 ${c.words} 词 · ${c.secs} 节`) : null,
  ];

  function mountChrome() {
    const id = document.body.dataset.page, c = id ? byId(id) : null;
    document.body.prepend(h("div", { class: "topbar" }, h("div", { class: "topbar-inner" },
      h("a", { class: "home", href: `${ROOT}index.html` }, "Flowers for Algernon · 导读"),
      h("span", { class: "crumb" }, c ? title(c) : ""),
      themeBtn())));
    document.body.append(h("footer", { class: "site-footer" },
      h("a", { href: "https://beian.miit.gov.cn/", target: "_blank", rel: "noopener" }, "京ICP备18057656号-1")));
    if (!c) return;
    const main = document.querySelector("main");
    document.title = `${title(c)} · Flowers for Algernon 导读`;
    const kicker = c.kind === "novel" ? `小说 · ${c.when}` : c.kind === "memoir" ? `回忆录 Algernon, Charlie, and I · ${MPARTS.filter((p) => c.ch.some((x) => x >= p.ch[0] && x <= p.ch[1])).map((p) => p.en).join(" / ")}` : "Flowers for Algernon";
    main.prepend(h("div", { class: "chapter-head" },
      h("div", { class: "kicker" }, kicker),
      h("h1", {}, c.t && c.kind !== "intro" && c.kind !== "extra" ? `${label(c)}　${c.t}` : label(c)),
      c.kind === "novel" ? h("div", { class: "by" }, `译本：${c.zh}`) : null,
      c.words ? h("div", { class: "badges" }, ...badges(c)) : null));
    const i = order(id);
    const prev = ALL.slice(0, i).reverse().find((x) => x.id === "00" || READY.has(x.id));
    const next = ALL.slice(i + 1).find((x) => READY.has(x.id));
    const done = h("button", { class: "btn" });
    const paint = () => { done.textContent = isDone(id) ? "✓ 已读完这一页" : "标记：这一页的原文读完了"; done.setAttribute("aria-pressed", isDone(id)); };
    done.onclick = () => { LS.set(`al-done-${id}`, isDone(id) ? null : "1"); paint(); };
    paint();
    main.append(h("div", { class: "chapter-end" }, done, h("div", { class: "nav" },
      prev ? h("a", { class: "btn", href: href(prev.id) }, `← ${label(prev)}`) : null,
      h("a", { class: "btn", href: `${ROOT}index.html` }, "目录"),
      next ? h("a", { class: "btn primary", href: href(next.id) }, `${label(next)} →`) : null)));
  }

  // 读前 / 读后分界：<section class="after"> 里是讲这一页情节的内容，默认收起；读完点一下才展开（记在 al-after-页），标记读完的页自动展开
  function wireGate() {
    const after = document.querySelector("section.after");
    if (!after) return;
    const id = document.body.dataset.page, key = `al-after-${id}`;
    const open = () => { document.body.classList.remove("after-locked"); LS.set(key, "1"); mountCurves(); };
    if (!LS.get(key) && !isDone(id)) document.body.classList.add("after-locked");
    after.before(h("div", { class: "gate" },
      h("b", {}, "读前部分到这里。先去读原书的这一段"),
      h("span", {}, "下面会讲到这一页的情节：查理的文字怎么变了、他想起了什么、讨论和回顾。"),
      h("button", { class: "btn primary", onclick: open }, "这一段我读完了，展开")));
  }

  // 分节地图：<ol class="secmap"><li class="sit">第一次坐下…</li><li data-sec="1"><b>日期</b>…</li>…</ol>；每节加「读过了」的勾，链到词条里的 #sK
  function wireSecmap() {
    const id = document.body.dataset.page;
    for (const li of document.querySelectorAll(".secmap li[data-sec]")) {
      const k = li.dataset.sec, key = `al-sec-${id}-${k}`;
      const box = h("input", { type: "checkbox", "aria-label": `第 ${k} 节读过了` });
      box.checked = secDone(id, k); li.classList.toggle("done", box.checked);
      box.onchange = () => { LS.set(key, box.checked ? "1" : null); li.classList.toggle("done", box.checked); };
      li.prepend(box, h("span", { class: "k" }, `§${k}`));
      if (document.getElementById(`s${k}`)) li.append(h("a", { class: "jump", href: `#s${k}` }, "词条 ↓"));
    }
  }
  const secProgress = (c) => {
    const k = Array.from({ length: c.secs || 0 }, (_, i) => i + 1).filter((i) => secDone(c.id, i)).length;
    return k && !isDone(c.id) ? h("span", { class: "sp" }, `　已读 ${k} 节`) : null;
  };

  // 词条：<div class="entry [trap|spell]"><div class="en">…</div><div class="loc" data-p="段号">原句里的 4–7 个词</div><div class="zh">…</div><div class="note">…</div></div>
  // spell 是查理拼错的词（.en 照书里的拼法，.zh 写还原的拼法和意思）
  function wireEntries() {
    const entries = [...document.querySelectorAll(".entry")];
    if (!entries.length) return;
    const id = document.body.dataset.page;
    const first = entries[0];
    const count = h("span", { class: "count" });
    const mk = (text, cls) => h("button", { class: "btn", "aria-pressed": String(!cls), onclick(e) {
      document.body.classList.remove("only-traps", "only-spell", "only-starred");
      if (cls) document.body.classList.add(cls);
      bar.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b === e.currentTarget)));
    } }, text);
    const hasSpell = entries.some((e) => e.classList.contains("spell"));
    const bar = h("div", { class: "toolbar" }, mk("全部", ""), mk("只看「每个字都认识」", "only-traps"), hasSpell ? mk("只看拼错的", "only-spell") : null, mk("只看我记下的", "only-starred"), count);
    (first.previousElementSibling?.matches("h3.sec-head") ? first.previousElementSibling : first).before(bar, h("p", { class: "empty-note" }, "还没有记下任何词条。回到「全部」，点词条右边的「记下」。"));
    const refresh = () => {
      const k = entries.filter((e) => e.classList.contains("starred")).length;
      document.body.classList.toggle("none-starred", k === 0);
      count.textContent = `共 ${entries.length} 条 · 已记下 ${k}`;
    };
    for (const e of entries) {
      const en = e.querySelector(".en"), text = en.textContent.trim();
      const key = `al-star-${id}-${text}`;
      if (e.classList.contains("trap")) en.append(h("span", { class: "tag" }, "每个字都认识"));
      if (e.classList.contains("spell")) en.append(h("span", { class: "tag spell" }, "查理拼的"));
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

  // 本地笔记：<textarea class="note" data-key="09-oneline">，输入即存到本机（键 al-note-09-oneline）
  function wireNotes() {
    for (const el of document.querySelectorAll("input.note, textarea.note")) {
      const key = `al-note-${el.dataset.key}`;
      el.value = LS.get(key) || "";
      let tip = null;
      if (el.tagName === "TEXTAREA") { tip = h("div", { class: "note-tip" }, el.value ? "已保存在本机浏览器" : "写下来会自动保存在本机浏览器"); el.after(tip); }
      let t = null;
      el.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => { LS.set(key, el.value.trim() ? el.value : null); if (tip) tip.textContent = "已保存在本机浏览器"; }, 400); });
    }
  }

  // 查理的文字曲线：<div class="curve"></div>。数据 window.AL_CURVE 由 tools/curve.py 生成（每条报告条目一个点）。
  // 在小说页里画到这一页为止，这一页的点加亮；在 curve.html（<div class="curve" data-all>）里画到读者标记读完的最后一页。
  const METRICS = [
    { k: "miss", t: "拼错的词", u: "%", max: 20, tip: "不在英文词表里的小写词占百分之几（人名不算；丢了撇号的 dont、im 算错）" },
    { k: "punct", t: "标点", u: "个 / 百词", max: 12, tip: "每一百个词里有几个逗号、分号、冒号、破折号" },
    { k: "long", t: "长词", u: "%", max: 8, tip: "九个字母以上的词占百分之几，粗看用词有多「学术」" },
    { k: "sent", t: "句长", u: "词", max: 30, tip: "平均每句多少个词（按句号、问号、叹号断句）" },
  ];
  function mountCurves() {
    const data = window.AL_CURVE || [];
    for (const box of document.querySelectorAll(".curve")) {
      if (box.dataset.drawn || !data.length || box.offsetParent === null) continue;
      box.dataset.drawn = "1";
      const page = document.body.dataset.page;
      const upto = box.hasAttribute("data-all") ? reachedIdx() : novel.findIndex((c) => c.id === page);
      const pts = data.filter((p) => novel.findIndex((c) => c.id === p.p) <= upto);
      if (!pts.length) { box.append(h("p", { class: "lede" }, "还没有标记读完的小说页。读完一页、在页末点「标记」之后，这里会画出到那一页为止的曲线。")); continue; }
      let m = METRICS.find((x) => x.k === LS.get("al-curve-metric")) || METRICS[0];
      const svgBox = h("div", { class: "curve-svg" }), tip = h("p", { class: "curve-tip" });
      const btns = METRICS.map((x) => h("button", { class: "btn", "aria-pressed": String(x === m), onclick() { m = x; LS.set("al-curve-metric", x.k); btns.forEach((b, i) => b.setAttribute("aria-pressed", String(METRICS[i] === m))); draw(); } }, x.t));
      box.append(h("div", { class: "toolbar" }, ...btns), svgBox, tip);
      const draw = () => {
        const W = 640, H = 220, L = 40, R = 12, T = 14, B = 34, n = data.length;
        const x = (i) => L + (i / Math.max(1, n - 1)) * (W - L - R), y = (v) => T + (1 - Math.min(v, m.max) / m.max) * (H - T - B);
        const svg = s("svg", { class: "diagram curve-chart", viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": `查理的文字曲线：${m.t}` });
        for (let g = 0; g <= 4; g++) {
          const v = (m.max / 4) * g;
          svg.append(s("line", { class: "ln-d", x1: L, x2: W - R, y1: y(v), y2: y(v) }), s("text", { class: "t-m", x: L - 6, y: y(v) + 4, "text-anchor": "end" }, String(Math.round(v))));
        }
        let lastR = 0;
        data.forEach((p, i) => {
          if (p.r !== lastR && [1, 7, 9, 11, 13, 15, 17].includes(p.r)) svg.append(s("text", { class: "t-m", x: x(i), y: H - 10, "text-anchor": "middle" }, String(p.r)));
          lastR = p.r;
        });
        svg.append(s("text", { class: "t-m", x: W - R, y: H - 10, "text-anchor": "end" }, "报告"));
        const idx = (p) => data.indexOf(p);
        svg.append(s("polyline", { class: "curve-line", points: pts.map((p) => `${x(idx(p))},${y(p[m.k])}`).join(" ") }));
        for (const p of pts) {
          const c = s("circle", { class: p.p === page && !box.hasAttribute("data-all") ? "curve-dot here" : "curve-dot", cx: x(idx(p)), cy: y(p[m.k]), r: p.p === page ? 4 : 2.6 });
          c.append(s("title", {}, `报告 ${p.r} · ${p.d}：${p[m.k]}${m.u}（${p.w} 词）`));
          svg.append(c);
        }
        if (pts.length < n) svg.append(s("text", { class: "t-m", x: W - R, y: T + 10, "text-anchor": "end" }, "后面的还没读到"));
        svgBox.replaceChildren(svg);
        tip.textContent = `${m.t}（${m.u}）：${m.tip}。超过 ${m.max} 的点画在顶上。`;
      };
      draw();
    }
  }

  // 首页：开读之前、小说（按报告）、回忆录（按部分）、专页
  function mountHome() {
    const toc = document.getElementById("toc");
    if (!toc) return;
    const item = (c) => {
      const ready = c.id === "00" || READY.has(c.id);
      return h("li", {}, h("a", Object.assign({ class: (isDone(c.id) ? "done " : "") + (ready ? "" : "todo") }, ready ? { href: href(c.id) } : {}),
        h("span", { class: "n" }, isDone(c.id) ? "✓" : c.kind === "novel" ? c.id : c.kind === "memoir" ? c.id.slice(1) : "·"),
        h("span", { class: "t" }, c.kind === "intro" || c.kind === "extra" ? c.t : c.t || label(c), h("span", { class: "te" }, c.kind === "novel" ? `${label(c)} · ${c.when}` : c.kind === "memoir" ? label(c) : "")),
        h("span", { class: "b" }, ...(ready ? badges(c) : [c.kind === "memoir" ? h("span", { class: "badge k-memoir" }, "回忆录") : null, h("span", { class: "badge" }, "待写")])),
        c.d ? h("span", { class: "d" }, c.d, secProgress(c)) : null));
    };
    toc.append(item(INTRO));
    toc.append(h("li", { class: "blk" }, "小说　Flowers for Algernon（1966）", h("span", { class: "d" }, "查理的 17 篇进步报告。长的报告本站拆成几页")));
    for (const c of PAGES.filter((x) => x.kind === "novel")) toc.append(item(c));
    toc.append(h("li", { class: "blk" }, "回忆录　Algernon, Charlie, and I（2004）", h("span", { class: "d" }, "作者讲这部小说从哪里来、怎么写成。读完小说再看")));
    for (const c of PAGES.filter((x) => x.kind !== "novel")) toc.append(item(c));
    const doneN = novel.filter((c) => isDone(c.id)).length;
    const p = document.getElementById("progress");
    if (p) p.append(h("div", { class: "progress" }, Object.assign(h("i"), { style: `width:${(100 * doneN) / novel.length}%` })), h("p", { class: "lede" }, `小说已读完 ${doneN} / ${novel.length} 页`));
    const wb = document.getElementById("wordbook");
    if (wb) {
      const keys = LS.keys("al-star-").sort();
      if (!keys.length) wb.append(h("p", { class: "lede" }, "还是空的。在各页里点词条右边的「记下」，它们会汇总到这里。"));
      for (const k of keys) {
        const mm = k.match(/^al-star-([0-9a-z]+)-(.*)$/); if (!mm) continue;
        let zh = ""; try { zh = JSON.parse(LS.get(k)).zh; } catch {}
        const c = byId(mm[1]);
        wb.append(h("div", {}, h("b", {}, mm[2]), h("span", {}, zh), h("a", { href: href(mm[1]) }, c ? label(c) : mm[1])));
      }
    }
  }

  // 从已读完的页里收集一类块（精彩回顾、记忆拼图），页面改了这里自动跟着变。只收标记读完的页，没读到的页只报个数。
  async function gather(pred, sel) {
    const out = [];
    for (const c of PAGES) {
      if (!READY.has(c.id) || !pred(c)) continue;
      if (!isDone(c.id)) { out.push({ c, locked: true }); continue; }
      try {
        const doc = new DOMParser().parseFromString(await (await fetch(href(c.id))).text(), "text/html");
        out.push({ c, doc, nodes: [...doc.querySelectorAll(sel)] });
      } catch { /* 本地用 file:// 打开时取不到，跳过 */ }
    }
    return out;
  }
  const lockedNote = (n) => (n ? h("p", { class: "lede locked" }, `还有 ${n} 页没有标记读完，读完后这里会补上。`) : null);

  // 全书回顾（recap.html 的 #recap）
  async function mountRecap() {
    const box = document.getElementById("recap");
    if (!box) return;
    const got = await gather(() => true, ".recall");
    let shown = 0, locked = 0, lastKind = "";
    for (const g of got) {
      if (g.locked) { locked++; continue; }
      const line = g.doc.querySelector(".recall-line"), items = g.nodes[0];
      if (!items) continue;
      if (g.c.kind !== lastKind) { lastKind = g.c.kind; box.append(h("h2", { class: "recap-part" }, g.c.kind === "novel" ? "小说" : g.c.kind === "memoir" ? "回忆录" : "专页")); }
      for (const a of items.querySelectorAll(".sec")) a.replaceWith(h("a", { class: "sec", href: href(g.c.id) }, a.textContent));
      box.append(h("section", { class: "recap-ch" }, h("h3", {}, h("a", { href: href(g.c.id) }, title(g.c))),
        line ? document.importNode(line, true) : null, document.importNode(items, true)));
      shown++;
    }
    if (!shown) box.append(h("p", { class: "lede" }, "还没有标记读完的页。"));
    const ln = lockedNote(locked); if (ln) box.append(ln);
  }

  // 记忆拼图（memory.html 的 #memory）：小说页「记忆拼图」一节里的 <div class="mem" data-age="6">，按查理当时的年纪排成一条线
  async function mountMemory() {
    const box = document.getElementById("memory");
    if (!box) return;
    const got = await gather((c) => c.kind === "novel", ".mem");
    const cards = [];
    let locked = 0;
    for (const g of got) {
      if (g.locked) { locked++; continue; }
      for (const m of g.nodes) cards.push({ c: g.c, m, age: parseFloat(m.dataset.age) });
    }
    cards.sort((a, b) => (isNaN(a.age) ? 99 : a.age) - (isNaN(b.age) ? 99 : b.age) || order(a.c.id) - order(b.c.id));
    if (!cards.length) box.append(h("p", { class: "lede" }, "还没有标记读完、带记忆拼图的页。"));
    const list = h("ol", { class: "memline" });
    for (const { c, m, age } of cards) {
      const node = document.importNode(m, true);
      node.append(h("a", { class: "from", href: href(c.id) }, `想起于${label(c)}`));
      list.append(h("li", {}, h("span", { class: "age" }, isNaN(age) ? "年纪不详" : `约 ${age} 岁`), node));
    }
    box.append(list);
    const ln = lockedNote(locked); if (ln) box.append(ln);
  }

  document.addEventListener("DOMContentLoaded", () => {
    mountChrome(); wireGate(); wireSecmap(); wireEntries(); wireNotes(); mountCurves(); mountHome(); mountRecap(); mountMemory();
  });
  // 跨设备同步：模块在首页仓库里（/_home/sync.js），所有教程站共用。只在线上加载；本地预览要联调时设 localStorage["sync-dev"] = "1"
  // 上线前要把 al- 加进 sync.js 的 PREFIXES 和 sync_server.py 的 KEY_RE，见 ~/tutorials-deploy/README.md。
  try { if (location.hostname === "t.miaowuao.cn" || localStorage.getItem("sync-dev")) document.head.append(Object.assign(document.createElement("script"), { src: "/_home/sync.js" })); } catch (e) {}
  window.AL = { h, LS, ROOT, href, label, isDone };
})();
