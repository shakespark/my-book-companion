#!/usr/bin/env python3
"""页面结构检查：python3 -I tools/lint.py chapters/01a.html …
页 id → 章和节从 assets/chapters.js 的 UP_PAGES 读（need 是这一页必须有的可省小节）；原文从 source/text/NN.txt 读（段号在一章之内连续）。
查：小节标题和顺序、读之前（一生的占位、带着读的问题）、分节地图（每节一条、地标、照抄英文开头、词数）、出场的人、背景小块、
经济学概念块（id、长度、全站不重复）和论证步骤、剪报和文件（每张文件图都有一块、大意）、词条（.en 重复、.loc 在这一页的原文里、在自己那一节下、密度、trap 占比、不含引号）、
扫描错字表、和 Sowell 的书对照（链接的老站页面和锚点存在）、对照今天（图例、结论标签、书里 / 当时 / 今天、核对日期）、
引用块（数量、长度、不能引 {Q} 和图片）、理解检查、读完想一想、精彩回顾、图片、页面里的 <style>/<script>/写死的颜色、直引号、原书材料的路径。
通用的几项在 ~/tutorials-deploy/scripts/lint_common.py。照 On Borrowed Time 的 lint 改。"""
import glob, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.expanduser("~/tutorials-deploy/scripts"))
from lint_common import norm, check_entries, check_quotes, check_images, check_markup, counts

SECS = ["这一页在做什么", "读之前：这一页在他一生的哪里", "分节地图", "出场的人", "背景：作者默认你知道的事",
        "先用中文过一遍：这一页的经济学", "书里的剪报和文件", "词与短语", "和 Sowell 的书对照", "对照今天",
        "值得停下来的句子", "检查一下理解", "读完想一想", "精彩回顾"]
# 可省的小节在 chapters.js 里的简称（UP_PAGES 的 need）
OPT = {"econ": "先用中文过一遍：这一页的经济学", "sowell": "和 Sowell 的书对照", "today": "对照今天"}  # need 里另有 "views"：经济学一节至少一块看法块
VERDICTS = {"成立", "部分成立", "被改写", "有争议"}
SISTER = {"odyssey": os.path.expanduser("~/a_personal_odyssey"), "letters": os.path.expanduser("~/a_man_of_letters")}
han = lambda s: len(re.findall(r"[一-鿿]", re.sub(r"<[^>]+>", "", s)))
plain = lambda s: re.sub(r"<[^>]+>", "", s)

js = open(os.path.join(ROOT, "assets/chapters.js"), encoding="utf-8").read()
PAGES = {}
for m in re.finditer(r'\{ id: "(\w+)", ch: (\d+), secs: \[([\d, ]+)\][^\n]*', js):
    need = re.search(r'need: \[([^\]]*)\]', m.group(0))
    PAGES[m.group(1)] = (int(m.group(2)), [int(x) for x in m.group(3).split(",")],
                         re.findall(r'"(\w+)"', need.group(1)) if need else [])


def load(ch, want):
    """读 source/text/NN.txt 里属于这一页的几节。返回 paras {段号: 文字}、quoted {{Q} 段号}、imgs {段号: (图号, 类型, 转写的行)}、secs [(节号, 第一段, 最后一段, 词数)]。"""
    paras, quoted, imgs, secs, k = {}, set(), {}, [], None
    for line in open(os.path.join(ROOT, f"source/text/{ch:02d}.txt"), encoding="utf-8").read().splitlines():
        if line.startswith("## 注"): break
        m = re.match(r"## §(\d+) ", line)
        if m:
            k = int(m.group(1))
            if k in want: secs.append([k, None, None, 0])
            continue
        m = re.match(r"\[(\d+)\] (\{Q\} |\{CAP\} )?(?:\{IMG (\d+)\} ?)?(.*)$", line)
        if not m or k not in want: continue
        p = int(m.group(1))
        if m.group(3):
            rows = m.group(4).split(" / ")
            kind = re.match(r"【(.+?)】", rows[0])
            imgs[p] = (m.group(3), kind.group(1) if kind else "?", [norm(x) for x in rows[1:]])
        else:
            paras[p] = norm(m.group(4))
            if m.group(2): quoted.add(p)
            secs[-1][3] += len(m.group(4).split())
        s = secs[-1]; s[1] = s[1] if s[1] is not None else p; s[2] = p
    return paras, quoted, imgs, [tuple(s) for s in secs]


