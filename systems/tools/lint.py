#!/usr/bin/env python3
"""页面结构检查：python3 -I tools/lint.py chapters/01a.html …
页 id → 章和节从 assets/chapters.js 读（TS_PAGES 的 secs、need，TS_SECS 每节的段号范围 p）；原文从 source/text/NN.txt 读，译本（简体）从 source/text/zh/NN.txt 读。
照 Fooled by Randomness 导读的 lint.py 改：没有读前 / 读后的分界、路线、人和背景、剧透名单；加了情境题（练一练）、一页两个模拟器（need 里的 sim2）、轻量页（need 里的 light，08 附录）。
查：小节标题和顺序、读之前、分节地图（每节一条，只写 .what）、概念块、模拟器、英文词条（.loc 在那一段、trap 占比）、译本勘误（英文定位在那一段、译本原句出自译本这一章）、
引用块（只在「读完」里）、读完、情境题、今天怎么看、本站怎么看、精彩回顾、图片、理解检查和「想一想」、译本（「译本：」只在 .zhv 里，别处不能和译本连续 12 个汉字相同）、写死的颜色、直引号、原书材料的路径。
另报「嫌疑」（？开头，不算不通过，作者在报告里逐条答）：相对位置词、「今天」栏里 2008 年以前的年份、卡片标题两句并列、「是一回事 / 同一件事」这类等同词、「没给出处 / 没点名」（先查书后注释）。
00 是主编页，不走这里，只跑 overlap 和 check。通用的几项在 ~/tutorials-deploy/scripts/lint_common.py。"""
import glob, html, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.expanduser("~/tutorials-deploy/scripts"))
from lint_common import norm, check_entries, check_quotes, check_images, check_markup, counts, page_text

SECS = ["这一页在做什么", "读之前：这一页在全书的哪里", "分节地图", "先用中文过一遍：这一页的概念",
        "动手：模拟器", "原文里的词和句", "译本勘误",
        "读完：作者到底说了什么", "练一练：情境题", "今天怎么看", "本站怎么看", "检查一下理解", "精彩回顾"]
SIM_SEC, WORD_SEC, DRILL_SEC = "动手：模拟器", "原文里的词和句", "练一练：情境题"
LIGHT = ["这一页在做什么", "读之前：这一页在全书的哪里", "分节地图", "译本勘误"]      # 轻量页（08 附录）必有的节；别的节可写可不写（模拟器、情境题除外）
PUB_YEAR = 2008                                                                        # 原书出版年：「今天」栏里早于它的年份多半该放进「当时」
DRILL_N = {"in": (1, 3), "05a": (3, 5), "05b": (3, 5), "06a": (3, 5), "06b": (3, 5), "07": (3, 5)}   # 情境题题数，其余页 2–4
VERDICTS = ["成立", "部分成立", "被改写", "有争议"]
ZH_KINDS = ["误译", "译反", "漏译", "术语", "数字"]
han = lambda s: len(re.findall(r"[一-鿿]", re.sub(r"<[^>]+>", "", s)))
plain = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

import json
js = open(os.path.join(ROOT, "assets/chapters.js"), encoding="utf-8").read()
PAGES, ORDER = {}, []
for m in re.finditer(r'\{ id: "(\w+)", ch: (\d+), secs: (\[[^\]]*\]), need: (\[[^\]]*\]), t: "([^"]*)", d: "([^"]*)" \}', js[js.index("TS_PAGES"):]):
    PAGES[m.group(1)] = (int(m.group(2)), json.loads(m.group(3)), json.loads(m.group(4))); ORDER.append(m.group(1))
SEC_TAB = {}   # 章 → {节号（字符串）: (第一段, 最后一段)}
for m in re.finditer(r'"(\d\d)": \[\n(.*?)\n  \]', js[js.index("TS_SECS"):], flags=re.S):
    SEC_TAB[int(m.group(1))] = {r["k"]: tuple(r["p"]) for r in (json.loads(x.strip().rstrip(",")) for x in m.group(2).splitlines())}
