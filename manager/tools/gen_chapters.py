#!/usr/bin/env python3
"""生成 assets/chapters.js：python3 -I tools/gen_chapters.py
读 source/text/NN.txt（原书：节、段号、纸书页码、词数、英文小标题和开头）、source/zh/NN.txt（译本：小節名、字数、开头几个字）、
source/SECS.tsv（主编定的本站节名、档、line）。页表写在下面 PAGES 里。
已有的 chapters.js 里每页的 t、d 和 MM_READY 保留（作者交稿后主编用 tools/accept.py 填的）。

节：每章 `## ` 前面的开头是 §0，之后第 k 个 `## ` 小标题是 §k；原书和译本的小标题一一对应（2026-10-27 核过：每章数目相同）。
引言没有小标题，整篇是 §0。结语并在第 10 章末尾，是 10 章的 §6。"""
import json, os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
S = lambda *p: os.path.join(ROOT, *p)

# 章号、原书章名、译本章名（译本目录照抄）
CHAPTERS = [(0, "Introduction: Great Managers Are Made, Not Born", "引言：好主管是後天養成，不是天生奇才"),
            (1, "What Is Management?", "什麼是管理？"), (2, "Your First Three Months", "新官上任三個月"),
            (3, "Leading a Small Team", "帶領小型團隊"), (4, "The Art of Feedback", "提供回饋的技巧"),
            (5, "Managing Yourself", "管理自己"), (6, "Amazing Meetings", "精彩會議"), (7, "Hiring Well", "雇用正確人選"),
            (8, "Making Things Happen", "讓事情發生"), (9, "Leading a Growing Team", "帶領成長中的團隊"),
            (10, "Nurturing Culture", "培養文化")]
# 页 id → 章。一章一页；引言是 in；结语在 10 页（10 章 §6）
PAGES = [("in", 0)] + [(f"{n:02d}", n) for n in range(1, 11)]
han = lambda s: len(re.findall(r"[一-鿿]", s))
PARA = re.compile(r"\[(\d+)(?: p(\w+))?\] (.*)$")


def en_secs(ch):
    secs, cur = [], None
    for x in open(S(f"source/text/{ch:02d}.txt"), encoding="utf-8").read().splitlines():
        if x.startswith(("## 脚注", "## 书后注释")): break
        if x.startswith("## ") or cur is None:
            cur = dict(k=len(secs), head=x[3:] if x.startswith("## ") else "", p=[], pg=[], w=0, first="")
            secs.append(cur)
            if x.startswith("## "): continue
        m = PARA.match(x)
        if not m: continue
        p, pg, t = int(m.group(1)), m.group(2), m.group(3)
        cur["p"].append(p)
        if pg and pg.isdigit(): cur["pg"].append(int(pg))
        if t.startswith("{F}"): continue
        body = re.sub(r"^\{\w\} ", "", t)
        cur["w"] += len(re.sub(r"\{[^}]*\}", "", body).split())
        if not cur["first"]:
            cur["first"] = " ".join(body.replace("*", "").split()[:6])
    return [s for s in secs if s["p"]]


def zh_secs(ch):
    secs, cur = [], None
    for x in open(S(f"source/zh/{ch:02d}.txt"), encoding="utf-8").read().splitlines():
        if x.startswith("## 注"): break
        if x.startswith("# "): continue
        if (x.startswith("## ") and ch != 0) or cur is None:
            cur = dict(head=x[3:] if x.startswith("## ") and ch != 0 else "", paras=[])
            secs.append(cur)
            if x.startswith("## "): continue
        m = re.match(r"\[\d+\] (.*)$", x)
        if m: cur["paras"].append(m.group(1))
    return [s for s in secs if s["paras"] or s["head"]]


def opening(paras):
    """译本这一节第一段的开头几个字：一字不差，读者在译本电子书里搜它。取到第一个标点（至少 6 个字），最多 12 个字。"""
    for x in paras:
        s = re.sub(r"^\{\w\} ", "", x.strip()).replace("*", "")
        if han(s) < 4: continue
        m = re.match(r"[^，。：；！？、「」『』“”‘’（）《》—…,.:;!?\s]{6,}", s)
        return re.split(r"[（(]", (m.group(0) if m else s)[:12])[0].strip()
    return ""


tab = {}
if os.path.exists(S("source/SECS.tsv")):
    for line in open(S("source/SECS.tsv"), encoding="utf-8").read().splitlines()[1:]:
        if not line.strip(): continue
        ch, k, t, tier, ln = (line.split("\t") + [""] * 5)[:5]
        tab[(int(ch), int(k))] = dict(t=t, tier=tier, line=ln)

old = open(S("assets/chapters.js"), encoding="utf-8").read() if os.path.exists(S("assets/chapters.js")) else ""
keep = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r'\{ id: "(\w+)",.*?t: "([^"]*)", d: "([^"]*)" \}', old)}
m = re.search(r"window\.MM_READY = (\[.*?\]);", old)
ready = json.loads(m.group(1)) if m else []

