#!/usr/bin/env python3
"""小说页结构检查：python3 -I tools/lint.py chapters/09.html …
查：读前 / 读后的小节和顺序（读后的几节必须在 <section class="after"> 里）、读之前（.gist、.where、带着读的问题）、
分节地图（每节一条、<b> 是本站定的日期标签、照抄英文开头、词数、本站分的节、长页分几次坐下）、背景小块的长度、
词条（.en 重复、.loc 是否在原文那一段里、是否在自己那一节的小标题下、顺序、密度、trap 占比、前几篇拼错的词够不够）、
查理的文字（曲线、字数）、记忆拼图（年纪、长度）、引用块（数量、长度、不能引 {Q} 段落）、读完想一想、对照今天（图例、核对日期）、
精彩回顾、图片、理解检查的题数、译本（「译本：」只能在 .zhv 里，引的句子要真在译本里、够短；别处不能和译本连续 12 个汉字相同）、
页面里的 <style>/<script>/写死的颜色、直引号、原书材料的路径。
回忆录页（m1–m7）的规则第 6 段再定，现在只查通用的几项。通用的检查在 ~/tutorials-deploy/scripts/lint_common.py。"""
import os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.expanduser("~/tutorials-deploy/scripts"))
from lint_common import norm, check_entries, check_quotes, check_images, check_markup, counts, page_text

BEFORE = ["读之前", "分节地图", "背景：书里默认你知道的事", "词与短语"]
AFTER = ["查理的文字", "记忆拼图", "值得停下来的句子", "读完想一想", "对照今天", "检查一下理解", "精彩回顾"]
OPTIONAL = {"记忆拼图", "对照今天"}
# 页 id → 报告号（和 tools/extract.py 的 PAGES 一致）
REPORTS = {"01": [1, 2, 3, 4, 5, 6], "07": [7, 8], "09": [9], "10": [10], "11a": [11], "11b": [11], "12": [12], "13a": [13], "13b": [13],
           "14a": [14], "14b": [14], "14c": [14], "15": [15], "16a": [16], "16b": [16], "16c": [16], "17a": [17], "17b": [17]}
# 查理拼错得多的页，「查理拼的」词条（entry spell）至少几条
SPELL_MIN = {"01": 15, "07": 12, "09": 4, "17b": 8}
MON = {m: i for i, ms in enumerate([["january"], ["february"], ["march", "mar", "martch"], ["april"], ["may"], ["june"], ["july"],
       ["august"], ["september"], ["october"], ["november", "nov"], ["december"]], 1) for m in ms}
han = lambda s: len(re.findall(r"[一-鿿]", re.sub(r"<[^>]+>", "", s)))

def load(src):
    """读 source/text/<页>.txt。返回 paras {段号: 文字}、quoted {是 {Q} 的段号}、secs [(节号, 报告, 日期, 是否本站分, 第一段, 最后一段, 词数)]。"""
    paras, quoted, secs = {}, set(), []
    for line in open(src, encoding="utf-8").read().splitlines():
        m = re.match(r"## §(\d+) 报告 (\d+) · (.*)$", line)
        if m: secs.append([int(m.group(1)), int(m.group(2)), m.group(3), "本站分" in m.group(3), None, None, 0]); continue
        m = re.match(r"\[(\d+)\] (\{Q\} )?(.*)$", line)
        if m:
            p = int(m.group(1)); paras[p] = norm(m.group(3))
            if m.group(2): quoted.add(p)
            s = secs[-1]; s[4] = s[4] or p; s[5] = p; s[6] += len(m.group(3).split())
    return paras, quoted, [tuple(s) for s in secs]

def want_label(secs, i):
    """分节地图 <b> 的标签：日期转成「4 月 1 日」，*** 之后和本站分的节加「（续）」，报告开头没有日期的写「报告 N」；
    一页包含几篇报告时，每篇报告的第一节前面加「报告 N · 」。"""
    k, r, d, ours = secs[i][:4]
    cont = "（续）" if "（" in d else ""
    base = d.split("（")[0].strip()
    m = re.match(r"([A-Za-z]+)\.? (\d+)$", base)
    t = re.match(r"(\d+:\d+) ([AP])\.M\.$", base)
    if m and m.group(1).lower() in MON: lab = f"{MON[m.group(1).lower()]} 月 {m.group(2)} 日"
    elif t: lab = ("上午 " if t.group(2) == "A" else "下午 ") + t.group(1)
    else: return f"报告 {r}" + cont
    first_of_report = i == 0 or secs[i - 1][1] != r
    multi = len({s[1] for s in secs}) > 1
    return (f"报告 {r} · " if multi and first_of_report else "") + lab + cont

