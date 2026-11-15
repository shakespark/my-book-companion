#!/usr/bin/env python3
"""生成 assets/chapters.js：python3 -I tools/gen_chapters.py
读 source/text/index.tsv（原书和译本对好的节：段号、词数、两边的小标题、开头）和 source/SECS.tsv（主编定的本站节名、档、line，可省的 zs；底稿 source/line/ 是它的来源）。
SECS.tsv 的 zs 列：这一节译本开头的几个字当不了搜索词（08 §1 开头是图、08 §2 开头只有「系统」两个字）时，换成这一节里另一截原句（一字不差），lint 照样核对。
页表写在下面 PAGES 里。已有的 chapters.js 里每页的 t、d 和 TS_READY 保留（作者交稿后主编用 tools/accept.py 填的）。"""
import json, os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
S = lambda *p: os.path.join(ROOT, *p)

# 章：n、原书章名、译本章名（照抄）、本站章名、所在的部（0 正文前，1–3 三部，4 附录）
CHAPTERS = [
    (0, "A Note from the Author · A Note from the Editor · Introduction: The Systems Lens", "前言 · 献词 · 引言 系统多棱镜", "前言和引言", 0),
    (1, "One. The Basics", "第1章 系统之基础", "系统的基本构造", 1),
    (2, "Two. A Brief Visit to the Systems Zoo", "第2章 系统大观园", "系统动物园", 1),
    (3, "Three. Why Systems Work So Well", "第3章 系统之美：系统的3大特征", "系统为什么运转得这么好", 2),
    (4, "Four. Why Systems Surprise Us", "第4章 系统之奇：系统的6大障碍", "系统为什么让人意外", 2),
    (5, "Five. System Traps . . . and Opportunities", "第5章 系统之危与机：系统的8大陷阱与对策", "系统陷阱和出路", 2),
    (6, "Six. Leverage Points—Places to Intervene in a System", "第6章 系统之杠杆点：系统的12大变革方式", "杠杆点", 3),
    (7, "Seven. Living in a World of Systems", "第7章 与系统共舞：系统的15大生存法则", "在系统的世界里生活", 3),
    (8, "Appendix", "附录", "附录", 4),
]
PARTS = [(0, "Front matter · Introduction", "前言和引言"), (1, "Part One: System Structure and Behavior", "第一部分　系统的结构和行为"),
         (2, "Part Two: Systems and Us", "第二部分　系统思考与我们"), (3, "Part Three: Creating Change—in Systems and in Our Philosophy", "第三部分　改变系统"),
         (4, "Appendix", "附录")]
# 页 id → (章, 节, need)。need：sim 有一个模拟器，sim2 有两个，drill 有「练一练：情境题」，light 轻量页（小节少，见 AUTHORING.md）
PAGES = [("in", 0, [1, 2, 3, 4, 5], ["drill"]),
         ("01a", 1, [1, 2, 3], ["sim", "drill"]), ("01b", 1, [4, 5, 6], ["sim", "drill"]),
         ("02a", 2, [1, 2, 3, 4], ["sim2", "drill"]), ("02b", 2, [5, 6], ["sim", "drill"]),
         ("03", 3, [1, 2, 3, 4], ["drill"]),
         ("04a", 4, [1, 2, 3, 4], ["drill"]), ("04b", 4, [5, 6, 7], ["drill"]),
         ("05a", 5, [1, 2, 3, 4, 5], ["drill"]), ("05b", 5, [6, 7, 8, 9], ["drill"]),
         ("06a", 6, [1, 2, 3, 4, 5, 6, 7], ["drill"]), ("06b", 6, list(range(8, 15)), ["drill"]),
         ("07", 7, list(range(1, 17)), ["drill"]),
         ("08", 8, [1, 2, 3, 4, 5, 6], ["light"])]


def opening(s):
    """译本这一节第一段的开头几个字：一字不差，读者在译本电子书里搜它。取到第一个标点（至少 6 个字），最多 12 个字。"""
    m = re.match(r"[^，。：；！？、「」『』（）《》—…,.:;!?\s]{6,}", s)
    return (m.group(0) if m else s)[:12]


def zh_label(z):
    if z == "（章首）": return "章首（第一个小标题之前）"
    if z.startswith("（引言）"): return f"引言 · {z[4:]}"
    return z


def en_label(c, e):
    """原书小标题。原书没有小标题的节（章首、引言三节、06 §14），给读者说清楚，靠 en 列的开头几个词在纸书里找。"""
    if e == "（章首）": return "（章首，第一个小标题之前）"
    if e.startswith("（引言）"): return "Introduction: The Systems Lens（原书引言没有小标题，译本加的；从这句起）"
    if e.startswith("（本站分）"): return "（原书这里没有小标题，译本加的；从这句起）"
    return e


rows = {}
for line in open(S("source/text/index.tsv"), encoding="utf-8").read().splitlines()[1:]:
    c, k, rng, w, en_h, zh_h, en_first, zw, zs = line.split("\t")
    a, b = map(int, rng.split("–"))
    rows[(int(c), int(k))] = dict(p=[a, b], w=int(w), enh=en_label(int(c), en_h), zh=zh_label(zh_h), en=en_first, zw=int(zw), zs=opening(zs))

