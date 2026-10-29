#!/usr/bin/env python3
"""生成 assets/chapters.js：python3 -I tools/gen_chapters.py
读 source/text/index.tsv（原书和译本对好的节：段号、词数、两边的小标题、开头）和 source/SECS.tsv（主编定的本站节名、档、line，可省的 zs；底稿 source/line/ 是它的来源）。
SECS.tsv 的 zs 列：这一节译本开头的几个字会剧透（后记开头就是 John 的下场）时，换成这一节里另一截不剧透的原句（一字不差），lint 照样核对。
页表写在下面 PAGES 里。已有的 chapters.js 里每页的 t、d 和 FB_READY 保留（作者交稿后主编用 tools/accept.py 填的）。"""
import json, os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
S = lambda *p: os.path.join(ROOT, *p)

# 章：n、原书章名、译本章名（繁体，照抄）、本站章名、所在的部（0 正文前，1–3 三部，4 书后）
CHAPTERS = [
    (0, "Preface · Prologue", "序 · 前言", "序和前言", 0),
    (1, "If You're So Rich, Why Aren't You So Smart?", "如果你那麼有錢，為什麼不是那麼聰明？", "你那么有钱，为什么不那么聪明", 1),
    (2, "A Bizarre Accounting Method", "怪異的會計衡量方法", "怪异的记账法", 1),
    (3, "A Mathematical Meditation on History", "用數學沉思歷史", "用数学沉思历史", 1),
    (4, "Randomness, Nonsense, and the Scientific Intellectual", "隨機性、胡說八道和科學知識分子", "随机、胡话和科学知识分子", 1),
    (5, "Survival of the Least Fit", "最不適者生存 —— 進化有可能被隨機性愚弄嗎？", "最不适者生存", 1),
    (6, "Skewness and Asymmetry", "偏態與不對稱", "偏态和不对称", 1),
    (7, "The Problem of Induction", "歸納的問題", "归纳问题", 1),
    (8, "Too Many Millionaires Next Door", "隔壁的百萬富翁太多", "隔壁的百万富翁太多", 2),
    (9, "It Is Easier to Buy and Sell than Fry an Egg", "買賣比煎蛋容易", "买卖比煎蛋容易", 2),
    (10, "Loser Takes All", "輸家通賠 —— 談人生中的非線性", "输家通赔：人生的非线性", 2),
    (11, "Randomness and Our Mind: We Are Probability Blind", "隨機性和我們的心智：我們是機率盲", "我们是概率盲", 2),
    (12, "Gamblers' Ticks and Pigeons in a Box", "賭徒的迷信和籠中的鴿子", "赌徒的迷信和笼中的鸽子", 3),
    (13, "Carneades Comes to Rome", "卡涅阿德斯到羅馬：談機率與懷疑論", "卡涅阿德斯来到罗马", 3),
    (14, "Bacchus Abandons Antony · Epilogue", "巴克斯拋棄安東尼 · 後記：梭倫說過", "酒神抛弃安东尼 · 后记", 3),   # 后记并进 14，是 §4
    (16, "Postscript: Three Afterthoughts in the Shower", "附筆：沖澡時想到的三件事", "附笔：冲澡时想到的三件事", 4),
]
PARTS = [(0, "Preface · Prologue", "序和前言"), (1, "Part I", "第一部　梭倫的警世之言"), (2, "Part II", "第二部　打字機前的猴子"), (3, "Part III", "第三部　在耳中塞蠟"), (4, "Postscript", "附筆")]
# 页 id → (章, 节, need)。节写这一章的节号（后记在提取时并进了第 14 章，是 14 §4）
PAGES = [("pr", 0, [1, 2, 3, 4, 5, 6, 11], []),
         ("01", 1, list(range(1, 12)), []), ("02", 2, list(range(1, 14)), []),
         ("03a", 3, list(range(1, 10)), ["sim"]), ("03b", 3, [10, 11, 12, 13], ["sim"]),
         ("04", 4, [1, 2, 3, 4], []), ("05", 5, list(range(1, 11)), []), ("06", 6, list(range(1, 10)), ["sim"]),
         ("07", 7, list(range(1, 12)), []), ("08", 8, list(range(1, 12)), []),
         ("09a", 9, list(range(1, 12)), ["sim"]), ("09b", 9, list(range(12, 22)), []),
         ("10", 10, list(range(1, 10)), []),
         ("11a", 11, list(range(1, 10)), []), ("11b", 11, list(range(10, 25)), ["sim"]),
         ("12", 12, list(range(1, 8)), []), ("13", 13, list(range(1, 8)), []),
         ("14", 14, [1, 2, 3, 4], []), ("16", 16, [1, 2, 3, 4, 5], [])]


def opening(s):
    """译本这一节第一段的开头几个字：一字不差，读者在译本电子书里搜它。取到第一个标点（至少 6 个字），最多 12 个字。"""
    m = re.match(r"[^，。：；！？、「」『』（）《》—…,.:;!?\s]{6,}", s)
    return (m.group(0) if m else s)[:12]


# 三部的篇首语：01 §1、08 §1–§4、12 §1–§4（这一章的章旨 {Q} 在篇首语最后一节的末尾，译本的「# 8 …」章题也在那里）
PROLOGUE = {(1, 1)} | {(8, k) for k in range(1, 5)} | {(12, k) for k in range(1, 5)}


def zh_label(c, k, z):
    if z == "（章首）": return "章首（第一個小標題之前）"
    if (c, k) in PROLOGUE: return f"第{'一二三'[(1, 8, 12).index(c)]}部篇首語 · {z}" if k > 1 else f"{z}（篇首語）"
    return z


