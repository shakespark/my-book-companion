#!/usr/bin/env python3
"""页面结构检查：python3 -I tools/lint.py chapters/04.html …
页 id → 章从 assets/chapters.js 读（MM_PAGES 的 ch，MM_SECS 每节的段号范围 p）；原文从 source/text/NN.txt 读，译本从 source/zh/NN.txt 读。
照 Impro 导读的 lint.py 改。读者读的是英文纸书，对着繁体译本：词条照英文伴读的格式（接得进跨书词本），译本勘误照 Impro。
查：小节标题和顺序、读之前、分节地图（每节一条，只写 .what）、概念块、情境卡、词条（.loc 在那一段、trap 占比）、人和背景、
译本勘误（英文定位在那一段、译本原句出自译本这一章）、引用块、读完、今天怎么看、本站怎么看、判断题、精彩回顾、
图片、理解检查和「想一想」、译本（「译本：」只在 .zhv 里，别处不能和译本连续 12 个汉字相同）、写死的颜色、直引号、原书材料的路径。
00 是主编页，不走这里，只跑 overlap 和 check。通用的几项在 ~/tutorials-deploy/scripts/lint_common.py。"""
import glob, html, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.expanduser("~/tutorials-deploy/scripts"))
from lint_common import norm, check_entries, check_quotes, check_images, check_markup, counts, page_text

SECS = ["这一章在做什么", "读之前：这一章在全书的哪里", "分节地图", "先用中文过一遍：这一章的概念", "遇到这些事：情境卡",
        "原文里的口语和行话", "书里的人和背景", "译本勘误", "值得停下来的句子", "读完：作者到底说了什么",
        "今天怎么看", "本站怎么看", "练一练：判断题", "检查一下理解", "精彩回顾"]
CASE_SEC, WORD_SEC, PEOPLE_SEC, DRILL_SEC = "遇到这些事：情境卡", "原文里的口语和行话", "书里的人和背景", "练一练：判断题"
VERDICTS = ["成立", "部分成立", "被改写", "有争议"]
ZH_KINDS = ["误译", "译反", "漏译", "术语", "数字"]
CASE_DT = ["先想清楚", "作者的办法", "本站补充", "小心"]
han = lambda s: len(re.findall(r"[一-鿿]", re.sub(r"<[^>]+>", "", s)))
plain = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

js = open(os.path.join(ROOT, "assets/chapters.js"), encoding="utf-8").read()
PAGES = {m.group(1): int(m.group(2)) for m in re.finditer(r'\{ id: "(\w+)", ch: (\d+),', js[js.index("window.MM_PAGES"):])}
SEC_TAB = {}   # 章 → {节号（字符串）: (第一段, 最后一段)}
for m in re.finditer(r'"(\d\d)": \[(.*?)\n  \]', js[js.index("window.MM_SECS"):js.index("window.MM_PAGES")], flags=re.S):
    SEC_TAB[int(m.group(1))] = {k: (int(a), int(b)) for k, a, b in re.findall(r'\{ k: (\d+), p: \[(\d+), (\d+)\]', m.group(2))}

FOOT = re.compile(r" ?\{\*\d+\}")


def load(ch):
    """读 source/text/NN.txt。返回 paras {段号: 归一化文字}、secs [(节号, 第一段, 最后一段, 词数)]、foots {脚注号: 文字}。"""
    tab = SEC_TAB.get(ch, {})
    paras, words, foots = {}, {k: 0 for k in tab}, {}
    for line in open(os.path.join(ROOT, f"source/text/{ch:02d}.txt"), encoding="utf-8").read().splitlines():
        m = re.match(r"\[\*(\d+)\] (.*)$", line)
        if m: foots[int(m.group(1))] = norm(m.group(2)); continue
        m = re.match(r"\[(\d+) p\w+\] (\{\w\} )?(.*)$", line)
        if not m: continue
        p, raw = int(m.group(1)), m.group(3)
        paras[p] = norm(FOOT.sub(" ¤ ", raw))       # 脚注号的位置留个记号：.loc、引用都不能跨过它
        k = next((k for k, (a, b) in tab.items() if a <= p <= b), None)
        if k is not None and m.group(2) != "{F} ": words[k] += len(FOOT.sub("", raw).split())
    return paras, [(k, a, b, words[k]) for k, (a, b) in tab.items()], foots