ZH_TITLES = sorted({re.sub(r"\s+", "", x) for x in re.findall(r'"zh": "([^"]+)"', js[js.index("TS_SECS"):]) + re.findall(r'zh: "([^"]+)"', js[js.index("TS_CHAPTERS"):js.index("TS_SECS")])}
                   | {re.sub(r"\s+", "", y) for x in re.findall(r'"zh": "([^"]+)"', js[js.index("TS_SECS"):]) for y in re.split(r"[：:]", x) if len(y) >= 6}, key=len, reverse=True)
CH_LAST, CH_N = {}, {}
for _pid, (_ch, _, _) in PAGES.items(): CH_LAST[_ch] = _pid; CH_N[_ch] = CH_N.get(_ch, 0) + 1


NOTE_REF = re.compile(r" ?\{注\d+\}")


def load(ch, want):
    """读 source/text/NN.txt 里属于这一页的几节和章末的注释（书后 Notes，[nK]）。返回 paras {段号: 归一化文字}、quoted {{Q} 段号：题词，多是别人的话}、secs [(节号, 第一段, 最后一段, 词数)]、notes {注号: 全文}。"""
    tab = SEC_TAB.get(ch, {})
    rng = {k: tab[k] for k in want if k in tab}
    paras, quoted, words, notes = {}, set(), {k: 0 for k in rng}, {}
    for line in open(os.path.join(ROOT, f"source/text/{ch:02d}.txt"), encoding="utf-8").read().splitlines():
        m = re.match(r"\[n(\d+)(?:\.\d+)?\] (?:\{\w\} )?(.*)$", line)
        if m: notes[int(m.group(1))] = notes.get(int(m.group(1)), "") + " " + norm(m.group(2)); continue
        m = re.match(r"\[(\d+)\] (\{\w\} )?(.*)$", line)
        if not m: continue
        p = int(m.group(1))
        k = next((k for k, (a, b) in rng.items() if a <= p <= b), None)
        if k is None: continue
        raw = m.group(3)
        paras[p] = norm(re.sub(r"\{图：[^}]*\}", " ¤ ", NOTE_REF.sub(" ¤ ", raw)))      # 注号、图的位置留个记号：.loc、引用都不能跨过它（书里那是上标，搜不到）
        if m.group(2) == "{Q} ": quoted.add(p)
        words[k] += len(NOTE_REF.sub("", raw).split())
    return paras, quoted, [(k, rng[k][0], rng[k][1], words[k]) for k in want if k in rng], notes


def zh_text(ch):
    """译本这一章的全文（简体），去掉空白、# 号、本站加的 §k、行首标记和图：.zhv 引的译文要一字不差地在这里面。"""
    p = os.path.join(ROOT, f"source/text/zh/{ch:02d}.txt")
    t = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    return re.sub(r"\s+|\*", "", re.sub(r"\{图：[^}]*\}", "", re.sub(r"^#+ (§\d+ )?|^\{[A-Z]\} ", "", t, flags=re.M)))


def ids(path, cls):
    return re.findall(rf'<div class="{cls}" id="([^"]+)">', open(path, encoding="utf-8").read())


QUOTE_IN = re.compile(r"[‘“”\"]|’(?![A-Za-z])|(?<![A-Za-z])’")  # ’ 夹在字母中间是撇号，放行
SEC_RE = r"§(\d+)"

