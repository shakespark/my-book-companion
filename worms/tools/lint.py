#!/usr/bin/env python3
"""页面结构检查：python3 -I tools/lint.py chapters/02b.html …
页 id → 篇和节从 assets/chapters.js 的 DW_PAGES 读；原文从 source/text/NN.txt 读（段号在一篇之内连续）。
查：小节标题和顺序、读之前（全书的线的占位、.crux、带着读的问题）、路线（SVG、只有一句「作者落在哪」、整节不能写成摘要）、
分节地图（每节一条、地标、照抄英文开头、词数）、概念块（id、长度、全站不重复）、人和作品的小块、
原典（.pd-orig 必须在 source/pd/*.txt 里找得到、配本站译文）、词条（.en 重复、.loc 在这一页的原文里、在自己那一节下、密度、trap 占比、不含引号）、
扫描错字表、引用块（数量、长度、只引作者自己的话）、读完（论点、合起来、一篇合起来）、本站怎么看（看法块、总体看法）、
精彩回顾、图片、理解检查和「想一想」、页面里的 <style>/<script>/写死的颜色、直引号、原书材料的路径。
00 和 vm（达尔文的蚯蚓书）是主编页，不走这里，只跑 overlap 和 check。
通用的几项在 ~/tutorials-deploy/scripts/lint_common.py。"""
import glob, html, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.expanduser("~/tutorials-deploy/scripts"))
from lint_common import norm, check_entries, check_quotes, check_images, check_markup, counts

SECS = ["这一页在做什么", "读之前：这一页在全书的哪里", "这一页的路线", "分节地图", "先用中文过一遍：这一页的概念",
        "书里的人和作品", "原典：达尔文和弗洛伊德的原文", "词与短语", "值得停下来的句子", "读完：作者到底说了什么",
        "本站怎么看", "检查一下理解", "精彩回顾"]
PD_SEC = "原典：达尔文和弗洛伊德的原文"
han = lambda s: len(re.findall(r"[一-鿿]", re.sub(r"<[^>]+>", "", s)))
plain = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

js = open(os.path.join(ROOT, "assets/chapters.js"), encoding="utf-8").read()
PAGES = {m.group(1): (int(m.group(2)), [int(x) for x in m.group(3).split(",")], m.group(4))
         for m in re.finditer(r'\{ id: "(\w+)", ch: (\d+), secs: \[([\d, ]+)\], need: \[([^\]]*)\]', js)}
CH_LAST = {}
for _pid, (_ch, _, _) in PAGES.items(): CH_LAST[_ch] = _pid
CH_PAGES = {c: sum(1 for v in PAGES.values() if v[0] == c) for c in CH_LAST}
CH_NAME = {1: "序章", 2: "达尔文篇", 3: "弗洛伊德篇", 4: "尾声"}


def pdnorm(s):
    """原典比对用：去斜体记号，引号统一，各种破折号统一，空白压成一个。"""
    s = norm(s.replace("_", "").replace("*", ""))
    s = re.sub(r"\s*(?:—|–|--)\s*", " — ", s)
    return re.sub(r"\s+", " ", s).strip()


PD = " ".join(pdnorm(open(f, encoding="utf-8").read()) for f in sorted(glob.glob(os.path.join(ROOT, "source/pd/*.txt"))))


def load(ch, want):
    """读 source/text/NN.txt 里属于这一页的几节。返回 paras {段号: 文字}、quoted {{Q}/{D} 段号}、secs [(节号, 第一段, 最后一段, 词数)]。"""
    paras, quoted, secs, k = {}, set(), [], None
    for line in open(os.path.join(ROOT, f"source/text/{ch:02d}.txt"), encoding="utf-8").read().splitlines():
        m = re.match(r"## §(\d+)", line)
        if m:
            k = int(m.group(1))
            if k in want: secs.append([k, None, None, 0])
            continue
        m = re.match(r"\[(\d+)\] (\{[QCD]\} )?(.*)$", line)
        if not m or k not in want: continue
        p = int(m.group(1))
        paras[p] = norm(m.group(3))
        if m.group(2) in ("{Q} ", "{D} "): quoted.add(p)
        s = secs[-1]; s[1] = s[1] or p; s[2] = p; s[3] += len(m.group(3).split())
    return paras, quoted, [tuple(s) for s in secs]