def zh_text(ch):
    """译本这一章的全文（含注），去掉空白和 # 号、段号：.zhv 引的译文要一字不差地在这里面。"""
    p = os.path.join(ROOT, f"source/zh/{ch:02d}.txt")
    t = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    return re.sub(r"\s+|\*", "", re.sub(r"^#+ |^\[\d+\] (\{\w\} )?", "", t, flags=re.M))


def ids(path, cls):
    return re.findall(rf'<div class="{cls}" id="([^"]+)">', open(path, encoding="utf-8").read())


QUOTE_IN = re.compile(r"[‘“”\"]|’(?![A-Za-z])|(?<![A-Za-z])’")  # ’ 夹在字母中间是撇号，放行
SEC_RE = r"§(\d+)"

bad = 0
for path in sys.argv[1:]:
    t = open(path, encoding="utf-8").read(); errs = []
    pid = re.search(r"(\w+)\.html$", path).group(1)
    if pid not in PAGES: print(f"✗ {path}  chapters.js 的 MM_PAGES 里没有页 {pid}"); bad += 1; continue
    ch = PAGES[pid]; light = pid == "in"          # 引言只有三千词、没有小标题，几项数量放宽
    paras, secs, foots = load(ch)
    want = [str(s[0]) for s in secs]
    if f'<body data-page="{pid}">' not in t: errs.append(f'<body> 应写成 <body data-page="{pid}">')
    def part(a):
        i = t.find(f"<h2>{a}</h2>")
        if i < 0: return ""
        j = t.find("<h2>", i + 4)
        return t[i:j if j > 0 else len(t)]
    def at_p(s, where):
        """data-p="18 21" 里的段号都要在这一章。"""
        return [f"{where}：data-p 里的 {x} 不是这一章的段号" for x in s.split() if not x.isdigit() or int(x) not in paras]
    def sec_of(p):
        return next((str(s[0]) for s in secs if s[1] <= p <= s[2]), None)

    # 小节标题和顺序
    present = [s for s in SECS if f"<h2>{s}</h2>" in t]
    for s in SECS:
        if s not in present: errs.append(f"缺少小节：{s}")
    pos = [t.find(f"<h2>{s}</h2>") for s in present]
    if pos != sorted(pos): errs.append("小节顺序不对，应为：" + " → ".join(SECS))
    for s in re.findall(r"<h2>(.*?)</h2>", t):
        if s not in SECS: errs.append(f"多出来的小节标题：{s}（标题一个字都不能改）")
    g = re.search(r'<div class="gist">(.*?)</div>', t, flags=re.S)
    if not g: errs.append("「这一章在做什么」要有 <div class=\"gist\">")
    elif han(g.group(1)) > 220: errs.append(f"「这一章在做什么」{han(g.group(1))} 个汉字，超过 220")

    # 读之前
    pre = part("读之前：这一章在全书的哪里")
    if '<div class="linehere"></div>' not in pre: errs.append("「读之前」第一行要写 <div class=\"linehere\"></div>（由 mm.js 画）")
    if '<div class="crux">' not in pre: errs.append("「读之前」要有一个 <div class=\"crux\">")
    nq = len(re.findall(r"<li>", re.search(r'<ol class="qs">(.*?)</ol>', pre, flags=re.S).group(1))) if '<ol class="qs">' in pre else 0
    if not 2 <= nq <= 4: errs.append(f"「读之前」带着读的问题（<ol class=\"qs\">）应有 2–4 个，现在 {nq} 个")
    lead = re.sub(r'<div class="crux">.*?</div>|<ol class="qs">.*?</ol>|<p class="lede">.*?</p>|<div class="heads-up">.*?</div>|<figure.*?</figure>', "", pre, flags=re.S)
    if han(lead) > 200: errs.append(f"「读之前」那段话 {han(lead)} 个汉字，超过 200")
    hu = re.findall(r'<div class="heads-up">(.*?)</div>', t, flags=re.S)
    if len(hu) > 1 or t.count('<div class="heads-up">') != pre.count('<div class="heads-up">'): errs.append("「别被带歪」框（div.heads-up）一页至多一个，只放在「读之前」里")
    for x in hu:
        if han(x) > 120: errs.append(f"「别被带歪」框 {han(x)} 个汉字，超过 120")

    # 分节地图：每节一条，只写 .what（节名、原书小标题、纸书页码、译本地标、字数、档由 mm.js 从 chapters.js 补）
    sm = part("分节地图")
    items = re.findall(r'<li data-sec="(\d+)"><span class="what">(.*?)</span></li>', sm, flags=re.S)
    if [i[0] for i in items] != want or sm.count("<li") != len(items):
        errs.append(f"分节地图的节号应为 {want}，实际认出 {[i[0] for i in items]}（写法：<li data-sec=\"k\"><span class=\"what\">…</span></li>，其余由脚本补）")
    for k, what in items:
        if han(what) > 90: errs.append(f"分节地图 §{k}：说明 {han(what)} 个汉字，超过 90")

    # 概念块
    cp = part("先用中文过一遍：这一章的概念")
    blocks = re.findall(r'<div class="concept" id="([^"]+)">(.*?)</div>\s*(?=<div class="concept"|<h2>|<p[ >]|<figure|$)', cp, flags=re.S)
    if cp.count('<div class="concept"') != len(blocks): errs.append("概念块的写法不对：<div class=\"concept\" id=\"c-…\"><h3>…</h3><p>…</p><p class=\"use\">…</p></div>")
    lo = 1 if light else 2
    if not lo <= len(blocks) <= 4: errs.append(f"概念块应有 {lo}–4 个，现在 {len(blocks)} 个")
    for cid, body in blocks:
        if not re.fullmatch(r"c-[a-z0-9-]+", cid): errs.append(f"概念块 id 要写成 c- 加小写英文：{cid}")
        if not re.match(r'\s*<h3><span class="sec">§\d+</span>', body): errs.append(f"概念块 {cid}：要以 <h3><span class=\"sec\">§k</span>中文名 <span class=\"en\">原文</span></h3> 开头")
        use = re.findall(r'<p class="use"><b>在这一章：</b>(.*?)</p>', body, flags=re.S)
        if len(use) != 1: errs.append(f"概念块 {cid}：要有一句 <p class=\"use\"><b>在这一章：</b>…</p>")
        elif han(use[0]) > 80: errs.append(f"概念块 {cid}：「在这一章」{han(use[0])} 个汉字，超过 80")
        main_ = re.sub(r'<h3>.*?</h3>|<p class="use">.*?</p>|<figure.*?</figure>|<svg.*?</svg>', "", body, flags=re.S)
        if han(main_) > 320: errs.append(f"概念块 {cid}：{han(main_)} 个汉字，超过 320")
    others = [o for o in glob.glob(os.path.join(ROOT, "chapters/*.html")) if os.path.abspath(o) != os.path.abspath(path)]
    for other in others:
        for cid in set(ids(other, "concept")) & {b[0] for b in blocks}:
            errs.append(f"概念 {cid} 在 {os.path.basename(other)} 里已经写过，这里改成 <a class=\"term\" href=\"{os.path.basename(other)}#{cid}\">…</a>")
    for href_, cid in re.findall(r'<a class="term" href="(\w+)\.html#(c-[a-z0-9-]+)">', t):
        f = os.path.join(ROOT, f"chapters/{href_}.html")
        if os.path.exists(f) and cid not in ids(f, "concept"): errs.append(f"概念链接 {href_}.html#{cid}：那一页没有这个概念块")

    # 情境卡：id 全站唯一；先想清楚 / 作者的办法 必有；最后一句书里哪一节、纸书页码
    cs = part(CASE_SEC)
    cases = re.findall(r'<div class="case" id="([^"]+)">(.*?)<p class="where">(.*?)</p>\s*</div>', cs, flags=re.S)
    if t.count('<div class="case"') != cs.count('<div class="case"'): errs.append("情境卡只放在「遇到这些事：情境卡」里")
    if cs.count('<div class="case"') != len(cases): errs.append("情境卡的写法不对：<div class=\"case\" id=\"k-…\"><h3><span class=\"sec\">§k</span>处境</h3><dl class=\"howto\">…</dl><p class=\"where\">书里：…</p></div>")
    lo, hi = (1, 3) if light else (2, 5)
    if not lo <= len(cases) <= hi: errs.append(f"情境卡应有 {lo}–{hi} 张，现在 {len(cases)} 张")
    for kid, body, where in cases:
        name = plain(re.search(r"<h3>(.*?)</h3>", body, flags=re.S).group(1))[:16] if "<h3>" in body else kid
        if not re.fullmatch(r"k-[a-z0-9-]+", kid): errs.append(f"情境卡 id 要写成 k- 加小写英文：{kid}")
        if not re.match(r'\s*<h3><span class="sec">§\d+</span>', body): errs.append(f"情境卡「{name}」：要以 <h3><span class=\"sec\">§k</span>处境</h3> 开头")
        dts = re.findall(r"<dt>(.*?)</dt>", body)
        for need_dt in CASE_DT[:2]:
            if need_dt not in dts: errs.append(f"情境卡「{name}」：<dl class=\"howto\"> 里要有 <dt>{need_dt}</dt>")
        if [d for d in CASE_DT if d in dts] != dts: errs.append(f"情境卡「{name}」：<dt> 只用 {' / '.join(CASE_DT)}，按这个顺序，现在是 {dts}")
        how = re.search(r"<dt>作者的办法</dt>\s*<dd>(.*?)</dd>", body, flags=re.S)
        if how and han(how.group(1)) > 220: errs.append(f"情境卡「{name}」：「作者的办法」{han(how.group(1))} 个汉字，超过 220（用自己的话，不照抄原书的清单）")
        if han(re.sub(r"<h3>.*?</h3>", "", body, flags=re.S)) > 480: errs.append(f"情境卡「{name}」：{han(body)} 个汉字，超过 480")
        if not re.match(r"书里：.*纸书 p\.\d+", plain(where)): errs.append(f"情境卡「{name}」：最后一句写 <p class=\"where\">书里：原书小标题，纸书 p.NN</p>")
        for other in others:
            if kid in ids(other, "case"): errs.append(f"情境卡 id {kid} 在 {os.path.basename(other)} 里已经用过")

    # 词条：英文伴读的格式；.loc 4–7 个词、在 data-p 那一段；trap 占四成以上
    ws = part(WORD_SEC)
    if t.count('<div class="entry') != ws.count('<div class="entry'): errs.append("词条（.entry）只放在「原文里的口语和行话」里")
    ents = re.findall(r'<div class="entry( trap)?"><div class="en">(.*?)</div><div class="loc" data-p="(\d+)">(.*?)</div><div class="zh">(.*?)</div>(?:<div class="note">(.*?)</div>)?</div>', ws, flags=re.S)
    if ws.count('<div class="entry') != len(ents): errs.append("词条的写法不对：<div class=\"entry [trap]\"><div class=\"en\">…</div><div class=\"loc\" data-p=\"段号\">… 4–7 个词 …</div><div class=\"zh\">…</div><div class=\"note\">…</div></div>（.note 可省）")
    lo, hi = (12, 40) if light else (20, 60)
    if not lo <= len(ents) <= hi: errs.append(f"词条应有 {lo}–{hi} 条，现在 {len(ents)} 条")
    errs += check_entries(ws, paras, trap_ratio=0.4, max_loc_words=7, scope="这一章")
    for trap, en_, p, loc, zh_, note in ents:
        n = len(norm(plain(loc)).strip("… ").split())
        if n < 4: errs.append(f".loc 太短（{n} 词，要 4–7 个）：{plain(loc)!r}")
        if "¤" in norm(plain(loc)) or "{*" in loc: errs.append(f".loc 不能跨过脚注号：{plain(loc)!r}")
        if note and han(note) > 100: errs.append(f"词条「{plain(en_)[:20]}」：.note {han(note)} 个汉字，超过 100")
        if han(zh_) > 40: errs.append(f"词条「{plain(en_)[:20]}」：.zh {han(zh_)} 个汉字，超过 40（短，只写这一句里的意思）")
    for h3 in re.findall(r"<h3[^>]*>(.*?)</h3>", ws, flags=re.S):
        if not re.match(r'<span class="sec">§\d+</span>', h3): errs.append(f"词条的分组标题要写成 <h3><span class=\"sec\">§k</span>原书小标题</h3>：{plain(h3)[:20]}")

    # 书里的人和背景
    pw = part(PEOPLE_SEC)
    blks = re.split(r"<h3>", pw)[1:]
    if not 3 <= len(blks) <= 8: errs.append(f"「{PEOPLE_SEC}」应有 3–8 个 <h3> 小块，现在 {len(blks)} 个")
    for b in blks:
        ttl = plain(b.split("</h3>")[0])
        if not re.match(r'<span class="sec">§\d+</span>', b): errs.append(f"「{PEOPLE_SEC}」小块标题前要有节号 <span class=\"sec\">§k</span>：{ttl}")
        body = re.sub(r'<figure.*?</figure>|<div class="who">.*?</div>\s*</div>', "", b.split("</h3>", 1)[-1], flags=re.S)
        if han(body) > 260: errs.append(f"「{PEOPLE_SEC}」{ttl}：{han(body)} 个汉字，超过 260")

    # 译本勘误：一条一块；英文定位在那一段里，译本原句一字不差出自译本这一章
    ze = part("译本勘误")
    zes = re.findall(r'<div class="zherr" data-p="(\d+)"><h4><span class="sec">' + SEC_RE + r'</span>(.*?)</h4>\s*<p class="loc">(.*?)</p>\s*<p class="zhq">(.*?)</p>\s*<p>(.*?)</p></div>', ze, flags=re.S)
    if ze.count('<div class="zherr"') != len(zes): errs.append("勘误块的写法不对：<div class=\"zherr\" data-p=\"段号\"><h4><span class=\"sec\">§k</span>标题<span class=\"mark\">误译</span></h4><p class=\"loc\">… 英文 4–7 个词 …</p><p class=\"zhq\"><span class=\"zhv\">译本：「…」</span></p><p>…</p></div>")
    if t.count('<div class="zherr"') != ze.count('<div class="zherr"'): errs.append("勘误块只放在「译本勘误」里")
    if ze and not 1 <= len(zes) <= 40: errs.append(f"「译本勘误」应有 1–40 条，现在 {len(zes)} 条（实在一处错都没有，在报告里说，主编放行）")
    last_p = 0
    for num, k, h4, loc, zhq, expl in zes:
        num, name = int(num), plain(h4)[:14]
        kinds = re.findall(r'<span class="mark(?: turn)?">(.*?)</span>', h4)
        if len(kinds) != 1 or kinds[0] not in ZH_KINDS: errs.append(f"勘误「{name}」：<h4> 里要有一个类型标签，五选一：{' / '.join(ZH_KINDS)}（译反用 class=\"mark turn\"）")
        if kinds == ["译反"] and 'class="mark turn"' not in h4: errs.append(f"勘误「{name}」：「译反」用 <span class=\"mark turn\">译反</span>")
        l_ = norm(plain(loc)).strip("… ").strip()
        if num not in paras: errs.append(f"勘误「{name}」：第 {num} 段不在这一章")
        if not (l_ in paras.get(num, "") and 4 <= len(l_.split()) <= 7): errs.append(f"勘误「{name}」：p.loc 要照抄第 {num} 段里连续的 4–7 个词：{l_!r}")
        if QUOTE_IN.search(plain(loc)): errs.append(f"勘误「{name}」：p.loc 不能含引号：{plain(loc)!r}")
        if zhq.count('<span class="zhv">') != 1: errs.append(f"勘误「{name}」：p.zhq 里要有一处 <span class=\"zhv\">译本：「…」</span>（漏译就引紧挨着的那一句）")
        if han(expl) > 140: errs.append(f"勘误「{name}」：说明 {han(expl)} 个汉字，超过 140")
        sk = sec_of(num)
        if sk is not None and sk != k: errs.append(f"勘误「{name}」：第 {num} 段在 §{sk}，不是 §{k}")
        if num < last_p: errs.append(f"勘误「{name}」：按段号排，第 {num} 段排在第 {last_p} 段之后")
        last_p = max(last_p, num)

    # 引用块：不超过 3 处，只放在「值得停下来的句子」
    errs += check_quotes(t, 3)
    for q in re.findall(r'<blockquote class="quote">(.*?)<cite>', t, flags=re.S):
        s = norm(plain(q)).strip("… ").strip()
        where = [p for p, v in paras.items() if s.replace("…", "") and all(x.strip() in v for x in s.split("…") if x.strip())]
        if not where: errs.append(f"引用块在这一章的原文里找不到（要一字不差，省略处用 …）：{s[:50]!r}")
        if len(s.replace("…", " ").split()) > 25: errs.append(f"引用块超过 25 个词：{s[:50]!r}")
    if t.count('<blockquote class="quote">') and t.find('<blockquote class="quote">') < t.find("<h2>值得停下来的句子</h2>"):
        errs.append("引用块只放在「值得停下来的句子」里")

    # 读完：作者到底说了什么
    rd = part("读完：作者到底说了什么")
    claims = re.findall(r'<div class="claim"><h4>(.*?)</h4><p>(.*?)</p><span class="sec" data-p="([^"]+)">(§[^<]+)</span></div>', rd, flags=re.S)
    if not 3 <= len(claims) <= 5 or len(claims) != rd.count('<div class="claim">'): errs.append(f"「读完」应有 3–5 条主张，写法 <div class=\"claim\"><h4>主张</h4><p>…</p><span class=\"sec\" data-p=\"段号 段号\">§k</span></div>，现在认出 {len(claims)} 条")
    for h4, body, dp, where in claims:
        if han(body) > 150: errs.append(f"「读完」{plain(h4)[:12]}…：{han(body)} 个汉字，超过 150")
        errs += at_p(dp, f"「读完」{plain(h4)[:12]}…")
    sw = re.findall(r'<p class="sowhat"><b>合起来：</b>(.*?)</p>', rd, flags=re.S)
    if len(sw) != 1: errs.append("「读完」最后要有一句 <p class=\"sowhat\"><b>合起来：</b>…</p>")
    elif han(sw[0]) > 120: errs.append(f"「合起来」{han(sw[0])} 个汉字，超过 120")
    if han(re.sub(r'<p class="lede">.*?</p>', "", rd, flags=re.S)) > 1000: errs.append(f"「读完」正文 {han(rd)} 个汉字，超过 1000")
    if '<blockquote' in rd: errs.append("「读完」里不引原文")

    # 今天怎么看：1–3 张卡
    td = part("今天怎么看")
    tcs = re.findall(r'<div class="today" data-verdict="([^"]+)"><h4>(.*?)</h4><dl>(.*?)</dl></div>', td, flags=re.S)
    if not 1 <= len(tcs) <= 3 or len(tcs) != td.count('<div class="today"'): errs.append(f"「今天怎么看」应有 1–3 张卡片，写法 <div class=\"today\" data-verdict=\"成立\"><h4>书里的说法：…</h4><dl>…</dl></div>，现在认出 {len(tcs)} 张")
    if td and '<ul class="verdicts">' not in td: errs.append("「今天怎么看」要照抄样板的结论图例 <ul class=\"verdicts\">")
    if t.count('<div class="today"') != td.count('<div class="today"'): errs.append("今天怎么看的卡片只放在「今天怎么看」里")
    for v, h4, dl in tcs:
        name = plain(h4)[:16]
        if v not in VERDICTS: errs.append(f"今天怎么看「{name}」：结论四选一：{' / '.join(VERDICTS)}")
        if not plain(h4).startswith("书里的说法："): errs.append(f"今天怎么看「{name}」：<h4> 以「书里的说法：」开头，结论判的就是这一句")
        dts = re.findall(r"<dt>(.*?)</dt>", dl)
        if dts[:3] != ["书里", "当时", "今天"] or not set(dts[3:]) <= {"另一边"}: errs.append(f"今天怎么看「{name}」：<dt> 依次是 书里 / 当时 / 今天（可再加 另一边），现在是 {dts}")
        if not re.search(r'<span class="asof">核对于 20\d\d-\d\d', dl): errs.append(f"今天怎么看「{name}」：「今天」最后要有 <span class=\"asof\">核对于 2026-10。依据：…</span>")
        m = re.search(r'<dt>书里</dt>\s*<dd>.*?<span class="at" data-p="([^"]+)">§[^<]+</span>', dl, flags=re.S)
        if not m: errs.append(f"今天怎么看「{name}」：「书里」要标出处 <span class=\"at\" data-p=\"段号\">§k</span>")
        else: errs += at_p(m.group(1), f"今天怎么看「{name}」")
        if han(dl) > 360: errs.append(f"今天怎么看「{name}」：{han(dl)} 个汉字，超过 360")

    # 本站怎么看：2–3 块看法，最后一句总体看法
    vw = part("本站怎么看")
    vws = re.findall(r'<div class="views"><h4>(.*?)</h4>\s*<p><b>主流看法：</b>(.*?)</p>\s*<p><b>作者的看法：</b>(.*?)</p>\s*<p class="ours"><b>本站的评论：</b>(.*?)</p></div>', vw, flags=re.S)
    if t.count('<div class="views">') != len(vws) or vw.count('<div class="views">') != len(vws): errs.append("看法块的写法不对，或不在「本站怎么看」里：<div class=\"views\"><h4>问题</h4><p><b>主流看法：</b>…</p><p><b>作者的看法：</b>…</p><p class=\"ours\"><b>本站的评论：</b>…</p></div>")
    if not 2 <= len(vws) <= 3: errs.append(f"「本站怎么看」应有 2–3 块看法，现在 {len(vws)} 块")
    for h4, a, b, c_ in vws:
        if han(a + b + c_) > 420: errs.append(f"看法块「{plain(h4)[:14]}」{han(a + b + c_)} 个汉字，超过 420")
        m = re.search(r'<span class="at" data-p="([^"]+)">§[^<]+</span>', b)
        if not m: errs.append(f"看法块「{plain(h4)[:14]}」：「作者的看法」要标出处 <span class=\"at\" data-p=\"段号\">§k</span>")
        else: errs += at_p(m.group(1), f"看法块「{plain(h4)[:14]}」")
    vd = re.findall(r'<p class="verdict"><b>本站的总体看法：</b>(.*?)</p>', vw, flags=re.S)
    if len(vd) != 1: errs.append("「本站怎么看」最后要有一句 <p class=\"verdict\"><b>本站的总体看法：</b>…</p>")
    elif han(vd[0]) > 160: errs.append(f"「本站的总体看法」{han(vd[0])} 个汉字，超过 160")

    # 判断题：id 全站唯一；处境、问题、折叠里的分析
    dr = part(DRILL_SEC)
    drills = re.findall(r'<div class="drill" id="([^"]+)">\s*<h3>(.*?)</h3>\s*<div class="scene">(.*?)</div>\s*<p class="ask">(.*?)</p>\s*<details class="reveal"><summary>(.*?)</summary>(.*?)</details>\s*</div>', dr, flags=re.S)
    if t.count('<div class="drill"') != dr.count('<div class="drill"'): errs.append("判断题只放在「练一练：判断题」里")
    if dr.count('<div class="drill"') != len(drills): errs.append("判断题的写法不对：<div class=\"drill\" id=\"d-…\"><h3><span class=\"sec\">§k</span>标题</h3><div class=\"scene\">…</div><p class=\"ask\">问题</p><details class=\"reveal\"><summary>想好了再点开</summary><p>…</p></details></div>")
    lo, hi = (1, 3) if light else (2, 4)
    if not lo <= len(drills) <= hi: errs.append(f"判断题应有 {lo}–{hi} 道，现在 {len(drills)} 道")
    for did, h3, scene, ask, summ, rv in drills:
        name = plain(h3)[:16]
        if not re.fullmatch(r"d-[a-z0-9-]+", did): errs.append(f"判断题 id 要写成 d- 加小写英文：{did}")
        if not re.match(r'<span class="sec">§\d+</span>', h3): errs.append(f"判断题「{name}」：<h3> 以 <span class=\"sec\">§k</span> 开头")
        if han(scene) > 260: errs.append(f"判断题「{name}」：处境 {han(scene)} 个汉字，超过 260")
        if plain(summ) != "想好了再点开": errs.append(f"判断题「{name}」：<summary> 写「想好了再点开」")
        if han(rv) > 300: errs.append(f"判断题「{name}」：分析 {han(rv)} 个汉字，超过 300")
        for other in others:
            if did in ids(other, "drill"): errs.append(f"判断题 id {did} 在 {os.path.basename(other)} 里已经用过")

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

    # 节号不能写到这一章以外
    for k in sorted(set(re.findall(r'class="(?:sec|at)"[^>]*>' + SEC_RE, t)) - set(want)):
        errs.append(f"页面上标了 §{k}，这一章只有 §{want[0]}–§{want[-1]}")

    # 译本：「译本：『…』」只能出现在 .zhv 里；引的要真在译本这一章，每处不超过 20 个汉字；勘误以外一页不超过 8 处；别处不能和译本连续 12 个汉字相同
    zh = zh_text(ch)
    zhvs = re.findall(r'<span class="zhv">(.*?)</span>', t, flags=re.S)
    free = re.sub(r'<p class="zhq">.*?</p>', "", t.replace(ze, ""), flags=re.S)
    n_out = len(re.findall(r'<span class="zhv">', free))
    if n_out > 8: errs.append(f"勘误以外的 .zhv {n_out} 处，超过 8 处")
    for z in zhvs:
        if not z.startswith("译本："): errs.append(f".zhv 以「译本：」开头：{z[:20]}")
        for q in re.findall(r"「(.*?)」", z):
            qq = re.sub(r"\s+", "", q)
            if han(qq) > 20: errs.append(f".zhv 引的译文 {han(qq)} 个汉字，超过 20：{q[:20]}")
            if zh and any(x and x not in zh for x in qq.split("……")): errs.append(f".zhv 引的译文在译本第 {ch} 章里找不到（要一字不差，繁体照抄，省略处用 ……）：{q[:20]}")
    rest = re.sub(r"\s+", "", page_text(re.sub(r'<span class="zhv">.*?</span>', "", t, flags=re.S)))
    if zh:
        hits = {rest[i:i + 12] for i in range(len(rest) - 11) if han(rest[i:i + 12]) == 12 and rest[i:i + 12] in zh}
        for x in sorted(hits)[:5]: errs.append(f"和译本有 12 个汉字以上相同的片段（只能放在 .zhv 里）：{x}")
    for m in re.finditer(r"译本(?:里|中|译作|译为|译成|写作|作「|叫|的译法)", page_text(re.sub(r'<span class="zhv">.*?</span>', "", t, flags=re.S))):
        errs.append(f"写译本怎么译，要放在 <span class=\"zhv\">译本：「…」</span> 里：…{m.group(0)}…")

    errs += check_images(t, path, min_photos=2, min_svgs=1, pattern=r"\.\./assets/img/(?:in|\d\d)-[a-z0-9-]+\.jpg")
    c = counts(t)
    if not 5 <= c["检查题"] <= 7: errs.append(f"理解检查应有 5–7 题，现在 {c['检查题']} 题")
    errs += check_markup(t)
    total = sum(s[3] for s in secs)
    print(("✗" if errs else "✓"), path, f"词条 {len(ents)}（trap {c['trap']}） 照片 {c['照片']} SVG {c['SVG']} 引用 {c['引用']} 检查题 {c['检查题']}",
          f"概念 {len(blocks)} 情境 {len(cases)} 判断 {len(drills)} 勘误 {len(zes)} 今天 {len(tcs)} 看法 {len(vws)} 回顾 {len(items_r)} 译本 {len(zhvs)} 原文 {total} 词")
    for e in errs: print("    " + e)
    bad += bool(errs)
sys.exit(1 if bad else 0)
