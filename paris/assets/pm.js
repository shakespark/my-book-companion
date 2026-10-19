// Paris to the Moon · 导读：共享脚本。注入顶栏、篇头、篇末导航、页脚；接管分节地图的打勾、词条的"记下"和筛选、本地笔记；首页目录和全书回顾。
// 页 id 是两位数：00 是「开读之前」，01–23 是各篇。localStorage 键一律带 pm- 前缀（全站各教程同一个域名）：
// pm-done-NN、pm-sec-NN-节号、pm-star-NN-词条、pm-note-NN-…、pm-theme。
(() => {
  const CH = window.PM_CHAPTERS || [], PARTS = window.PM_PARTS || [], READY = new Set(window.PM_READY || []);
  const ROOT = document.currentScript.src.replace(/assets\/pm\.js.*$/, "");
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
  const chHref = (n) => `${ROOT}chapters/${pad(n)}.html`;
  const chLabel = (n) => (n === 0 ? "开读之前" : `第 ${n} 篇`);
  const chTitle = (c) => `${chLabel(c.n)} · ${c.t}`;
  const isDone = (n) => LS.get(`pm-done-${pad(n)}`) === "1";
  const secDone = (n, k) => LS.get(`pm-sec-${pad(n)}-${k}`) === "1";
  const INTRO = { n: 0, part: 0, t: "这本书、这家人、这五年", en: "", words: 0, secs: 0, d: "作者是谁，一家人什么时候来、什么时候走，这五年法国发生了什么" };
  const find = (n) => (n === 0 ? INTRO : CH.find((x) => x.n === n));
  const badges = (c) => [
    c.journal ? h("span", { class: "badge k-journal" }, "圣诞日记") : null,
    h("span", { class: "badge" }, `英文约 ${c.words} 词 · ${c.secs} 节`),
  ];

  const saved = LS.get("pm-theme");
  if (saved) document.documentElement.dataset.theme = saved;
  function themeBtn() {
    return h("button", { class: "btn", "aria-label": "切换深色/浅色", onclick() {
      const dark = document.documentElement.dataset.theme ? document.documentElement.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
      const next = dark ? "light" : "dark";
      document.documentElement.dataset.theme = next; LS.set("pm-theme", next);
    } }, "深/浅");
  }

  function mountChrome() {
    const n = document.body.dataset.page == null ? null : Number(document.body.dataset.page);
    const c = n == null ? null : find(n);
    document.body.prepend(h("div", { class: "topbar" }, h("div", { class: "topbar-inner" },
      h("a", { class: "home", href: `${ROOT}index.html` }, "Paris to the Moon · 导读"),
      h("span", { class: "crumb" }, c ? chTitle(c) : ""),
      themeBtn())));
    document.body.append(h("footer", { class: "site-footer" },
      h("a", { href: "https://beian.miit.gov.cn/", target: "_blank", rel: "noopener" }, "京ICP备18057656号-1")));
    if (!c) return;
    const main = document.querySelector("main");
    document.title = `${chTitle(c)} · Paris to the Moon 导读`;
    const part = PARTS[c.part - 1];
    main.prepend(h("div", { class: "chapter-head" },
      h("div", { class: "kicker" }, part ? `第 ${c.part} 部分 ${part.en} · ${c.en}` : "Paris to the Moon"),
      h("h1", {}, `${chLabel(n)}　${c.t}`),
      n ? h("div", { class: "by" }, `原题 ${c.en}（中文是本站译的）`, c.zh ? `　·　译本篇名：${c.zh}` : null, c.ny ? `　·　原载《纽约客》${c.ny}` : null) : null,
      n ? h("div", { class: "badges" }, ...badges(c)) : null));
    const order = [0, ...CH.map((x) => x.n)];
    const i = order.indexOf(n), prev = order[i - 1], next = order[i + 1];
    const done = h("button", { class: "btn" });
    const paint = () => { done.textContent = isDone(n) ? `✓ 已读完这${n ? "一篇" : "一页"}` : `标记：这${n ? "一篇" : "一页"}读完了`; done.setAttribute("aria-pressed", isDone(n)); };
    done.onclick = () => { LS.set(`pm-done-${pad(n)}`, isDone(n) ? null : "1"); paint(); };
    paint();
    main.append(h("div", { class: "chapter-end" }, done, h("div", { class: "nav" },
      prev != null && READY.has(prev) ? h("a", { class: "btn", href: chHref(prev) }, `← ${chLabel(prev)}`) : null,
      h("a", { class: "btn", href: `${ROOT}index.html` }, "目录"),
      next != null && READY.has(next) ? h("a", { class: "btn primary", href: chHref(next) }, `${chLabel(next)} →`) : null)));
  }

  // 词条：<div class="entry [trap]"><div class="en">…</div><div class="loc" data-p="段号">原句里的 4–7 个词</div><div class="zh">…</div><div class="note">…</div></div>
  function wireEntries() {
    const entries = [...document.querySelectorAll(".entry")];
    if (!entries.length) return;
    const n = pad(Number(document.body.dataset.page));
    const first = entries[0];
    const count = h("span", { class: "count" });
    const mk = (label, cls) => h("button", { class: "btn", "aria-pressed": String(!cls), onclick(e) {
      document.body.classList.remove("only-traps", "only-starred");
      if (cls) document.body.classList.add(cls);
      bar.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b === e.currentTarget)));
    } }, label);
    const bar = h("div", { class: "toolbar" }, mk("全部", ""), mk("只看「每个字都认识」", "only-traps"), mk("只看我记下的", "only-starred"), count);
    (first.previousElementSibling?.matches("h3.sec-head") ? first.previousElementSibling : first).before(bar, h("p", { class: "empty-note" }, "还没有记下任何词条。回到「全部」，点词条右边的「记下」。"));
    const refresh = () => {
      const k = entries.filter((e) => e.classList.contains("starred")).length;
      document.body.classList.toggle("none-starred", k === 0);
      count.textContent = `共 ${entries.length} 条 · 已记下 ${k}`;
    };
    for (const e of entries) {
      const en = e.querySelector(".en"), text = en.textContent.trim();
      const key = `pm-star-${n}-${text}`;
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

  // 分节地图：<ol class="secmap"><li class="sit">第一次坐下 …</li><li data-sec="1"><b>中文地标</b><span class="en">英文开头…</span>…</li>…</ol>
  // 每节前面加一个"读过了"的勾，并链到词条里对应的 #sK；li.sit 是"一次坐下读到哪"的分隔，不打勾。
  function wireSecmap() {
    const n = Number(document.body.dataset.page);
    for (const li of document.querySelectorAll(".secmap li[data-sec]")) {
      const k = li.dataset.sec, key = `pm-sec-${pad(n)}-${k}`;
      const box = h("input", { type: "checkbox", "aria-label": `第 ${k} 节读过了` });
      box.checked = secDone(n, k); li.classList.toggle("done", box.checked);
      box.onchange = () => { LS.set(key, box.checked ? "1" : null); li.classList.toggle("done", box.checked); };
      li.prepend(box, h("span", { class: "k" }, `§${k}`));
      if (document.getElementById(`s${k}`)) li.append(h("a", { class: "jump", href: `#s${k}` }, "词条 ↓"));
    }
  }
  const secProgress = (c) => {
    const k = Array.from({ length: c.secs }, (_, i) => i + 1).filter((i) => secDone(c.n, i)).length;
    return k && !isDone(c.n) ? h("span", { class: "sp" }, `　已读 ${k} 节`) : null;
  };

  // 本地笔记：<input class="note" data-key="01-f1"> / <textarea class="note" data-key="01-oneline">，输入即存到本机（键 pm-note-01-f1）
  function wireNotes() {
    for (const el of document.querySelectorAll("input.note, textarea.note")) {
      const key = `pm-note-${el.dataset.key}`;
      el.value = LS.get(key) || "";
      let tip = null;
      if (el.tagName === "TEXTAREA") { tip = h("div", { class: "note-tip" }, el.value ? "已保存在本机浏览器" : "写下来会自动保存在本机浏览器"); el.after(tip); }
      let t = null;
      el.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => { LS.set(key, el.value.trim() ? el.value : null); if (tip) tip.textContent = "已保存在本机浏览器"; }, 400); });
    }
  }

  // 首页：按原书四部分分块的目录、进度、我的词本
  function mountHome() {
    const toc = document.getElementById("toc");
    if (!toc) return;
    toc.append(item(INTRO));
    PARTS.forEach((p, i) => {
      toc.append(h("li", { class: "blk" }, `第 ${i + 1} 部分　${p.t}`, h("span", { class: "te" }, `　${p.en}` + (p.zh ? `　译本：${p.zh}` : "")), p.d ? h("span", { class: "d" }, p.d) : null));
      for (const c of CH.filter((x) => x.part === i + 1)) toc.append(item(c));
    });
    function item(c) {
      const ready = READY.has(c.n);
      return h("li", {}, h("a", Object.assign({ class: (isDone(c.n) ? "done " : "") + (ready ? "" : "todo") }, ready ? { href: chHref(c.n) } : {}),
        h("span", { class: "n" }, isDone(c.n) ? "✓" : c.n ? String(c.n) : "·"),
        h("span", { class: "t" }, c.n ? c.t : chLabel(0), h("span", { class: "te" }, c.n ? c.en + (c.zh ? `　译本：${c.zh}` : "") : c.t)),
        h("span", { class: "b" }, ...(c.n ? (ready ? badges(c) : [c.journal ? h("span", { class: "badge k-journal" }, "圣诞日记") : null, h("span", { class: "badge" }, "待写")]) : [])),
        c.d ? h("span", { class: "d" }, c.d, c.n ? secProgress(c) : null) : null));
    }
    const doneN = CH.filter((c) => isDone(c.n)).length;
    const p = document.getElementById("progress");
    if (p) p.append(h("div", { class: "progress" }, Object.assign(h("i"), { style: `width:${(100 * doneN) / CH.length}%` })), h("p", { class: "lede" }, `已读完 ${doneN} / ${CH.length} 篇`));
    const wb = document.getElementById("wordbook");
    if (wb) {
      const keys = LS.keys("pm-star-").sort();
      if (!keys.length) wb.append(h("p", { class: "lede" }, "还是空的。在各篇的页面里点词条右边的「记下」，它们会汇总到这里。"));
      for (const k of keys) {
        const m = k.match(/^pm-star-(\d\d)-(.*)$/); if (!m) continue;
        let zh = ""; try { zh = JSON.parse(LS.get(k)).zh; } catch {}
        wb.append(h("div", {}, h("b", {}, m[2]), h("span", {}, zh), h("a", { href: chHref(Number(m[1])) }, chLabel(Number(m[1])))));
      }
    }
  }

  // 全书回顾（recap.html 的 #recap）：读各个已完成篇目页的「精彩回顾」，按原书顺序汇总。篇目页改了，这里自动跟着变。
  async function mountRecap() {
    const box = document.getElementById("recap");
    if (!box) return;
    let shown = 0, lastPart = 0;
    for (const c of CH) {
      if (!READY.has(c.n)) continue;
      let doc;
      try { doc = new DOMParser().parseFromString(await (await fetch(chHref(c.n))).text(), "text/html"); } catch { continue; }
      const line = doc.querySelector(".recall-line"), items = doc.querySelector(".recall");
      if (!items) continue;
      if (c.part !== lastPart) { lastPart = c.part; box.append(h("h2", { class: "recap-part" }, `第 ${c.part} 部分　${PARTS[c.part - 1].t}`)); }
      for (const a of items.querySelectorAll(".sec")) a.replaceWith(h("a", { class: "sec", href: chHref(c.n) }, a.textContent));
      box.append(h("section", { class: "recap-ch" },
        h("h3", {}, h("a", { href: chHref(c.n) }, chTitle(c))),
        h("p", { class: "lede" }, c.en + (c.zh ? `　译本：${c.zh}` : "")),
        line ? document.importNode(line, true) : null, document.importNode(items, true)));
      shown++;
    }
    if (!shown) box.append(h("p", { class: "lede" }, "还没有写好的篇目。"));
  }

  document.addEventListener("DOMContentLoaded", () => { mountChrome(); wireSecmap(); wireEntries(); wireNotes(); mountHome(); mountRecap(); });
  // 跨设备同步：模块在首页仓库里（/_home/sync.js），所有教程站共用。只在线上加载；本地预览要联调时设 localStorage["sync-dev"] = "1"
  // 上线前要把 pm- 加进 sync.js 的 PREFIXES 和 sync_server.py 的 KEY_RE，见 ~/tutorials-deploy/README.md。
  try { if (location.hostname === "t.miaowuao.cn" || localStorage.getItem("sync-dev")) document.head.append(Object.assign(document.createElement("script"), { src: "/_home/sync.js" })); } catch (e) {}
  window.PM = { h, LS, ROOT, chHref, chLabel, isDone };
})();
