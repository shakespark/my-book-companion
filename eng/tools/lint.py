#!/usr/bin/env python3
"""页面结构检查：python3 -I tools/lint.py chapters/03a.html …
页 id → 章和节从 assets/chapters.js 读（EG_PAGES 的 secs、need，EG_SECS 每节的段号范围 p，字符串「1–5」或「3」）；原文从 source/text/NN.txt 读（行首 [k]，{Q} 引文、{B} 方框，{F} 图注行不编号）。
照 Thinking in Systems 导读的 lint.py 改：去掉译本（勘误、.zhv、和译本重合）和情境题，加「书里的人和项目」（照 Uncontrolled 的）、分节地图里 .at 的原文定位。
查：小节标题和顺序、读之前、分节地图（每节一条，只写 .what；超过 1000 词的节一处 .at）、概念块、模拟器、书里的人和项目（.lede、3–8 块、每块 260 字、.who 人物卡）、英文词条（.loc 在那一段、8–20 条、trap 占比）、
.at 原文定位（4–7 个词一字不差在 data-p 那一段）、引用块（只在「读完」里）、读完、今天怎么看、本站怎么看、精彩回顾、图片（照片 2、SVG 2）、理解检查和「想一想」、写死的颜色、直引号、原书材料的路径。
另报「嫌疑」（？开头，不算不通过，作者在报告里逐条答）：相对位置词、「今天」栏里 2012 年以前的年份、卡片标题两句并列、「是一回事 / 同一件事」这类等同词、「没给出处 / 没点名」（先查 References）。
00 是主编页，不走这里，只跑 overlap 和 check。通用的几项在 ~/tutorials-deploy/scripts/lint_common.py。"""
import glob, html, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.expanduser("~/tutorials-deploy/scripts"))
from lint_common import norm, check_entries, check_quotes, check_images, check_markup, counts, page_text

SECS = ["这一页在做什么", "读之前：这一页在全书的哪里", "分节地图", "先用中文过一遍：这一页的概念",
        "动手：模拟器", "书里的人和项目", "原文里的词和句",
        "读完：作者到底说了什么", "今天怎么看", "本站怎么看", "检查一下理解", "精彩回顾"]
SIM_SEC, WORD_SEC, PEOPLE_SEC = "动手：模拟器", "原文里的词和句", "书里的人和项目"
LIGHT = ["这一页在做什么", "读之前：这一页在全书的哪里", "分节地图"]      # 轻量页（need 里有 light；这本书暂时没有）必有的节；别的节可写可不写（模拟器除外）
PUB_YEAR = 2012                                                         # 原书出版年：「今天」栏里早于它的年份多半该放进「当时」
VERDICTS = ["成立", "部分成立", "被改写", "有争议"]
LONG_SEC = 1000                                                         # 超过这么多词的节，分节地图里要一处 .at 点出节里的转折
# 人物卡：<div class="who"><div><b>原名</b><span class="en">生卒年</span>一句话</div>…</div>，一人一张
WHO_RE = r'<div class="who">(?:\s*<div><b>[^<]+</b><span class="en">[^<]*</span>(?:(?!</?div\b)[\s\S])*?</div>)+\s*</div>'
han = lambda s: len(re.findall(r"[一-鿿]", re.sub(r"<[^>]+>", "", s)))
plain = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

import json
js = open(os.path.join(ROOT, "assets/chapters.js"), encoding="utf-8").read()
PAGES, ORDER = {}, []
for m in re.finditer(r'\{ id: "(\w+)", ch: (\d+), secs: (\[[^\]]*\]), need: (\[[^\]]*\]), t: "([^"]*)", d: "([^"]*)" \}', js[js.index("window.EG_PAGES"):]):
    PAGES[m.group(1)] = (int(m.group(2)), json.loads(m.group(3)), json.loads(m.group(4))); ORDER.append(m.group(1))
prange = lambda p: tuple(map(int, p.split("–"))) if "–" in p else (int(p), int(p))
SEC_TAB = {}   # 章 → {节号（字符串）: (第一段, 最后一段)}
for m in re.finditer(r'"(\d\d)": \[\n(.*?)\n  \]', js[js.index("window.EG_SECS"):js.index("window.EG_PAGES")], flags=re.S):
    SEC_TAB[int(m.group(1))] = {r["k"]: prange(r["p"]) for r in (json.loads(x.strip().rstrip(",")) for x in m.group(2).splitlines())}