def concept_ids(path):
    return re.findall(r'<div class="concept" id="([^"]+)">', open(path, encoding="utf-8").read())


QUOTE_IN = re.compile(r"[‘“”\"]|’(?![A-Za-z])|(?<![A-Za-z])’")  # ’ 夹在字母中间是撇号，放行

bad = 0
for path in sys.argv[1:]:
    t = open(path, encoding="utf-8").read(); errs = []
    pid = re.search(r"(\w+)\.html$", path).group(1)
    if pid not in PAGES: print(f"✗ {path}  chapters.js 的 DW_PAGES 里没有页 {pid}"); bad += 1; continue
    ch, want, need = PAGES[pid]
    paras, quoted, secs = load(ch, want)
    if f'<body data-page="{pid}">' not in t: errs.append(f'<body> 应写成 <body data-page="{pid}">')
    def part(a):
        i = t.find(f"<h2>{a}</h2>")
        if i < 0: return ""
        j = t.find("<h2>", i + 4)
        return t[i:j if j > 0 else len(t)]

    # 小节标题和顺序；「原典」在 chapters.js 的 need 里有 pd 时必写，没有时可写可不写
    must = [s for s in SECS if s != PD_SEC or '"pd"' in need]
    present = [s for s in SECS if f"<h2>{s}</h2>" in t]
    for s in must:
        if s not in present: errs.append(f"缺少小节：{s}")
    pos = [t.find(f"<h2>{s}</h2>") for s in present]
    if pos != sorted(pos): errs.append("小节顺序不对，应为：" + " → ".join(SECS))
    for s in re.findall(r"<h2>(.*?)</h2>", t):
        if s not in SECS: errs.append(f"多出来的小节标题：{s}（标题一个字都不能改）")
    g = re.search(r'<div class="gist">(.*?)</div>', t, flags=re.S)
    if not g: errs.append("「这一页在做什么」要有 <div class=\"gist\">")
    elif han(g.group(1)) > 200: errs.append(f"「这一页在做什么」{han(g.group(1))} 个汉字，超过 200")

    # 读之前
    pre = part("读之前：这一页在全书的哪里")
    if '<div class="linehere"></div>' not in pre: errs.append("「读之前」第一行要写 <div class=\"linehere\"></div>（全书的线由 dw.js 画）")
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
        e = norm(plain(en)).strip("… ").strip()
        first = next((paras[p] for p in range(p0, p1 + 1) if p in paras and p not in quoted), "").lstrip("'\" ")
        min_w = 3 if QUOTE_IN.search(" ".join(first.split()[:4])) else 4  # 开头第 4 个词就带引号的，抄 3 个词
        if not (first.startswith(e) and min_w <= len(e.split()) <= 7): errs.append(f"分节地图 §{k}：.en 照抄这一节第一段（不算 {{Q}} 引文）开头 4–7 个词（段首的引号不抄），后面加 …：{e!r}")
        if QUOTE_IN.search(plain(en)): errs.append(f"分节地图 §{k}：.en 不能含引号：{plain(en)!r}")
        if abs(int(w) - words) > max(60, words * 0.1): errs.append(f"分节地图 §{k}：词数写的是 {w}，实际约 {words}")
        if han(what) > 60: errs.append(f"分节地图 §{k}：说明 {han(what)} 个汉字，超过 60")

    # 概念块
    cp = part("先用中文过一遍：这一页的概念")
    blocks = re.findall(r'<div class="concept" id="([^"]+)">(.*?)</div>\s*(?=<div class="concept"|<h2>|<p class="lede">|<figure|$)', cp, flags=re.S)
    if cp.count('<div class="concept"') != len(blocks): errs.append("概念块的写法不对：<div class=\"concept\" id=\"c-…\"><h3>…</h3><p>…</p><p class=\"use\">…</p></div>")
    if not 2 <= len(blocks) <= 5: errs.append(f"概念块应有 2–5 个，现在 {len(blocks)} 个")
    for cid, body in blocks:
        if not re.fullmatch(r"c-[a-z0-9-]+", cid): errs.append(f"概念块 id 要写成 c- 加小写英文：{cid}")
        if not re.match(r'\s*<h3><span class="sec">§\d+</span>', body): errs.append(f"概念块 {cid}：要以 <h3><span class=\"sec\">§k</span>中文名 <span class=\"en\">原文</span></h3> 开头")
        use = re.findall(r'<p class="use"><b>在这一页：</b>(.*?)</p>', body, flags=re.S)
        if len(use) != 1: errs.append(f"概念块 {cid}：要有一句 <p class=\"use\"><b>在这一页：</b>…</p>")
        elif han(use[0]) > 80: errs.append(f"概念块 {cid}：「在这一页」{han(use[0])} 个汉字，超过 80")
        main_ = re.sub(r'<h3>.*?</h3>|<p class="use">.*?</p>|<figure.*?</figure>', "", body, flags=re.S)
        if han(main_) > 300: errs.append(f"概念块 {cid}：{han(main_)} 个汉字，超过 300")
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
        ttl = plain(b.split("</h3>")[0])
        if not re.match(r'<span class="sec">§\d+</span>', b): errs.append(f"「书里的人和作品」小块标题前要有节号 <span class=\"sec\">§k</span>：{ttl}")
        body = re.sub(r'<figure.*?</figure>|<div class="who">.*?</div>\s*</div>', "", b.split("</h3>", 1)[-1], flags=re.S)
        if han(body) > 240: errs.append(f"「书里的人和作品」{ttl}：{han(body)} 个汉字，超过 240")

    # 原典：达尔文、弗洛伊德的原文（公有领域），英文或德文原文必须在 source/pd/*.txt 里
    pdp = part(PD_SEC)
    pds = re.findall(r'<div class="pd" data-p="(\d+)">\s*<h4>(.*?)</h4>\s*<p class="where">(.*?)</p>\s*<blockquote class="pd-orig"(?: lang="(?:en|de)")?>(.*?)</blockquote>\s*<p class="pd-zh"><b>本站译：</b>(.*?)</p>\s*(?:<p class="pd-note">(.*?)</p>\s*)?</div>', pdp, flags=re.S)
    if pdp.count('<div class="pd"') != len(pds): errs.append("原典块的写法不对：<div class=\"pd\" data-p=\"段号\"><h4>…</h4><p class=\"where\">…</p><blockquote class=\"pd-orig\" lang=\"en|de\">原文</blockquote><p class=\"pd-zh\"><b>本站译：</b>…</p>（可选 <p class=\"pd-note\">…</p>）</div>")
    if pdp and not 1 <= len(pds) <= 4: errs.append(f"原典块应有 1–4 块，现在 {len(pds)} 块")
    if t.count('class="pd-orig"') != len(pds): errs.append("<blockquote class=\"pd-orig\"> 只能放在「原典」一节的原典块里")
    if pdp and not PD: errs.append("找不到 source/pd/*.txt，没法核对原典")
    for p, h4, where, orig, zh, note in pds:
        name = plain(h4)[:20]
        if int(p) not in paras: errs.append(f"原典「{name}」：data-p={p} 不在这一页")
        if not re.match(r'<span class="sec">§\d+</span>', h4): errs.append(f"原典「{name}」：<h4> 要以 <span class=\"sec\">§k</span> 开头")
        o = pdnorm(plain(orig))
        frags = [x.strip(" .,;:") for x in re.split(r"\s*(?:…|\.\.\.)\s*", o) if len(x.split()) >= 3]
        for x in frags:
            if PD and x not in PD: errs.append(f"原典「{name}」：这段原文在 source/pd/ 里找不到（要一字不差，省略处用 …）：{x[:60]!r}")
        if len(o.replace("…", " ").split()) > 220: errs.append(f"原典「{name}」：原文 {len(o.split())} 词，超过 220")
        if not han(zh): errs.append(f"原典「{name}」：要有本站的中文全译")

    # 词条：在自己那一节的小标题下
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
    if t.count('<div class="entry') != ws.count('<div class="entry'): errs.append("词条只放在「词与短语」里")
    ocr = re.findall(r'<li><span class="loc" data-p="(\d+)">(.*?)</span>', ws)
    errs += check_entries(re.sub(r'<ul class="ocr">.*?</ul>', "", ws, flags=re.S), paras, per_k=6, max_n=80, trap_ratio=0.4, scope="这一页")
    for loc in re.findall(r'<div class="loc" data-p="\d+">(.*?)</div>', t):
        if QUOTE_IN.search(plain(loc)): errs.append(f".loc 不能含引号（Kindle 上不好打，搜不到）：{plain(loc)!r}")
    for p, loc in ocr:
        s = norm(plain(loc)).strip("… ").strip()
        if s not in paras.get(int(p), ""): errs.append(f"扫描错字表：{s!r} 不在第 {p} 段")

    # 引用块：不超过 2 处，只引作者自己的话
    errs += check_quotes(t, 2)
    for q in re.findall(r'<blockquote class="quote">(.*?)<cite>', t, flags=re.S):
        s = norm(plain(q)).strip("… ").strip()
        where = [p for p, v in paras.items() if s.replace("…", "") and all(x.strip() in v for x in s.split("…") if x.strip())]
        if not where: errs.append(f"引用块在这一页的原文里找不到（要一字不差，省略处用 …）：{s[:50]!r}")
        elif all(p in quoted for p in where): errs.append(f"引用块引的是 {{Q}} 段落（别人的话），只引作者自己写的：{s[:50]!r}")
        if len(s.replace("…", " ").split()) > 25: errs.append(f"引用块超过 25 个词：{s[:50]!r}")
    if t.count('<blockquote class="quote">') and t.find('<blockquote class="quote">') < t.find("<h2>值得停下来的句子</h2>"):
        errs.append("引用块只放在「值得停下来的句子」里")

    # 读完：作者到底说了什么
    rd = part("读完：作者到底说了什么")
    claims = re.findall(r'<div class="claim"><h4>(.*?)</h4><p>(.*?)</p><span class="sec">(§[^<]+)</span></div>', rd, flags=re.S)
    if not 3 <= len(claims) <= 5 or len(claims) != rd.count('<div class="claim">'): errs.append(f"「读完」应有 3–5 条论点，写法 <div class=\"claim\"><h4>论点</h4><p>…</p><span class=\"sec\">§k 第 n 段</span></div>，现在认出 {len(claims)} 条")
    for h4, body, where in claims:
        if han(body) > 140: errs.append(f"「读完」{plain(h4)[:12]}…：{han(body)} 个汉字，超过 140")
        if not re.search(r"第 \d+", where): errs.append(f"「读完」{plain(h4)[:12]}…：节号后面要写依据在第几段")
        for p_ in re.findall(r"(\d+)", re.sub(r"§\d+", "", where)):
            if int(p_) not in paras: errs.append(f"「读完」{plain(h4)[:12]}…：第 {p_} 段不在这一页")
    sw = re.findall(r'<p class="sowhat"><b>合起来：</b>(.*?)</p>', rd, flags=re.S)
    if len(sw) != 1: errs.append("「读完」最后要有一句 <p class=\"sowhat\"><b>合起来：</b>…</p>")
    elif han(sw[0]) > 120: errs.append(f"「合起来」{han(sw[0])} 个汉字，超过 120")
    cs = re.findall(r'<p class="chapsum"><b>(.*?)合起来：</b>(.*?)</p>', rd, flags=re.S)
    if CH_PAGES[ch] > 1 and CH_LAST[ch] == pid:
        if len(cs) != 1 or cs[0][0] != CH_NAME[ch]: errs.append(f"这是{CH_NAME[ch]}的最后一页，「读完」要在最后加 <p class=\"chapsum\"><b>{CH_NAME[ch]}合起来：</b>…</p>")
        elif han(cs[0][1]) > 220: errs.append(f"「{CH_NAME[ch]}合起来」{han(cs[0][1])} 个汉字，超过 220")
    elif cs: errs.append(f"只有一篇的最后一页才写「这一篇合起来」（{CH_NAME[ch]}的最后一页是 {CH_LAST[ch]}）")
    if han(re.sub(r'<p class="lede">.*?</p>', "", rd, flags=re.S)) > 900: errs.append(f"「读完」正文 {han(rd)} 个汉字，超过 900")
    if '<blockquote' in rd: errs.append("「读完」里不引原文")

    # 本站怎么看：2–3 块看法，最后一句总体看法
    vw = part("本站怎么看")
    vws = re.findall(r'<div class="views"><h4>(.*?)</h4>\s*<p><b>主流看法：</b>(.*?)</p>\s*<p><b>作者的看法：</b>(.*?)</p>\s*<p class="ours"><b>本站的评论：</b>(.*?)</p></div>', vw, flags=re.S)
    if t.count('<div class="views">') != len(vws) or vw.count('<div class="views">') != len(vws): errs.append("看法块的写法不对，或不在「本站怎么看」里：<div class=\"views\"><h4>问题</h4><p><b>主流看法：</b>…</p><p><b>作者的看法：</b>…</p><p class=\"ours\"><b>本站的评论：</b>…</p></div>")
    if not 2 <= len(vws) <= 3: errs.append(f"「本站怎么看」应有 2–3 块看法，现在 {len(vws)} 块")
    for h4, a, b, c_ in vws:
        if han(a + b + c_) > 380: errs.append(f"看法块「{plain(h4)[:14]}」{han(a + b + c_)} 个汉字，超过 380")
        if not re.search(r"第 \d+", b): errs.append(f"看法块「{plain(h4)[:14]}」：「作者的看法」要标段号（第 n 段）")
    vd = re.findall(r'<p class="verdict"><b>本站的总体看法：</b>(.*?)</p>', vw, flags=re.S)
    if len(vd) != 1: errs.append("「本站怎么看」最后要有一句 <p class=\"verdict\"><b>本站的总体看法：</b>…</p>")
    elif han(vd[0]) > 160: errs.append(f"「本站的总体看法」{han(vd[0])} 个汉字，超过 160")

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

    # 节号不能写到这一页以外
    for k in sorted({int(k) for k in re.findall(r'class="sec">§(\d+)', t)} - set(want)):
        errs.append(f"页面上标了 §{k}，这一页只有 {want}")

    errs += check_images(t, path, min_photos=3, min_svgs=1, pattern=r"\.\./assets/img/(?:\d\d[a-c]?|vm)-[a-z0-9-]+\.jpg")
    c = counts(t)
    if not 5 <= c["检查题"] <= 7: errs.append(f"理解检查应有 5–7 题，现在 {c['检查题']} 题")
    errs += check_markup(t)
    total = sum(s[3] for s in secs)
    print(("✗" if errs else "✓"), path, " ".join(f"{k} {v}" for k, v in c.items()),
          f"概念 {len(blocks)} 原典 {len(pds)} 地图 {len(items)} 看法 {len(vws)} 回顾 {len(items_r)} 原文 {total} 词")
    for e in errs: print("    " + e)
    bad += bool(errs)
sys.exit(1 if bad else 0)