def zh_text(rs):
    t = ""
    for r in rs:
        p = os.path.join(ROOT, f"source/text/zh/r{r:02d}.txt")
        if os.path.exists(p): t += re.sub(r"^#.*$|^## .*$|\{注\} |\{Q\} ", "", open(p, encoding="utf-8").read(), flags=re.M)
    return re.sub(r"\s+", "", t)

if sys.argv[1:2] == ["--map"]:
    # 打印分节地图的骨架（标签、词数、开头几个词），作者照着填 .what：python3 -I tools/lint.py --map 09
    for pid in sys.argv[2:]:
        paras, quoted, secs = load(os.path.join(ROOT, f"source/text/{pid}.txt"))
        for i, (k, r, d, ours, p0, p1, words) in enumerate(secs):
            first = next((paras[p] for p in range(p0, p1 + 1) if p not in quoted), "")
            first = re.sub(r'"(?=\w)', "“", first).replace('"', "”").replace("'", "’")   # 页面里用弯引号，lint 比对时会统一
            cls = ' class="ours"' if ours else ""
            print(f'  <li data-sec="{k}"{cls}><b>{want_label(secs, i)}<span class="w">约 {round(words, -2) or words} 词</span></b><span class="en">{" ".join(first.split()[:6])} …</span><span class="what"></span></li>   <!-- 第 {p0}–{p1} 段 -->')
    sys.exit(0)

