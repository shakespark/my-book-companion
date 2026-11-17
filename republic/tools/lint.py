#!/usr/bin/env python3
"""页面结构检查：python3 -I tools/lint.py chapters/01a.html …（不给参数就查页表里的每一页）
页 id → 卷、节的范围从 assets/chapters.js 的 RP_PAGES 读；全文块交给 tools/gen_text.py 核对（指纹对不上就是过期，要重跑）。
照 Thinking in Systems 导读的 lint.py 改：去掉了分节地图、英文词条、译本勘误、模拟器、情境题、理解检查和「今天」栏的出版年规则；
加了全文块（TEXT 标记之间，所有文字规则都跳过它）、人物卡、背景卡、论证路线、链到全文的节号（a.at）、译名表里定了不用的译法。
查：小节标题、顺序和 id、读之前三节、论证路线（每步的类别、说话人、节号链接、字数）、概念、今天怎么看（四档结论、图例、谁说的）、本站怎么看、
精彩回顾、节号链接（要在这一页的范围里，文字和链接对得上）、图片、写死的颜色、直引号、原书材料的路径、译名。
没写的小节（还留着 p.wip 或「写作占位」注释）报「未写」；只剩「未写」时那一行开头是 ○，写完全部才是 ✓。
另报「嫌疑」（？开头，不算不通过，作者在报告里逐条答）：相对位置词、卡片标题两句并列、「是一回事 / 同一件事」这类等同词、
「没给出处 / 没点名」（先查 Shorey 脚注）、今天怎么看的出处没写年份、「美德」（译名表定的是德性）。
00 是主编页，不走这里，只跑 check。通用的几项在 ~/tutorials-deploy/scripts/lint_common.py。"""
import html, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.expanduser("~/tutorials-deploy/scripts"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lint_common import check_images, check_markup, page_text
import gen_text as G

SECS = [("argue", "读之前：这一段在争什么"), ("people", "读之前：出场的人"), ("background", "读之前：需要的背景"), ("fulltext", "全文"),
        ("route", "读完：论证路线"), ("concepts", "读完：概念"), ("today", "今天怎么看"), ("views", "本站怎么看"), ("recap", "精彩回顾")]
KINDS = ["主张", "问", "认", "推出", "反驳", "插话"]
VERDICTS = ["站得住", "部分站得住", "多数不买账", "有争议"]
BANNED = {r"非正义": "不正义", r"(?<!正)不义": "不正义", r"暴君": "僭主", r"特拉西马库斯|色拉叙马库斯|塞拉西马柯|忒拉叙马科斯": "色拉叙马霍斯",
          r"克法卢斯|刻法洛斯|克法罗斯": "克法洛斯", r"玻勒马库斯|波勒马库斯|波勒马霍斯|珀勒马科斯": "玻勒马霍斯", r"阿得曼托斯|阿第曼图": "阿德曼托斯",
          r"西蒙尼德(?!斯)": "西蒙尼德斯", r"比雷埃夫斯港口|庇里尤斯|比雷埃斯": "比雷埃夫斯"}
han = lambda s: len(re.findall(r"[一-鿿]", re.sub(r"<[^>]+>", "", s)))
plain = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
GLOSS = open(os.path.join(ROOT, "GLOSSARY.md"), encoding="utf-8").read()
NAMES = set(re.findall(r"[一-鿿]+(?:·[一-鿿]+)*", GLOSS))  # 整份译名表里的中文词，各卷后补的人名都算
PAGES = G.pages()
SECLIST = {}


def secs_of(pid):
    if pid not in SECLIST: SECLIST[pid] = G.page_secs(pid)[1]
    return SECLIST[pid]


def two_clauses(s):
    return re.search(r"[^，；。]{4,}[，；][^，；。]{4,}", s)


bad = 0
paths = sys.argv[1:] or [os.path.join(ROOT, f"chapters/{p}.html") for p in PAGES]
for path in paths:
    t = open(path, encoding="utf-8").read(); errs, todo, sus = [], [], []
    pid = re.search(r"(\w+)\.html$", path).group(1)
    if pid not in PAGES: print(f"✗ {path}  chapters.js 的 RP_PAGES 里没有页 {pid}（00 是主编页，不跑 lint）"); bad += 1; continue
    want = secs_of(pid); wset = set(want)
    if f'<body data-page="{pid}">' not in t: errs.append(f'<body> 应写成 <body data-page="{pid}">')

    # 全文块：有、在「全文」一节里、是最新的
    blk = G.page_block(t) or ""
    if not blk: errs.append("没有全文块（<!-- TEXT:BEGIN --> … <!-- TEXT:END -->），跑 python3 -I tools/gen_text.py " + pid)
    else:
        m = re.search(r'data-src="(\w+)"', blk)
        if not m or m.group(1) != G.fingerprint(pid): errs.append(f"全文块过期（译文、路标或 Shorey 改过）：重跑 python3 -I tools/gen_text.py {pid}")
    raw = t.replace(blk, "") if blk else t
    bare = re.sub(r"<!--.*?-->", "", raw, flags=re.S)          # 页壳里注释中的写法示例不算页面内容
    nzh = re.search(r'data-zh="(\d)"', blk); nzh = nzh and nzh.group(1) == "1"
    nnote, nmark = blk.count('class="fn-t"'), blk.count('<aside class="mark"')

    # 小节标题、id 和顺序
    hs = re.findall(r'<h2(?: id="([^"]*)")?>(.*?)</h2>', bare)
    if [x[1] for x in hs] != [s[1] for s in SECS]:
        errs.append("小节标题和顺序应为：" + " → ".join(s[1] for s in SECS) + f"（现在：{' → '.join(x[1] for x in hs)}；标题一个字都不能改）")
    for hid, name in hs:
        d = dict((b, a) for a, b in SECS)
        if name in d and hid != d[name]: errs.append(f"<h2>{name}</h2> 的 id 应为 {d[name]}（页头的跳转靠它）")
    def part(name, src=None):
        src = bare if src is None else src
        m = re.search(r"<h2[^>]*>" + re.escape(name) + r"</h2>", src)
        if not m: return ""
        j = src.find("<h2", m.end())
        return src[m.start():j if j > 0 else len(src)]
    if blk:
        i, b0 = t.find("<h2 id=\"fulltext\">全文</h2>"), t.find(G.BEGIN)
        j = t.find("<h2", i + 4)
        if not (0 <= i < b0 and (j < 0 or b0 < j)): errs.append("全文块要放在「全文」一节里")
    written = {}
    for _, name in SECS:
        if name == "全文": continue
        p = part(name, raw)
        w = not ('class="wip"' in p or "写作占位" in p)
        written[name] = w
        if not w: todo.append(f"未写：{name}")
    for bad_cls, what in (("entry", "英文词条"), ("zherr", "译本勘误"), ("gate", "读前 / 读后的分界线"), ("secmap", "分节地图"), ("drill", "情境题")):
        if f'class="{bad_cls}' in bare: errs.append(f"这本书没有{what}（class=\"{bad_cls}\"）")

    # 读之前
    if written["读之前：这一段在争什么"]:
        g = re.findall(r'<div class="gist">(.*?)</div>', part("读之前：这一段在争什么"), flags=re.S)
        if len(g) != 1: errs.append("「这一段在争什么」写成一个 <div class=\"gist\"><p>…</p></div>")
        elif han(g[0]) > 200: errs.append(f"「这一段在争什么」{han(g[0])} 个汉字，超过 200")
    if written["读之前：出场的人"]:
        pp = part("读之前：出场的人")
        cards = re.findall(r'<div class="person" id="([^"]+)"><h3>(.*?)</h3>(.*?)</div>', pp, flags=re.S)
        if not cards or len(cards) != pp.count('class="person"') or '<div class="people">' not in pp:
            errs.append("人物卡的写法：<div class=\"people\"><div class=\"person\" id=\"p-英文名\"><h3>中文名 <span class=\"en\">English</span></h3><p class=\"role\">身份</p><p>…</p></div>…</div>")
        for cid, h3, body in cards:
            name = plain(re.sub(r'<span class="en">.*?</span>', "", h3))
            if not re.fullmatch(r"p-[a-z0-9-]+", cid): errs.append(f"人物卡 id 写成 p- 加小写英文：{cid}")
            if '<span class="en">' not in h3: errs.append(f"人物卡「{name}」：h3 里要有 <span class=\"en\">英文名</span>")
            en = re.search(r'<span class="en">\s*(.)', h3)
            if en and en.group(1).isupper() and not all(n.strip() in NAMES for n in name.split("、")): sus.append(f"人物卡「{name}」：不在 GLOSSARY.md 的人名里；新译名写进报告的「新译名」，主编并进去")
            role = re.findall(r'<p class="role">(.*?)</p>', body, flags=re.S)
            if len(role) != 1: errs.append(f"人物卡「{name}」：要有一句 <p class=\"role\">身份</p>")
            elif han(role[0]) > 30: errs.append(f"人物卡「{name}」：身份 {han(role[0])} 个汉字，超过 30")
            if han(re.sub(r'<p class="role">.*?</p>', "", body, flags=re.S)) > 150: errs.append(f"人物卡「{name}」：正文超过 150 个汉字")
    if written["读之前：需要的背景"]:
        pb = part("读之前：需要的背景")
        cards = re.findall(r'<div class="bg" id="([^"]+)"><h3>(.*?)</h3>(.*?)</div>', pb, flags=re.S)
        if not cards or len(cards) != pb.count('class="bg"'): errs.append("背景卡的写法：<div class=\"bg\" id=\"b-英文名\"><h3>名字</h3><p>…</p>（可加 <p class=\"see\">节号链接</p>）</div>")
        for cid, h3, body in cards:
            if not re.fullmatch(r"b-[a-z0-9-]+", cid): errs.append(f"背景卡 id 写成 b- 加小写英文：{cid}")
            if han(re.sub(r'<p class="see">.*?</p>', "", body, flags=re.S)) > 200: errs.append(f"背景卡「{plain(h3)[:12]}」超过 200 个汉字")

    # 读完：论证路线
    rt = part("读完：论证路线")
    if written["读完：论证路线"]:
        steps = re.findall(r'<li data-kind="([^"]*)">(.*?)</li>', "".join(re.findall(r'<ol class="route">(.*?)</ol>', rt, flags=re.S)), flags=re.S)
        if not 6 <= len(steps) <= 24: errs.append(f"论证路线应有 6–24 步（写成 <ol class=\"route\"><li data-kind=\"主张\">…</li>…</ol>），现在认出 {len(steps)} 步")
        if len(steps) != len(re.findall(r"<li[\s>]", rt)): errs.append("论证路线里每个 <li> 都要写成 <li data-kind=\"…\">，放在 <ol class=\"route\"> 里")
        for k, body in steps:
            name = plain(body)[:16]
            if k not in KINDS: errs.append(f"论证路线「{name}」：data-kind 六选一：{' / '.join(KINDS)}")
            if k not in ("推出", "反驳") and '<span class="spk">' not in body: errs.append(f"论证路线「{name}」：{k}要写是谁，<span class=\"spk\">人名</span>")
            if '<a class="at"' not in body: errs.append(f"论证路线「{name}」：每步要链回全文，<a class=\"at\" href=\"#s327a\">327a</a>")
            if han(re.sub(r'<a class="at".*?</a>|<span class="spk">.*?</span>', "", body)) > 80: errs.append(f"论证路线「{name}」：超过 80 个汉字")

    # 读完：概念
    if written["读完：概念"]:
        pc = part("读完：概念")
        blocks = re.findall(r'<div class="concept" id="([^"]+)">\s*<h3>(.*?)</h3>(.*?)</div>', pc, flags=re.S)
        if not 1 <= len(blocks) <= 5 or len(blocks) != pc.count('class="concept"'): errs.append(f"概念应有 1–5 块，写法 <div class=\"concept\" id=\"c-英文\"><h3>中文 <span class=\"en\">转写 · English</span></h3><p>…</p></div>，现在认出 {len(blocks)} 块")
        for cid, h3, body in blocks:
            if not re.fullmatch(r"c-[a-z0-9-]+", cid): errs.append(f"概念 id 写成 c- 加小写英文：{cid}")
            if han(body) > 300: errs.append(f"概念「{plain(h3)[:10]}」{han(body)} 个汉字，超过 300")

    # 今天怎么看
    td = part("今天怎么看")
    if written["今天怎么看"]:
        tcs = re.findall(r'<div class="today" data-verdict="([^"]*)"><h4>(.*?)</h4>(.*?)</div>', td, flags=re.S)
        if '<ul class="verdicts">' not in td: errs.append("「今天怎么看」要照抄页壳里的结论图例 <ul class=\"verdicts\">")
        if not 2 <= len(tcs) <= 4 or len(tcs) != td.count('class="today"'): errs.append(f"「今天怎么看」应有 2–4 张卡，写法 <div class=\"today\" data-verdict=\"有争议\"><h4>…</h4><p>…</p><p class=\"src\">谁说的：…</p></div>，现在认出 {len(tcs)} 张")
        for v, h4, body in tcs:
            name = plain(h4)[:16]
            if v not in VERDICTS: errs.append(f"今天怎么看「{name}」：结论四选一：{' / '.join(VERDICTS)}")
            src = re.findall(r'<p class="src">(.*?)</p>', body, flags=re.S)
            if len(src) != 1: errs.append(f"今天怎么看「{name}」：最后要有一句 <p class=\"src\">谁说的：人名、著作、年份</p>")
            elif not re.search(r"(?<!\d)(1\d\d\d|20[0-2]\d)(?!\d)|前\s*\d+\s*年|\d+\s*(年|世纪)", src[0]): sus.append(f"今天怎么看「{name}」：出处没写年份，学界的看法要能找到是谁、哪一年说的")
            if han(body) > 300: errs.append(f"今天怎么看「{name}」：{han(body)} 个汉字，超过 300")
            if two_clauses(plain(h4).split("：", 1)[-1]): sus.append(f"今天怎么看「{name}」：标题像两句并列，结论只能判一句；收窄成一句")
    if bare.count('class="today"') != td.count('class="today"'): errs.append("今天怎么看的卡片只放在「今天怎么看」里")

    # 本站怎么看
    vw = part("本站怎么看")
    if written["本站怎么看"]:
        vws = re.findall(r'<div class="views"><h4>(.*?)</h4>(.*?)</div>', vw, flags=re.S)
        if not 1 <= len(vws) <= 3 or len(vws) != vw.count('class="views"'): errs.append(f"「本站怎么看」应有 1–3 块，写法 <div class=\"views\"><h4>问题</h4><p>…</p></div>，现在认出 {len(vws)} 块")
        for h4, body in vws:
            if han(body) > 400: errs.append(f"看法块「{plain(h4)[:14]}」{han(body)} 个汉字，超过 400")
            if two_clauses(plain(h4)): sus.append(f"看法块「{plain(h4)[:14]}」：标题像两句并列，收窄成一个问题")
        vd = re.findall(r'<p class="verdict"><b>本站的总体看法：</b>(.*?)</p>', vw, flags=re.S)
        if len(vd) != 1: errs.append("「本站怎么看」最后要有一句 <p class=\"verdict\"><b>本站的总体看法：</b>…</p>")
        elif han(vd[0]) > 160: errs.append(f"「本站的总体看法」{han(vd[0])} 个汉字，超过 160")

    # 精彩回顾
    rc = part("精彩回顾")
    if written["精彩回顾"]:
        if '<p class="recall-line"><b>一句话：</b>' not in rc: errs.append("「精彩回顾」要有 <p class=\"recall-line\"><b>一句话：</b>…</p>")
        items = re.findall(r'<div class="item"><b>(.*?)</b><p>(.*?)</p><a class="at" href="#s\w+">[^<]+</a></div>', rc, flags=re.S)
        if not 4 <= len(items) <= 6 or len(items) != rc.count('<div class="item">'): errs.append(f"「精彩回顾」应有 4–6 张卡，写法 <div class=\"item\"><b>标题</b><p>…</p><a class=\"at\" href=\"#s327a\">327a</a></div>，现在认出 {len(items)} 张")
        for b_, p_ in items:
            if han(p_) > 100: errs.append(f"「精彩回顾」{plain(b_)[:12]}：{han(p_)} 个汉字，超过 100")
            if two_clauses(plain(b_)): sus.append(f"「精彩回顾」{plain(b_)[:12]}：标题像两句并列，收窄成一句")

    # 节号链接：要在这一页（或那一页）的范围里；a.at 的文字是节号或「起–止」，起点和 href 一致
    for m in re.finditer(r'<a class="at" href="([^"]*)">(.*?)</a>', bare):
        hr, lab = m.group(1), plain(m.group(2))
        mm = re.fullmatch(r"(?:(\w+)\.html)?#s(\d{3}[a-e])", hr)
        if not mm: errs.append(f"a.at 的链接写成 #s327a（这一页）或 01b.html#s332a（别的页）：{hr}"); continue
        tp, s = mm.group(1) or pid, mm.group(2)
        if tp not in PAGES: errs.append(f"a.at 链到了没有的页：{hr}"); continue
        rng = secs_of(tp)
        if s not in rng: errs.append(f"a.at 链到的 {s} 不在页 {tp}（{rng[0]}–{rng[-1]}）里")
        lm = re.fullmatch(r"(\d{3}[a-e])(?:–(\d{3}[a-e]))?", lab)
        if not lm or lm.group(1) != s: errs.append(f"a.at 的文字要是节号或「起–止」，起点和链接一致：{lab} → {hr}")
        elif lm.group(2) and (lm.group(2) not in rng or rng.index(lm.group(2)) <= rng.index(s)): errs.append(f"a.at 的范围 {lab} 不对（止要在起之后、在页 {tp} 里）")
    ids = set(re.findall(r'\bid="([^"]+)"', t))
    for hr in re.findall(r'href="#([^"]+)"', bare):
        if hr not in ids: errs.append(f"页内链接 #{hr} 在这一页找不到")

    # 通用：图片、标记；译名
    errs += check_images(bare, path, pattern=r"\.\./assets/img/\d\d[a-z]?-[a-z0-9-]+\.jpg")
    errs += check_markup(bare)
    txt = page_text(bare)
    for pat, right in BANNED.items():
        for x in sorted(set(re.findall(pat, txt))): errs.append(f"「{x}」：译名表定的是「{right}」")

    # 嫌疑（只提示，不算不通过；作者在报告里逐条答：改了，或者为什么不改）
    for m in re.finditer(r"上一节|下一节|上一页说|前面说过|前面讲过|前文|上文|下文|后面会讲|开头那段|末尾那段|这一段开头|这段末尾", txt):
        sus.append(f"相对位置词「{m.group(0)}」：指路用斯特方码链接（a.at）或小节名")
    for m in re.finditer(r"是一回事|是同一回事|同一件事|是同一个东西|等同于|就等于", txt):
        sus.append(f"等同词「{m.group(0)}」：书里真的说两件事相同吗？多半是「相关 / 相似」，回原文看一眼")
    for m in re.finditer(r"没(?:有)?(?:给|注明|交代)(?:出)?(?:处|来源)|没(?:有)?点名|没说是谁|未注明出处", txt):
        sus.append(f"「{m.group(0)}」：先查 Shorey 的脚注（阅读包里的 notes-{pid}.txt），他常常注了出处")
    if "美德" in txt: sus.append("「美德」：译名表里 ἀρετή 定的是「德性」；说日常意义的美德可以不改，在报告里说明")

    routes = len(re.findall(r'<li data-kind=', rt))
    head = (f"全文 {len(want)} 节（" + ("中文" if nzh else "只有英文") + f"，注 {nnote}，路标 {nmark}）"
            + f" 人物 {bare.count('class=\"person\"')} 背景 {bare.count('class=\"bg\"')} 路线 {routes} 步 概念 {bare.count('class=\"concept\"')}"
            + f" 今天 {td.count('class=\"today\"')} 看法 {vw.count('class=\"views\"')} 回顾 {rc.count('<div class=\"item\">')}"
            + f" 照片 {len(set(re.findall(r'<img[^>]+src=', bare)))} SVG {len(re.findall(r'<svg', bare))}")
    mark = "✗" if errs else "○" if todo else "✓"
    print(mark, os.path.relpath(path, os.getcwd()) if os.path.isabs(path) else path, head)
    for e in errs + todo: print("    " + e)
    for e in sus: print("    ？" + e)
    bad += bool(errs or todo)
sys.exit(1 if bad else 0)
