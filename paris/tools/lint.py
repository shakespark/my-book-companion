#!/usr/bin/env python3
"""篇目页结构检查：python3 tools/lint.py chapters/03.html …
查：小节标题和顺序、读之前（.crux 和带着读的问题）、路线（SVG、只有一句「作者落在哪」、整节不能写成摘要）、
分节地图（每节一条、中文地标、照抄英文开头、词数、本站分的节要标出、长篇分几次坐下）、背景小块的长度、
词条（.en 重复、.loc 是否在原文那一段里、是否在自己那一节的小标题下、顺序、密度、trap 占比）、
引用块（数量、长度、不能引 {Q} 段落）、后来（核对日期）、精彩回顾、图片、理解检查的题数、
不能替译本说话（「译本译作」之类）、页面里的 <style>/<script>/写死的颜色、直引号、原书材料的路径。
通用的几项在 ~/tutorials-deploy/scripts/lint_common.py。"""
import os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.expanduser("~/tutorials-deploy/scripts"))
from lint_common import norm, check_entries, check_quotes, check_images, check_markup, counts

SECS = ["这一篇在做什么", "读之前：这篇的来历", "这一篇的路线", "分节地图", "背景：作者默认你知道的事",
        "词与短语", "后来", "值得停下来的句子", "检查一下理解", "精彩回顾"]
OPTIONAL = {"后来"}
han = lambda s: len(re.findall(r"[一-鿿]", re.sub(r"<[^>]+>", "", s)))

def load(src):
    """读 source/text/NN.txt。返回 paras {段号: 文字}、quoted {是 {Q} 的段号}、secs [(节号, 是否本站分, 第一段, 最后一段, 词数)]。"""
    paras, quoted, secs = {}, set(), []
    for line in open(src, encoding="utf-8").read().splitlines():
        m = re.match(r"## §(\d+) (.*)$", line)
        if m: secs.append([int(m.group(1)), "本站分" in m.group(2), None, None, 0]); continue
        m = re.match(r"\[(\d+)\] (\{Q\} )?(.*)$", line)
        if m:
            p = int(m.group(1)); paras[p] = norm(m.group(3))
            if m.group(2): quoted.add(p)
            s = secs[-1]; s[2] = s[2] or p; s[3] = p; s[4] += len(m.group(3).split())
    return paras, quoted, [tuple(s) for s in secs]

