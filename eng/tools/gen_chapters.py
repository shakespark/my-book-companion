#!/usr/bin/env python3
"""生成 assets/chapters.js：python3 -I tools/gen_chapters.py      正常只打印一行，出错才打印细节。
原书章内没有小标题，节是本站分的：source/SECS.tsv 一节一行（章、节、段、本站节名、档、line、en），底稿 source/line/ 是它的来源。
词数由脚本从 source/text/NN.txt 算（不算 {F} 图注行）；en（这一节第一段开头 4–7 个词，读者在 Kindle 里搜）要一字不差地在那一段里，且全章只出现一次。
节表要把每章的正文段号不重不漏地分完。页表写在下面 PAGES 里。已有的 chapters.js 里每页的 t、d 和 EG_READY 保留（作者交稿后主编用 tools/accept.py 填的）。"""
import json, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
S = lambda *p: os.path.join(ROOT, *p)

# 章：n、原书章名、本站章名、所在的段（一章一段）
CHAPTERS = [
    (0, "Preface", "序", 0),
    (1, "From idea to reality", "从想法到现实", 1),
    (2, "The age of gravity – time for work", "重力的时代：做功", 2),
    (3, "The age of heat – you can’t get something for nothing", "热的时代：天下没有白吃的午餐", 3),
    (4, "The age of electromagnetism – the power of attraction", "电磁的时代：吸引的力量", 4),
    (5, "The age of information – getting smaller", "信息的时代：越做越小", 5),
    (6, "The age of systems – risky futures", "系统的时代：有风险的未来", 6),
]
PARTS = [(1, "From idea to reality", "引子：什么是工程"), (2, "Gravity", "重力"), (3, "Heat", "热"),
         (4, "Electromagnetism", "电磁"), (5, "Information", "信息"), (6, "Systems", "系统")]
# 页 id → (章, 段号范围, need)。这一页包含起始段落在范围里的节。need：sim 有一个模拟器，sim2 有两个，light 轻量页。
# 拆页点照底稿的建议（2026-11-19 E 步）：03 从 [23]、04 从 [26]、06 从 [19]。
PAGES = [("01", 1, (1, 39), []),   # Preface（第 0 章）不做作者页，放在 00「开读之前」；它的节照样在 SECS 里
         ("02", 2, (1, 45), ["sim"]),
         ("03a", 3, (1, 22), ["sim"]), ("03b", 3, (23, 38), []),
         ("04a", 4, (1, 25), ["sim"]), ("04b", 4, (26, 45), []),
         ("05", 5, (1, 26), ["sim"]),
         ("06a", 6, (1, 18), ["sim"]), ("06b", 6, (19, 35), ["sim"])]

err = []
paras = {}   # (章, 段号) → 文字
for c, *_ in CHAPTERS:
    for line in open(S(f"source/text/{c:02d}.txt"), encoding="utf-8"):
        m = re.match(r"\[(\d+)\] (.*)", line)
        if m: paras[(c, int(m.group(1)))] = re.sub(r"\{b:(.*?)\}", r"\1", re.sub(r"^\{[QB]\} ", "", m.group(2))).replace("*", "")
nparas = {c: max(k for (cc, k) in paras if cc == c) for c, *_ in CHAPTERS}

SECS = {}
if os.path.exists(S("source/SECS.tsv")):
    for i, line in enumerate(open(S("source/SECS.tsv"), encoding="utf-8").read().splitlines()[1:], 2):
        if not line.strip(): continue
        c, k, rng, t, tier, ln, en = (line.split("\t") + [""] * 7)[:7]
        c = int(c); a, b = (map(int, rng.split("–")) if "–" in rng else (int(rng), int(rng)))
        w = sum(len(paras[(c, j)].split()) for j in range(a, b + 1) if (c, j) in paras)
        if en and en not in paras.get((c, a), ""): err.append(f"SECS.tsv 第 {i} 行：{c} §{k} 的 en 不在第 {a} 段里：{en}")
        if en and sum(p.count(en) for (cc, _), p in paras.items() if cc == c) > 1: err.append(f"SECS.tsv 第 {i} 行：{c} §{k} 的 en 在全章出现不止一次：{en}")
        if re.search(r"\[\d", t + ln): err.append(f"SECS.tsv 第 {i} 行：{c} §{k} 的节名或 line 里有读者看不到的段号 [k]，改成原文开头几个词或「下一节」")
        if tier and tier not in ("先读", "有空", "可跳过"): err.append(f"SECS.tsv 第 {i} 行：档只能是 先读 / 有空 / 可跳过：{tier}")
        SECS.setdefault(f"{c:02d}", []).append(dict(k=k, lab=f"§{k}", p=f"{a}–{b}" if a != b else str(a), a=a, b=b, w=w, t=t, tier=tier, en=en, line=ln))