bad = 0
for path in sys.argv[1:]:
    t = open(path, encoding="utf-8").read(); errs = []
    pid = re.search(r"([0-9a-z]+)\.html$", path).group(1)
    if pid not in REPORTS:
        errs += check_markup(t)
        print(("✗" if errs else "✓"), path, "（回忆录页和专页的规则还没定，只查了通用的几项）")
        for e in errs: print("    " + e)
        bad += bool(errs); continue
    paras, quoted, secs = load(os.path.join(ROOT, f"source/text/{pid}.txt"))
    if f'<body data-page="{pid}">' not in t: errs.append(f'<body> 应写成 <body data-page="{pid}">')
    def part(a):
        i = t.find(f"<h2>{a}</h2>")
        if i < 0: return ""
        j = t.find("<h2>", i + 4)
        return t[i:j if j > 0 else len(t)]

    # 小节标题、顺序、读前 / 读后
    SECS = BEFORE + AFTER
    present = [s for s in SECS if f"<h2>{s}</h2>" in t]
    for s in SECS:
        if s not in present and s not in OPTIONAL: errs.append(f"缺少小节：{s}")
    pos = [t.find(f"<h2>{s}</h2>") for s in present]
    if pos != sorted(pos): errs.append("小节顺序不对，应为：" + " → ".join(SECS))
    for s in re.findall(r"<h2>(.*?)</h2>", t):
        if s not in SECS: errs.append(f"多出来的小节标题：{s}（标题一个字都不能改）")
    a0 = t.find('<section class="after">')
    if a0 < 0: errs.append('读后的几节要放在 <section class="after"> … </section> 里（它前面由 al.js 插入「先去读原书」的分界）')
    else:
        for s in present:
            i = t.find(f"<h2>{s}</h2>")
            if s in BEFORE and i > a0: errs.append(f"「{s}」是读前的一节，要放在 <section class=\"after\"> 前面")
            if s in AFTER and i < a0: errs.append(f"「{s}」是读后的一节，要放在 <section class=\"after\"> 里面")

    # 读之前
    pre = part("读之前")
    g = re.search(r'<div class="gist">(.*?)</div>', pre, flags=re.S)
    if not g: errs.append("「读之前」要有 <div class=\"gist\">")
    elif han(g.group(1)) > 180: errs.append(f"「读之前」的 .gist {han(g.group(1))} 个汉字，超过 180")
    w = re.search(r'<div class="where">(.*?)</div>', pre, flags=re.S)
    if not w: errs.append("「读之前」要有 <div class=\"where\">（查理此刻）")
    elif han(w.group(1)) > 150: errs.append(f"「查理此刻」{han(w.group(1))} 个汉字，超过 150")
    nq = len(re.findall(r"<li>", re.search(r'<ol class="qs">(.*?)</ol>', pre, flags=re.S).group(1))) if '<ol class="qs">' in pre else 0
    if not 2 <= nq <= 4: errs.append(f"「读之前」带着读的问题（<ol class=\"qs\">）应有 2–4 个，现在 {nq} 个")

    # 分节地图：每节一条；<b> 是本站定的标签加词数；.en 照抄这一节第一段（不算 {Q}）开头 4–7 个词
    sm = part("分节地图")
    items = re.findall(r'<li data-sec="(\d+)"( class="ours")?><b>(.*?)<span class="w">约 (\d+) 词</span></b><span class="en">(.*?)</span><span class="what">(.*?)</span></li>', sm, flags=re.S)
    want = [s[0] for s in secs]
    if [int(i[0]) for i in items] != want: errs.append(f"分节地图的节号应为 {want}，实际是 {[int(i[0]) for i in items]}（写法照规范：<li data-sec><b>标签<span class=\"w\">约 N 词</span></b><span class=\"en\">…</span><span class=\"what\">…</span></li>）")
    for i, ((k, ours, b, w_, en, what), sec) in enumerate(zip(items, secs)):
        _, _, _, is_ours, p0, p1, words = sec
        if bool(ours) != is_ours: errs.append(f"分节地图 §{k}：" + ("这一节是本站分的，<li> 要加 class=\"ours\"" if is_ours else "这一节是原书的分隔，不要加 class=\"ours\""))
        lab = re.sub(r"<[^>]+>", "", b).strip()
        if lab != want_label(secs, i): errs.append(f"分节地图 §{k}：<b> 应写「{want_label(secs, i)}」，现在是「{lab}」")
        e = norm(re.sub(r"<[^>]+>", "", en)).strip("… ").strip()
        first = next((paras[p] for p in range(p0, p1 + 1) if p in paras and p not in quoted), "")
        if not (first.startswith(e) and 4 <= len(e.split()) <= 7): errs.append(f"分节地图 §{k}：.en 照抄这一节第一段（不算引文）开头 4–7 个词，后面加 …：{e!r}")
        if abs(int(w_) - words) > max(60, words * 0.1): errs.append(f"分节地图 §{k}：词数写的是 {w_}，实际约 {words}")
        if han(what) > 40: errs.append(f"分节地图 §{k}：说明 {han(what)} 个汉字，超过 40")
    total = sum(s[6] for s in secs)
    sits = len(re.findall(r'<li class="sit">', sm))
    if total > 6000 and not 2 <= sits <= 3: errs.append(f"这一页 {total} 词，分节地图要用 <li class=\"sit\"> 分成 2–3 次坐下，现在 {sits} 次")
    if total <= 6000 and sits: errs.append("6000 词以内的页不分坐下")
    if any(s[3] for s in secs) and "本站" not in re.sub(r"<ol.*?</ol>", "", sm, flags=re.S): errs.append("分节地图里有本站分的节，lede 要说明哪几节是本站分的（原书这里没有分隔）")

    # 背景
    bg = part("背景：书里默认你知道的事")
    blocks = re.split(r"<h3>", bg)[1:]
    if not 3 <= len(blocks) <= 8: errs.append(f"「背景」应有 3–8 个 <h3> 小块，现在 {len(blocks)} 个")
    for b in blocks:
        title = re.sub(r"<[^>]+>", "", b.split("</h3>")[0])
        if not re.match(r'<span class="sec">§\d+</span>', b): errs.append(f"「背景」小块标题前要有节号 <span class=\"sec\">§k</span>：{title}")
        body = re.sub(r"<figure.*?</figure>|<div class=\"who\">.*?</div>\s*</div>", "", b.split("</h3>", 1)[-1], flags=re.S)
        if han(body) > 220: errs.append(f"「背景」{title}：{han(body)} 个汉字，超过 220")

    # 词条：在自己那一节的小标题下；密度；trap 占「非拼写」词条的三分之一；拼错的词够不够
    ws = part("词与短语")
    rng = {s[0]: (s[4], s[5]) for s in secs}
    cur = None
    for m in re.finditer(r'<h3 class="sec-head" id="s(\d+)">|<div class="loc" data-p="(\d+)">', ws):
        if m.group(1): cur = int(m.group(1)); continue
        p = int(m.group(2))
        if cur is None: errs.append(f"第 {p} 段的词条前面没有节的小标题 <h3 class=\"sec-head\" id=\"sK\">"); continue
        a, b = rng.get(cur, (0, -1))
        if not a <= p <= b: errs.append(f"第 {p} 段的词条放在了 §{cur} 下面（§{cur} 是第 {a}–{b} 段）")
    for k in re.findall(r'<h3 class="sec-head" id="s(\d+)">', ws):
        if int(k) not in rng: errs.append(f"词与短语：没有 §{k} 这一节")
    errs += check_entries(t, paras, per_k=4, max_n=80, scope="这一页")
    n_spell = len(re.findall(r'class="entry spell"', t)); n_trap = len(re.findall(r'class="entry trap"', t))
    n_all = len(re.findall(r'<div class="en">', t))
    if n_all - n_spell and n_trap < (n_all - n_spell) / 3: errs.append(f"trap 只有 {n_trap} 条，不到拼写以外词条（{n_all - n_spell} 条）的三分之一")
    if n_spell < SPELL_MIN.get(pid, 0): errs.append(f"「查理拼的」词条（entry spell）只有 {n_spell} 条，这一页至少 {SPELL_MIN[pid]} 条")
    if re.search(r'class="entry (?:trap spell|spell trap)"', t): errs.append("一条词条不能既是 trap 又是 spell")

    # 查理的文字：曲线 + 不长的说明
    cw = part("查理的文字")
    if '<div class="curve"></div>' not in cw: errs.append("「查理的文字」要有 <div class=\"curve\"></div>（曲线由 al.js 画）")
    if han(re.sub(r'<span class="zhv">.*?</span>', "", cw, flags=re.S)) > 320: errs.append(f"「查理的文字」正文超过 320 个汉字（不算 .zhv）")

    # 记忆拼图（可省）
    mm = part("记忆拼图")
    if mm:
        cards = re.findall(r'<div class="mem" data-age="([^"]*)"><b>(.*?)</b><p>(.*?)</p><span class="sec">§\d+</span></div>', mm, flags=re.S)
        if not cards or len(cards) != mm.count('<div class="mem"'): errs.append("「记忆拼图」的卡片写法：<div class=\"mem\" data-age=\"6\"><b>标题</b><p>…</p><span class=\"sec\">§k</span></div>（年纪推不出来写 data-age=\"?\"）")
        for age, b_, p_ in cards:
            if not re.fullmatch(r"\d+(\.\d)?|\?", age): errs.append(f"记忆拼图「{b_}」：data-age 写数字（约几岁），推不出来写 ?")
            if han(p_) > 120: errs.append(f"记忆拼图「{b_}」：{han(p_)} 个汉字，超过 120")

    # 引用块：不超过 2 处，只引查理写的（不引 {Q} 段落）
    errs += check_quotes(t, 2)
    for q in re.findall(r'<blockquote class="quote">(.*?)<cite>', t, flags=re.S):
        s = norm(re.sub(r"<[^>]+>", "", q)).strip("… ").strip()
        where = [p for p, v in paras.items() if s.replace("…", "") and all(x.strip() in v for x in s.split("…") if x.strip())]
        if not where: errs.append(f"引用块在原文里找不到（要一字不差，省略处用 …）：{s[:50]!r}")
        elif all(p in quoted for p in where): errs.append(f"引用块引的是 {{Q}} 段落（剪报、信），只引查理写的：{s[:50]!r}")
        if len(s.replace("…", " ").split()) > 25: errs.append(f"引用块超过 25 个词：{s[:50]!r}")

    # 读完想一想：2–3 题，每题一个笔记框和「本站的看法」
    th = part("读完想一想")
    nt = th.count('<div class="think">')
    if not 2 <= nt <= 3: errs.append(f"「读完想一想」应有 2–3 题（<div class=\"think\">），现在 {nt} 题")
    if th.count('<textarea class="note"') < nt: errs.append("「读完想一想」每题要有一个 <textarea class=\"note\" data-key=\"页-t1\">")
    for v in re.findall(r'<details class="reveal"><summary>本站的看法</summary>(.*?)</details>', th, flags=re.S):
        if han(v) > 200: errs.append(f"「本站的看法」{han(v)} 个汉字，超过 200")
    if th.count("<summary>本站的看法</summary>") != nt: errs.append("「读完想一想」每题后面跟一个 <details class=\"reveal\"><summary>本站的看法</summary>…</details>")

    # 对照今天（可省）：要有图例，每张卡片写明判的是哪句话、核对日期
    td = part("对照今天")
    if td:
        if '<ul class="verdicts">' not in td: errs.append("「对照今天」开头要有图例 <ul class=\"verdicts\">（照样板抄）")
        cards = re.findall(r'<div class="today" data-verdict="(成立|部分成立|被改写)"><h4>(.*?)</h4>(.*?)</div>', td, flags=re.S)
        if not 1 <= len(cards) <= 2 or len(cards) != td.count('<div class="today"'): errs.append(f"「对照今天」应有 1–2 张卡片，data-verdict 只能是 成立 / 部分成立 / 被改写，现在认出 {len(cards)} 张")
        for v, h4, body in cards:
            if not h4.startswith("书里的说法："): errs.append(f"「对照今天」{h4}：<h4> 以「书里的说法：」开头，写明判的是哪句话")
            if not re.search(r'<span class="asof">核对于 20\d\d-\d\d。依据：', body): errs.append(f"「对照今天」{h4}：要写 <span class=\"asof\">核对于 YYYY-MM。依据：…</span>")

    # 精彩回顾
    rc = part("精彩回顾")
    if '<p class="recall-line">' not in rc: errs.append("「精彩回顾」要有 <p class=\"recall-line\"><b>一句话：</b>…</p>")
    items_r = re.findall(r'<div class="item"><b>(.*?)</b><p>(.*?)</p><span class="sec">(§[^<]+)</span></div>', rc, flags=re.S)
    if not 4 <= len(items_r) <= 6 or len(items_r) != rc.count('<div class="item">'): errs.append(f"「精彩回顾」应有 4–6 张卡片，写法 <div class=\"item\"><b>标题</b><p>…</p><span class=\"sec\">§k</span></div>，现在认出 {len(items_r)} 张")
    for b_, p_, _ in items_r:
        if han(p_) > 100: errs.append(f"「精彩回顾」{b_}：{han(p_)} 个汉字，超过 100")

    # 译本：「译本：『…』」只能出现在 .zhv 里；引的句子要真在译本这几篇里，每处不超过 20 个汉字，一页不超过 6 处
    zh = zh_text(REPORTS[pid])
    zhvs = re.findall(r'<span class="zhv">(.*?)</span>', t, flags=re.S)
    if len(zhvs) > 6: errs.append(f"译本译法（.zhv）{len(zhvs)} 处，超过 6 处")
    for z in zhvs:
        if not z.startswith("译本："): errs.append(f".zhv 以「译本：」开头：{z[:20]}")
        for q in re.findall(r"「(.*?)」", z):
            qq = re.sub(r"\s+", "", q)
            if han(qq) > 20: errs.append(f".zhv 引的译文 {han(qq)} 个汉字，超过 20：{q[:20]}")
            if zh and any(x and x not in zh for x in qq.split("……")): errs.append(f".zhv 引的译文在译本这几篇里找不到（要一字不差，省略处用 ……）：{q[:20]}")
    rest = re.sub(r"\s+", "", page_text(re.sub(r'<span class="zhv">.*?</span>', "", t, flags=re.S)))
    if zh:
        hits = {rest[i:i + 12] for i in range(len(rest) - 11) if han(rest[i:i + 12]) == 12 and rest[i:i + 12] in zh}
        for x in sorted(hits)[:5]: errs.append(f"和译本有 12 个汉字以上相同的片段（只能放在 .zhv 里）：{x}")
    for m in re.finditer(r"译本(?:里|中|译作|译为|写作|作「|叫|的译法)", re.sub(r'<span class="zhv">.*?</span>', "", page_text(t), flags=re.S)):
        errs.append(f"写译本怎么译，要放在 <span class=\"zhv\">译本：「…」</span> 里：…{m.group(0)}…")
    for k in re.findall(r'class="note" data-key="([^"]+)"', t):
        if not k.startswith(f"{pid}-"): errs.append(f"笔记的 data-key 要以 {pid}- 开头：{k}")

    errs += check_images(t, path, min_photos=1, min_svgs=1, pattern=r"\.\./assets/img/[0-9a-z]{2,3}-[a-z0-9-]+\.jpg")
    c = counts(t)
    if not 4 <= c["检查题"] <= 6: errs.append(f"理解检查应有 4–6 题，现在 {c['检查题']} 题")
    errs += check_markup(t)
    print(("✗" if errs else "✓"), path, " ".join(f"{k} {v}" for k, v in c.items()), f"拼写 {n_spell} 地图 {len(items)} 坐下 {sits} 回顾 {len(items_r)} 译本 {len(zhvs)} 原文 {total} 词")
    for e in errs: print("    " + e)
    bad += bool(errs)
sys.exit(1 if bad else 0)
