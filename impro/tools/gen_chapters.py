#!/usr/bin/env python3
"""生成 assets/chapters.js：python3 -I tools/gen_chapters.py
读 source/text/index.tsv（原书的节、段号、词数、英文开头）、source/text/zh/NN.txt（译本的节、小标题、字数、开头几个字）、
source/SECS.tsv（主编定的本站节名、档、line；底稿 source/line/ 是它的来源）。页表写在下面 PAGES 里。
已有的 chapters.js 里每页的 t、d、篇的 d 和 IM_READY 保留（作者交稿后主编用 tools/accept.py 填的）。"""
import json, os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
S = lambda *p: os.path.join(ROOT, *p)

CHAPTERS = [(1, "Introduction + Notes on Myself", "序言 · 关于我自己"), (2, "Status", "姿态"), (3, "Spontaneity", "自发性"),
            (4, "Narrative Skills", "叙事技巧"), (5, "Masks and Trance", "面具与催眠")]
# 页 id → (篇, 节, need)。04 篇 §3 拆成 3a（Lists 到 ‘Experts’）、3b（‘Verbal Chase’ 起）
PAGES = [("01a", 1, list(range(1, 12)), ["game"]), ("01b", 1, [12, 13, 14, 15], ["game"]),
         ("02a", 2, [1, 2], ["sim", "game"]), ("02b", 2, [3], ["game"]), ("02c", 2, [4, 5, 6], ["game"]), ("02d", 2, [7, 8, 9], ["game"]),
         ("03a", 3, [1, 2, 3], ["game"]), ("03b", 3, [4, 5], ["sim", "game"]), ("03c", 3, [6, 7], ["game"]),
         ("04a", 4, [1, 2], ["game"]), ("04b", 4, ["3a"], ["game"]), ("04c", 4, ["3b", 4, 5], ["game"]),
         ("05a", 5, [1, 2, 3, 4], ["game"]), ("05b", 5, [5, 6, 7], ["game"]), ("05c", 5, [8], ["game"]), ("05d", 5, [9, 10, 11, 15], ["game"]),
         ("05e", 5, [12, 13], ["game"]), ("05f", 5, [14], ["game"])]
SPLIT = {(4, 3): [("3a", None), ("3b", "‘Verbal Chase’")]}      # 原书小标题；译本那边按「快问快答」分
ZSPLIT = {(4, 3): "快问快答"}
han = lambda s: len(re.findall(r"[一-鿿]", s))

# 原书：index.tsv 一行一节
en = {}
for line in open(S("source/text/index.tsv"), encoding="utf-8").read().splitlines()[1:]:
    ch, k, rng, w, subs, first = line.split("\t")
    a, b = map(int, rng.split("–"))
    en[(int(ch), int(k))] = dict(p=[a, b], w=int(w), en=first, subs=subs)


def en_split(ch, k, head):
    """把原书一节按某个 ### 小标题拆成两段，返回 [(p0, p1, 词数, 开头)]。"""
    L = open(S(f"source/text/{ch:02d}.txt"), encoding="utf-8").read().splitlines()
    out, cur, insec = [], None, False
    for x in L:
        if x.startswith("## "): insec = x.startswith(f"## §{k} ") or x == f"## §{k}"; continue
        if not insec: continue
        if x == f"### {head}": cur = None
        m = re.match(r"\[(\d+)\] (?:\{\w\} )?(.*)$", x)
        if not m: continue
        p = int(m.group(1))
        if cur is None:
            cur = [p, p, 0, " ".join(m.group(2).replace("*", "").split()[:6])]; out.append(cur)
        cur[1] = p; cur[2] += len(m.group(2).split())
    return out


# 译本：每节的小标题、### 小标题、字数、开头几个字
def zh_secs(ch):
    L = open(S(f"source/text/zh/{ch:02d}.txt"), encoding="utf-8").read().splitlines()
    secs, cur = {}, None
    for x in L:
        m = re.match(r"## §(\d+) ?(.*)$", x)
        if m:
            cur = int(m.group(1)); secs[cur] = dict(head=m.group(2), subs=[], paras=[]); continue
        if cur is None or not x.strip() or x.startswith("# "): continue
        if x.startswith("### "): secs[cur]["subs"].append(x[4:]); secs[cur]["paras"].append(("H", x[4:])); continue
        if x.startswith(("{译注}", "{原注}")): continue
        secs[cur]["paras"].append(("P", x))
    return secs


def opening(paras):
    """这一节在译本里第一段的开头几个字：一字不差，读者在译本电子书里搜它。取到第一个标点（至少 6 个字），最多 12 个字。"""
    for kind, x in paras:
        if kind != "P": continue
        s = x.strip().replace("*", "")
        m = re.match(r"[^，。：；！？、“”‘’（）《》—…,.:;!?\s]{6,}", s)
        return (m.group(0) if m else s)[:12]
    return ""


def zh_label(ch, k, z):
    num = "" if ch == 1 else f"{k}"
    head = z["head"]
    if ch == 1:
        return "开头（第一个小标题之前）" if head == "（篇首）" else head
    if head and ch == 5 and k == 15: return "附录"
    lab = f"{num} {head}".strip()
    if z["subs"] and not head: lab += "（" + " · ".join(z["subs"]) + "）"
    return lab