def concept_ids(path):
    return re.findall(r'<div class="concept" id="([^"]+)">', open(path, encoding="utf-8").read())


bad = 0
for path in sys.argv[1:]:
    t = open(path, encoding="utf-8").read(); errs = []
    pid = re.search(r"(\w+)\.html$", path).group(1)
    if pid not in PAGES: print(f"✗ {path}  chapters.js 的 UP_PAGES 里没有页 {pid}"); bad += 1; continue
    ch, want, need_opt = PAGES[pid]
    paras, quoted, imgs, secs = load(ch, want)
    docs = {p: v for p, v in imgs.items() if v[1] != "照片"}  # 剪报、文件、信……（照片不用讲）
    if f'<body data-page="{pid}">' not in t: errs.append(f'<body> 应写成 <body data-page="{pid}">')
    def part(a):
        i = t.find(f"<h2>{a}</h2>")
        if i < 0: return ""
        j = t.find("<h2>", i + 4)
        return t[i:j if j > 0 else len(t)]

    # 小节标题和顺序
    need = [s for s in SECS if (s not in OPT.values() or s in {OPT[x] for x in need_opt if x in OPT}) and (s != "书里的剪报和文件" or docs)]
    present = [s for s in SECS if f"<h2>{s}</h2>" in t]
    for s in need:
        if s not in present: errs.append(f"缺少小节：{s}" + ("（chapters.js 里这一页的 need 要求有）" if s in OPT.values() else ""))
    if not docs and "书里的剪报和文件" in present: errs.append("这一页没有剪报和文件的图，不要写「书里的剪报和文件」")
    pos = [t.find(f"<h2>{s}</h2>") for s in present]
    if pos != sorted(pos): errs.append("小节顺序不对，应为：" + " → ".join(s for s in SECS if s in present or s in need))
    for s in re.findall(r"<h2>(.*?)</h2>", t):
        if s not in SECS: errs.append(f"多出来的小节标题：{s}（标题一个字都不能改）")
    g = re.search(r'<div class="gist">(.*?)</div>', t, flags=re.S)
    if not g: errs.append("「这一页在做什么」要有 <div class=\"gist\">")
    elif han(g.group(1)) > 200: errs.append(f"「这一页在做什么」{han(g.group(1))} 个汉字，超过 200")

    # 读之前
    pre = part("读之前：这一页在他一生的哪里")
    if '<div class="lifehere"></div>' not in pre: errs.append("「读之前」第一行要写 <div class=\"lifehere\"></div>（一生的几段由 up.js 画）")
    nq = len(re.findall(r"<li>", re.search(r'<ol class="qs">(.*?)</ol>', pre, flags=re.S).group(1))) if '<ol class="qs">' in pre else 0
    if not 2 <= nq <= 4: errs.append(f"「读之前」带着读的问题（<ol class=\"qs\">）应有 2–4 个，现在 {nq} 个")
    lead = re.sub(r'<ol class="qs">.*?</ol>|<p class="lede">.*?</p>|<figure.*?</figure>', "", pre, flags=re.S)
    if han(lead) > 220: errs.append(f"「读之前」那段话 {han(lead)} 个汉字，超过 220")

    # 分节地图
    sm = part("分节地图")
    items = re.findall(r'<li data-sec="(\d+)"><b>(.*?)<span class="w">约 (\d+) 词</span></b><span class="en">(.*?)</span><span class="what">(.*?)</span></li>', sm, flags=re.S)
    if [int(i[0]) for i in items] != want: errs.append(f"分节地图的节号应为 {want}，实际是 {[int(i[0]) for i in items]}（写法照规范：<li data-sec><b>地标<span class=\"w\">约 N 词</span></b><span class=\"en\">…</span><span class=\"what\">…</span></li>）")
    for (k, b, w, en, what), (_, p0, p1, words) in zip(items, secs):
        if not han(b): errs.append(f"分节地图 §{k}：<b> 要写中文地标")
        if han(b) > 22: errs.append(f"分节地图 §{k}：地标 {han(b)} 个汉字，超过 22")
        e = norm(plain(en)).strip("… ").strip()
        first = next((paras[p] for p in range(p0, p1 + 1) if p in paras and p not in quoted), "")
        if not (first.startswith(e) and 4 <= len(e.split()) <= 7): errs.append(f"分节地图 §{k}：.en 照抄这一节第一段（不算引文和图片）开头 4–7 个词，后面加 …：{e!r}")
        if re.search(r'[“”"]', en) and '"' not in " ".join(first.split()[:4]): errs.append(f"分节地图 §{k}：.en 不能含引号（这一节开头躲得开）：{en!r}")
        if abs(int(w) - words) > max(60, words * 0.1): errs.append(f"分节地图 §{k}：词数写的是 {w}，实际约 {words}")
        if han(what) > 40: errs.append(f"分节地图 §{k}：说明 {han(what)} 个汉字，超过 40")

    # 出场的人
    pp = part("出场的人")
    cards = re.findall(r'<div><b>(.*?)</b><span class="en">(.*?)</span>(.*?)</div>', re.sub(r'<p class="lede">.*?</p>', "", pp, flags=re.S), flags=re.S)
    if '<div class="who">' not in pp or not 1 <= len(cards) <= 12: errs.append(f"「出场的人」要有 <div class=\"who\">，里面 1–12 张卡片 <div><b>名字</b><span class=\"en\">原名，生卒年或身份</span>……</div>，现在认出 {len(cards)} 张")
    for b, en, body in cards:
        if han(body) > 110: errs.append(f"出场的人「{plain(b)}」：{han(body)} 个汉字，超过 110")

    # 背景
    bg = part("背景：作者默认你知道的事")
    blks = re.split(r"<h3>", bg)[1:]
    if not 3 <= len(blks) <= 8: errs.append(f"「背景」应有 3–8 个 <h3> 小块，现在 {len(blks)} 个")
    for b in blks:
        ttl = plain(b.split("</h3>")[0])
        if not re.match(r'<span class="sec">(§\d+|序言)</span>', b): errs.append(f"「背景」小块标题前要有节号 <span class=\"sec\">§k</span>：{ttl}")
        body = re.sub(r'<figure.*?</figure>|<div class="table-wrap">.*?</div>', "", b.split("</h3>", 1)[-1], flags=re.S)
        if han(body) > 260: errs.append(f"「背景」{ttl}：{han(body)} 个汉字，超过 260")

    # 经济学：概念块和论证步骤
    cp = part("先用中文过一遍：这一页的经济学")
    blocks = re.findall(r'<div class="concept" id="([^"]+)">(.*?)</div>\s*(?=<div class="concept"|<div class="views"|<h2>|<p class="lede">|<p class="argue-cap">|<ol class="argue">|<figure|$)', cp, flags=re.S)
    if cp and cp.count('<div class="concept"') != len(blocks): errs.append("概念块的写法不对：<div class=\"concept\" id=\"c-…\"><h3>…</h3><p>…</p><p class=\"use\">…</p></div>")
    if cp and not 1 <= len(blocks) <= 4 and '<ol class="argue">' not in cp: errs.append(f"「经济学」应有 1–4 个概念块，或一段论证步骤，现在 {len(blocks)} 个概念块")
    for cid, body in blocks:
        if not re.fullmatch(r"c-[a-z0-9-]+", cid): errs.append(f"概念块 id 要写成 c- 加小写英文：{cid}")
        if not re.match(r'\s*<h3><span class="sec">(§\d+|序言)</span>', body): errs.append(f"概念块 {cid}：要以 <h3><span class=\"sec\">§k</span>中文名 <span class=\"en\">原文</span></h3> 开头")
        use = re.findall(r'<p class="use"><b>在这一页：</b>(.*?)</p>', body, flags=re.S)
        if len(use) != 1: errs.append(f"概念块 {cid}：要有一句 <p class=\"use\"><b>在这一页：</b>…</p>")
        elif han(use[0]) > 80: errs.append(f"概念块 {cid}：「在这一页」{han(use[0])} 个汉字，超过 80")
        main_ = re.sub(r'<h3>.*?</h3>|<p class="use">.*?</p>|<figure.*?</figure>', "", body, flags=re.S)
        if han(main_) > 280: errs.append(f"概念块 {cid}：{han(main_)} 个汉字，超过 280")
    for other in glob.glob(os.path.join(ROOT, "chapters/*.html")):
        if os.path.abspath(other) == os.path.abspath(path): continue
        for cid in set(concept_ids(other)) & {b[0] for b in blocks}:
            errs.append(f"概念 {cid} 在 {os.path.basename(other)} 里已经写过，这里改成 <a class=\"term\" href=\"{os.path.basename(other)}#{cid}\">…</a>")
    for href_, cid in re.findall(r'<a class="term" href="(\w+)\.html#(c-[a-z0-9-]+)">', t):
        f = os.path.join(ROOT, f"chapters/{href_}.html")
        if os.path.exists(f) and cid not in concept_ids(f): errs.append(f"概念链接 {href_}.html#{cid}：那一页没有这个概念块")
    for ol in re.findall(r'<ol class="argue">(.*?)</ol>', t, flags=re.S):
        steps = re.findall(r"<li>(.*?)</li>", ol, flags=re.S)
        if not 2 <= len(steps) <= 6: errs.append(f"论证步骤应有 2–6 步，现在 {len(steps)} 步")
        for s in steps:
            if han(s) > 90: errs.append(f"论证步骤「{plain(s)[:12]}…」{han(s)} 个汉字，超过 90")
            if not re.search(r'<span class="sec">(§\d+|序言)[^<]*</span>', s): errs.append(f"论证步骤「{plain(s)[:12]}…」后面要标依据 <span class=\"sec\">§k 第 n 段</span>")
    if '<ol class="argue">' in t and '<ol class="argue">' not in cp: errs.append("论证步骤只放在「先用中文过一遍：这一页的经济学」里")
    vws = re.findall(r'<div class="views"><h4>(.*?)</h4>\s*<p><b>主流看法：</b>(.*?)</p>\s*<p><b>作者的看法：</b>(.*?)</p>\s*<p class="ours"><b>本站的评论：</b>(.*?)</p></div>', cp, flags=re.S)
    if t.count('<div class="views">') != len(vws): errs.append("「主流看法 / 作者的看法 / 本站的评论」的写法不对，照 AUTHORING.md 第 6 节，且只放在经济学一节里")
    if "views" in need_opt and not vws: errs.append("这一页要有至少一块 <div class=\"views\">（主流看法 / 作者的看法 / 本站的评论）")
    for h4, a, b, c_ in vws:
        if han(a + b + c_) > 320: errs.append(f"看法块「{plain(h4)[:14]}」{han(a + b + c_)} 个汉字，超过 320")
        if re.search(r"另一本书|他的专著|The State against Blacks 里", c_): errs.append(f"看法块「{plain(h4)[:14]}」：不要让读者去看他别的书")

    # 书里的剪报和文件：每张文件图一块
    iq = part("书里的剪报和文件")
    by_img = {v[0]: (p, v[2]) for p, v in docs.items()}
    qblocks = re.findall(r'<div class="imgq" data-img="([\d ]+)">(.*?)</div>\s*(?=<div class|<h2>|<figure|$)', iq, flags=re.S)
    got = [i for b in qblocks for i in b[0].split()]
    if iq.count('<div class="imgq"') != len(qblocks): errs.append("剪报和文件的写法不对：<div class=\"imgq\" data-img=\"图号 图号…\"><h4>…</h4><p class=\"where\">…</p><p class=\"gq\"><b>大意：</b>…</p></div>")
    for i in sorted(set(by_img) - set(got)): errs.append(f"剪报和文件：第 {by_img[i][0]} 段的图 {i} 没有落在任何一块里")
    for i in sorted(set(got) - set(by_img)): errs.append(f"剪报和文件：这一页没有图 {i}（照片不用写）")
    for i in sorted({i for i in got if got.count(i) > 1}): errs.append(f"剪报和文件：图 {i} 出现在两块里")
    if got != sorted(got, key=lambda i: by_img.get(i, (0,))[0]): errs.append("剪报和文件：块按段号排，data-img 里的图号也按段号排")
    for ids, body in qblocks:
        ids = [i for i in ids.split() if i in by_img]
        if not ids: continue
        name = "图 " + "、".join(ids)
        p = by_img[ids[0]][0]
        if not re.search(r'<h4><span class="sec">(§\d+|序言)</span>第 ' + str(p) + r'(–\d+)? 段', body): errs.append(f"{name}：<h4> 要以 <span class=\"sec\">§k</span>第 {p} 段（或第 {p}–n 段）开头")
        if '<p class="where">' not in body: errs.append(f"{name}：要有 <p class=\"where\">（在屏幕上哪里）")
        gq = re.findall(r'<p class="gq"><b>大意：</b>(.*?)</p>', body, flags=re.S)
        if len(gq) != 1: errs.append(f"{name}：要有一句 <p class=\"gq\"><b>大意：</b>…</p>")
        elif han(gq[0]) > 160: errs.append(f"{name}：大意 {han(gq[0])} 个汉字，超过 160")
    for i, k in re.findall(r'<div class="loc" data-img="(\d+)">第 (\d+) 行</div>', t):
        if i not in by_img: errs.append(f"图里的词条指向了这一页没有的文件图 {i}")
        elif not 1 <= int(k) <= len(by_img[i][1]): errs.append(f"图里的词条：图 {i} 的转写只有 {len(by_img[i][1])} 行，没有第 {k} 行")
    img_entries = re.findall(r'<div class="entry(?: trap)? img">.*?</div></div>', t)
    if len(img_entries) != len(re.findall(r'data-img="\d+">第 \d+ 行', t)): errs.append("图里的词条写成 <div class=\"entry img\">…<div class=\"loc\" data-img=\"图号\">第 k 行</div>…</div>")
    if img_entries and t.find(img_entries[0]) < t.find("<h2>书里的剪报和文件</h2>"): errs.append("图里的词条放在「书里的剪报和文件」里，紧跟它那张图")

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
    errs += check_entries(ws_entries, paras, per_k=8, max_n=70, trap_ratio=1 / 3, scope="这一页")
    for loc in re.findall(r'<div class="loc" data-p="\d+">(.*?)</div>', t):
        if re.search(r'[“”"]', loc): errs.append(f".loc 不能含引号（读者的电子书是直引号，页面只能写弯引号，搜不到）：{loc!r}")
    for p, loc in ocr:
        s = norm(plain(loc)).strip("… ").strip()
        if s not in paras.get(int(p), ""): errs.append(f"扫描错字表：{s!r} 不在第 {p} 段")

    # 和 Sowell 的书对照
    sw = part("和 Sowell 的书对照")
    if sw:
        scards = re.findall(r'<div class="sowell">(.*?)</dl>(.*?)</div>', sw, flags=re.S)
        if not scards or len(scards) != sw.count('<div class="sowell">'): errs.append("「和 Sowell 的书对照」写法：<div class=\"sowell\"><h4>…</h4><dl><dt>这本书</dt><dd>…</dd><dt>Odyssey</dt><dd>… <a class=\"go\" href=\"/odyssey/chapters/09a.html#…\">…</a></dd></dl>（两边说法不同时加 <p class=\"diff\"><b>两边不一样：</b>…</p>）</div>")
        for body, after in scards:
            h4 = plain(re.search(r"<h4>(.*?)</h4>", body, flags=re.S).group(1)) if "<h4>" in body else "?"
            if "<dt>这本书</dt>" not in body: errs.append(f"Sowell 对照「{h4}」：要有 <dt>这本书</dt>")
            links = re.findall(r'<a class="go" href="/(odyssey|letters)/chapters/(\w+)\.html(?:#([\w-]+))?">', body)
            if not links: errs.append(f"Sowell 对照「{h4}」：要有链到老站页面的 <a class=\"go\" href=\"/odyssey/chapters/….html\">")
            for site, pg, anc in links:
                f = os.path.join(SISTER[site], "chapters", pg + ".html")
                if not os.path.exists(f): errs.append(f"Sowell 对照「{h4}」：/{site}/chapters/{pg}.html 不存在"); continue
                if anc and not re.search(r'id="' + re.escape(anc) + '"', open(f, encoding="utf-8").read()): errs.append(f"Sowell 对照「{h4}」：{pg}.html 里没有 id=\"{anc}\"")
            if han(body) > 300: errs.append(f"Sowell 对照「{h4}」：{han(body)} 个汉字，超过 300")

    # 对照今天
    td = part("对照今天")
    if td:
        if '<ul class="verdicts">' not in td: errs.append("「对照今天」开头要有结论图例 <ul class=\"verdicts\">（照样板抄）")
        tcs = re.findall(r'<div class="today" data-verdict="([^"]+)"><h4>(.*?)</h4><dl>(.*?)</dl></div>', td, flags=re.S)
        if not 1 <= len(tcs) <= 4 or len(tcs) != td.count('<div class="today"'): errs.append(f"「对照今天」应有 1–4 张卡片，写法 <div class=\"today\" data-verdict=\"成立\"><h4>书里的说法：…</h4><dl>…</dl></div>，现在认出 {len(tcs)} 张")
        for v, h4, dl in tcs:
            name = plain(h4)[:16]
            if v not in VERDICTS: errs.append(f"对照今天「{name}」：结论只能是 {'、'.join(sorted(VERDICTS))}，不是 {v}")
            if not h4.startswith("书里的说法："): errs.append(f"对照今天「{name}」：<h4> 以「书里的说法：」开头，写清结论判的是哪句话")
            dts = re.findall(r"<dt>(.*?)</dt>", dl)
            if [d[:2] for d in dts][:3] != ["书里", "当时", "今天"]: errs.append(f"对照今天「{name}」：<dt> 依次是 书里 / 当时（年份）/ 今天，可再加「另一边」")
            if not re.search(r'<span class="asof">核对于 20\d\d-\d\d', dl): errs.append(f"对照今天「{name}」：「今天」里要有 <span class=\"asof\">核对于 2026-10。依据：…</span>")
            if han(dl) > 420: errs.append(f"对照今天「{name}」：{han(dl)} 个汉字，超过 420")

    # 引用块：不超过 2 处，只引作者自己的话
    errs += check_quotes(t, 2)
    for q in re.findall(r'<blockquote class="quote">(.*?)<cite>', t, flags=re.S):
        s = norm(plain(q)).strip("… ").strip()
        where = [p for p, v in paras.items() if s.replace("…", "") and all(x.strip() in v for x in s.split("…") if x.strip())]
        if not where: errs.append(f"引用块在这一页的原文里找不到（要一字不差，省略处用 …；不能引图片里的字）：{s[:50]!r}")
        elif all(p in quoted for p in where): errs.append(f"引用块引的是 {{Q}} 段落（别人的话），只引作者自己写的：{s[:50]!r}")
        if len(s.replace("…", " ").split()) > 25: errs.append(f"引用块超过 25 个词：{s[:50]!r}")

    # 检查一下理解：5–7 题、一句话
    ck = part("检查一下理解")
    if f'data-key="{pid}-oneline"' not in ck: errs.append(f"「检查一下理解」最后要有 <textarea class=\"note\" data-key=\"{pid}-oneline\">")

    # 读完想一想：2–3 个问题，各有笔记框
    pd = part("读完想一想")
    pz = re.findall(r'<div class="ponder"><p>(.*?)</p>(.*?)<textarea class="note" data-key="' + pid + r'-ponder-(\d)"></textarea></div>', pd, flags=re.S)
    if not 2 <= len(pz) <= 3 or len(pz) != pd.count('<div class="ponder">'): errs.append(f"「读完想一想」应有 2–3 个 <div class=\"ponder\"><p>问题</p>（可选 <details class=\"sides\">…</details>）<textarea class=\"note\" data-key=\"{pid}-ponder-N\"></textarea></div>，现在认出 {len(pz)} 个")
    for q, mid, n in pz:
        if han(q) > 90: errs.append(f"想一想 {n}：问题 {han(q)} 个汉字，超过 90")
        if han(mid) > 260: errs.append(f"想一想 {n}：「几种看法」{han(mid)} 个汉字，超过 260")
    for k in re.findall(r'class="note" data-key="([^"]+)"', t):
        if not k.startswith(f"{pid}-"): errs.append(f"笔记的 data-key 要以 {pid}- 开头：{k}")

    # 精彩回顾
    rc = part("精彩回顾")
    if '<p class="recall-line">' not in rc: errs.append("「精彩回顾」要有 <p class=\"recall-line\"><b>一句话：</b>…</p>")
    items_r = re.findall(r'<div class="item"><b>(.*?)</b><p>(.*?)</p><span class="sec">([^<]+)</span></div>', rc, flags=re.S)
    if not 4 <= len(items_r) <= 6 or len(items_r) != rc.count('<div class="item">'): errs.append(f"「精彩回顾」应有 4–6 张卡片，写法 <div class=\"item\"><b>标题</b><p>…</p><span class=\"sec\">§k</span></div>，现在认出 {len(items_r)} 张")
    for b_, p_, _ in items_r:
        if han(p_) > 100: errs.append(f"「精彩回顾」{b_}：{han(p_)} 个汉字，超过 100")

    # 节号不能写到这一页以外
    for k in sorted({int(k) for k in re.findall(r'class="sec">§(\d+)', t)} - set(want)):
        errs.append(f"页面上标了 §{k}，这一页只有 {want}")
    if "序言" in re.findall(r'class="sec">(序言)', t) and 0 not in want: errs.append("这一页没有序言")

    errs += check_images(t, path, min_photos=3, min_svgs=1, pattern=r"\.\./assets/img/\d\d[a-d]?-[a-z0-9-]+\.jpg")
    c = counts(t)
    if not 5 <= c["检查题"] <= 7: errs.append(f"理解检查应有 5–7 题，现在 {c['检查题']} 题")
    errs += check_markup(t)
    total = sum(s[3] for s in secs)
    print(("✗" if errs else "✓"), path, " ".join(f"{k} {v}" for k, v in c.items()),
          f"图里词条 {len(img_entries)} 概念 {len(blocks)} 文件 {len(qblocks)}/{len(docs)} 地图 {len(items)} 人 {len(cards)} 回顾 {len(items_r)} 原文 {total} 词")
    for e in errs: print("    " + e)
    bad += bool(errs)
sys.exit(1 if bad else 0)