bad = 0
for path in sys.argv[1:]:
    t = open(path, encoding="utf-8").read(); errs = []
    nn = re.search(r"(\d\d)\.html$", path).group(1)
    paras, quoted, secs = load(os.path.join(ROOT, f"source/text/{nn}.txt"))
    if f'<body data-page="{nn}">' not in t: errs.append(f'<body> 应写成 <body data-page="{nn}">')
    def part(a):
        i = t.find(f"<h2>{a}</h2>")
        if i < 0: return ""
        j = t.find("<h2>", i + 4)
        return t[i:j if j > 0 else len(t)]

    # 小节标题和顺序
    present = [s for s in SECS if f"<h2>{s}</h2>" in t]
    for s in SECS:
        if s not in present and s not in OPTIONAL: errs.append(f"缺少小节：{s}")
    pos = [t.find(f"<h2>{s}</h2>") for s in present]
    if pos != sorted(pos): errs.append("小节顺序不对，应为：" + " → ".join(SECS))
    for s in re.findall(r"<h2>(.*?)</h2>", t):
        if s not in SECS: errs.append(f"多出来的小节标题：{s}（标题一个字都不能改）")
    g = re.search(r'<div class="gist">(.*?)</div>', t, flags=re.S)
    if not g: errs.append("「这一篇在做什么」要有 <div class=\"gist\">")
    elif han(g.group(1)) > 200: errs.append(f"「这一篇在做什么」{han(g.group(1))} 个汉字，超过 200")

    # 读之前
    pre = part("读之前：这篇的来历")
    if '<div class="crux">' not in pre: errs.append("「读之前」要有一个 <div class=\"crux\">")
    nq = len(re.findall(r"<li>", re.search(r'<ol class="qs">(.*?)</ol>', pre, flags=re.S).group(1))) if '<ol class="qs">' in pre else 0
    if not 2 <= nq <= 4: errs.append(f"「读之前」带着读的问题（<ol class=\"qs\">）应有 2–4 个，现在 {nq} 个")

    # 路线：一张 SVG，一句「作者落在哪」；整节文字有上限，免得写成按原书顺序的摘要
    rt = part("这一篇的路线")
    if "<svg" not in rt: errs.append("「路线」要有一张自己画的 SVG")
    lands = re.findall(r'<p class="landing"><b>作者落在哪：</b>(.*?)</p>', rt, flags=re.S)
    if len(lands) != 1: errs.append(f"「路线」要有且只有一句 <p class=\"landing\"><b>作者落在哪：</b>…</p>，现在 {len(lands)} 句")
    elif han(lands[0]) > 130: errs.append(f"「作者落在哪」{han(lands[0])} 个汉字，超过 130")
    prose = re.sub(r"<svg.*?</svg>|<figcaption>.*?</figcaption>", "", rt, flags=re.S)
    if han(prose) > 380: errs.append(f"「路线」正文 {han(prose)} 个汉字，超过 380（只讲怎么走，不复述内容）")

    # 分节地图：每节一条；<b> 是中文地标；.en 照抄这一节第一段（不算 {Q}）开头 4–7 个词
    sm = part("分节地图")
    items = re.findall(r'<li data-sec="(\d+)"( class="ours")?><b>(.*?)<span class="w">约 (\d+) 词</span></b><span class="en">(.*?)</span><span class="what">(.*?)</span></li>', sm, flags=re.S)
    want = [s[0] for s in secs]
    if [int(i[0]) for i in items] != want: errs.append(f"分节地图的节号应为 {want}，实际是 {[int(i[0]) for i in items]}（写法照规范：<li data-sec><b>地标<span class=\"w\">约 N 词</span></b><span class=\"en\">…</span><span class=\"what\">…</span></li>）")
    for (k, ours, b, w, en, what), (_, is_ours, p0, p1, words) in zip(items, secs):
        if bool(ours) != is_ours: errs.append(f"分节地图 §{k}：" + ("这一节是本站分的，<li> 要加 class=\"ours\"" if is_ours else "这一节是原书的分隔，不要加 class=\"ours\""))
        if not han(b): errs.append(f"分节地图 §{k}：<b> 要写中文地标（读译本时认得出的场面、人名、地名）")
        if han(b) > 22: errs.append(f"分节地图 §{k}：地标 {han(b)} 个汉字，超过 22")
        e = norm(re.sub(r"<[^>]+>", "", en)).strip("… ").strip()
        first = next((paras[p] for p in range(p0, p1 + 1) if p in paras and p not in quoted), "")
        if not (first.startswith(e) and 4 <= len(e.split()) <= 7): errs.append(f"分节地图 §{k}：.en 照抄这一节第一段（不算引文）开头 4–7 个词，后面加 …：{e!r}")
        if abs(int(w) - words) > max(60, words * 0.1): errs.append(f"分节地图 §{k}：词数写的是 {w}，实际约 {words}")
        if han(what) > 40: errs.append(f"分节地图 §{k}：说明 {han(what)} 个汉字，超过 40")
    total = sum(s[4] for s in secs)
    sits = len(re.findall(r'<li class="sit">', sm))
    if total > 6000 and not 2 <= sits <= 3: errs.append(f"这一篇 {total} 词，分节地图要用 <li class=\"sit\"> 分成 2–3 次坐下，现在 {sits} 次")
    if total <= 6000 and sits: errs.append("6000 词以内的篇不分坐下")
    if any(s[1] for s in secs) and "本站" not in re.sub(r"<ol.*?</ol>", "", sm, flags=re.S): errs.append("分节地图里有本站分的节，lede 要说明哪几节是本站分的（原书这里没有分隔）")

    # 背景：小块不太长
    bg = part("背景：作者默认你知道的事")
    blocks = re.split(r"<h3>", bg)[1:]
    if not 4 <= len(blocks) <= 10: errs.append(f"「背景」应有 4–10 个 <h3> 小块，现在 {len(blocks)} 个")
    for b in blocks:
        title = re.sub(r"<[^>]+>", "", b.split("</h3>")[0])
        if not re.match(r'<span class="sec">§\d+</span>', b): errs.append(f"「背景」小块标题前要有节号 <span class=\"sec\">§k</span>：{title}")
        body = re.sub(r"<figure.*?</figure>|<div class=\"who\">.*?</div>\s*</div>", "", b.split("</h3>", 1)[-1], flags=re.S)
        if han(body) > 220: errs.append(f"「背景」{title}：{han(body)} 个汉字，超过 220")

    # 词条：在自己那一节的小标题下
    ws = part("词与短语")
    rng = {s[0]: (s[2], s[3]) for s in secs}
    cur = None
    for m in re.finditer(r'<h3 class="sec-head" id="s(\d+)">|<div class="loc" data-p="(\d+)">', ws):
        if m.group(1): cur = int(m.group(1)); continue
        p = int(m.group(2))
        if cur is None: errs.append(f"第 {p} 段的词条前面没有节的小标题 <h3 class=\"sec-head\" id=\"sK\">"); continue
        a, b = rng.get(cur, (0, -1))
        if not a <= p <= b: errs.append(f"第 {p} 段的词条放在了 §{cur} 下面（§{cur} 是第 {a}–{b} 段）")
    for k in re.findall(r'<h3 class="sec-head" id="s(\d+)">', ws):
        if int(k) not in rng: errs.append(f"词与短语：没有 §{k} 这一节")
    errs += check_entries(t, paras, per_k=4, max_n=70, trap_ratio=1 / 3, scope="这一篇")

    # 引用块：不超过 2 处，只引作者自己的话
    errs += check_quotes(t, 2)
    for q in re.findall(r'<blockquote class="quote">(.*?)<cite>', t, flags=re.S):
        s = norm(re.sub(r"<[^>]+>", "", q)).strip("… ").strip()
        where = [p for p, v in paras.items() if s.replace("…", "") and all(x.strip() in v for x in s.split("…") if x.strip())]
        if not where: errs.append(f"引用块在原文里找不到（要一字不差，省略处用 …）：{s[:50]!r}")
        elif all(p in quoted for p in where): errs.append(f"引用块引的是 {{Q}} 段落（别人的话），只引作者自己写的：{s[:50]!r}")
        if len(s.replace("…", " ").split()) > 25: errs.append(f"引用块超过 25 个词：{s[:50]!r}")

    # 后来（可省）
    lt = part("后来")
    if lt:
        cards = re.findall(r'<div class="later"><h4>(.*?)</h4>(.*?)</div>', lt, flags=re.S)
        if not 1 <= len(cards) <= 3: errs.append(f"「后来」应有 1–3 张卡片（<div class=\"later\"><h4>…</h4><p>…</p></div>），现在 {len(cards)} 张")
        for h4, body in cards:
            if not re.search(r'<span class="asof">核对于 20\d\d-\d\d。依据：', body): errs.append(f"「后来」{h4}：要写 <span class=\"asof\">核对于 YYYY-MM。依据：…</span>")
            if han(body) > 260: errs.append(f"「后来」{h4}：{han(body)} 个汉字，超过 260")

    # 精彩回顾：一句话 + 4–6 张卡片，每张标节号、不超过 100 个汉字
    rc = part("精彩回顾")
    if '<p class="recall-line">' not in rc: errs.append("「精彩回顾」要有 <p class=\"recall-line\"><b>一句话：</b>…</p>")
    items_r = re.findall(r'<div class="item"><b>(.*?)</b><p>(.*?)</p><span class="sec">(§[^<]+)</span></div>', rc, flags=re.S)
    if not 4 <= len(items_r) <= 6 or len(items_r) != rc.count('<div class="item">'): errs.append(f"「精彩回顾」应有 4–6 张卡片，写法 <div class=\"item\"><b>标题</b><p>…</p><span class=\"sec\">§k</span></div>，现在认出 {len(items_r)} 张")
    for b_, p_, _ in items_r:
        if han(p_) > 100: errs.append(f"「精彩回顾」{b_}：{han(p_)} 个汉字，超过 100")

    # 不替译本说话：本站没有译本的文本
    for m in re.finditer(r"译本(?:里|中|译作|译为|写作|作「|叫|的译法|第\s*\d+\s*页)", re.sub(r"<[^>]+>", "", t)):
        errs.append(f"页面替译本说话了（本站没有译本文本，不写译本怎么译、在哪一页）：…{m.group(0)}…")
    for k in re.findall(r'class="note" data-key="([^"]+)"', t):
        if not k.startswith(f"{nn}-"): errs.append(f"笔记的 data-key 要以 {nn}- 开头：{k}")

    errs += check_images(t, path, min_photos=3, min_svgs=1)
    c = counts(t)
    if not 5 <= c["检查题"] <= 7: errs.append(f"理解检查应有 5–7 题，现在 {c['检查题']} 题")
    errs += check_markup(t)
    print(("✗" if errs else "✓"), path, " ".join(f"{k} {v}" for k, v in c.items()), f"地图 {len(items)} 坐下 {sits} 回顾 {len(items_r)} 原文 {total} 词")
    for e in errs: print("    " + e)
    bad += bool(errs)
sys.exit(1 if bad else 0)