bad = 0
for path in sys.argv[1:]:
    t = open(path, encoding="utf-8").read(); errs, sus = [], []
    pid = re.search(r"(\w+)\.html$", path).group(1)
    if pid not in PAGES: print(f"✗ {path}  chapters.js 的 TS_PAGES 里没有页 {pid}"); bad += 1; continue
    ch, want, need = PAGES[pid]
    light = "light" in need; nsim_want = 2 if "sim2" in need else 1 if "sim" in need else 0
    paras, quoted, secs, notes = load(ch, want)
    if not secs: print(f"✗ {path}  chapters.js 的 TS_SECS 里没有第 {ch} 章的节 {want}"); bad += 1; continue
    if f'<body data-page="{pid}">' not in t: errs.append(f'<body> 应写成 <body data-page="{pid}">')
    def part(a):
        i = t.find(f"<h2>{a}</h2>")
        if i < 0: return ""
        j = t.find("<h2>", i + 4)
        return t[i:j if j > 0 else len(t)]
    def at_p(s, where):
        """data-p="18 21" 里的段号都要在这一页；n3 表示注 3。"""
        out = []
        for x in s.split():
            if re.fullmatch(r"n\d+", x):
                if int(x[1:]) not in notes: out.append(f"{where}：data-p 里的 {x}，这一章没有注 {x[1:]}")
            elif not x.isdigit() or int(x) not in paras: out.append(f"{where}：data-p 里的 {x} 不是这一页的段号")
        return out
    def cover(dp, label, where):
        """data-p 里每一段所在的节，都要列在节号标签里（「§4 §7」）：跨节了标签只写一节，读者回书时会找错地方。"""
        want_ = {next((s[0] for s in secs if s[1] <= int(x) <= s[2]), None) for x in dp.split() if x.isdigit()} - {None}
        miss = sorted(want_ - set(re.findall(SEC_RE, label)), key=int)
        return [f"{where}：data-p 里有 §{'、§'.join(miss)} 的段，节号标签（{plain(label)}）要列全"] if miss else []

    # 小节标题和顺序：模拟器只在 need 里有 sim / sim2 的页，情境题只在有 drill 的页；轻量页只要 LIGHT 那几节
    allowed = [x for x in SECS if (x != SIM_SEC or nsim_want) and (x != DRILL_SEC or "drill" in need)]
    must = LIGHT if light else allowed
    present = [x for x in SECS if f"<h2>{x}</h2>" in t]
    for x in must:
        if x not in present: errs.append(f"缺少小节：{x}")
    for x in set(present) - set(allowed): errs.append(f"这一页不该有「{x}」（看 chapters.js 的 need）")
    pos = [t.find(f"<h2>{x}</h2>") for x in present]
    if pos != sorted(pos): errs.append("小节顺序不对，应为：" + " → ".join(SECS))
    for x in re.findall(r"<h2>(.*?)</h2>", t):
        if x not in SECS: errs.append(f"多出来的小节标题：{x}（标题一个字都不能改）")
    if 'class="gate"' in t: errs.append("这本书没有读前 / 读后的分界线，不写 div.gate")
    g = re.search(r'<div class="gist">(.*?)</div>', t, flags=re.S)
    if not g: errs.append("「这一页在做什么」要有 <div class=\"gist\">")
    elif han(g.group(1)) > 200: errs.append(f"「这一页在做什么」{han(g.group(1))} 个汉字，超过 200")

    # 读之前
    pre = part("读之前：这一页在全书的哪里")
    if '<div class="linehere"></div>' not in pre: errs.append("「读之前」第一行要写 <div class=\"linehere\"></div>（由 ts.js 画）")
    if '<div class="crux">' not in pre: errs.append("「读之前」要有一个 <div class=\"crux\">")
    nq = len(re.findall(r"<li>", re.search(r'<ol class="qs">(.*?)</ol>', pre, flags=re.S).group(1))) if '<ol class="qs">' in pre else 0
    if not 2 <= nq <= 4: errs.append(f"「读之前」带着读的问题（<ol class=\"qs\">）应有 2–4 个，现在 {nq} 个")
    lead = re.sub(r'<div class="crux">.*?</div>|<ol class="qs">.*?</ol>|<p class="lede">.*?</p>|<div class="heads-up">.*?</div>', "", pre, flags=re.S)
    if han(lead) > 200: errs.append(f"「读之前」那段话 {han(lead)} 个汉字，超过 200")
    hu = re.findall(r'<div class="heads-up">(.*?)</div>', t, flags=re.S)
    if len(hu) > 1 or t.count('<div class="heads-up">') != pre.count('<div class="heads-up">'): errs.append("「别被带歪」框（div.heads-up）一页至多一个，只放在「读之前」里")
    for x in hu:
        if han(x) > 120: errs.append(f"「别被带歪」框 {han(x)} 个汉字，超过 120")

    # 分节地图：每节一条，只写 .what（节名、译本地标、英文开头、字数、档由 ts.js 从 chapters.js 补）
    sm = part("分节地图")
    items = re.findall(r'<li data-sec="(\w+)"><span class="what">(.*?)</span></li>', sm, flags=re.S)
    if [i[0] for i in items] != want or sm.count("<li") != len(items):
        errs.append(f"分节地图的节号应为 {want}，实际认出 {[i[0] for i in items]}（写法：<li data-sec=\"k\"><span class=\"what\">…</span></li>，其余由脚本补）")
    for k, what in items:
        if han(what) > 90: errs.append(f"分节地图 §{k}：说明 {han(what)} 个汉字，超过 90")

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

    # 英文词条：英文伴读的格式（接得进跨书词本）；.loc 4–7 个词、在 data-p 那一段；6–20 条，trap 占三分之一以上
    ws = part(WORD_SEC)
    if t.count('<div class="entry') != ws.count('<div class="entry'): errs.append(f"词条（.entry）只放在「{WORD_SEC}」里")
    ents = re.findall(r'<div class="entry( trap)?"><div class="en">(.*?)</div><div class="loc" data-p="(\d+)">(.*?)</div><div class="zh">(.*?)</div>(?:<div class="note">(.*?)</div>)?</div>', ws, flags=re.S)
    if ws.count('<div class="entry') != len(ents): errs.append("词条的写法不对：<div class=\"entry [trap]\"><div class=\"en\">…</div><div class=\"loc\" data-p=\"段号\">… 4–7 个词 …</div><div class=\"zh\">…</div><div class=\"note\">…</div></div>（.note 可省）")
    if ws and not 6 <= len(ents) <= 20: errs.append(f"词条应有 6–20 条，现在 {len(ents)} 条")
    if ents: errs += check_entries(ws, paras, trap_ratio=1 / 3, max_loc_words=7, scope="这一页")
    for trap, en_, p, loc, zh_, note in ents:
        n = len(norm(plain(loc)).strip("… ").split())
        if n < 4: errs.append(f".loc 太短（{n} 词，要 4–7 个）：{plain(loc)!r}")
        if "¤" in norm(plain(loc)): errs.append(f".loc 不能跨过脚注号：{plain(loc)!r}")
        if QUOTE_IN.search(plain(loc)): errs.append(f".loc 不能含引号（电子书里不好搜）：{plain(loc)!r}")
        if note and han(note) > 100: errs.append(f"词条「{plain(en_)[:20]}」：.note {han(note)} 个汉字，超过 100")
        if han(zh_) > 40: errs.append(f"词条「{plain(en_)[:20]}」：.zh {han(zh_)} 个汉字，超过 40（短，只写这一句里的意思）")

    # 译本勘误：一条一块；英文定位在那一段（或那条脚注）里，译本原句一字不差出自译本这一章
    ze = part("译本勘误")
    zes = re.findall(r'<div class="zherr" data-(p|n)="(\d+)"><h4><span class="sec">' + SEC_RE + r'</span>(.*?)</h4>\s*<p class="loc">(.*?)</p>\s*<p class="zhq">(.*?)</p>\s*<p>(.*?)</p></div>', ze, flags=re.S)
    if ze.count('<div class="zherr"') != len(zes): errs.append("勘误块的写法不对：<div class=\"zherr\" data-p=\"段号\"（书后注释用 data-n=\"注号\"）><h4><span class=\"sec\">§k</span>标题<span class=\"mark\">误译</span></h4><p class=\"loc\">… 英文 4–7 个词 …</p><p class=\"zhq\"><span class=\"zhv\">译本：「…」</span></p><p>…</p></div>")
    if t.count('<div class="zherr"') != ze.count('<div class="zherr"'): errs.append("勘误块只放在「译本勘误」里")
    if ze and not 1 <= len(zes) <= 40: errs.append(f"「译本勘误」应有 1–40 条，现在 {len(zes)} 条（实在一处错都没有，在报告里说，主编放行）")
    last_p = 0
    for pn, num, k, h4, loc, zhq, expl in zes:
        num, name = int(num), plain(h4)[:14]
        kinds = re.findall(r'<span class="mark(?: turn)?">(.*?)</span>', h4)
        if len(kinds) != 1 or kinds[0] not in ZH_KINDS: errs.append(f"勘误「{name}」：<h4> 里要有一个类型标签，五选一：{' / '.join(ZH_KINDS)}（译反用 class=\"mark turn\"）")
        if kinds == ["译反"] and 'class="mark turn"' not in h4: errs.append(f"勘误「{name}」：「译反」用 <span class=\"mark turn\">译反</span>")
        l_ = norm(plain(loc)).strip("… ").strip()
        src_ = paras.get(num, "") if pn == "p" else notes.get(num, "")
        if pn == "p" and num not in paras: errs.append(f"勘误「{name}」：第 {num} 段不在这一页")
        if pn == "n" and num not in notes: errs.append(f"勘误「{name}」：这一章没有注 {num}")
        if not (l_ in src_ and 4 <= len(l_.split()) <= 7): errs.append(f"勘误「{name}」：p.loc 要照抄{'第 ' + str(num) + ' 段' if pn == 'p' else '注 ' + str(num)}里连续的 4–7 个词：{l_!r}")
        if QUOTE_IN.search(plain(loc)): errs.append(f"勘误「{name}」：p.loc 不能含引号：{plain(loc)!r}")
        if zhq.count('<span class="zhv">') != 1: errs.append(f"勘误「{name}」：p.zhq 里要有一处 <span class=\"zhv\">译本：「…」</span>（漏译就引紧挨着的那一句）")
        if han(expl) > 140: errs.append(f"勘误「{name}」：说明 {han(expl)} 个汉字，超过 140")
        if pn == "p":
            sk = next((s[0] for s in secs if s[1] <= num <= s[2]), None)
            if sk is not None and sk != k: errs.append(f"勘误「{name}」：第 {num} 段在 §{sk}，不是 §{k}")
            if num < last_p: errs.append(f"勘误「{name}」：按段号排，第 {num} 段排在第 {last_p} 段之后")
            last_p = max(last_p, num)

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

    # 练一练：情境题
    dr = part(DRILL_SEC)
    drills = re.findall(r'<div class="drill" id="([^"]+)">\s*<h3><span class="sec">(§[^<]+)</span>(.*?)</h3>\s*<div class="scene">(.*?)</div>\s*<p class="ask">(.*?)</p>\s*(?:<ol class="opts">.*?</ol>\s*)?<details class="reveal"><summary>想好了再点开</summary>(.*?)</details>\s*</div>', dr, flags=re.S)
    if t.count('<div class="drill"') != len(drills) or dr.count('<div class="drill"') != len(drills):
        errs.append("情境题的写法不对，或不在「练一练：情境题」里：<div class=\"drill\" id=\"d-…\"><h3><span class=\"sec\">§k</span>标题</h3><div class=\"scene\"><p>…</p></div><p class=\"ask\">…</p>（可加 <ol class=\"opts\">…</ol>）<details class=\"reveal\"><summary>想好了再点开</summary><p>…</p><p class=\"where\">书里对应：…</p></details></div>")
    if "drill" in need:
        lo, hi = DRILL_N.get(pid, (2, 4))
        if not lo <= len(drills) <= hi: errs.append(f"情境题应有 {lo}–{hi} 道，现在 {len(drills)} 道")
    for did, lab, ttl, scene, ask, rev in drills:
        name = plain(ttl)[:14]
        if not re.fullmatch(r"d-[a-z0-9-]+", did): errs.append(f"情境题 id 要写成 d- 加小写英文：{did}")
        if han(scene) > 260: errs.append(f"情境题「{name}」：处境 {han(scene)} 个汉字，超过 260")
        where = re.findall(r'<p class="where">书里对应：(.*?)</p>', rev, flags=re.S)
        if len(where) != 1: errs.append(f"情境题「{name}」：分析最后要有一句 <p class=\"where\">书里对应：§k …</p>")
        if han(re.sub(r'<p class="where">.*?</p>', "", rev, flags=re.S)) > 300: errs.append(f"情境题「{name}」：分析超过 300 个汉字")
    for other in glob.glob(os.path.join(ROOT, "chapters/*.html")):
        if os.path.abspath(other) == os.path.abspath(path): continue
        for did in set(ids(other, "drill")) & {d[0] for d in drills}: errs.append(f"情境题 id {did} 和 {os.path.basename(other)} 重了")

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
        if not re.search(r'<span class="asof">核对于 20\d\d-\d\d', dl): errs.append(f"今天怎么看「{name}」：「今天」最后要有 <span class=\"asof\">核对于 2026-10。依据：…</span>")
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

    # 译本：「译本：『…』」只能出现在 .zhv 里；引的要真在译本这一章，每处不超过 20 个汉字；勘误以外一页不超过 6 处；别处不能和译本连续 12 个汉字相同
    zh = zh_text(ch)
    zhvs = re.findall(r'<span class="zhv">(.*?)</span>', bare, flags=re.S)
    free = re.sub(r'<p class="zhq">.*?</p>', "", bare.replace(ze, ""), flags=re.S)
    n_out = len(re.findall(r'<span class="zhv">', free))
    if n_out > 6: errs.append(f"勘误以外的 .zhv {n_out} 处，超过 6 处")
    for z in zhvs:
        if not z.startswith("译本："): errs.append(f".zhv 以「译本：」开头：{z[:20]}")
        for q in re.findall(r"「(.*?)」", z):
            qq = re.sub(r"\s+", "", q)
            if han(qq) > 20: errs.append(f".zhv 引的译文 {han(qq)} 个汉字，超过 20：{q[:20]}")
            if zh and any(x and x not in zh for x in qq.split("……")): errs.append(f".zhv 引的译文在译本这一章里找不到（要一字不差，省略处用 ……）：{q[:20]}")
    rest = re.sub(r"\s+", "", page_text(re.sub(r'<span class="zhv">.*?</span>', "", bare, flags=re.S)))
    for x in ZH_TITLES: rest = rest.replace(x, "¤")       # 指路写的译本小标题、章名不算抄译本
    if zh:
        hits = {rest[i:i + 12] for i in range(len(rest) - 11) if han(rest[i:i + 12]) == 12 and rest[i:i + 12] in zh}
        for x in sorted(hits)[:5]: errs.append(f"和译本有 12 个汉字以上相同的片段（只能放在 .zhv 里；页面和译本都是简体，最容易不知不觉抄进来）：{x}")
    for m in re.finditer(r"译本(?:里|中|译作|译为|译成|写作|作「|叫|的译法)", page_text(re.sub(r'<span class="zhv">.*?</span>', "", bare, flags=re.S))):
        errs.append(f"写译本怎么译，要放在 <span class=\"zhv\">译本：「…」</span> 里：…{m.group(0)}…")

    # 嫌疑（只提示，不算不通过；作者在报告里逐条答：改了，或者为什么不改）
    txt = page_text(bare)
    for m in re.finditer(r"上一节|下一节|上一页说|前面说过|前面讲过|前文|上文|下文|后面会讲|本章末尾|这一章末尾|章末|节末|开头那段|末尾那段", txt):
        sus.append(f"相对位置词「{m.group(0)}」：指路用 h2 的名字、§k 或译本原句")
    for m in re.finditer(r"是一回事|是同一回事|同一件事|是同一个东西|等同于|就等于", txt):
        sus.append(f"等同词「{m.group(0)}」：书里真的说两件事相同吗？多半是「相关 / 相似」，回原文看一眼")
    for m in re.finditer(r"没(?:有)?(?:给|注明|交代)(?:出)?(?:处|来源)|没(?:有)?点名|没说是谁|未注明出处", txt):
        sus.append(f"「{m.group(0)}」：先查书后注释（source/text/{ch:02d}.txt 章末「## 注释」），原书的注常常有出处")

    errs += check_images(t, path, min_photos=0 if light else 1, min_svgs=0 if light else 2, pattern=r"\.\./assets/img/(in|\d\d[ab]?)-[a-z0-9-]+\.jpg")
    c = counts(t)
    if ck and not 5 <= c["检查题"] <= 7: errs.append(f"理解检查应有 5–7 题，现在 {c['检查题']} 题")
    errs += check_markup(bare)
    total = sum(s[3] for s in secs)
    print(("✗" if errs else "✓"), path, f"词条 {len(ents)}（trap {c['trap']}） 照片 {c['照片']} SVG {c['SVG']} 引用 {c['引用']} 检查题 {c['检查题']}",
          f"概念 {len(blocks)} 模拟器 {len(simids)} 情境题 {len(drills)} 勘误 {len(zes)} 今天 {len(tcs)} 看法 {len(vws)} 回顾 {len(items_r)} 译本 {len(zhvs)} 原文 {total} 词")
    for e in errs: print("    " + e)
    for e in sus: print("    ？" + e)
    bad += bool(errs)
sys.exit(1 if bad else 0)