for ch, rs in SECS.items():
    got = sorted(j for r in rs for j in range(r["a"], r["b"] + 1))
    if got != list(range(1, nparas[int(ch)] + 1)): err.append(f"第 {int(ch)} 章的节没有把段 1–{nparas[int(ch)]} 不重不漏地分完")

old = open(S("assets/chapters.js"), encoding="utf-8").read() if os.path.exists(S("assets/chapters.js")) else ""
keep = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r'\{ id: "(\w+)",.*?t: "([^"]*)", d: "([^"]*)" \}', old)}
m = re.search(r"window\.EG_READY = (\[.*?\]);", old)
ready = json.loads(m.group(1)) if m else []

pages = []
for pid, ch, (a, b), need in PAGES:
    secs = [r["k"] for r in SECS.get(f"{ch:02d}", []) if a <= r["a"] <= b]
    pages.append((pid, ch, secs, need))

js = ["// 全站目录。tools/gen_chapters.py 生成，别手改节表；每页的 t、d 和 EG_READY 由 tools/accept.py 填（重新生成时保留）。tools/lint.py 从这里读页和节。",
      "// EG_PARTS：全书六段（一章一段：引子和五个时代）。EG_CHAPTERS：n 章号（0 是 Preface），en 原书章名，t 本站章名，part 所在的段。",
      "// EG_SECS：每章的节。原书章内没有小标题，节是本站按段号分的。k 节号（data-sec 写它），lab 显示的节号，",
      "//   p 段号范围（source/text/NN.txt 的 [k]），w 英文词数，en 这一节第一段开头几个词（读者在 Kindle 里搜它），t 本站中文节名，tier 档（先读 / 有空 / 可跳过），line 这一节起什么作用。",
      "// EG_PAGES：页。secs 这一页包含的节，need（sim / sim2：一个 / 两个模拟器，light：轻量页；lint 查），t 本站标题（不超过 10 个字），d 一句话（不超过 24 个字）。"]
js.append("window.EG_PARTS = [")
for n, en, zh in PARTS: js.append(f"  {{ n: {n}, en: {json.dumps(en)}, zh: {json.dumps(zh, ensure_ascii=False)} }},")
js.append("];")
js.append("window.EG_CHAPTERS = [")
for n, en, t, part in CHAPTERS:
    js.append(f"  {{ n: {n}, part: {part}, en: {json.dumps(en, ensure_ascii=False)}, t: {json.dumps(t, ensure_ascii=False)} }},")
js.append("];")
js.append("window.EG_SECS = {")
for ch, rs in SECS.items():
    js.append(f'  "{ch}": [')
    for r in rs: js.append("    " + json.dumps({x: r[x] for x in ("k", "lab", "p", "w", "t", "tier", "en", "line")}, ensure_ascii=False) + ",")
    js.append("  ],")
js.append("};")
js.append("window.EG_PAGES = [")
for pid, ch, secs, need in pages:
    t, d = keep.get(pid, ("", ""))
    js.append(f'  {{ id: "{pid}", ch: {ch}, secs: {json.dumps(secs)}, need: {json.dumps(need)}, t: {json.dumps(t, ensure_ascii=False)}, d: {json.dumps(d, ensure_ascii=False)} }},')
js.append("];")
js.append('window.EG_EXTRA = { "00": { t: "开读之前", d: "作者、全书地图、最短读法" } };')
js.append(f"window.EG_READY = {json.dumps(ready)};")
open(S("assets/chapters.js"), "w", encoding="utf-8").write("\n".join(js) + "\n")

n = sum(len(v) for v in SECS.values())
core = sum(r["w"] for v in SECS.values() for r in v if r["tier"] == "先读"); tot = sum(r["w"] for v in SECS.values() for r in v)
if err: print("\n".join("  ✗ " + e for e in err))
print(f"{len(pages)} 页，{n} 节；先读 {core} / {tot} 词（{100 * core / max(tot, 1):.0f}%）；没定节名的 {sum(1 for v in SECS.values() for r in v if not r['t'])} 节" + ("" if not err else f"；{len(err)} 处错"))
sys.exit(1 if err else 0)