rows = {}
for line in open(S("source/text/index.tsv"), encoding="utf-8").read().splitlines()[1:]:
    c, k, rng, w, en_h, zh_h, en_first, zw, zs = line.split("\t")
    a, b = map(int, rng.split("–"))
    rows[(int(c), int(k))] = dict(p=[a, b], w=int(w), enh=en_h, zh=zh_label(int(c), int(k), zh_h), en=en_first, zw=int(zw), zs=opening(zs))

tab = {}
if os.path.exists(S("source/SECS.tsv")):
    for line in open(S("source/SECS.tsv"), encoding="utf-8").read().splitlines()[1:]:
        if not line.strip(): continue
        c, k, t, tier, ln, zs = (line.split("\t") + [""] * 6)[:6]
        tab[(int(c), int(k))] = dict(t=t, tier=tier, line=ln, **({"zs": zs} if zs else {}))   # zs 列可省：译本开头会剧透时，主编换一截不剧透的

old = open(S("assets/chapters.js"), encoding="utf-8").read() if os.path.exists(S("assets/chapters.js")) else ""
keep = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r'\{ id: "(\w+)",.*?t: "([^"]*)", d: "([^"]*)" \}', old)}
m = re.search(r"window\.FB_READY = (\[.*?\]);", old)
ready = json.loads(m.group(1)) if m else []

SECS = {}
for pid, ch, secs, _ in PAGES:
    out = SECS.setdefault(f"{ch:02d}", [])
    for k in secs:
        r = dict(k=str(k), lab=f"§{k}", **rows[(ch, k)])
        r.update(tab.get((ch, k), dict(t="", tier="", line="")))
        out.append(r)

js = ["// 全站目录。tools/gen_chapters.py 生成，别手改节表；每页的 t、d 和 FB_READY 由 tools/accept.py 填（重新生成时保留）。tools/lint.py 从这里读页和节。",
      "// FB_PARTS：全书五段（正文前、三部、书后的附笔）。FB_CHAPTERS：n 章号（0 是序和前言；14 含后记），en 原书章名，zh 译本章名（繁体照抄），t 本站章名，part 所在的段。",
      "// FB_SECS：每章的节，节就是原书和译本一一对应的小标题（后记并进 14，是 §4）。k 节号（data-sec 写它），lab 显示的节号，",
      "//   p 段号范围（source/text/NN.txt 的 [k]），w 英文词数，enh 原书小标题，en 原文开头几个词，zh 译本小标题（繁体照抄），zs 这一节在译本里开头的几个字（读者在译本电子书里搜它），",
      "//   zw 译本字数，t 本站中文节名，tier 档（先读 / 有空 / 可跳过），line 这一节起什么作用。",
      "// FB_PAGES：页。secs 这一页包含的节，need 这一页必写的可省小节（sim：动手：模拟器；lint 查），t 本站标题（不超过 10 个字），d 一句话（不超过 24 个字，不剧透）。"]
js.append("window.FB_PARTS = [")
for n, en, zh in PARTS: js.append(f"  {{ n: {n}, en: {json.dumps(en)}, zh: {json.dumps(zh, ensure_ascii=False)} }},")
js.append("];")
js.append("window.FB_CHAPTERS = [")
for n, en, zh, t, part in CHAPTERS:
    js.append(f"  {{ n: {n}, part: {part}, en: {json.dumps(en, ensure_ascii=False)}, zh: {json.dumps(zh, ensure_ascii=False)}, t: {json.dumps(t, ensure_ascii=False)} }},")
js.append("];")
js.append("window.FB_SECS = {")
for ch, rs in SECS.items():
    js.append(f'  "{ch}": [')
    for r in rs:
        js.append("    " + json.dumps({x: r[x] for x in ("k", "lab", "p", "w", "zw", "t", "tier", "enh", "en", "zh", "zs", "line")}, ensure_ascii=False) + ",")
    js.append("  ],")
js.append("};")
js.append("window.FB_PAGES = [")
for pid, ch, secs, need in PAGES:
    t, d = keep.get(pid, ("", ""))
    js.append(f'  {{ id: "{pid}", ch: {ch}, secs: {json.dumps([str(k) for k in secs])}, need: {json.dumps(need)}, t: {json.dumps(t, ensure_ascii=False)}, d: {json.dumps(d, ensure_ascii=False)} }},')
js.append("];")
js.append('window.FB_EXTRA = { "00": { t: "开读之前", d: "作者、全书地图、译本须知、最短读法" } };')
js.append(f"window.FB_READY = {json.dumps(ready)};")
open(S("assets/chapters.js"), "w", encoding="utf-8").write("\n".join(js) + "\n")
for ch, rs in SECS.items():      # zs 要一字不差地在译本这一章里（读者拿它搜），手填的覆盖值也查
    zt = re.sub(r"\s+", "", open(S(f"source/text/zh/{ch}.txt"), encoding="utf-8").read())
    for r in rs:
        if r["zs"] and re.sub(r"\s+", "", r["zs"]) not in zt: print(f"  ✗ {ch} §{r['k']} 的 zs 在译本里找不到：{r['zs']}")
n = sum(len(v) for v in SECS.values())
core = sum(r["zw"] for v in SECS.values() for r in v if r["tier"] == "先读"); tot = sum(r["zw"] for v in SECS.values() for r in v)
print(f"{len(PAGES)} 页，{n} 节；先读 {core} / {tot} 字（{100 * core / max(tot, 1):.0f}%）；没定节名的 {sum(1 for v in SECS.values() for r in v if not r['t'])} 节")