CH_LAST, CH_N = {}, {}
for _pid, (_ch, _, _) in PAGES.items(): CH_LAST[_ch] = _pid; CH_N[_ch] = CH_N.get(_ch, 0) + 1


def load(ch, want):
    """读 source/text/NN.txt 里属于这一页的几节。返回 paras {段号: 归一化文字}、quoted {{Q} 段号：缩进的引文，多是别人的话}、secs [(节号, 第一段, 最后一段, 词数)]。{F} 图注行不编号，不算。"""
    tab = SEC_TAB.get(ch, {})
    rng = {k: tab[k] for k in want if k in tab}
    paras, quoted, words = {}, set(), {k: 0 for k in rng}
    for line in open(os.path.join(ROOT, f"source/text/{ch:02d}.txt"), encoding="utf-8").read().splitlines():
        m = re.match(r"\[(\d+)\] (\{[QB]\} )?(.*)$", line)
        if not m: continue
        p = int(m.group(1))
        k = next((k for k, (a, b) in rng.items() if a <= p <= b), None)
        if k is None: continue
        raw = re.sub(r"\{b:([^}]*)\}", r"\1", m.group(3))      # {b:…} 是原书粗体（第 1 章 Box 1），和 * 一样不算原文
        paras[p] = norm(raw)
        if m.group(2) == "{Q} ": quoted.add(p)
        words[k] += len(raw.split())
    return paras, quoted, [(k, rng[k][0], rng[k][1], words[k]) for k in want if k in rng]


def ids(path, cls):
    return re.findall(rf'<div class="{cls}" id="([^"]+)">', open(path, encoding="utf-8").read())


QUOTE_IN = re.compile(r"[‘“”\"]|’(?![A-Za-z])|(?<![A-Za-z])’")  # ’ 夹在字母中间是撇号，放行
SEC_RE = r"§(\d+)"