SECS, PG = {}, {}
for ch, _, _ in CHAPTERS:
    pg = {}
    for x in open(S(f"source/text/{ch:02d}.txt"), encoding="utf-8").read().splitlines():
        m = PARA.match(x)
        if m and m.group(2) and m.group(2).isdigit(): pg[int(m.group(1))] = int(m.group(2))
    PG[f"{ch:02d}"] = [pg.get(i, 0) for i in range(max(pg) + 1)]
    E, Z = en_secs(ch), zh_secs(ch)
    if ch == 0: Z = [dict(head="", paras=sum((z["paras"] for z in Z), []))]
    assert len(E) == len(Z), f"第 {ch} 章：原书 {len(E)} 节，译本 {len(Z)} 节"
    rows = []
    for e, z in zip(E, Z):
        r = dict(k=e["k"], p=[min(e["p"]), max(e["p"])], pg=[min(e["pg"]), max(e["pg"])], w=e["w"],
                 en=e["head"] or ("Introduction" if ch == 0 else "（开头，第一个小标题之前）"), eo=e["first"],
                 zh=z["head"] or ("引言" if ch == 0 else "（開頭）"), zs=opening(z["paras"]), zw=sum(han(x) for x in z["paras"]))
        r.update(tab.get((ch, e["k"]), dict(t="", tier="", line="")))
        rows.append(r)
    SECS[f"{ch:02d}"] = rows

js = ["// 全站目录。tools/gen_chapters.py 生成，别手改节表；每页的 t、d 和 MM_READY 由 tools/accept.py 填（重新生成时保留）。页 id 和 tools/lint.py 用同一套（lint 从这里读）。",
      "// MM_CHAPTERS：引言（0）和十章。en 原书章名，t 译本章名。结语并在第 10 章末尾（10 章 §6）。",
      "// MM_SECS：每章的节。§0 是第一个小标题之前的开头，§k 是第 k 个小标题（原书和译本一一对应）。k 节号，p 段号范围（source/text/NN.txt 的 [k]），",
      "//   pg 纸书页码范围，w 英文词数，en 原书小标题，eo 这一节英文开头几个词，zh 译本小標題，zs 这一节在译本里开头的几个字（在译本电子书里搜它），zw 译本字数，",
      "//   t 本站中文节名，tier 档（先读 / 有空 / 可跳过），line 这一节起什么作用。",
      "// MM_PAGES：页，一章一页（引言是 in）。t 本站标题（不超过 10 个字），d 一句话（不超过 24 个字）。"]
js.append("window.MM_CHAPTERS = [")
for n, e, t in CHAPTERS:
    js.append(f'  {{ n: {n}, en: {json.dumps(e)}, t: {json.dumps(t, ensure_ascii=False)} }},')
js.append("];")
js.append("window.MM_SECS = {")
for ch, rows in SECS.items():
    js.append(f'  "{ch}": [')
    for r in rows:
        js.append(f'    {{ k: {r["k"]}, p: [{r["p"][0]}, {r["p"][1]}], pg: [{r["pg"][0]}, {r["pg"][1]}], w: {r["w"]}, zw: {r["zw"]}, '
                  f't: {json.dumps(r["t"], ensure_ascii=False)}, tier: {json.dumps(r["tier"], ensure_ascii=False)}, '
                  f'en: {json.dumps(r["en"], ensure_ascii=False)}, eo: {json.dumps(r["eo"], ensure_ascii=False)}, '
                  f'zh: {json.dumps(r["zh"], ensure_ascii=False)}, zs: {json.dumps(r["zs"], ensure_ascii=False)}, line: {json.dumps(r["line"], ensure_ascii=False)} }},')
    js.append("  ],")
js.append("};")
js.append("// MM_PG：每章每段开头所在的纸书页（下标是段号），mm.js 拿它给词条、勘误的 .loc 标页码。")
js.append("window.MM_PG = {")
for ch, xs in PG.items(): js.append(f'  "{ch}": {json.dumps(xs)},')
js.append("};")
js.append("window.MM_PAGES = [")
for pid, ch in PAGES:
    t, d = keep.get(pid, ("", ""))
    js.append(f'  {{ id: "{pid}", ch: {ch}, t: {json.dumps(t, ensure_ascii=False)}, d: {json.dumps(d, ensure_ascii=False)} }},')
js.append("];")
js.append(f'window.MM_EXTRA = {{ "00": {{ t: "开读之前", d: "" }} }};')
js.append(f"window.MM_READY = {json.dumps(ready)};")
open(S("assets/chapters.js"), "w", encoding="utf-8").write("\n".join(js) + "\n")
for ch, rows in SECS.items():
    for r in rows: print(ch, r["k"], r["p"], f'p{r["pg"][0]}–{r["pg"][1]}', r["w"], r["zw"], r["en"][:40], "|", r["zh"], "|", r["eo"], "|", r["zs"], "|", r["t"], r["tier"])
