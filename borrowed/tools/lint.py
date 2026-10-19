#!/usr/bin/env python3
"""页面结构检查：python3 -I tools/lint.py chapters/01a.html …
页 id → 章和节从 assets/chapters.js 的 BT_PAGES 读；原文从 source/text/NN.txt 读（段号在一章之内连续）。
查：小节标题和顺序、读之前（全书的线的占位、.crux、带着读的问题）、路线（SVG、只有一句「作者落在哪」、整节不能写成摘要）、
分节地图（每节一条、地标、照抄英文开头、词数）、概念块（id、长度、全站不重复）、人和作品的小块、
图里的引文（每张图都有一块、逐行或大意、.l 对得上图里的字）、词条（.en 重复、.loc 在这一页的原文里、在自己那一节下、密度、trap 占比；图里的词条另查）、
扫描错字表、引用块（数量、长度、不能引 {Q} 和图片）、精彩回顾、图片、理解检查和「想一想」、页面里的 <style>/<script>/写死的颜色、直引号、原书材料的路径。
通用的几项在 ~/tutorials-deploy/scripts/lint_common.py。"""
import glob, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.expanduser("~/tutorials-deploy/scripts"))
from lint_common import norm, check_entries, check_quotes, check_images, check_markup, counts

SECS = ["这一页在做什么", "读之前：这一页在全书的哪里", "这一页的路线", "分节地图", "先用中文过一遍：这一页的概念",
        "书里的人和作品", "图里的引文", "词与短语", "读完：作者到底说了什么", "值得停下来的句子", "检查一下理解", "精彩回顾"]
han = lambda s: len(re.findall(r"[一-鿿]", re.sub(r"<[^>]+>", "", s)))
WORD = re.compile(r"[^\W_]+(?:'[^\W_]+)?")

js = open(os.path.join(ROOT, "assets/chapters.js"), encoding="utf-8").read()
PAGES = {m.group(1): (int(m.group(2)), [int(x) for x in m.group(3).split(",")])
         for m in re.finditer(r'\{ id: "(\w+)", ch: (\d+), secs: \[([\d, ]+)\]', js)}
# 一章拆成几页的，最后一页要写「这一章合起来」
CH_LAST = {}
for _pid, (_ch, _) in PAGES.items(): CH_LAST[_ch] = _pid
CH_PAGES = {c: sum(1 for v in PAGES.values() if v[0] == c) for c in CH_LAST}


def load(ch, want):
    """读 source/text/NN.txt 里属于这一页的几节。返回 paras {段号: 文字}、quoted {{Q} 段号}、imgs {段号: (图号, 转写的行)}、secs [(节号, 第一段, 最后一段, 词数)]。"""
    paras, quoted, imgs, secs, k = {}, set(), {}, [], None
    for line in open(os.path.join(ROOT, f"source/text/{ch:02d}.txt"), encoding="utf-8").read().splitlines():
        if line.startswith("## 注"): break
        m = re.match(r"## §(\d+) ", line)
        if m:
            k = int(m.group(1))
            if k in want: secs.append([k, None, None, 0])
            continue
        m = re.match(r"\[(\d+)\] (\{Q\} )?(?:\{IMG (\d+)\} ?)?(.*)$", line)
        if not m or k not in want: continue
        p = int(m.group(1))
        if m.group(3): imgs[p] = (m.group(3), [norm(x) for x in m.group(4).split(" / ")])
        else:
            paras[p] = norm(m.group(4))
            if m.group(2): quoted.add(p)
            secs[-1][3] += len(m.group(4).split())
        s = secs[-1]; s[1] = s[1] or p; s[2] = p
    return paras, quoted, imgs, [tuple(s) for s in secs]


def concept_ids(path):
    return re.findall(r'<div class="concept" id="([^"]+)">', open(path, encoding="utf-8").read())