bad = 0
for path in sys.argv[1:]:
    t = open(path, encoding="utf-8").read(); errs, sus = [], []
    pid = re.search(r"(\w+)\.html$", path).group(1)
    if pid not in PAGES: print(f"✗ {path}  chapters.js 的 EG_PAGES 里没有页 {pid}（00 是主编页，只跑 overlap 和 check）"); bad += 1; continue
    ch, want, need = PAGES[pid]
    light = "light" in need; nsim_want = 2 if "sim2" in need else 1 if "sim" in need else 0
    paras, quoted, secs = load(ch, want)
    if not secs: print(f"✗ {path}  chapters.js 的 EG_SECS 里没有第 {ch} 章的节 {want}"); bad += 1; continue
    if f'<body data-page="{pid}">' not in t: errs.append(f'<body> 应写成 <body data-page="{pid}">')
    def part(a):
        i = t.find(f"<h2>{a}</h2>")
        if i < 0: return ""
        j = t.find("<h2>", i + 4)
        return t[i:j if j > 0 else len(t)]
    def at_p(s, where):
        """data-p="18 21" 里的段号都要在这一页。"""
        return [f"{where}：data-p 里的 {x} 不是这一页的段号" for x in s.split() if not x.isdigit() or int(x) not in paras]
    def cover(dp, label, where):
        """data-p 里每一段所在的节，都要列在节号标签里（「§4 §7」）：跨节了标签只写一节，读者回书时会找错地方。"""
        want_ = {next((s[0] for s in secs if s[1] <= int(x) <= s[2]), None) for x in dp.split() if x.isdigit()} - {None}
        miss = sorted(want_ - set(re.findall(SEC_RE, label)), key=int)
        return [f"{where}：data-p 里有 §{'、§'.join(miss)} 的段，节号标签（{plain(label)}）要列全"] if miss else []

    # 小节标题和顺序：模拟器只在 need 里有 sim / sim2 的页；轻量页只要 LIGHT 那几节
    allowed = [x for x in SECS if x != SIM_SEC or nsim_want]
    must = LIGHT if light else allowed
    present = [x for x in SECS if f"<h2>{x}</h2>" in t]
    for x in must:
        if x not in present: errs.append(f"缺少小节：{x}")
    for x in set(present) - set(allowed): errs.append(f"这一页不该有「{x}」（看 chapters.js 的 need）")
    pos = [t.find(f"<h2>{x}</h2>") for x in present]
    if pos != sorted(pos): errs.append("小节顺序不对，应为：" + " → ".join(SECS))
    for x in re.findall(r"<h2>(.*?)</h2>", t):
        if x not in SECS: errs.append(f"多出来的小节标题：{x}（标题一个字都不能改）")
    vis = re.sub(r"<[^>]+>", "", re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S))
    for m in re.finditer(r".{0,20}\[\d[\d–, -]*\]", vis): errs.append(f"页面上有读者看不到的段号 [k]：…{m.group(0).strip()}（写「书里」或给原文 4–7 个词）")
    if 'class="gate"' in t: errs.append("这本书没有读前 / 读后的分界线，不写 div.gate")
    g = re.search(r'<div class="gist">(.*?)</div>', t, flags=re.S)
    if not g: errs.append("「这一页在做什么」要有 <div class=\"gist\">")
    elif han(g.group(1)) > 200: errs.append(f"「这一页在做什么」{han(g.group(1))} 个汉字，超过 200")
    if g and not re.match(r'\s*(<figure|<svg)', t[g.end():]): errs.append("「这一页在做什么」的 div.gist 后面要紧跟一张图（<figure> 或 <svg>）")

    # 读之前
    pre = part("读之前：这一页在全书的哪里")
    if '<div class="linehere"></div>' not in pre: errs.append("「读之前」第一行要写 <div class=\"linehere\"></div>（由 eg.js 画）")
    if '<div class="crux">' not in pre: errs.append("「读之前」要有一个 <div class=\"crux\">")
    nq = len(re.findall(r"<li>", re.search(r'<ol class="qs">(.*?)</ol>', pre, flags=re.S).group(1))) if '<ol class="qs">' in pre else 0
    if not 2 <= nq <= 4: errs.append(f"「读之前」带着读的问题（<ol class=\"qs\">）应有 2–4 个，现在 {nq} 个")
    lead = re.sub(r'<div class="crux">.*?</div>|<ol class="qs">.*?</ol>|<p class="lede">.*?</p>|<div class="heads-up">.*?</div>', "", pre, flags=re.S)
    if han(lead) > 200: errs.append(f"「读之前」那段话 {han(lead)} 个汉字，超过 200")
    hu = re.findall(r'<div class="heads-up">(.*?)</div>', t, flags=re.S)
    if len(hu) > 1 or t.count('<div class="heads-up">') != pre.count('<div class="heads-up">'): errs.append("「别被带歪」框（div.heads-up）一页至多一个，只放在「读之前」里")
    for x in hu:
        if han(x) > 120: errs.append(f"「别被带歪」框 {han(x)} 个汉字，超过 120")

    # 分节地图：每节一条，只写 .what（节名、段号、英文开头、词数、档由 eg.js 从 chapters.js 补）；超过 1000 词的节一处 .at 点出节里的转折
    sm = part("分节地图")
    items = re.findall(r'<li data-sec="(\w+)"><span class="what">(.*?)</span></li>', sm, flags=re.S)
    if [i[0] for i in items] != want or sm.count("<li") != len(items):
        errs.append(f"分节地图的节号应为 {want}，实际认出 {[i[0] for i in items]}（写法：<li data-sec=\"k\"><span class=\"what\">…</span></li>，其余由脚本补）")
    sinfo = {s[0]: s for s in secs}
    for k, what in items:
        if han(what) > 90: errs.append(f"分节地图 §{k}：说明 {han(what)} 个汉字，超过 90")
        ats = re.findall(r'<span class="at" data-p="([^"]*)">(?!§)', what)
        if k in sinfo:
            _, a, b, w = sinfo[k]
            if w > LONG_SEC and not ats: errs.append(f"分节地图 §{k}：这一节 {w} 词，超过 {LONG_SEC}，要用一处 <span class=\"at\" data-p=\"段号\">原文 4–7 个词</span> 点出节里的转折")
            if len(ats) > 1: errs.append(f"分节地图 §{k}：.at 只用一处，现在 {len(ats)} 处")
            for dp in ats:
                if not (dp.isdigit() and a <= int(dp) <= b): errs.append(f"分节地图 §{k}：.at 的 data-p={dp!r} 不在这一节（第 {a}–{b} 段）")

    # 概念块
    cp = part("先用中文过一遍：这一页的概念")
    blocks = re.findall(r'<div class="concept" id="([^"]+)">(.*?)</div>\s*(?=<div class="concept"|<h2>|<p[ >]|<figure|$)', cp, flags=re.S)
    if cp.count('<div class="concept"') != len(blocks): errs.append("概念块的写法不对：<div class=\"concept\" id=\"c-…\"><h3>…</h3><p>…</p><p class=\"use\">…</p></div>")
    if not (0 if light else 2) <= len(blocks) <= 5: errs.append(f"概念块应有 {'0' if light else '2'}–5 个，现在 {len(blocks)} 个")
    for cid, body in blocks:
        if not re.fullmatch(r"c-[a-z0-9-]+", cid): errs.append(f"概念块 id 要写成 c- 加小写英文：{cid}")
        if not re.match(r'\s*<h3><span class="sec">§\d+</span>', body): errs.append(f"概念块 {cid}：要以 <h3><span class=\"sec\">§k</span>中文名 <span class=\"en\">原文</span></h3> 开头")
        use = re.findall(r'<p class="use"><b>在这一页：</b>(.*?)</p>', body, flags=re.S)
        if len(use) != 1: errs.append(f"概念块 {cid}：要有一句 <p class=\"use\"><b>在这一页：</b>…</p>")
        elif han(use[0]) > 80: errs.append(f"概念块 {cid}：「在这一页」{han(use[0])} 个汉字，超过 80")
        main_ = re.sub(r'<h3>.*?</h3>|<p class="use">.*?</p>|<figure.*?</figure>|<svg.*?</svg>', "", body, flags=re.S)
        if han(main_) > 320: errs.append(f"概念块 {cid}：{han(main_)} 个汉字，超过 320")
    others = [o for o in glob.glob(os.path.join(ROOT, "chapters/*.html")) if os.path.abspath(o) != os.path.abspath(path)]
    for other in others:
        for cid in set(ids(other, "concept")) & {b[0] for b in blocks}:
            errs.append(f"概念 {cid} 在 {os.path.basename(other)} 里已经写过，这里改成 <a class=\"term\" href=\"{os.path.basename(other)}#{cid}\">…</a>")
    for href_, cid in re.findall(r'<a class="term" href="(\w+)\.html#(c-[a-z0-9-]+)">', t):
        f = os.path.join(ROOT, f"chapters/{href_}.html")
        if os.path.exists(f) and cid not in ids(f, "concept"): errs.append(f"概念链接 {href_}.html#{cid}：那一页没有这个概念块")

    # 模拟器：need 里 sim 一个（id sim-<页>），sim2 两个（id sim-<页>-<小写英文>）；脚本只为它们服务
    simids = re.findall(r'<div class="sim" id="(sim-[^"]+)">', t)
    scripts = re.findall(r"<script(?![^>]*src=)[^>]*>.*?</script>", t, flags=re.S)
    styles = re.findall(r"<style[^>]*>.*?</style>", t, flags=re.S)
    if nsim_want:
        sp = part(SIM_SEC)
        if len(simids) != nsim_want: errs.append(f"这一页要有 {nsim_want} 个模拟器（chapters.js 的 need），现在 {len(simids)} 个")
        okid = (lambda x: x == f"sim-{pid}") if nsim_want == 1 else (lambda x: re.fullmatch(rf"sim-{pid}-[a-z]+", x))
        for x in simids:
            if not okid(x): errs.append(f"模拟器的 id 应为 " + (f"sim-{pid}" if nsim_want == 1 else f"sim-{pid}-<小写英文>") + f"：{x}")
            if f'<div class="sim" id="{x}">' not in sp: errs.append(f"模拟器 {x} 要放在「动手：模拟器」里")
        if len(scripts) != 1: errs.append(f"模拟器的脚本写在页面末尾一个 <script> 里，现在 {len(scripts)} 段")
        for st in styles:
            for sel in re.findall(r"(?:^|})\s*([^{}@]+)\{", re.sub(r"/\*.*?\*/", "", st[st.find(">") + 1:], flags=re.S)):
                if not all(x.strip().startswith(f"#sim-{pid}") for x in sel.split(",")): errs.append(f"页面 <style> 里的选择器要以 #sim-{pid} 开头：{sel.strip()[:40]}")
            if re.search(r"#[0-9a-fA-F]{3,6}\b|rgb\(", st): errs.append("页面 <style> 里写死了颜色，用 var(--…)")
        if "</main>" in t and scripts and t.find(scripts[0]) < t.find("</main>"): errs.append("模拟器的 <script> 放在 </main> 之后")
        if len(re.findall(r"先猜", sp)) < nsim_want: errs.append("「动手：模拟器」里每个模拟器之前要有一段「先猜：……」")
    elif simids or scripts or styles: errs.append("这一页没有模拟器（chapters.js 的 need 里没有 sim），页面里不能有 .sim、<script> 或 <style>")
    bare = t
    for x in scripts + styles: bare = bare.replace(x, "")

    # 书里的人和项目：一句 .lede，3–8 个 <h3><span class="sec">§k</span>标题</h3> 小块，按节号不倒序；每块不算人物卡和图不超过 260 个汉字；.who 只在这一节
    pw = part(PEOPLE_SEC)
    nwho = len(re.findall(r'<div class="who">', t)); npeople = 0
    if nwho != pw.count('<div class="who">'): errs.append(f"人物卡（.who）只放在「{PEOPLE_SEC}」里")
    if nwho != len(re.findall(WHO_RE, t)): errs.append("人物卡的写法不对：<div class=\"who\"><div><b>原名</b><span class=\"en\">生卒年</span>一句话</div></div>（一人一个内层 <div>）")
    if pw:
        head, *blks = pw.split("<h3>"); npeople = len(blks)
        if '<p class="lede">' not in head: errs.append(f"「{PEOPLE_SEC}」开头要有一句 <p class=\"lede\">…</p>（照抄样板）")
        if not 3 <= len(blks) <= 8: errs.append(f"「{PEOPLE_SEC}」应有 3–8 个 <h3> 小块，现在 {len(blks)} 个")
        last_k = 0
        for b in blks:
            ttl = plain(b.split("</h3>")[0])
            m = re.match(r'<span class="sec">§(\d+)</span>', b)
            if not m: errs.append(f"「{PEOPLE_SEC}」小块标题前要有节号 <span class=\"sec\">§k</span>：{ttl}")
            elif int(m.group(1)) < last_k: errs.append(f"「{PEOPLE_SEC}」按在书里出现的顺序排：{ttl} 排在 §{last_k} 之后")
            else: last_k = int(m.group(1))
            body = re.sub(WHO_RE + r'|<figure.*?</figure>', "", b.split("</h3>", 1)[-1], flags=re.S)
            if han(body) > 260: errs.append(f"「{PEOPLE_SEC}」{ttl}：{han(body)} 个汉字，超过 260（不算人物卡和图）")

    # 英文词条：英文伴读的格式（接得进跨书词本）；.loc 4–7 个词、在 data-p 那一段；8–20 条，trap 占三分之一以上
    ws = part(WORD_SEC)
    if t.count('<div class="entry') != ws.count('<div class="entry'): errs.append(f"词条（.entry）只放在「{WORD_SEC}」里")
    ents = re.findall(r'<div class="entry( trap)?"><div class="en">(.*?)</div><div class="loc" data-p="(\d+)">(.*?)</div><div class="zh">(.*?)</div>(?:<div class="note">(.*?)</div>)?</div>', ws, flags=re.S)
    if ws.count('<div class="entry') != len(ents): errs.append("词条的写法不对：<div class=\"entry [trap]\"><div class=\"en\">…</div><div class=\"loc\" data-p=\"段号\">… 4–7 个词 …</div><div class=\"zh\">…</div><div class=\"note\">…</div></div>（.note 可省）")
    if ws and not 8 <= len(ents) <= 20: errs.append(f"词条应有 8–20 条，现在 {len(ents)} 条")
    if ents: errs += check_entries(ws, paras, trap_ratio=1 / 3, max_loc_words=7, scope="这一页")
    for trap, en_, p, loc, zh_, note in ents:
        n = len(norm(plain(loc)).strip("… ").split())
        if n < 4: errs.append(f".loc 太短（{n} 词，要 4–7 个）：{plain(loc)!r}")
        if QUOTE_IN.search(plain(loc)): errs.append(f".loc 不能含引号（电子书里不好搜）：{plain(loc)!r}")
        if note and han(note) > 100: errs.append(f"词条「{plain(en_)[:20]}」：.note {han(note)} 个汉字，超过 100")
        if han(zh_) > 40: errs.append(f"词条「{plain(en_)[:20]}」：.zh {han(zh_)} 个汉字，超过 40（短，只写这一句里的意思）")

    # 引用块：不超过 2 处，只引作者自己的话
    errs += check_quotes(t, 2)
    for q in re.findall(r'<blockquote class="quote">(.*?)<cite>', t, flags=re.S):
        s = norm(plain(q)).strip("… ").strip()
        where = [p for p, v in paras.items() if s.replace("…", "") and all(x.strip() in v for x in s.split("…") if x.strip())]
        if not where: errs.append(f"引用块在这一页的原文里找不到（要一字不差，省略处用 …）：{s[:50]!r}")
        elif all(p in quoted for p in where): errs.append(f"引用块引的是 {{Q}} 题词（多是别人的话），只引作者自己写的：{s[:50]!r}")
        elif all(paras[p][:1] in "'\"" for p in where): errs.append(f"引用块所在的段落以引号开头，多半是别人的话或课堂对白（原书电子版没把引文标出来），只引作者自己写的；确实是作者的话就在报告里说，主编放行：{s[:50]!r}")
        if len(s.replace("…", " ").split()) > 25: errs.append(f"引用块超过 25 个词：{s[:50]!r}")
    if t.count('<blockquote class="quote">') != part("读完：作者到底说了什么").count('<blockquote class="quote">'):
        errs.append("引用块只放在「读完：作者到底说了什么」里")

    # 读完：作者到底说了什么
    rd = part("读完：作者到底说了什么")
    claims = re.findall(r'<div class="claim"><h4>(.*?)</h4><p>(.*?)</p><span class="sec" data-p="([^"]+)">(§[^<]+)</span></div>', rd, flags=re.S)
    if rd and (not 3 <= len(claims) <= 5 or len(claims) != rd.count('<div class="claim">')): errs.append(f"「读完」应有 3–5 条论点，写法 <div class=\"claim\"><h4>论点</h4><p>…</p><span class=\"sec\" data-p=\"段号 段号\">§k</span></div>，现在认出 {len(claims)} 条")
    for h4, body, dp, where in claims:
        if han(body) > 150: errs.append(f"「读完」{plain(h4)[:12]}…：{han(body)} 个汉字，超过 150")
        errs += at_p(dp, f"「读完」{plain(h4)[:12]}…") + cover(dp, where, f"「读完」{plain(h4)[:12]}…")
    sw = re.findall(r'<p class="sowhat"><b>合起来：</b>(.*?)</p>', rd, flags=re.S)
    if rd and len(sw) != 1: errs.append("「读完」最后要有一句 <p class=\"sowhat\"><b>合起来：</b>…</p>")
    elif sw and han(sw[0]) > 120: errs.append(f"「合起来」{han(sw[0])} 个汉字，超过 120")
    cs = re.findall(r'<p class="chapsum"><b>这一章合起来：</b>(.*?)</p>', rd, flags=re.S)
    if CH_N[ch] > 1 and CH_LAST[ch] == pid:
        if len(cs) != 1: errs.append("这是这一章的最后一页，「读完」要在最后加 <p class=\"chapsum\"><b>这一章合起来：</b>…</p>")
        elif han(cs[0]) > 260: errs.append(f"「这一章合起来」{han(cs[0])} 个汉字，超过 260")
    elif cs: errs.append(f"只有拆页的章的最后一页才写「这一章合起来」（第 {ch} 章的最后一页是 {CH_LAST[ch]}）")
    rd_body = re.sub(r'<p class="lede">.*?</p>|<blockquote.*?</blockquote>', "", rd, flags=re.S)
    if han(rd_body) > 1100: errs.append(f"「读完」正文 {han(rd_body)} 个汉字，超过 1100（不算引用块）")

    # 今天怎么看：1–3 张卡
    td = part("今天怎么看")
    tcs = re.findall(r'<div class="today" data-verdict="([^"]+)"><h4>(.*?)</h4><dl>(.*?)</dl></div>', td, flags=re.S)
    if td and (not 1 <= len(tcs) <= 3 or len(tcs) != td.count('<div class="today"')): errs.append(f"「今天怎么看」应有 1–3 张卡片，写法 <div class=\"today\" data-verdict=\"成立\"><h4>书里的说法：…</h4><dl>…</dl></div>，现在认出 {len(tcs)} 张")
    if td and '<ul class="verdicts">' not in td: errs.append("「今天怎么看」要照抄样板的结论图例 <ul class=\"verdicts\">")
    if t.count('<div class="today"') != td.count('<div class="today"'): errs.append("今天怎么看的卡片只放在「今天怎么看」里")
    for v, h4, dl in tcs:
        name = plain(h4)[:16]
        if v not in VERDICTS: errs.append(f"今天怎么看「{name}」：结论四选一：{' / '.join(VERDICTS)}")
        if not plain(h4).startswith("书里的说法："): errs.append(f"今天怎么看「{name}」：<h4> 以「书里的说法：」开头，结论判的就是这一句")
        dts = re.findall(r"<dt>(.*?)</dt>", dl)
        if dts[:3] != ["书里", "当时", "今天"] or not set(dts[3:]) <= {"另一边"}: errs.append(f"今天怎么看「{name}」：<dt> 依次是 书里 / 当时 / 今天（可再加 另一边），现在是 {dts}")
        if not re.search(r'<span class="asof">核对于 20\d\d-\d\d', dl): errs.append(f"今天怎么看「{name}」：「今天」最后要有 <span class=\"asof\">核对于 2026-11。依据：…</span>")
        m = re.search(r'<dt>书里</dt>\s*<dd>.*?<span class="at" data-p="([^"]+)">§[^<]+</span>', dl, flags=re.S)
        if not m: errs.append(f"今天怎么看「{name}」：「书里」要标出处 <span class=\"at\" data-p=\"段号\">§k</span>")
        else: errs += at_p(m.group(1), f"今天怎么看「{name}」")
        if han(dl) > 360: errs.append(f"今天怎么看「{name}」：{han(dl)} 个汉字，超过 360")
        m = re.search(r"<dt>今天</dt>\s*<dd>(.*?)</dd>", dl, flags=re.S)
        old = sorted({y for y in re.findall(r"(?<!\d)(1[89]\d\d|20[0-2]\d)(?!\d)", re.sub(r'<span class="asof">.*?</span>', "", m.group(1) if m else "")) if int(y) < PUB_YEAR})
        if old: sus.append(f"今天怎么看「{name}」：「今天」栏里有 {PUB_YEAR} 年以前的年份 {'、'.join(old)}，书出版时已有的事放「当时」（是后来的研究回头讲旧事就不用改）")
        head = plain(h4).replace("书里的说法：", "", 1)
        if re.search(r"[^，；]{4,}[，；][^，；]{4,}", head): sus.append(f"今天怎么看「{name}」：标题像两句并列，结论标签只能判一句；收窄成一句")

    # 本站怎么看：2–3 块看法，最后一句总体看法
    vw = part("本站怎么看")
    vws = re.findall(r'<div class="views"><h4>(.*?)</h4>\s*<p><b>主流看法：</b>(.*?)</p>\s*<p><b>作者的看法：</b>(.*?)</p>\s*<p class="ours"><b>本站的评论：</b>(.*?)</p></div>', vw, flags=re.S)
    if t.count('<div class="views">') != len(vws) or vw.count('<div class="views">') != len(vws): errs.append("看法块的写法不对，或不在「本站怎么看」里：<div class=\"views\"><h4>问题</h4><p><b>主流看法：</b>…</p><p><b>作者的看法：</b>…</p><p class=\"ours\"><b>本站的评论：</b>…</p></div>")
    if vw and not 2 <= len(vws) <= 3: errs.append(f"「本站怎么看」应有 2–3 块看法，现在 {len(vws)} 块")
    for h4, a, b, c_ in vws:
        if han(a + b + c_) > 420: errs.append(f"看法块「{plain(h4)[:14]}」{han(a + b + c_)} 个汉字，超过 420")
        m = re.search(r'<span class="at" data-p="([^"]+)">§[^<]+</span>', b)
        if not m: errs.append(f"看法块「{plain(h4)[:14]}」：「作者的看法」要标出处 <span class=\"at\" data-p=\"段号\">§k</span>")
        else: errs += at_p(m.group(1), f"看法块「{plain(h4)[:14]}」")
    vd = re.findall(r'<p class="verdict"><b>本站的总体看法：</b>(.*?)</p>', vw, flags=re.S)
    if vw and len(vd) != 1: errs.append("「本站怎么看」最后要有一句 <p class=\"verdict\"><b>本站的总体看法：</b>…</p>")
    elif vd and han(vd[0]) > 160: errs.append(f"「本站的总体看法」{han(vd[0])} 个汉字，超过 160")

    # 检查一下理解：5–7 题、一句话、想一想
    ck = part("检查一下理解")
    if ck and f'data-key="{pid}-oneline"' not in ck: errs.append(f"「检查一下理解」要有 <textarea class=\"note\" data-key=\"{pid}-oneline\">")
    if ck and not re.search(r'<div class="ponder"><p>想一想：.*?</p>\s*<textarea class="note" data-key="' + pid + r'-ponder"', ck, flags=re.S): errs.append(f"「检查一下理解」最后要有 <div class=\"ponder\"><p>想一想：…</p><textarea class=\"note\" data-key=\"{pid}-ponder\"></textarea></div>")
    for k in re.findall(r'class="note" data-key="([^"]+)"', t):
        if not k.startswith(f"{pid}-"): errs.append(f"笔记的 data-key 要以 {pid}- 开头：{k}")

    # 精彩回顾
    rc = part("精彩回顾")
    if rc and '<p class="recall-line">' not in rc: errs.append("「精彩回顾」要有 <p class=\"recall-line\"><b>一句话：</b>…</p>")
    items_r = re.findall(r'<div class="item"><b>(.*?)</b><p>(.*?)</p><span class="sec">(§[^<]+)</span></div>', rc, flags=re.S)
    if rc and (not 4 <= len(items_r) <= 6 or len(items_r) != rc.count('<div class="item">')): errs.append(f"「精彩回顾」应有 4–6 张卡片，写法 <div class=\"item\"><b>标题</b><p>…</p><span class=\"sec\">§k</span></div>，现在认出 {len(items_r)} 张")
    for b_, p_, _ in items_r:
        if han(p_) > 100: errs.append(f"「精彩回顾」{b_}：{han(p_)} 个汉字，超过 100")

    for dp, lab in re.findall(r'<span class="at" data-p="([^"]+)">(§[^<]+)</span>', t): errs += cover(dp, lab, "标出处的 <span class=\"at\">")

    # 节号不能写到这一页以外
    for k in sorted(set(re.findall(r'class="(?:sec|at)"[^>]*>' + SEC_RE, t)) - set(want)):
        errs.append(f"页面上标了 §{k}，这一页只有 {want}")

    # 原文定位 .at（文字不以 § 开头的）：连续 4–7 个词，一字不差在 data-p 那一段里（读者拿去 Kindle 里搜）
    for dp, at in re.findall(r'<span class="at" data-p="([^"]*)">(?!§)(.*?)</span>', t, flags=re.S):
        s_ = norm(plain(at)).strip("… ").strip()
        n = len(s_.split())
        if not dp.isdigit(): errs.append(f".at 的 data-p 只写一个段号：{dp!r}（{plain(at)[:40]}）"); continue
        if int(dp) not in paras: errs.append(f".at 的 data-p={dp} 不是这一页的段号：{plain(at)[:40]!r}")
        elif s_ not in paras[int(dp)]:
            where = [k for k, v in paras.items() if s_ and s_ in v]
            errs.append(f".at 的原文不在第 {dp} 段（要一字不差，斜体的 * 不抄）：{s_!r}" + (f"（在第 {where[0]} 段）" if where else "（这一页的原文里都找不到）"))
        if not 4 <= n <= 7: errs.append(f".at 的原文要 4–7 个词，现在 {n} 个：{s_!r}")
        if QUOTE_IN.search(plain(at)): errs.append(f".at 不能含引号（电子书里不好搜）：{plain(at)!r}")

    # 嫌疑（只提示，不算不通过；作者在报告里逐条答：改了，或者为什么不改）
    txt = page_text(bare)
    for m in re.finditer(r"上一节|下一节|上一页说|前面说过|前面讲过|前文|上文|下文|后面会讲|本章末尾|这一章末尾|章末|节末|开头那段|末尾那段", txt):
        sus.append(f"相对位置词「{m.group(0)}」：指路用 h2 的名字、§k 或原文 4–7 个词")
    for m in re.finditer(r"是一回事|是同一回事|同一件事|是同一个东西|等同于|就等于", txt):
        sus.append(f"等同词「{m.group(0)}」：书里真的说两件事相同吗？多半是「相关 / 相似」，回原文看一眼")
    for m in re.finditer(r"没(?:有)?(?:给|注明|交代)(?:出)?(?:处|来源)|没(?:有)?点名|没说是谁|未注明出处", txt):
        sus.append(f"「{m.group(0)}」：先查书后的 References（source/text/refs.txt 里第 {ch} 章的条目，有几条是作者的补充说明），常常有出处")

    errs += check_images(t, path, min_photos=0 if light else 2, min_svgs=0 if light else 2, pattern=r"\.\./assets/img/\d\d[ab]?-[a-z0-9-]+\.jpg")
    c = counts(t)
    if ck and not 5 <= c["检查题"] <= 7: errs.append(f"理解检查应有 5–7 题，现在 {c['检查题']} 题")
    errs += check_markup(bare)
    total = sum(s[3] for s in secs)
    print(("✗" if errs else "✓"), path, f"词条 {len(ents)}（trap {c['trap']}） 照片 {c['照片']} SVG {c['SVG']} 引用 {c['引用']} 检查题 {c['检查题']}",
          f"概念 {len(blocks)} 模拟器 {len(simids)} 人和项目 {npeople}（人物卡 {nwho}） 今天 {len(tcs)} 看法 {len(vws)} 回顾 {len(items_r)} 原文 {total} 词")
    for e in errs: print("    " + e)
    for e in sus: print("    ？" + e)
    bad += bool(errs)
sys.exit(1 if bad else 0)