tab = {}
if os.path.exists(S("source/SECS.tsv")):
    for line in open(S("source/SECS.tsv"), encoding="utf-8").read().splitlines()[1:]:
        if not line.strip(): continue
        c, k, t, tier, ln, zs = (line.split("\t") + [""] * 6)[:6]
        tab[(int(c), int(k))] = dict(t=t, tier=tier, line=ln, **({"zs": zs} if zs else {}))   # zs 列可省：译本开头会剧透时，主编换一截不剧透的

old = open(S("assets/chapters.js"), encoding="utf-8").read() if os.path.exists(S("assets/chapters.js")) else ""
keep = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r'\{ id: "(\w+)",.*?t: "([^"]*)", d: "([^"]*)" \}', old)}
m = re.search(r"window\.TS_READY = (\[.*?\]);", old)
ready = json.loads(m.group(1)) if m else []

SECS = {}
for pid, ch, secs, _ in PAGES:
    out = SECS.setdefault(f"{ch:02d}", [])
    for k in secs:
        r = dict(k=str(k), lab=f"§{k}", **rows[(ch, k)])
        r.update(tab.get((ch, k), dict(t="", tier="", line="")))
        out.append(r)

js = ["// 全站目录。tools/gen_chapters.py 生成，别手改节表；每页的 t、d 和 TS_READY 由 tools/accept.py 填（重新生成时保留）。tools/lint.py 从这里读页和节。",
      "// TS_PARTS：全书五段（前言和引言、三部、附录）。TS_CHAPTERS：n 章号（0 是前言、献词和引言），en 原书章名，zh 译本章名（照抄），t 本站章名，part 所在的段。",
      "// TS_SECS：每章的节，节就是原书和译本一一对应的小标题。k 节号（data-sec 写它），lab 显示的节号，",
      "//   p 段号范围（source/text/NN.txt 的 [k]），w 英文词数，enh 原书小标题，en 原文开头几个词，zh 译本小标题（照抄），zs 这一节在译本里开头的几个字（读者在译本电子书里搜它），",
      "//   zw 译本字数，t 本站中文节名，tier 档（先读 / 有空 / 可跳过），line 这一节起什么作用。",
      "// TS_PAGES：页。secs 这一页包含的节，need（sim / sim2：一个 / 两个模拟器，drill：练一练，light：轻量页；lint 查），t 本站标题（不超过 10 个字），d 一句话（不超过 24 个字，不剧透）。"]
js.append("window.TS_PARTS = [")
for n, en, zh in PARTS: js.append(f"  {{ n: {n}, en: {json.dumps(en)}, zh: {json.dumps(zh, ensure_ascii=False)} }},")
js.append("];")
js.append("window.TS_CHAPTERS = [")
for n, en, zh, t, part in CHAPTERS:
    js.append(f"  {{ n: {n}, part: {part}, en: {json.dumps(en, ensure_ascii=False)}, zh: {json.dumps(zh, ensure_ascii=False)}, t: {json.dumps(t, ensure_ascii=False)} }},")
js.append("];")
js.append("window.TS_SECS = {")
for ch, rs in SECS.items():
    js.append(f'  "{ch}": [')
    for r in rs:
        js.append("    " + json.dumps({x: r[x] for x in ("k", "lab", "p", "w", "zw", "t", "tier", "enh", "en", "zh", "zs", "line")}, ensure_ascii=False) + ",")
    js.append("  ],")
js.append("};")
js.append("window.TS_PAGES = [")
for pid, ch, secs, need in PAGES:
    t, d = keep.get(pid, ("", ""))
    js.append(f'  {{ id: "{pid}", ch: {ch}, secs: {json.dumps([str(k) for k in secs])}, need: {json.dumps(need)}, t: {json.dumps(t, ensure_ascii=False)}, d: {json.dumps(d, ensure_ascii=False)} }},')
js.append("];")
js.append('window.TS_EXTRA = { "00": { t: "开读之前", d: "作者、全书地图、译本须知、最短读法" } };')
js.append(f"window.TS_READY = {json.dumps(ready)};")
open(S("assets/chapters.js"), "w", encoding="utf-8").write("\n".join(js) + "\n")
for ch, rs in SECS.items():      # zs 要一字不差地在译本这一章里（读者拿它搜），手填的覆盖值也查
    zt = re.sub(r"\s+", "", open(S(f"source/text/zh/{ch}.txt"), encoding="utf-8").read())
    for r in rs:
        if r["zs"] and re.sub(r"\s+", "", r["zs"]) not in zt: print(f"  ✗ {ch} §{r['k']} 的 zs 在译本里找不到：{r['zs']}")
n = sum(len(v) for v in SECS.values())
core = sum(r["zw"] for v in SECS.values() for r in v if r["tier"] == "先读"); tot = sum(r["zw"] for v in SECS.values() for r in v)
print(f"{len(PAGES)} 页，{n} 节；先读 {core} / {tot} 字（{100 * core / max(tot, 1):.0f}%）；没定节名的 {sum(1 for v in SECS.values() for r in v if not r['t'])} 节")
