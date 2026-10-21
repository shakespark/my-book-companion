#!/usr/bin/env python3
"""页面结构检查：python3 -I tools/lint.py chapters/07.html …
页 id → 章和节从 assets/chapters.js 读（UC_PAGES 的 secs，UC_SECS 每节的段号范围 p）；原文从 source/text/NN.txt 读（段号在一章之内连续，00 是导言）。
照 The Selfish Gene 导读的 lint.py 改：没有译本、没有作者尾注；「读之前」可以有一个「别被带歪」框。
查：小节标题和顺序、读之前（全书的线的占位、.crux、带着读的问题）、路线（SVG、只有一句「作者落在哪」、整节不能写成摘要）、
分节地图（每节一条、地标、照抄 chapters.js 的英文开头、词数）、概念块（id、长度、全站不重复）、模拟器（该有的页有且只有一个，脚本和样式只为它服务）、
人和研究的小块、词条（.en 重复、.loc 在这一页的原文里、在自己那一节下、不含引号、不跨分数和星号、密度、trap 占比）、
引用块（数量、长度、只引作者自己的话）、读完（论点、合起来、一章合起来）、
对照今天（卡片、结论标签、核对日期）、本站怎么看（看法块、总体看法）、精彩回顾、图片、理解检查和「想一想」、写死的颜色、直引号、原书材料的路径。
00 是主编页，不走这里，只跑 overlap 和 check。通用的几项在 ~/tutorials-deploy/scripts/lint_common.py。"""
import glob, html, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.expanduser("~/tutorials-deploy/scripts"))
from lint_common import norm, check_entries, check_quotes, check_images, check_markup, counts, page_text

SECS = ["这一页在做什么", "读之前：这一页在全书的哪里", "这一页的路线", "分节地图", "先用中文过一遍：这一页的概念",
        "动手：模拟器", "书里的人、研究和背景", "词与短语", "值得停下来的句子",
        "读完：作者到底说了什么", "对照今天", "本站怎么看", "检查一下理解", "精彩回顾"]
SIM_SEC, PEOPLE_SEC = "动手：模拟器", "书里的人、研究和背景"
VERDICTS = ["成立", "部分成立", "被改写", "有争议"]
han = lambda s: len(re.findall(r"[一-鿿]", re.sub(r"<[^>]+>", "", s)))
plain = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

js = open(os.path.join(ROOT, "assets/chapters.js"), encoding="utf-8").read()
PAGES = {m.group(1): (int(m.group(2)), [int(x) for x in m.group(3).split(",")], m.group(4))
         for m in re.finditer(r'\{ id: "(\w+)", ch: (\d+), secs: \[([\d, ]+)\], need: \[([^\]]*)\]', js[js.index("UC_PAGES"):])}
SEC_TAB = {}   # 章 → {节号: (第一段, 最后一段, en)}
for m in re.finditer(r'"(\d\d)": \[(.*?)\n  \]', js, flags=re.S):
    SEC_TAB[int(m.group(1))] = {int(k): (int(a), int(b), en) for k, a, b, en in
                                re.findall(r'\{ k: (\d+), p: \[(\d+), (\d+)\], t: "[^"]*", en: "([^"]*)"', m.group(2))}
CH_LAST, CH_N = {}, {}
for _pid, (_ch, _, _) in PAGES.items(): CH_LAST[_ch] = _pid; CH_N[_ch] = CH_N.get(_ch, 0) + 1

def load(ch, want):
    """读 source/text/NN.txt 里属于这一页的几节。返回 paras {段号: 归一化文字}、quoted {{Q}{F} 段号：别人的话和图题}、secs [(节号, 第一段, 最后一段, 词数)]。"""
    tab = SEC_TAB.get(ch, {})
    rng = {k: tab[k][:2] for k in want if k in tab}
    paras, quoted, words = {}, set(), {k: 0 for k in rng}
    for line in open(os.path.join(ROOT, f"source/text/{ch:02d}.txt"), encoding="utf-8").read().splitlines():
        if line.startswith("## 书后注释"): break
        m = re.match(r"\[(\d+)\] (\{[QFL]\} )?(.*)$", line)
        if not m: continue
        p = int(m.group(1))
        k = next((k for k, (a, b) in rng.items() if a <= p <= b), None)
        if k is None: continue
        paras[p] = norm(m.group(3))
        if m.group(2) in ("{Q} ", "{F} "): quoted.add(p)
        words[k] += len(m.group(3).split())
    return paras, quoted, [(k, rng[k][0], rng[k][1], words[k]) for k in want if k in rng]


