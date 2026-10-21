#!/usr/bin/env python3
"""页面结构检查：python3 -I tools/lint.py chapters/05.html …
页 → 章和节从 assets/chapters.js 读（tools/build_chapters.py 生成：WN_PAGES 的 kind、chs、need，WN_SECS 每节的章、段号、节名、英文开头、杨译地标）；
原文从 source/text/<章>.txt 读（段号一章之内连续），杨译从 source/text/zh/<章>.txt 和 zh/daodu/ 读。
两种页：核心页（kind core）和轻量页（kind light），小节列表不同，见 CORE、LIGHT。
查：小节标题和顺序、读之前、路线（SVG、一句「斯密落在哪」）、分节地图（照抄 chapters.js 的节名、杨译地标、英文开头）、概念块（id、长度、全站不重复）、
模拟器、故事和背景、原典（斯密原文一字不差、每块长度、本站译、熟词生义）、译本勘误、读完（论点 + 今天看的标签）、对照今天、本站怎么看、
检查一下理解、精彩回顾、图片、节号、杨译（只在 .zhv 里、够短、一字不差；别处不能和杨译连续 12 个汉字相同）、写死的颜色、直引号、原书材料路径。
英文长片段的重合（斯密原文只能放在原典里、海尔布罗纳一处都不能抄）由 tools/overlap.py 查。00 是主编页，只跑 overlap 和 check。"""
import glob, html, json, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.expanduser("~/tutorials-deploy/scripts"))
from lint_common import norm, check_images, check_markup, counts, page_text

CORE = ["这一页在做什么", "读之前：这一页在全书的哪里", "这一页的路线", "分节地图", "先用中文过一遍：这一页的概念",
        "动手：模拟器", "故事和背景", "原典：斯密的原话", "译本勘误", "读完：斯密到底说了什么", "对照今天", "本站怎么看",
        "检查一下理解", "精彩回顾"]
LIGHT = ["这一页在做什么", "他想证明什么", "分节地图", "先用中文过一遍：这一页的概念", "故事和背景", "原典：斯密的原话",
         "译本勘误", "今天怎么看", "精彩回顾"]
OPTIONAL = {"译本勘误", "动手：模拟器"} | {"先用中文过一遍：这一页的概念"}  # 轻量页的概念、两种页的勘误可省；模拟器看 need
VERDICTS = ["成立", "部分成立", "过时", "被推翻", "有争议"]
ZH_KINDS = ["误译", "译反", "漏译", "术语", "数字"]
LIMITS = {  # 核心页 / 轻量页
    "concept": ((2, 5), (0, 3)), "story": ((3, 8), (1, 4)), "pd": ((2, 5), (1, 3)), "zherr": ((1, 12), (1, 6)),
    "claim": ((3, 5), (2, 4)), "today": ((3, 5), (0, 2)), "views": ((2, 3), (0, 1)), "recall": ((4, 6), (2, 4)),
    "photos": ((3, 2), (1, 1)),  # (照片, SVG)
}
han = lambda s: len(re.findall(r"[一-鿿]", re.sub(r"<[^>]+>", "", s)))
plain = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

js = open(os.path.join(ROOT, "assets/chapters.js"), encoding="utf-8").read()
PAGES, SECS = {}, {}
for line in js.splitlines():
    s = line.strip().rstrip(",")
    if s.startswith('{"id"'):
        p = json.loads(s); PAGES[p["id"]] = p
cur = None
for line in js.splitlines():
    m = re.match(r'\s*"(\d\d)": \[$', line)
    if m: cur = m.group(1); SECS[cur] = []; continue
    s = line.strip().rstrip(",")
    if cur and s.startswith('{"k"'): SECS[cur].append(json.loads(s))
    if s == "]": cur = None

CLEAN = re.compile(r"\{M:[^}]*\}|\{n\d+\}|\{T\}")


def load_en(ch):
    out = {}
    for line in open(os.path.join(ROOT, f"source/text/{ch}.txt"), encoding="utf-8").read().splitlines():
        if line.startswith("## 注"): break
        m = re.match(r"\[(\d+)\] (.*)$", line)
        if m: out[int(m.group(1))] = norm(CLEAN.sub(" ", m.group(2)))
    return out