bad = 0
for path in sys.argv[1:]:
    t = open(path, encoding="utf-8").read(); errs = []
    pid = re.search(r"(\w+)\.html$", path).group(1)
    if pid not in PAGES: print(f"✗ {path}  chapters.js 的 BT_PAGES 里没有页 {pid}"); bad += 1; continue
    ch, want = PAGES[pid]
    paras, quoted, imgs, secs = load(ch, want)
    if f'<body data-page="{pid}">' not in t: errs.append(f'<body> 应写成 <body data-page="{pid}">')
    def part(a):
        i = t.find(f"<h2>{a}</h2>")
        if i < 0: return ""
        j = t.find("<h2>", i + 4)
        return t[i:j if j > 0 else len(t)]

    # 小节标题和顺序；「图里的引文」只在这一页有图片引文时要
    need = [s for s in SECS if s != "图里的引文" or imgs]
    present = [s for s in SECS if f"<h2>{s}</h2>" in t]
    for s in need:
        if s not in present: errs.append(f"缺少小节：{s}")
    if not imgs and "图里的引文" in present: errs.append("这一页没有图片引文，不要写「图里的引文」")
    pos = [t.find(f"<h2>{s}</h2>") for s in present]
    if pos != sorted(pos): errs.append("小节顺序不对，应为：" + " → ".join(need))
    for s in re.findall(r"<h2>(.*?)</h2>", t):
        if s not in SECS: errs.append(f"多出来的小节标题：{s}（标题一个字都不能改）")
    g = re.search(r'<div class="gist">(.*?)</div>', t, flags=re.S)
    if not g: errs.append("「这一页在做什么」要有 <div class=\"gist\">")
    elif han(g.group(1)) > 200: errs.append(f"「这一页在做什么」{han(g.group(1))} 个汉字，超过 200")

    # 读之前
    pre = part("读之前：这一页在全书的哪里")
    if '<div class="linehere"></div>' not in pre: errs.append("「读之前」第一行要写 <div class=\"linehere\"></div>（全书的线由 bt.js 画）")
    if '<div class="crux">' not in pre: errs.append("「读之前」要有一个 <div class=\"crux\">")
    nq = len(re.findall(r"<li>", re.search(r'<ol class="qs">(.*?)</ol>', pre, flags=re.S).group(1))) if '<ol class="qs">' in pre else 0
    if not 2 <= nq <= 4: errs.append(f"「读之前」带着读的问题（<ol class=\"qs\">）应有 2–4 个，现在 {nq} 个")
    lead = re.sub(r'<div class="crux">.*?</div>|<ol class="qs">.*?</ol>|<p class="lede">.*?</p>', "", pre, flags=re.S)
    if han(lead) > 200: errs.append(f"「读之前」那段话 {han(lead)} 个汉字，超过 200")

    # 路线
    rt = part("这一页的路线")
    if "<svg" not in rt: errs.append("「路线」要有一张自己画的 SVG")
    lands = re.findall(r'<p class="landing"><b>作者落在哪：</b>(.*?)</p>', rt, flags=re.S)
    if len(lands) != 1: errs.append(f"「路线」要有且只有一句 <p class=\"landing\"><b>作者落在哪：</b>…</p>，现在 {len(lands)} 句")
    elif han(lands[0]) > 130: errs.append(f"「作者落在哪」{han(lands[0])} 个汉字，超过 130")
    if t.count('class="landing"') != len(lands): errs.append("p.landing 只能出现在「路线」里")
    prose = re.sub(r"<svg.*?</svg>|<figcaption>.*?</figcaption>", "", rt, flags=re.S)
    if han(prose) > 380: errs.append(f"「路线」正文 {han(prose)} 个汉字，超过 380（只讲怎么走，不复述内容）")

    # 分节地图
    sm = part("分节地图")
    items = re.findall(r'<li data-sec="(\d+)"><b>(.*?)<span class="w">约 (\d+) 词</span></b><span class="en">(.*?)</span><span class="what">(.*?)</span></li>', sm, flags=re.S)
    if [int(i[0]) for i in items] != want: errs.append(f"分节地图的节号应为 {want}，实际是 {[int(i[0]) for i in items]}（写法照规范：<li data-sec><b>地标<span class=\"w\">约 N 词</span></b><span class=\"en\">…</span><span class=\"what\">…</span></li>）")
    for (k, b, w, en, what), (_, p0, p1, words) in zip(items, secs):
        if not han(b): errs.append(f"分节地图 §{k}：<b> 要写中文地标")
        if han(b) > 22: errs.append(f"分节地图 §{k}：地标 {han(b)} 个汉字，超过 22")
        e = norm(re.sub(r"<[^>]+>", "", en)).strip("… ").strip()
        first = next((paras[p] for p in range(p0, p1 + 1) if p in paras and p not in quoted), "")
        if not (first.startswith(e) and 4 <= len(e.split()) <= 7): errs.append(f"分节地图 §{k}：.en 照抄这一节第一段（不算引文和图片）开头 4–7 个词，后面加 …：{e!r}")
        if abs(int(w) - words) > max(60, words * 0.1): errs.append(f"分节地图 §{k}：词数写的是 {w}，实际约 {words}")
        if han(what) > 40: errs.append(f"分节地图 §{k}：说明 {han(what)} 个汉字，超过 40")
    if '<li class="sit">' in sm: errs.append("这本书的页都在 5500 词以内，分节地图不分坐下")

    # 概念块
    cp = part("先用中文过一遍：这一页的概念")
    blocks = re.findall(r'<div class="concept" id="([^"]+)">(.*?)</div>\s*(?=<div class="concept"|<h2>|<p class="lede">|$)', cp, flags=re.S)
    if cp.count('<div class="concept"') != len(blocks): errs.append("概念块的写法不对：<div class=\"concept\" id=\"c-…\"><h3>…</h3><p>…</p><p class=\"use\">…</p></div>")
    if not 1 <= len(blocks) <= 5: errs.append(f"概念块应有 1–5 个，现在 {len(blocks)} 个")
    for cid, body in blocks:
        if not re.fullmatch(r"c-[a-z0-9-]+", cid): errs.append(f"概念块 id 要写成 c- 加小写英文：{cid}")
        if not re.match(r'\s*<h3><span class="sec">§\d+</span>', body): errs.append(f"概念块 {cid}：要以 <h3><span class=\"sec\">§k</span>中文名 <span class=\"en\">原文</span></h3> 开头")
        use = re.findall(r'<p class="use"><b>在这一页：</b>(.*?)</p>', body, flags=re.S)
        if len(use) != 1: errs.append(f"概念块 {cid}：要有一句 <p class=\"use\"><b>在这一页：</b>…</p>")
        elif han(use[0]) > 70: errs.append(f"概念块 {cid}：「在这一页」{han(use[0])} 个汉字，超过 70")
        main_ = re.sub(r'<h3>.*?</h3>|<p class="use">.*?</p>|<figure.*?</figure>', "", body, flags=re.S)
        if han(main_) > 260: errs.append(f"概念块 {cid}：{han(main_)} 个汉字，超过 260")
    for other in glob.glob(os.path.join(ROOT, "chapters/*.html")):
        if os.path.abspath(other) == os.path.abspath(path): continue
        for cid in set(concept_ids(other)) & {b[0] for b in blocks}:
            errs.append(f"概念 {cid} 在 {os.path.basename(other)} 里已经写过，这里改成 <a class=\"term\" href=\"{os.path.basename(other)}#{cid}\">…</a>")
    for href_, cid in re.findall(r'<a class="term" href="(\w+)\.html#(c-[a-z0-9-]+)">', t):
        f = os.path.join(ROOT, f"chapters/{href_}.html")
        if os.path.exists(f) and cid not in concept_ids(f): errs.append(f"概念链接 {href_}.html#{cid}：那一页没有这个概念块")

    # 书里的人和作品
    pw = part("书里的人和作品")
    blks = re.split(r"<h3>", pw)[1:]
    if not 3 <= len(blks) <= 8: errs.append(f"「书里的人和作品」应有 3–8 个 <h3> 小块，现在 {len(blks)} 个")
    for b in blks:
        ttl = re.sub(r"<[^>]+>", "", b.split("</h3>")[0])
        if not re.match(r'<span class="sec">§\d+</span>', b): errs.append(f"「书里的人和作品」小块标题前要有节号 <span class=\"sec\">§k</span>：{ttl}")
        body = re.sub(r'<figure.*?</figure>|<div class="who">.*?</div>\s*</div>', "", b.split("</h3>", 1)[-1], flags=re.S)
        if han(body) > 240: errs.append(f"「书里的人和作品」{ttl}：{han(body)} 个汉字，超过 240")

    # 图里的引文：每张图一块
    iq = part("图里的引文")
    by_img = {v[0]: (p, v[1]) for p, v in imgs.items()}
    qblocks = re.findall(r'<div class="imgq" data-img="([\d ]+)">(.*?)</div>\s*(?=<div class|<h2>|$)', iq, flags=re.S)
    got = [i for b in qblocks for i in b[0].split()]
    if iq.count('<div class="imgq"') != len(qblocks): errs.append("图里的引文的写法不对：<div class=\"imgq\" data-img=\"图号 图号…\"><h4>…</h4><p class=\"where\">…</p><ol class=\"lines\">…</ol> 或 <p class=\"gq\">…</p></div>")
    for i in sorted(set(by_img) - set(got)): errs.append(f"图里的引文：第 {by_img[i][0]} 段的图 {i} 没有落在任何一块里")
    for i in sorted(set(got) - set(by_img)): errs.append(f"图里的引文：这一页没有图 {i}")
    for i in sorted({i for i in got if got.count(i) > 1}): errs.append(f"图里的引文：图 {i} 出现在两块里")
    if got != sorted(got, key=lambda i: by_img.get(i, (0,))[0]): errs.append("图里的引文：块按段号排，data-img 里的图号也按段号排")
    for ids, body in qblocks:
        ids = [i for i in ids.split() if i in by_img]
        if not ids: continue
        name = "图 " + "、".join(ids)
        p, lines = by_img[ids[0]][0], [x for i in ids for x in by_img[i][1]]
        if not re.search(r'<h4><span class="sec">§\d+</span>第 ' + str(p) + r'(–\d+)? 段', body): errs.append(f"{name}：<h4> 要以 <span class=\"sec\">§k</span>第 {p} 段（或第 {p}–n 段）开头")
        if '<p class="where">' not in body: errs.append(f"{name}：要有 <p class=\"where\">（在屏幕上哪里）")
        lis = re.findall(r'<li><span class="l">(.*?)</span>(.*?)</li>', body, flags=re.S)
        gq = re.findall(r'<p class="gq"><b>大意：</b>(.*?)</p>', body, flags=re.S)
        if not lis and not gq: errs.append(f"{name}：要么逐行（<ol class=\"lines\">），要么给大意（<p class=\"gq\"><b>大意：</b>…</p>）")
        for g_ in gq:
            if han(g_) > 80: errs.append(f"{name}：大意 {han(g_)} 个汉字，超过 80")
        i = name
        for l, zh in lis:
            s = norm(re.sub(r"<[^>]+>", "", l)).strip("… ").strip()
            if len(WORD.findall(s)) > 4: errs.append(f"{i}：.l 只写这一行开头 1–4 个词：{s!r}")
            if not any(x.startswith(s) for x in lines): errs.append(f"{i}：.l 和图里任何一行的开头都对不上（照图抄）：{s!r}")
            if not han(zh): errs.append(f"{i}：{s!r} 这一行没有中文意思")
    for i, k in re.findall(r'<div class="loc" data-img="(\d+)">第 (\d+) 行</div>', t):  # 图里的词条指一张图
        if i not in by_img: errs.append(f"图里的词条指向了这一页没有的图 {i}")
        elif not 1 <= int(k) <= len(by_img[i][1]): errs.append(f"图里的词条：图 {i} 只有 {len(by_img[i][1])} 行，没有第 {k} 行")
    img_entries = re.findall(r'<div class="entry(?: trap)? img">.*?</div></div>', t)
    if len(img_entries) != len(re.findall(r'data-img="\d+">第 \d+ 行', t)): errs.append("图里的词条写成 <div class=\"entry img\">…<div class=\"loc\" data-img=\"图号\">第 k 行</div>…</div>")
    if img_entries and t.find(img_entries[0]) < t.find("<h2>图里的引文</h2>"): errs.append("图里的词条放在「图里的引文」里，紧跟它那张图")

    # 词条（不算图里的）：在自己那一节的小标题下
    tt = re.sub(r'<div class="entry(?: trap)? img">.*?</div></div>', "", t)
    ws = part("词与短语")
    rng = {s[0]: (s[1], s[2]) for s in secs}
    cur = None
    for m in re.finditer(r'<h3 class="sec-head" id="s(\d+)">|<div class="loc" data-p="(\d+)">', ws):
        if m.group(1): cur = int(m.group(1)); continue
        p = int(m.group(2))
        if cur is None: errs.append(f"第 {p} 段的词条前面没有节的小标题 <h3 class=\"sec-head\" id=\"sK\">"); continue
        a, b = rng.get(cur, (0, -1))
        if not a <= p <= b: errs.append(f"第 {p} 段的词条放在了 §{cur} 下面（§{cur} 是第 {a}–{b} 段）")
    for k in re.findall(r'<h3 class="sec-head" id="s(\d+)">', ws):
        if int(k) not in rng: errs.append(f"词与短语：这一页没有 §{k}")
    ocr = re.findall(r'<li><span class="loc" data-p="(\d+)">(.*?)</span>', ws)
    ws_entries = re.sub(r'<ul class="ocr">.*?</ul>', "", tt, flags=re.S)
    errs += check_entries(ws_entries, paras, per_k=5, max_n=80, trap_ratio=1 / 3, scope="这一页")
    for loc in re.findall(r'<div class="loc" data-p="\d+">(.*?)</div>', t):
        if re.search(r'[“”"]', loc): errs.append(f".loc 不能含引号（读者的电子书是直引号，页面只能写弯引号，搜不到）：{loc!r}")
    # 分节地图的 .en 照抄一节开头，这一节开头前 4 个词里就有引号的躲不开，放行
    for (k, b, w, en, what), (_, p0, p1, words) in zip(items, secs):
        first = next((paras[p] for p in range(p0, p1 + 1) if p in paras and p not in quoted), "")
        if re.search(r'[“”"]', en) and '"' not in " ".join(first.split()[:4]): errs.append(f"分节地图 §{k}：.en 不能含引号（这一节开头躲得开）：{en!r}")
    for p, loc in ocr:
        s = norm(re.sub(r"<[^>]+>", "", loc)).strip("… ").strip()
        if s not in paras.get(int(p), ""): errs.append(f"扫描错字表：{s!r} 不在第 {p} 段")

    # 读完：作者到底说了什么
    rd = part("读完：作者到底说了什么")
    claims = re.findall(r'<div class="claim"><h4>(.*?)</h4><p>(.*?)</p><span class="sec">(§[^<]+)</span></div>', rd, flags=re.S)
    if not 3 <= len(claims) <= 5 or len(claims) != rd.count('<div class="claim">'): errs.append(f"「读完」应有 3–5 条论点，写法 <div class=\"claim\"><h4>论点</h4><p>…</p><span class=\"sec\">§k 第 n 段</span></div>，现在认出 {len(claims)} 条")
    for h4, body, where in claims:
        if han(body) > 120: errs.append(f"「读完」{re.sub(r'<[^>]+>', '', h4)[:12]}…：{han(body)} 个汉字，超过 120")
        if not re.search(r"第 \d+", where): errs.append(f"「读完」{re.sub(r'<[^>]+>', '', h4)[:12]}…：节号后面要写依据在第几段")
        for p_ in re.findall(r"(\d+)", re.sub(r"§\d+", "", where)):
            if int(p_) not in paras and int(p_) not in imgs: errs.append(f"「读完」{re.sub(r'<[^>]+>', '', h4)[:12]}…：第 {p_} 段不在这一页")
    sw = re.findall(r'<p class="sowhat"><b>合起来：</b>(.*?)</p>', rd, flags=re.S)
    if len(sw) != 1: errs.append("「读完」最后要有一句 <p class=\"sowhat\"><b>合起来：</b>…</p>")
    elif han(sw[0]) > 100: errs.append(f"「合起来」{han(sw[0])} 个汉字，超过 100")
    cs = re.findall(r'<p class="chapsum"><b>第 (\d+) 章合起来：</b>(.*?)</p>', rd, flags=re.S)
    if CH_PAGES[ch] > 1 and CH_LAST[ch] == pid:
        if len(cs) != 1 or int(cs[0][0]) != ch: errs.append(f"这是第 {ch} 章的最后一页，「读完」要在最后加 <p class=\"chapsum\"><b>第 {ch} 章合起来：</b>…</p>")
        elif han(cs[0][1]) > 200: errs.append(f"「第 {ch} 章合起来」{han(cs[0][1])} 个汉字，超过 200")
    elif cs: errs.append(f"只有一章的最后一页才写「这一章合起来」（第 {ch} 章的最后一页是 {CH_LAST[ch]}）")
    if han(re.sub(r'<p class="lede">.*?</p>', "", rd, flags=re.S)) > 700: errs.append(f"「读完」正文 {han(rd)} 个汉字，超过 700")
    if '<blockquote' in rd: errs.append("「读完」里不引原文")

    # 引用块：不超过 2 处，只引作者自己的话
    errs += check_quotes(t, 2)
    for q in re.findall(r'<blockquote class="quote">(.*?)<cite>', t, flags=re.S):
        s = norm(re.sub(r"<[^>]+>", "", q)).strip("… ").strip()
        where = [p for p, v in paras.items() if s.replace("…", "") and all(x.strip() in v for x in s.split("…") if x.strip())]
        if not where: errs.append(f"引用块在这一页的原文里找不到（要一字不差，省略处用 …；不能引图片里的字）：{s[:50]!r}")
        elif all(p in quoted for p in where): errs.append(f"引用块引的是 {{Q}} 段落（别人的话），只引作者自己写的：{s[:50]!r}")
        if len(s.replace("…", " ").split()) > 25: errs.append(f"引用块超过 25 个词：{s[:50]!r}")

    # 检查一下理解：5–7 题、一句话、想一想
    ck = part("检查一下理解")
    if f'data-key="{pid}-oneline"' not in ck: errs.append(f"「检查一下理解」要有 <textarea class=\"note\" data-key=\"{pid}-oneline\">")
    if not re.search(r'<div class="ponder"><p>想一想：.*?</p>\s*<textarea class="note" data-key="' + pid + r'-ponder"', ck, flags=re.S): errs.append(f"「检查一下理解」最后要有 <div class=\"ponder\"><p>想一想：…</p><textarea class=\"note\" data-key=\"{pid}-ponder\"></textarea></div>")
    for k in re.findall(r'class="note" data-key="([^"]+)"', t):
        if not k.startswith(f"{pid}-"): errs.append(f"笔记的 data-key 要以 {pid}- 开头：{k}")

    # 精彩回顾
    rc = part("精彩回顾")
    if '<p class="recall-line">' not in rc: errs.append("「精彩回顾」要有 <p class=\"recall-line\"><b>一句话：</b>…</p>")
    items_r = re.findall(r'<div class="item"><b>(.*?)</b><p>(.*?)</p><span class="sec">(§[^<]+)</span></div>', rc, flags=re.S)
    if not 4 <= len(items_r) <= 6 or len(items_r) != rc.count('<div class="item">'): errs.append(f"「精彩回顾」应有 4–6 张卡片，写法 <div class=\"item\"><b>标题</b><p>…</p><span class=\"sec\">§k</span></div>，现在认出 {len(items_r)} 张")
    for b_, p_, _ in items_r:
        if han(p_) > 100: errs.append(f"「精彩回顾」{b_}：{han(p_)} 个汉字，超过 100")

    # 节号不能写到这一页以外（尾声不用节号）
    for k in sorted({int(k) for k in re.findall(r'class="sec">§(\d+)', t)} - set(want)):
        errs.append(f"页面上标了 §{k}，这一页只有 {want}")

    errs += check_images(t, path, min_photos=3, min_svgs=1, pattern=r"\.\./assets/img/\d\d[a-d]?-[a-z0-9-]+\.jpg")
    c = counts(t)
    if not 5 <= c["检查题"] <= 7: errs.append(f"理解检查应有 5–7 题，现在 {c['检查题']} 题")
    errs += check_markup(t)
    total = sum(s[3] for s in secs)
    print(("✗" if errs else "✓"), path, " ".join(f"{k} {v}" for k, v in c.items()),
          f"图里词条 {len(img_entries)} 概念 {len(blocks)} 图引文 {len(qblocks)}/{len(imgs)} 地图 {len(items)} 回顾 {len(items_r)} 原文 {total} 词")
    for e in errs: print("    " + e)
    bad += bool(errs)
sys.exit(1 if bad else 0)