def concept_ids(path):
    return re.findall(r'<div class="concept" id="([^"]+)">', open(path, encoding="utf-8").read())


QUOTE_IN = re.compile(r"[‘“”\"]|’(?![A-Za-z])|(?<![A-Za-z])’")  # ’ 夹在字母中间是撇号，放行

bad = 0
for path in sys.argv[1:]:
    t = open(path, encoding="utf-8").read(); errs = []
    pid = re.search(r"(\w+)\.html$", path).group(1)
    if pid not in PAGES: print(f"✗ {path}  chapters.js 的 UC_PAGES 里没有页 {pid}"); bad += 1; continue
    ch, want, need = PAGES[pid]
    paras, quoted, secs = load(ch, want)
    if not secs: print(f"✗ {path}  chapters.js 的 UC_SECS 里没有第 {ch} 章的节 {want}"); bad += 1; continue
    if f'<body data-page="{pid}">' not in t: errs.append(f'<body> 应写成 <body data-page="{pid}">')
    def part(a):
        i = t.find(f"<h2>{a}</h2>")
        if i < 0: return ""
        j = t.find("<h2>", i + 4)
        return t[i:j if j > 0 else len(t)]

    # 小节标题和顺序；模拟器只在 need 里有 sim 的页
    must = [s for s in SECS if s != SIM_SEC or '"sim"' in need]
    present = [s for s in SECS if f"<h2>{s}</h2>" in t]
    for s in must:
        if s not in present: errs.append(f"缺少小节：{s}")
    for s in set(present) - set(must): errs.append(f"这一页不该有「{s}」（模拟器看 chapters.js 的 need）")
    pos = [t.find(f"<h2>{s}</h2>") for s in present]
    if pos != sorted(pos): errs.append("小节顺序不对，应为：" + " → ".join(SECS))
    for s in re.findall(r"<h2>(.*?)</h2>", t):
        if s not in SECS: errs.append(f"多出来的小节标题：{s}（标题一个字都不能改）")
    g = re.search(r'<div class="gist">(.*?)</div>', t, flags=re.S)
    if not g: errs.append("「这一页在做什么」要有 <div class=\"gist\">")
    elif han(g.group(1)) > 200: errs.append(f"「这一页在做什么」{han(g.group(1))} 个汉字，超过 200")

    # 读之前
    pre = part("读之前：这一页在全书的哪里")
    if '<div class="linehere"></div>' not in pre: errs.append("「读之前」第一行要写 <div class=\"linehere\"></div>（全书的线由 uc.js 画）")
    if '<div class="crux">' not in pre: errs.append("「读之前」要有一个 <div class=\"crux\">")
    nq = len(re.findall(r"<li>", re.search(r'<ol class="qs">(.*?)</ol>', pre, flags=re.S).group(1))) if '<ol class="qs">' in pre else 0
    if not 2 <= nq <= 4: errs.append(f"「读之前」带着读的问题（<ol class=\"qs\">）应有 2–4 个，现在 {nq} 个")
    lead = re.sub(r'<div class="crux">.*?</div>|<ol class="qs">.*?</ol>|<p class="lede">.*?</p>|<div class="heads-up">.*?</div>', "", pre, flags=re.S)
    if han(lead) > 200: errs.append(f"「读之前」那段话 {han(lead)} 个汉字，超过 200")
    hu = re.findall(r'<div class="heads-up">(.*?)</div>', t, flags=re.S)
    if len(hu) > 1 or t.count('<div class="heads-up">') != pre.count('<div class="heads-up">'): errs.append("「别被带歪」框（div.heads-up）一页至多一个，只放在「读之前」里")
    for x in hu:
        if han(x) > 120: errs.append(f"「别被带歪」框 {han(x)} 个汉字，超过 120")

    # 路线
    rt = part("这一页的路线")
    if "<svg" not in rt: errs.append("「路线」要有一张自己画的 SVG")
    lands = re.findall(r'<p class="landing"><b>作者落在哪：</b>(.*?)</p>', rt, flags=re.S)
    if len(lands) != 1: errs.append(f"「路线」要有且只有一句 <p class=\"landing\"><b>作者落在哪：</b>…</p>，现在 {len(lands)} 句")
    elif han(lands[0]) > 130: errs.append(f"「作者落在哪」{han(lands[0])} 个汉字，超过 130")
    if t.count('class="landing"') != len(lands): errs.append("p.landing 只能出现在「路线」里")
    prose = re.sub(r"<svg.*?</svg>|<figcaption>.*?</figcaption>", "", rt, flags=re.S)
    if han(prose) > 380: errs.append(f"「路线」正文 {han(prose)} 个汉字，超过 380（只讲怎么走，不复述内容）")

    # 分节地图：节名和英文开头照 chapters.js
    sm = part("分节地图")
    items = re.findall(r'<li data-sec="(\d+)"><b>(.*?)<span class="w">约 (\d+) 词</span></b><span class="en">(.*?)</span><span class="what">(.*?)</span></li>', sm, flags=re.S)
    if [int(i[0]) for i in items] != want: errs.append(f"分节地图的节号应为 {want}，实际是 {[int(i[0]) for i in items]}（写法照规范：<li data-sec><b>节名<span class=\"w\">约 N 词</span></b><span class=\"en\">…</span><span class=\"what\">…</span></li>）")
    for (k, b, w, en, what), (_, p0, p1, words) in zip(items, secs):
        if not han(b): errs.append(f"分节地图 §{k}：<b> 要写中文节名（照 chapters.js）")
        e = norm(plain(en)).strip("… ").strip()
        want_en = norm(SEC_TAB[ch][int(k)][2])
        if e != want_en: errs.append(f"分节地图 §{k}：.en 照抄 chapters.js 里这一节的 en（{want_en!r}），后面加 …：现在是 {e!r}")
        first = next((paras[p] for p in range(p0, p1 + 1) if p in paras and p not in quoted), "").lstrip("'\" ")
        if not first.startswith(want_en): errs.append(f"分节地图 §{k}：chapters.js 的 en 不是这一节第一段的开头（报告主编）：{want_en!r}")
        if QUOTE_IN.search(plain(en)): errs.append(f"分节地图 §{k}：.en 不能含引号：{plain(en)!r}")
        if abs(int(w) - words) > max(60, words * 0.1): errs.append(f"分节地图 §{k}：词数写的是 {w}，实际约 {words}")
        if han(what) > 70: errs.append(f"分节地图 §{k}：说明 {han(what)} 个汉字，超过 70")

    # 概念块
    cp = part("先用中文过一遍：这一页的概念")
    blocks = re.findall(r'<div class="concept" id="([^"]+)">(.*?)</div>\s*(?=<div class="concept"|<h2>|<p[ >]|<figure|$)', cp, flags=re.S)
    if cp.count('<div class="concept"') != len(blocks): errs.append("概念块的写法不对：<div class=\"concept\" id=\"c-…\"><h3>…</h3><p>…</p><p class=\"use\">…</p></div>")
    if not 2 <= len(blocks) <= 5: errs.append(f"概念块应有 2–5 个，现在 {len(blocks)} 个")
    for cid, body in blocks:
        if not re.fullmatch(r"c-[a-z0-9-]+", cid): errs.append(f"概念块 id 要写成 c- 加小写英文：{cid}")
        if not re.match(r'\s*<h3><span class="sec">§\d+</span>', body): errs.append(f"概念块 {cid}：要以 <h3><span class=\"sec\">§k</span>中文名 <span class=\"en\">原文</span></h3> 开头")
        use = re.findall(r'<p class="use"><b>在这一页：</b>(.*?)</p>', body, flags=re.S)
        if len(use) != 1: errs.append(f"概念块 {cid}：要有一句 <p class=\"use\"><b>在这一页：</b>…</p>")
        elif han(use[0]) > 80: errs.append(f"概念块 {cid}：「在这一页」{han(use[0])} 个汉字，超过 80")
        main_ = re.sub(r'<h3>.*?</h3>|<p class="use">.*?</p>|<figure.*?</figure>|<svg.*?</svg>', "", body, flags=re.S)
        if han(main_) > 320: errs.append(f"概念块 {cid}：{han(main_)} 个汉字，超过 320")
    for other in glob.glob(os.path.join(ROOT, "chapters/*.html")):
        if os.path.abspath(other) == os.path.abspath(path): continue
        for cid in set(concept_ids(other)) & {b[0] for b in blocks}:
            errs.append(f"概念 {cid} 在 {os.path.basename(other)} 里已经写过，这里改成 <a class=\"term\" href=\"{os.path.basename(other)}#{cid}\">…</a>")
    for href_, cid in re.findall(r'<a class="term" href="(\w+)\.html#(c-[a-z0-9-]+)">', t):
        f = os.path.join(ROOT, f"chapters/{href_}.html")
        if os.path.exists(f) and cid not in concept_ids(f): errs.append(f"概念链接 {href_}.html#{cid}：那一页没有这个概念块")

    # 模拟器：该有的页有且只有一个；脚本只为它服务
    nsim = len(re.findall(r'<div class="sim" id="sim-', t))
    scripts = re.findall(r"<script(?![^>]*src=)[^>]*>.*?</script>", t, flags=re.S)
    styles = re.findall(r"<style[^>]*>.*?</style>", t, flags=re.S)
    if '"sim"' in need:
        sp = part(SIM_SEC)
        if f'<div class="sim" id="sim-{pid}">' not in sp: errs.append(f"「动手：模拟器」里要有 <div class=\"sim\" id=\"sim-{pid}\">")
        if nsim != 1: errs.append(f"一页只有一个模拟器，现在 {nsim} 个")
        if len(scripts) != 1: errs.append(f"模拟器的脚本写在页面末尾一个 <script> 里，现在 {len(scripts)} 段")
        for st in styles:
            for sel in re.findall(r"(?:^|})\s*([^{}@]+)\{", re.sub(r"/\*.*?\*/", "", st[st.find(">") + 1:], flags=re.S)):
                if not all(x.strip().startswith(f"#sim-{pid}") for x in sel.split(",")): errs.append(f"页面 <style> 里的选择器要以 #sim-{pid} 开头：{sel.strip()[:40]}")
            if re.search(r"#[0-9a-fA-F]{3,6}\b|rgb\(", st): errs.append("页面 <style> 里写死了颜色，用 var(--…)")
        if "</main>" in t and scripts and t.find(scripts[0]) < t.find("</main>"): errs.append("模拟器的 <script> 放在 </main> 之后")
        if not re.search(r"先猜", sp): errs.append("「动手：模拟器」在模拟器之前要有一段「先猜：……」")
    elif nsim or scripts or styles: errs.append("这一页没有模拟器（chapters.js 的 need 里没有 sim），页面里不能有 .sim、<script> 或 <style>")
    bare = t
    for x in scripts + styles: bare = bare.replace(x, "")

    # 书里的人和研究
    pw = part(PEOPLE_SEC)
    blks = re.split(r"<h3>", pw)[1:]
    if not 3 <= len(blks) <= 8: errs.append(f"「{PEOPLE_SEC}」应有 3–8 个 <h3> 小块，现在 {len(blks)} 个")
    for b in blks:
        ttl = plain(b.split("</h3>")[0])
        if not re.match(r'<span class="sec">§\d+</span>', b): errs.append(f"「{PEOPLE_SEC}」小块标题前要有节号 <span class=\"sec\">§k</span>：{ttl}")
        body = re.sub(r'<figure.*?</figure>|<div class="who">.*?</div>\s*</div>', "", b.split("</h3>", 1)[-1], flags=re.S)
        if han(body) > 260: errs.append(f"「{PEOPLE_SEC}」{ttl}：{han(body)} 个汉字，超过 260")

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
    errs += check_entries(ws, paras, per_k=3, max_n=60, trap_ratio=0.3, scope="这一页")
    for loc in re.findall(r'<div class="loc" data-p="\d+">(.*?)</div>', t):
        if QUOTE_IN.search(plain(loc)): errs.append(f".loc 不能含引号（Kindle 上不好打，搜不到）：{plain(loc)!r}")

    # 引用块：不超过 2 处，只引作者自己的话
    errs += check_quotes(t, 2)
    for q in re.findall(r'<blockquote class="quote">(.*?)<cite>', t, flags=re.S):
        s = norm(plain(q)).strip("… ").strip()
        where = [p for p, v in paras.items() if s.replace("…", "") and all(x.strip() in v for x in s.split("…") if x.strip())]
        if not where: errs.append(f"引用块在这一页的原文里找不到（要一字不差，省略处用 …）：{s[:50]!r}")
        elif all(p in quoted for p in where): errs.append(f"引用块引的是 {{Q}} 段落（别人的话）或图题，只引作者自己写的：{s[:50]!r}")
        if len(s.replace("…", " ").split()) > 25: errs.append(f"引用块超过 25 个词：{s[:50]!r}")
    if t.count('<blockquote class="quote">') and t.find('<blockquote class="quote">') < t.find("<h2>值得停下来的句子</h2>"):
        errs.append("引用块只放在「值得停下来的句子」里")

    # 读完：作者到底说了什么
    rd = part("读完：作者到底说了什么")
    claims = re.findall(r'<div class="claim"><h4>(.*?)</h4><p>(.*?)</p><span class="sec">(§[^<]+)</span></div>', rd, flags=re.S)
    if not 3 <= len(claims) <= 5 or len(claims) != rd.count('<div class="claim">'): errs.append(f"「读完」应有 3–5 条论点，写法 <div class=\"claim\"><h4>论点</h4><p>…</p><span class=\"sec\">§k 第 n 段</span></div>，现在认出 {len(claims)} 条")
    for h4, body, where in claims:
        if han(body) > 150: errs.append(f"「读完」{plain(h4)[:12]}…：{han(body)} 个汉字，超过 150")
        if not re.search(r"第 \d+", where): errs.append(f"「读完」{plain(h4)[:12]}…：节号后面要写依据在第几段")
        for p_ in re.findall(r"(\d+)", re.sub(r"§\d+", "", where)):
            if int(p_) not in paras: errs.append(f"「读完」{plain(h4)[:12]}…：第 {p_} 段不在这一页")
    sw = re.findall(r'<p class="sowhat"><b>合起来：</b>(.*?)</p>', rd, flags=re.S)
    if len(sw) != 1: errs.append("「读完」最后要有一句 <p class=\"sowhat\"><b>合起来：</b>…</p>")
    elif han(sw[0]) > 120: errs.append(f"「合起来」{han(sw[0])} 个汉字，超过 120")
    cs = re.findall(r'<p class="chapsum"><b>第 (\d+) 章合起来：</b>(.*?)</p>', rd, flags=re.S)
    if CH_N[ch] > 1 and CH_LAST[ch] == pid:
        if len(cs) != 1 or int(cs[0][0]) != ch: errs.append(f"这是第 {ch} 章的最后一页，「读完」要在最后加 <p class=\"chapsum\"><b>第 {ch} 章合起来：</b>…</p>")
        elif han(cs[0][1]) > 220: errs.append(f"「第 {ch} 章合起来」{han(cs[0][1])} 个汉字，超过 220")
    elif cs: errs.append(f"只有拆成两页的章的最后一页才写「第 N 章合起来」（第 {ch} 章的最后一页是 {CH_LAST[ch]}）")
    if han(re.sub(r'<p class="lede">.*?</p>', "", rd, flags=re.S)) > 1000: errs.append(f"「读完」正文 {han(rd)} 个汉字，超过 1000")
    if '<blockquote' in rd: errs.append("「读完」里不引原文")

    # 对照今天：1–3 张卡
    td = part("对照今天")
    tcs = re.findall(r'<div class="today" data-verdict="([^"]+)"><h4>(.*?)</h4><dl>(.*?)</dl></div>', td, flags=re.S)
    if not 1 <= len(tcs) <= 3 or len(tcs) != td.count('<div class="today"'): errs.append(f"「对照今天」应有 1–3 张卡片，写法 <div class=\"today\" data-verdict=\"成立\"><h4>书里的说法：…</h4><dl>…</dl></div>，现在认出 {len(tcs)} 张")
    if td and '<ul class="verdicts">' not in td: errs.append("「对照今天」要照抄样板的结论图例 <ul class=\"verdicts\">")
    if t.count('<div class="today"') != td.count('<div class="today"'): errs.append("对照今天的卡片只放在「对照今天」里")
    for v, h4, dl in tcs:
        name = plain(h4)[:16]
        if v not in VERDICTS: errs.append(f"对照今天「{name}」：结论四选一：{' / '.join(VERDICTS)}")
        if not plain(h4).startswith("书里的说法："): errs.append(f"对照今天「{name}」：<h4> 以「书里的说法：」开头，结论判的就是这一句")
        dts = re.findall(r"<dt>(.*?)</dt>", dl)
        if dts[:3] != ["书里", "当时", "今天"] or not set(dts[3:]) <= {"另一边"}: errs.append(f"对照今天「{name}」：<dt> 依次是 书里 / 当时 / 今天（可再加 另一边），现在是 {dts}")
        if not re.search(r'<span class="asof">核对于 20\d\d-\d\d', dl): errs.append(f"对照今天「{name}」：「今天」最后要有 <span class=\"asof\">核对于 2026-10。依据：…</span>")
        if not re.search(r"第 \d+(?:[–-]\d+)? 段", dl): errs.append(f"对照今天「{name}」：「书里」要标段号（第 n 段）")
        if han(dl) > 360: errs.append(f"对照今天「{name}」：{han(dl)} 个汉字，超过 360")

    # 本站怎么看：2–3 块看法，最后一句总体看法
    vw = part("本站怎么看")
    vws = re.findall(r'<div class="views"><h4>(.*?)</h4>\s*<p><b>主流看法：</b>(.*?)</p>\s*<p><b>作者的看法：</b>(.*?)</p>\s*<p class="ours"><b>本站的评论：</b>(.*?)</p></div>', vw, flags=re.S)
    if t.count('<div class="views">') != len(vws) or vw.count('<div class="views">') != len(vws): errs.append("看法块的写法不对，或不在「本站怎么看」里：<div class=\"views\"><h4>问题</h4><p><b>主流看法：</b>…</p><p><b>作者的看法：</b>…</p><p class=\"ours\"><b>本站的评论：</b>…</p></div>")
    if not 2 <= len(vws) <= 3: errs.append(f"「本站怎么看」应有 2–3 块看法，现在 {len(vws)} 块")
    for h4, a, b, c_ in vws:
        if han(a + b + c_) > 400: errs.append(f"看法块「{plain(h4)[:14]}」{han(a + b + c_)} 个汉字，超过 400")
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

    errs += check_images(t, path, min_photos=2, min_svgs=2, pattern=r"\.\./assets/img/(?:\d\d[ab]?|in)-[a-z0-9-]+\.jpg")
    c = counts(t)
    if not 5 <= c["检查题"] <= 7: errs.append(f"理解检查应有 5–7 题，现在 {c['检查题']} 题")
    errs += check_markup(bare)
    total = sum(s[3] for s in secs)
    print(("✗" if errs else "✓"), path, " ".join(f"{k} {v}" for k, v in c.items()),
          f"概念 {len(blocks)} 模拟器 {nsim} 地图 {len(items)} 今天 {len(tcs)} 看法 {len(vws)} 回顾 {len(items_r)} 原文 {total} 词")
    for e in errs: print("    " + e)
    bad += bool(errs)
sys.exit(1 if bad else 0)