tab = {}
if os.path.exists(S("source/SECS.tsv")):
    for line in open(S("source/SECS.tsv"), encoding="utf-8").read().splitlines()[1:]:
        if not line.strip(): continue
        ch, k, t, tier, ln = (line.split("\t") + [""] * 5)[:5]
        tab[(int(ch), k)] = dict(t=t, tier=tier, line=ln)

old = open(S("assets/chapters.js"), encoding="utf-8").read() if os.path.exists(S("assets/chapters.js")) else ""
keep = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r'\{ id: "(\w+)",.*?t: "([^"]*)", d: "([^"]*)" \}', old)}
keep_ch = {int(m.group(1)): m.group(2) for m in re.finditer(r'\{ n: (\d+),.*?d: "([^"]*)" \}', old)}
m = re.search(r"window\.IM_READY = (\[.*?\]);", old)
ready = json.loads(m.group(1)) if m else []

SECS = {}
for ch, _, _ in CHAPTERS:
    zs = zh_secs(ch); rows = []
    for (c, k), e in sorted(en.items()):
        if c != ch: continue
        z = zs[k]
        if (ch, k) in SPLIT:
            parts = en_split(ch, k, SPLIT[(ch, k)][1][1])
            cut = next(i for i, (kind, x) in enumerate(z["paras"]) if kind == "H" and ZSPLIT[(ch, k)] in x)
            zparts = [z["paras"][:cut], z["paras"][cut:]]
            for (kk, _), (p0, p1, w, first), zp in zip(SPLIT[(ch, k)], parts, zparts):
                subs = [x for kind, x in zp if kind == "H"]
                rows.append(dict(k=kk, p=[p0, p1], w=w, en=first, zh=f"{k}（{' · '.join(subs)}）", zs=opening(zp),
                                 zw=sum(han(x) for kind, x in zp if kind == "P")))
        else:
            rows.append(dict(k=k, p=e["p"], w=e["w"], en=e["en"], zh=zh_label(ch, k, z), zs=opening(z["paras"]),
                             zw=sum(han(x) for kind, x in z["paras"] if kind == "P")))
    for r in rows:
        r.update(tab.get((ch, str(r["k"])), dict(t="", tier="", line="")))
    SECS[f"{ch:02d}"] = rows

js = ["// 全站目录。tools/gen_chapters.py 生成，别手改节表；每页的 t、d 和 IM_READY 由 tools/accept.py 填（重新生成时保留）。页 id 和 tools/lint.py 用同一套（lint 从这里读）。",
      "// IM_CHAPTERS：五篇（01 篇是序言加 Notes on Myself，05 篇末尾并进了全书附录）。en 原书篇名，t 译本篇名，d 一句话（主编补）。",
      "// IM_SECS：每篇的节，就是原书和译本的编号小节（04 篇 §3 本站拆成 3a、3b）。k 节号，p 段号范围（source/text/NN.txt 的 [k]），w 英文词数，en 这一节英文开头几个词，",
      "//   zh 译本的节号和小标题，zs 这一节在译本里开头的几个字（读者在译本电子书里搜它），zw 译本字数（汉字），t 本站中文节名，tier 档（先读 / 有空 / 可跳过），line 这一节起什么作用。",
      "// IM_PAGES：页。secs 这一页包含的节，need 这一页必写的可省小节（sim：动手：模拟器；lint 查），t 本站标题（不超过 10 个字），d 一句话（不超过 24 个字）。"]
js.append("window.IM_CHAPTERS = [")
for n, e, t in CHAPTERS:
    js.append(f'  {{ n: {n}, en: {json.dumps(e)}, t: {json.dumps(t, ensure_ascii=False)}, d: {json.dumps(keep_ch.get(n, ""), ensure_ascii=False)} }},')
js.append("];")
js.append("window.IM_SECS = {")
for ch, rows in SECS.items():
    js.append(f'  "{ch}": [')
    for r in rows:
        k = json.dumps(r["k"])
        js.append(f'    {{ k: {k}, p: [{r["p"][0]}, {r["p"][1]}], w: {r["w"]}, zw: {r["zw"]}, t: {json.dumps(r["t"], ensure_ascii=False)}, '
                  f'tier: {json.dumps(r["tier"], ensure_ascii=False)}, en: {json.dumps(r["en"], ensure_ascii=False)}, '
                  f'zh: {json.dumps(r["zh"], ensure_ascii=False)}, zs: {json.dumps(r["zs"], ensure_ascii=False)}, line: {json.dumps(r["line"], ensure_ascii=False)} }},')
    js.append("  ],")
js.append("};")
js.append("window.IM_PAGES = [")
for pid, ch, secs, need in PAGES:
    t, d = keep.get(pid, ("", ""))
    js.append(f'  {{ id: "{pid}", ch: {ch}, secs: {json.dumps(secs)}, need: {json.dumps(need)}, t: {json.dumps(t, ensure_ascii=False)}, d: {json.dumps(d, ensure_ascii=False)} }},')
js.append("];")
js.append(f'window.IM_EXTRA = {{ "00": {{ t: "开读之前", d: "" }} }};')
js.append(f"window.IM_READY = {json.dumps(ready)};")
open(S("assets/chapters.js"), "w", encoding="utf-8").write("\n".join(js) + "\n")
for ch, rows in SECS.items():
    for r in rows: print(ch, r["k"], r["p"], r["w"], r["zw"], r["zh"], "|", r["zs"], "|", r["t"], r["tier"])