def zh_all(chs):
    t = ""
    for ch in chs:
        for f in (f"source/text/zh/{ch}.txt", f"source/text/zh/daodu/{ch}.txt"):
            p = os.path.join(ROOT, f)
            if os.path.exists(p): t += open(p, encoding="utf-8").read()
    return re.sub(r"\s+", "", re.sub(r"^\{M\} |^## 译注", "", t, flags=re.M))


ZH_EXTRA = ""
for f in glob.glob(os.path.join(ROOT, "source/text/zh/daodu/*-book.txt")) + [os.path.join(ROOT, "source/text/zh/front.txt")]:
    if os.path.exists(f): ZH_EXTRA += re.sub(r"\s+", "", open(f, encoding="utf-8").read())


def concept_ids(path):
    return re.findall(r'<div class="concept" id="([^"]+)">', open(path, encoding="utf-8").read())


QUOTE_IN = re.compile(r"[‘“”\"]|’(?![A-Za-z])|(?<![A-Za-z])’")
bad = 0
for path in sys.argv[1:]:
    t = open(path, encoding="utf-8").read(); errs = []
    pid = re.search(r"(\w+)\.html$", path).group(1)
    if pid not in PAGES: print(f"✗ {path}  chapters.js 的 WN_PAGES 里没有页 {pid}"); bad += 1; continue
    P = PAGES[pid]; core = P["kind"] == "core"; L = 0 if core else 1
    secs = SECS.get(pid, [])
    if not secs: print(f"✗ {path}  chapters.js 的 WN_SECS 里没有页 {pid} 的节（先跑 tools/build_chapters.py）"); bad += 1; continue
    want = [s["k"] for s in secs]
    EN = {ch: load_en(ch) for ch in P["chs"]}
    inpage = lambda ch, p: any(s["ch"] == ch and s["p"][0] <= p <= s["p"][1] for s in secs)
    sec_of = lambda ch, p: next((s["k"] for s in secs if s["ch"] == ch and s["p"][0] <= p <= s["p"][1]), None)
    if f'<body data-page="{pid}">' not in t: errs.append(f'<body> 应写成 <body data-page="{pid}">')

    def part(a):
        i = t.find(f"<h2>{a}</h2>")
        if i < 0: return ""
        j = t.find("<h2>", i + 4)
        return t[i:j if j > 0 else len(t)]

    def lim(key, n, what):
        lo, hi = LIMITS[key][L]
        if not lo <= n <= hi: errs.append(f"{what}应有 {lo}–{hi} 个（{'核心' if core else '轻量'}页），现在 {n} 个")

    # 小节标题和顺序
    SECTS = CORE if core else LIGHT
    must = [s for s in SECTS if s not in OPTIONAL or (s == "动手：模拟器" and "sim" in P["need"]) or (s == "先用中文过一遍：这一页的概念" and core)]
    present = [s for s in SECTS if f"<h2>{s}</h2>" in t]
    for s in must:
        if s not in present: errs.append(f"缺少小节：{s}")
    if "动手：模拟器" in present and "sim" not in P["need"]: errs.append("这一页不该有「动手：模拟器」（看 chapters.js 的 need）")
    pos = [t.find(f"<h2>{s}</h2>") for s in present]
    if pos != sorted(pos): errs.append("小节顺序不对，应为：" + " → ".join(SECTS))
    for s in re.findall(r"<h2>(.*?)</h2>", t):
        if s not in SECTS: errs.append(f"多出来的小节标题：{s}（标题一个字都不能改；{'核心' if core else '轻量'}页的小节见规范）")
    g = re.search(r'<div class="gist">(.*?)</div>', t, flags=re.S)
    if not g: errs.append("「这一页在做什么」要有 <div class=\"gist\">")
    elif han(g.group(1)) > 200: errs.append(f"「这一页在做什么」{han(g.group(1))} 个汉字，超过 200")

    # 读之前 / 路线（核心页）；他想证明什么（轻量页）
    route = part("这一页的路线") if core else part("他想证明什么")
    pre = part("读之前：这一页在全书的哪里") if core else route
    if '<div class="linehere"></div>' not in pre: errs.append(f"「{'读之前' if core else '他想证明什么'}」第一行要写 <div class=\"linehere\"></div>")
    if core:
        if '<div class="crux">' not in pre: errs.append("「读之前」要有一个 <div class=\"crux\">")
        nq = len(re.findall(r"<li>", re.search(r'<ol class="qs">(.*?)</ol>', pre, flags=re.S).group(1))) if '<ol class="qs">' in pre else 0
        if not 2 <= nq <= 4: errs.append(f"「读之前」带着读的问题（<ol class=\"qs\">）应有 2–4 个，现在 {nq} 个")
        lead = re.sub(r'<div class="crux">.*?</div>|<div class="heads-up">.*?</div>|<ol class="qs">.*?</ol>|<p class="lede">.*?</p>', "", pre, flags=re.S)
        hu = re.findall(r'<div class="heads-up">(.*?)</div>', t, flags=re.S)
        if len(hu) > 1: errs.append("「别被带歪」（.heads-up）一页至多一个")
        for x in hu:
            if han(x) > 100: errs.append(f"「别被带歪」{han(x)} 个汉字，超过 100")
        if han(lead) > 200: errs.append(f"「读之前」那段话 {han(lead)} 个汉字，超过 200")
    if "<svg" not in route: errs.append(f"「{'这一页的路线' if core else '他想证明什么'}」要有一张自己画的 SVG")
    lands = re.findall(r'<p class="landing"><b>斯密落在哪：</b>(.*?)</p>', route, flags=re.S)
    if len(lands) != 1: errs.append(f"「{'这一页的路线' if core else '他想证明什么'}」要有且只有一句 <p class=\"landing\"><b>斯密落在哪：</b>…</p>")
    elif han(lands[0]) > 130: errs.append(f"「斯密落在哪」{han(lands[0])} 个汉字，超过 130")
    if t.count('class="landing"') != len(lands): errs.append("p.landing 只能出现在「路线」（轻量页：「他想证明什么」）里")
    prose = re.sub(r"<svg.*?</svg>|<figcaption>.*?</figcaption>|<div class=\"heads-up\">.*?</div>", "", route, flags=re.S)
    cap = 380 if core else 450
    if han(prose) > cap: errs.append(f"「{'这一页的路线' if core else '他想证明什么'}」正文 {han(prose)} 个汉字，超过 {cap}（讲怎么走、想证明什么，不复述内容）")

    # 分节地图：照抄 chapters.js
    sm = part("分节地图")
    items = re.findall(r'<li data-sec="(\d+)"><b>(.*?)</b><span class="zh">(.*?)</span><span class="en">(.*?)</span><span class="what">(.*?)</span></li>', sm, flags=re.S)
    if [int(i[0]) for i in items] != want: errs.append(f"分节地图的节号应为 {want}，认出 {[int(i[0]) for i in items]}（写法：<li data-sec=\"k\"><b>节名</b><span class=\"zh\">杨译地标</span><span class=\"en\">英文开头 …</span><span class=\"what\">…</span></li>）")
    for (k, b, zh, en, what), s in zip(items, secs):
        if plain(b) != s["t"]: errs.append(f"分节地图 §{k}：<b> 照抄 chapters.js 的节名「{s['t']}」，现在是「{plain(b)}」")
        if plain(zh) != s["zh"]: errs.append(f"分节地图 §{k}：.zh 照抄 chapters.js 的杨译地标「{s['zh']}」，现在是「{plain(zh)}」")
        e = norm(plain(en)).strip("… ").strip()
        if e != norm(s["en"]): errs.append(f"分节地图 §{k}：.en 照抄 chapters.js 的 en（{s['en']!r}），后面加 …：现在是 {e!r}")
        first = EN[s["ch"]].get(s["p"][0], "")
        if not first.lstrip("'\" ").startswith(norm(s["en"])): errs.append(f"分节地图 §{k}：chapters.js 的 en 不是 {s['ch']} 第 {s['p'][0]} 段的开头（报告主编）")
        cap = 70 if core else 90
        if han(what) > cap: errs.append(f"分节地图 §{k}：说明 {han(what)} 个汉字，超过 {cap}")
        if s["tier"] == "可跳过" and not re.search(r"跳", plain(what)): errs.append(f"分节地图 §{k}：「可跳过」的节，说明里要写一句为什么可以跳")

    # 概念块
    cp = part("先用中文过一遍：这一页的概念")
    blocks = re.findall(r'<div class="concept" id="([^"]+)">(.*?)</div>\s*(?=<div class="concept"|<h2>|<p[ >]|<figure|$)', cp, flags=re.S)
    if cp.count('<div class="concept"') != len(blocks): errs.append("概念块的写法不对：<div class=\"concept\" id=\"c-…\"><h3>…</h3><p>…</p><p class=\"now\">…</p><p class=\"use\">…</p></div>")
    if cp or core: lim("concept", len(blocks), "概念块")
    for cid, body in blocks:
        if not re.fullmatch(r"c-[a-z0-9-]+", cid): errs.append(f"概念块 id 要写成 c- 加小写英文：{cid}")
        if not re.match(r'\s*<h3><span class="sec">§\d+</span>', body): errs.append(f"概念块 {cid}：要以 <h3><span class=\"sec\">§k</span>中文名 <span class=\"en\">原文</span></h3> 开头")
        use = re.findall(r'<p class="use"><b>在这一页：</b>(.*?)</p>', body, flags=re.S)
        if len(use) != 1: errs.append(f"概念块 {cid}：要有一句 <p class=\"use\"><b>在这一页：</b>…</p>")
        elif han(use[0]) > 80: errs.append(f"概念块 {cid}：「在这一页」{han(use[0])} 个汉字，超过 80")
        now = re.findall(r'<p class="now"><b>今天：</b>(.*?)</p>', body, flags=re.S)
        if len(now) != 1: errs.append(f"概念块 {cid}：要有一句 <p class=\"now\"><b>今天：</b>…</p>（今天的经济学怎么用、怎么叫这个概念）")
        elif han(now[0]) > 100: errs.append(f"概念块 {cid}：「今天」{han(now[0])} 个汉字，超过 100")
        main_ = re.sub(r'<h3>.*?</h3>|<p class="use">.*?</p>|<p class="now">.*?</p>|<figure.*?</figure>|<svg.*?</svg>', "", body, flags=re.S)
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
    if "sim" in P["need"]:
        sp = part("动手：模拟器")
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

    # 故事和背景
    st_ = part("故事和背景")
    blks = re.split(r"<h3>", st_)[1:]
    lim("story", len(blks), "「故事和背景」的 <h3> 小块")
    for b in blks:
        ttl = plain(b.split("</h3>")[0])
        if not re.match(r'<span class="sec">§\d+</span>', b): errs.append(f"「故事和背景」小块标题前要有节号 <span class=\"sec\">§k</span>：{ttl}")
        body = re.sub(r'<figure.*?</figure>|<div class="who">.*?</div>\s*</div>', "", b.split("</h3>", 1)[-1], flags=re.S)
        if han(body) > 300: errs.append(f"「故事和背景」{ttl}：{han(body)} 个汉字，超过 300")

    # 原典：斯密原文一字不差，出自这一页的段落
    pd = part("原典：斯密的原话")
    pds = re.findall(r'<div class="pd" data-ch="([\d-]+)" data-p="(\d+)">\s*<h4><span class="sec">§(\d+)</span>(.*?)</h4>\s*<p class="where">(.*?)</p>\s*<blockquote class="pd-orig" lang="en">(.*?)</blockquote>\s*<p class="pd-zh"><b>本站译：</b>(.*?)</p>(.*?)</div>', pd, flags=re.S)
    if pd.count('<div class="pd"') != len(pds): errs.append("原典块的写法不对：<div class=\"pd\" data-ch=\"章号\" data-p=\"段号\"><h4><span class=\"sec\">§k</span>标题</h4><p class=\"where\">…</p><blockquote class=\"pd-orig\" lang=\"en\">原文</blockquote><p class=\"pd-zh\"><b>本站译：</b>…</p>（可加 <p class=\"pd-note\">、<ul class=\"oldwords\">）</div>")
    if t.count('<div class="pd"') != pd.count('<div class="pd"'): errs.append("原典块只放在「原典：斯密的原话」里")
    lim("pd", len(pds), "原典块")
    for ch, p, k, h4, where, orig, zh_, rest in pds:
        p, name = int(p), plain(h4)[:14]
        if ch not in EN: errs.append(f"原典「{name}」：章 {ch} 不在这一页"); continue
        if not inpage(ch, p): errs.append(f"原典「{name}」：{ch} 第 {p} 段不在这一页")
        elif sec_of(ch, p) != int(k): errs.append(f"原典「{name}」：{ch} 第 {p} 段在 §{sec_of(ch, p)}，不是 §{k}")
        o = norm(plain(orig))
        nw = len(o.replace("…", " ").split())
        if nw > 220: errs.append(f"原典「{name}」：原文 {nw} 词，超过 220")
        src = " ".join(EN[ch].get(q, "") for q in range(p, p + 4))
        for seg in [x.strip(" .") for x in re.split(r"…|\.\.\.", o)]:
            if seg and norm(seg) not in src: errs.append(f"原典「{name}」：这一截在 {ch} 第 {p} 段起的几段里找不到（要一字不差，省略处用 …）：{seg[:50]!r}")
        if han(where) > 120: errs.append(f"原典「{name}」：.where {han(where)} 个汉字，超过 120")
        notes_ = re.findall(r'<p class="pd-note">(.*?)</p>', rest, flags=re.S)
        if notes_ and han(notes_[0]) > 140: errs.append(f"原典「{name}」：.pd-note {han(notes_[0])} 个汉字，超过 140")
        for li in re.findall(r"<li>(.*?)</li>", rest, flags=re.S):
            if not li.startswith("<b>"): errs.append(f"原典「{name}」：熟词生义每条 <li><b>英文词</b>在这里的意思……</li>")
            elif han(li) > 70: errs.append(f"原典「{name}」：熟词生义「{plain(li)[:10]}」{han(li)} 个汉字，超过 70")
    if t.count('<ul class="oldwords">') != pd.count('<ul class="oldwords">'): errs.append("<ul class=\"oldwords\"> 只放在原典块里")

    # 译本勘误（可省；写了就照格式）
    ze = part("译本勘误")
    zes = re.findall(r'<div class="zherr" data-ch="([\d-]+)" data-p="(\d+)"><h4><span class="sec">§(\d+)</span>(.*?)</h4>\s*<p class="loc">(.*?)</p>\s*<p class="zhq">(.*?)</p>\s*<p>(.*?)</p></div>', ze, flags=re.S)
    if ze.count('<div class="zherr"') != len(zes): errs.append("勘误块的写法不对：<div class=\"zherr\" data-ch=\"章号\" data-p=\"段号\"><h4><span class=\"sec\">§k</span>标题<span class=\"mark\">误译</span></h4><p class=\"loc\">… 英文 4–7 个词 …</p><p class=\"zhq\"><span class=\"zhv\">译本：「…」</span></p><p>…</p></div>")
    if t.count('<div class="zherr"') != ze.count('<div class="zherr"'): errs.append("勘误块只放在「译本勘误」里")
    if ze: lim("zherr", len(zes), "勘误块（一条都没有就不写这一节）")
    for ch, num, k, h4, loc, zhq, expl in zes:
        num, name = int(num), plain(h4)[:14]
        kinds = re.findall(r'<span class="mark(?: turn)?">(.*?)</span>', h4)
        if len(kinds) != 1 or kinds[0] not in ZH_KINDS: errs.append(f"勘误「{name}」：<h4> 里要有一个类型标签，五选一：{' / '.join(ZH_KINDS)}（译反用 class=\"mark turn\"）")
        if kinds == ["译反"] and 'class="mark turn"' not in h4: errs.append(f"勘误「{name}」：「译反」用 <span class=\"mark turn\">译反</span>")
        l_ = norm(plain(loc)).strip("… ").strip()
        if ch not in EN or not inpage(ch, num): errs.append(f"勘误「{name}」：{ch} 第 {num} 段不在这一页"); continue
        if not (l_ in EN[ch].get(num, "") and 4 <= len(l_.split()) <= 7): errs.append(f"勘误「{name}」：p.loc 要照抄 {ch} 第 {num} 段里连续的 4–7 个词：{l_!r}")
        if QUOTE_IN.search(plain(loc)): errs.append(f"勘误「{name}」：p.loc 不能含引号：{plain(loc)!r}")
        if zhq.count('<span class="zhv">') != 1: errs.append(f"勘误「{name}」：p.zhq 里要有一处 <span class=\"zhv\">译本：「…」</span>")
        if han(expl) > 140: errs.append(f"勘误「{name}」：说明 {han(expl)} 个汉字，超过 140")
        if sec_of(ch, num) != int(k): errs.append(f"勘误「{name}」：在 §{sec_of(ch, num)}，不是 §{k}")

    # 读完（核心页）/ 今天怎么看（轻量页）：论点 + 今天看的标签
    rd = part("读完：斯密到底说了什么") if core else part("今天怎么看")
    claims = re.findall(r'<div class="claim"><h4>(.*?)</h4><p>(.*?)</p><span class="vchip" data-verdict="([^"]+)"></span><span class="sec">([^<]+)</span></div>', rd, flags=re.S)
    if len(claims) != rd.count('<div class="claim">'): errs.append("论点的写法不对：<div class=\"claim\"><h4>论点</h4><p>…</p><span class=\"vchip\" data-verdict=\"成立\"></span><span class=\"sec\">§k 第 n 段</span></div>")
    lim("claim", len(claims), "论点（.claim）")
    for h4, body, v, where in claims:
        nm = plain(h4)[:12]
        if han(body) > 150: errs.append(f"论点「{nm}…」：{han(body)} 个汉字，超过 150")
        if v not in VERDICTS: errs.append(f"论点「{nm}…」：今天看的标签五选一：{' / '.join(VERDICTS)}")
        if not re.search(r"第 \d+", where): errs.append(f"论点「{nm}…」：节号后面要写依据在第几段")
    if core:
        sw = re.findall(r'<p class="sowhat"><b>合起来：</b>(.*?)</p>', rd, flags=re.S)
        if len(sw) != 1: errs.append("「读完」最后要有一句 <p class=\"sowhat\"><b>合起来：</b>…</p>")
        elif han(sw[0]) > 120: errs.append(f"「合起来」{han(sw[0])} 个汉字，超过 120")
        if han(re.sub(r'<p class="lede">.*?</p>', "", rd, flags=re.S)) > 1000: errs.append(f"「读完」正文超过 1000 个汉字")
    if '<blockquote' in rd: errs.append(f"「{'读完' if core else '今天怎么看'}」里不引原文（原文放原典）")

    # 对照今天（核心页一节；轻量页的卡片放在「今天怎么看」里，可省）
    td = part("对照今天") if core else rd
    tcs = re.findall(r'<div class="today" data-verdict="([^"]+)"><h4>(.*?)</h4><dl>(.*?)</dl></div>', td, flags=re.S)
    if len(tcs) != td.count('<div class="today"'): errs.append("对照今天卡片的写法不对：<div class=\"today\" data-verdict=\"成立\"><h4>书里的说法：…</h4><dl>…</dl></div>")
    lim("today", len(tcs), "对照今天的卡片")
    if tcs and '<ul class="verdicts">' not in td: errs.append("有对照今天的卡片，要照抄样板的结论图例 <ul class=\"verdicts\">")
    if t.count('<div class="today"') != td.count('<div class="today"'): errs.append(f"对照今天的卡片只放在「{'对照今天' if core else '今天怎么看'}」里")
    for v, h4, dl in tcs:
        name = plain(h4)[:16]
        if v not in VERDICTS: errs.append(f"对照今天「{name}」：结论五选一：{' / '.join(VERDICTS)}")
        if not plain(h4).startswith("书里的说法："): errs.append(f"对照今天「{name}」：<h4> 以「书里的说法：」开头，结论判的就是这一句")
        dts = re.findall(r"<dt>(.*?)</dt>", dl)
        if dts[:3] != ["书里", "当时", "今天"] or not set(dts[3:]) <= {"另一边"}: errs.append(f"对照今天「{name}」：<dt> 依次是 书里 / 当时 / 今天（可再加 另一边），现在是 {dts}")
        if not re.search(r'<span class="asof">核对于 20\d\d-\d\d', dl): errs.append(f"对照今天「{name}」：「今天」最后要有 <span class=\"asof\">核对于 2026-10。依据：…</span>")
        if not re.search(r"第 \d+(?:[–-]\d+)? 段", dl): errs.append(f"对照今天「{name}」：「书里」要标段号（第 n 段）")
        if han(dl) > 380: errs.append(f"对照今天「{name}」：{han(dl)} 个汉字，超过 380")

    # 本站怎么看（核心页一节；轻量页至多一块，放在「今天怎么看」里）
    vw = part("本站怎么看") if core else rd
    vws = re.findall(r'<div class="views"><h4>(.*?)</h4>\s*<p><b>主流看法：</b>(.*?)</p>\s*<p><b>斯密的看法：</b>(.*?)</p>\s*<p class="ours"><b>本站的评论：</b>(.*?)</p></div>', vw, flags=re.S)
    if t.count('<div class="views">') != len(vws) or vw.count('<div class="views">') != len(vws): errs.append(f"看法块的写法不对，或不在「{'本站怎么看' if core else '今天怎么看'}」里：<div class=\"views\"><h4>问题</h4><p><b>主流看法：</b>…</p><p><b>斯密的看法：</b>…</p><p class=\"ours\"><b>本站的评论：</b>…</p></div>")
    lim("views", len(vws), "看法块")
    for h4, a, b, c_ in vws:
        if han(a + b + c_) > 420: errs.append(f"看法块「{plain(h4)[:14]}」{han(a + b + c_)} 个汉字，超过 420")
        if not re.search(r"第 \d+", b): errs.append(f"看法块「{plain(h4)[:14]}」：「斯密的看法」要标段号（第 n 段）")
    vd = re.findall(r'<p class="verdict"><b>本站的总体看法：</b>(.*?)</p>', vw, flags=re.S)
    if len(vd) != 1: errs.append(f"「{'本站怎么看' if core else '今天怎么看'}」最后要有一句 <p class=\"verdict\"><b>本站的总体看法：</b>…</p>")
    elif han(vd[0]) > 160: errs.append(f"「本站的总体看法」{han(vd[0])} 个汉字，超过 160")

    # 检查一下理解（核心页）
    c = counts(t)
    if core:
        ck = part("检查一下理解")
        if f'data-key="{pid}-oneline"' not in ck: errs.append(f"「检查一下理解」要有 <textarea class=\"note\" data-key=\"{pid}-oneline\">")
        if not re.search(r'<div class="ponder"><p>想一想：.*?</p>\s*<textarea class="note" data-key="' + pid + r'-ponder"', ck, flags=re.S): errs.append(f"「检查一下理解」最后要有 <div class=\"ponder\"><p>想一想：…</p><textarea class=\"note\" data-key=\"{pid}-ponder\"></textarea></div>")
        if not 5 <= c["检查题"] <= 7: errs.append(f"理解检查应有 5–7 题，现在 {c['检查题']} 题")
    elif c["检查题"]: errs.append("轻量页不写理解检查")
    for k in re.findall(r'class="note" data-key="([^"]+)"', t):
        if not k.startswith(f"{pid}-"): errs.append(f"笔记的 data-key 要以 {pid}- 开头：{k}")

    # 精彩回顾
    rc = part("精彩回顾")
    if '<p class="recall-line">' not in rc: errs.append("「精彩回顾」要有 <p class=\"recall-line\"><b>一句话：</b>…</p>")
    items_r = re.findall(r'<div class="item"><b>(.*?)</b><p>(.*?)</p><span class="sec">(§[^<]+)</span></div>', rc, flags=re.S)
    if len(items_r) != rc.count('<div class="item">'): errs.append("精彩回顾卡片的写法不对：<div class=\"item\"><b>标题</b><p>…</p><span class=\"sec\">§k</span></div>")
    lim("recall", len(items_r), "「精彩回顾」的卡片")
    for b_, p_, _ in items_r:
        if han(p_) > 100: errs.append(f"「精彩回顾」{b_}：{han(p_)} 个汉字，超过 100")

    # 节号不能写到这一页以外
    for k in sorted({int(k) for k in re.findall(r'class="sec">§(\d+)', t)} - set(want)):
        errs.append(f"页面上标了 §{k}，这一页只有 {want}")

    # 杨译：「译本：『…』」只能出现在 .zhv 里，一字不差、每处 ≤20 字、勘误以外一页 ≤6 处；别处不能和杨译连续 12 个汉字相同
    zh = zh_all(P["chs"])
    # 正文里指路用的杨译小标题：<span class="zh">…</span>，要一字不差是这几章里 {M} 开头的那一行（分节地图里的另由上面核对）
    MS = set()
    for ch in P["chs"]:
        for l in open(os.path.join(ROOT, f"source/text/zh/{ch}.txt"), encoding="utf-8").read().splitlines():
            if l.startswith("{M} "): MS.add(l[4:].strip())
    for z in re.findall(r'<span class="zh">(.*?)</span>', re.sub(r'<ol class="secmap">.*?</ol>', "", t, flags=re.S)):
        if plain(z) not in MS: errs.append(f"<span class=\"zh\"> 里要一字不差是杨译这几章的小标题（source/text/zh/ 里 {{M}} 开头的行）：{plain(z)[:20]}")
    nosm = re.sub(r'<span class="zh">.*?</span>', "", bare, flags=re.S)  # 分节地图的杨译地标是照抄的小标题，单独核对过
    zhvs = re.findall(r'<span class="zhv">(.*?)</span>', nosm, flags=re.S)
    n_out = len(re.findall(r'<span class="zhv">', nosm.replace(ze, "")))
    if n_out > 6: errs.append(f"「译本勘误」以外的 .zhv {n_out} 处，超过 6 处")
    for z in zhvs:
        if not z.startswith("译本："): errs.append(f".zhv 以「译本：」开头：{z[:20]}")
        for q in re.findall(r"「(.*?)」", z):
            qq = re.sub(r"\s+", "", q)
            if han(qq) > 20: errs.append(f".zhv 引的译文 {han(qq)} 个汉字，超过 20：{q[:20]}")
            if any(x and x not in zh for x in qq.split("……")): errs.append(f".zhv 引的译文在杨译这几章里找不到（要一字不差，省略处用 ……）：{q[:20]}")
    rest = re.sub(r"\s+", "", page_text(re.sub(r'<span class="zhv">.*?</span>', "", nosm, flags=re.S)))
    pool = zh + ZH_EXTRA
    hits = {rest[i:i + 12] for i in range(len(rest) - 11) if han(rest[i:i + 12]) == 12 and rest[i:i + 12] in pool}
    for x in sorted(hits)[:5]: errs.append(f"和杨译（正文、导读或译者导言）有 12 个汉字以上相同的片段（只能放在 .zhv 里）：{x}")
    for m in re.finditer(r"(?:杨译|译本)(?:里|中|译作|译为|译成|写作|作「|叫|的译法)「", page_text(re.sub(r'<span class="zhv">.*?</span>', "", nosm, flags=re.S))):
        errs.append(f"引杨译的原话，要放在 <span class=\"zhv\">译本：「…」</span> 里：…{m.group(0)}…")

    ph, sv = LIMITS["photos"][L]
    errs += check_images(t, path, min_photos=ph, min_svgs=sv, pattern=r"\.\./assets/img/\d\d-[a-z0-9-]+\.jpg")
    errs += check_markup(bare)
    zc = sum(s["zc"] for s in secs)
    print(("✗" if errs else "✓"), path, f"{'核心' if core else '轻量'}", " ".join(f"{k} {v}" for k, v in c.items() if k not in ("词条", "trap", "引用")),
          f"概念 {len(blocks)} 故事 {len(blks)} 原典 {len(pds)} 勘误 {len(zes)} 地图 {len(items)} 论点 {len(claims)} 今天 {len(tcs)} 看法 {len(vws)} 回顾 {len(items_r)} 译本 {len(zhvs)} 杨译 {zc} 字")
    for e in errs: print("    " + e)
    bad += bool(errs)
sys.exit(1 if bad else 0)
