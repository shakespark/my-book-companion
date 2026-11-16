#!/usr/bin/env python3
"""全文块生成：把一页的英中对照全文写进章节页的 <!-- TEXT:BEGIN --> … <!-- TEXT:END --> 之间（重跑覆盖，不手改那一段）。

用法（在 republic/ 下或任何地方都行）：
  python3 -I tools/gen_text.py <页>…              生成并写进 chapters/<页>.html；顺手更新 assets/chapters.js 里这一页的 n、w、zw
  python3 -I tools/gen_text.py --all              页表里的每一页
  python3 -I tools/gen_text.py --en-only <页>     不读译文，只出英文（译文写到一半时先看排版）
  python3 -I tools/gen_text.py --zh 文件 --out 文件 <页>    测试：用别处的译文、写到别处的页面文件（不动 chapters.js）
  python3 -I tools/gen_text.py --check <页>…      只核对页面里的全文块是不是最新的（输入的指纹对不对得上），不写
  python3 -I tools/gen_text.py --slice <页> <目录>    给 pack.sh：切出这一页的 Shorey 正文和 Shorey 脚注，写 <目录>/shorey-<页>.txt、notes-<页>.txt

输入：
  assets/chapters.js            页表：页 → 卷号、第一节、最后一节
  source/text/index.tsv         斯特方节的顺序
  source/text/NN.txt            Shorey 正文（[327a] 节标记在行中间、空行分段、> 开头是诗行、[^n] 脚注记号、[cit. …] 是 Perseus 加的出处）
  source/text/notes/NN.txt      Shorey 脚注，一行一条：[^n] (节号) 注文
  text/zh/<页>.txt              中文译文，格式见 TRANSLATE.md：[327a] 独占一行；节内一行一个说话轮次；空行分段；> 开头是诗行；
                                末尾「## 注」之后一行一条 [^n] / [^zN] 注文
  text/marks/<页>.txt           论证路标（导读作者写，可以没有）：一行一条「节号 | 文字」，插在那一节前面；# 开头是注释

输出的显示规则：Shorey 正文里没被译者选中的 [^n] 和 [cit. …] 不显示；选中的注在中英两边都显示同一个小号数字，按中文里出现的顺序编号；
诗行排成诗。核对：中文的节标记和页表的节一一对上（不多不少、顺序一样、没有空节），注的记号和「## 注」的条目一一对上，
[^n] 要是这一页 Shorey 正文里有的脚注。对不上就把问题全列出来、退出码 1，不写页面。正常时只打印一行。
"""
import hashlib, html, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
VERSION = "1"                      # 改了输出格式就加一，旧页面的指纹随之过期
BEGIN, END = "<!-- TEXT:BEGIN", "<!-- TEXT:END -->"
SEC = re.compile(r"\[(\d{3}[a-e])\]")
CREDIT = (
    '<p class="ft-credit" id="ft-credit"><b>底本和许可：</b>英译是 Paul Shorey 译本（Loeb 古典丛书，1930 / 1935），'
    '译文对照用的希腊文是 John Burnet 校订本（页面上不显示），都取自 '
    '<a href="https://www.perseus.tufts.edu/" rel="noopener">Perseus Digital Library</a> 的电子版'
    '（源文件在 <a href="https://github.com/PerseusDL/canonical-greekLit" rel="noopener">PerseusDL/canonical-greekLit</a>），'
    '按 <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.zh-hans" rel="noopener">CC BY-SA 4.0</a> 使用。'
    '本站的改动：按斯特方节分块，去掉 Perseus 加的出处标注，Shorey 的脚注只选了一部分、改写成中文注。'
    '中文是本站新译：以 Shorey 英译为底本，对过 Jowett 英译（1892，公版）和希腊文，不是从希腊文直译的学术译本；'
    '中文译文同样按 CC BY-SA 4.0 放出。</p>')
HOW = (
    '<p class="ft-how">中文是本站的新译，英文是 Shorey 的译本。每块开头的 <b>327a</b> 这种号码是斯特方码：'
    '1578 年 Stephanus 印的柏拉图全集的页码加栏位 a–e，各种译本都标它，找同一句话靠它；点它得到这一节的链接。'
    '小号数字是注，点一下打开。标着「导读」的浅色窄条是本站加的路标，不是柏拉图的话。</p>')


class Bad(Exception):
    pass


def rd(p):
    return open(p, encoding="utf-8").read()


def pages():
    js = rd(os.path.join(ROOT, "assets/chapters.js"))
    out = {}
    for m in re.finditer(r'\{ id: "(\w+)", book: (\d+), from: "(\w+)", to: "(\w+)"', js):
        out[m.group(1)] = (int(m.group(2)), m.group(3), m.group(4))
    return out


def order(book):
    rows = [l.split("\t") for l in rd(os.path.join(ROOT, "source/text/index.tsv")).splitlines()[1:]]
    return [r[1] for r in rows if r[0] == str(book)]


def page_secs(pid):
    pg = pages()
    if pid not in pg:
        raise Bad(f"assets/chapters.js 的 RP_PAGES 里没有页 {pid}")
    book, a, b = pg[pid]
    o = order(book)
    if a not in o or b not in o:
        raise Bad(f"页 {pid} 的范围 {a}–{b} 不在第 {book} 卷的节表里")
    return book, o[o.index(a):o.index(b) + 1]


def shorey(book, secs):
    """{节号: 原始文字}，节号是 secs 里的；一节从它的标记到下一个标记（可能跨段）。"""
    t = rd(os.path.join(ROOT, f"source/text/{book:02d}.txt"))
    ms = list(SEC.finditer(t))
    out = {}
    for i, m in enumerate(ms):
        if m.group(1) in secs:
            out[m.group(1)] = t[m.end():ms[i + 1].start() if i + 1 < len(ms) else len(t)].strip(" ")
    miss = [s for s in secs if s not in out]
    if miss:
        raise Bad(f"Shorey 正文里找不到这些节：{' '.join(miss)}")
    return out


def shorey_notes(book, secs):
    out = {}
    for l in rd(os.path.join(ROOT, f"source/text/notes/{book:02d}.txt")).splitlines():
        m = re.match(r"\[\^(\d+)\] \((\d{3}[a-e])\) (.*)$", l)
        if m and m.group(2) in secs:
            out[m.group(1)] = l
    return out


def zh_path(pid):
    return os.path.join(ROOT, f"text/zh/{pid}.txt")


def marks_path(pid):
    return os.path.join(ROOT, f"text/marks/{pid}.txt")


def fingerprint(pid, zh_file=None, en_only=False):
    book, secs = page_secs(pid)
    en = shorey(book, secs)
    zf = zh_file or zh_path(pid)
    zh = "" if en_only or not os.path.exists(zf) else rd(zf)
    mk = rd(marks_path(pid)) if os.path.exists(marks_path(pid)) else ""
    raw = "\x00".join([VERSION, pid, "".join(en[s] for s in secs), "\n".join(shorey_notes(book, secs).values()), zh, mk])
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def esc(s):
    return html.escape(s, quote=False)


def parse_zh(text, secs, en_text, en_notes):
    """返回 ({节号: [行]}, {注号: 注文}, [注号按出现顺序])；问题收进列表，一起报。"""
    errs = []
    body, _, notes_part = text.partition("\n## 注")
    notes_part = notes_part.split("\n", 1)[1] if "\n" in notes_part else ""   # 去掉「## 注」那一行剩下的部分
    lines, cur, got = {}, None, []
    for i, l in enumerate(body.splitlines(), 1):
        m = re.fullmatch(r"\s*\[(\d{3}[a-e])\]\s*", l)
        if m:
            cur = m.group(1)
            if cur in lines:
                errs.append(f"第 {i} 行：节标记 [{cur}] 重复")
            got.append(cur)
            lines[cur] = []
        elif cur is None:
            if l.strip():
                errs.append(f"第 {i} 行：第一个节标记之前有文字：{l[:30]}")
        else:
            lines[cur].append(l.rstrip())
    if got != secs:
        extra = [s for s in got if s not in secs]
        miss = [s for s in secs if s not in got]
        if extra: errs.append(f"多出来的节标记（不在这一页 {secs[0]}–{secs[-1]} 里）：{' '.join(extra)}")
        if miss: errs.append(f"缺少的节标记：{' '.join(miss)}")
        if not extra and not miss: errs.append("节标记的顺序和底本不一样：" + " ".join(got))
    for s in got:
        if not any(x.strip() for x in lines.get(s, [])):
            errs.append(f"[{s}] 是空节")
    notes = {}
    for l in notes_part.splitlines():
        if not l.strip():
            continue
        m = re.fullmatch(r"\[\^(\d+|z\d+)\]\s+(.+)", l.strip())
        if not m:
            errs.append(f"「## 注」里认不出的行（应为 [^n] 注文 或 [^zN] 注文）：{l[:30]}")
            continue
        if m.group(1) in notes:
            errs.append(f"注 [^{m.group(1)}] 有两条")
        notes[m.group(1)] = m.group(2).strip()
    refs = []
    for s in got:
        for r in re.findall(r"\[\^([^\]]*)\]", "\n".join(lines.get(s, []))):
            if not re.fullmatch(r"\d+|z\d+", r):
                errs.append(f"[{s}] 里认不出的注记号 [^{r}]")
            elif r in refs:
                errs.append(f"注记号 [^{r}] 在正文里出现了不止一次")
            else:
                refs.append(r)
    for r in refs:
        if r not in notes: errs.append(f"正文里有 [^{r}]，「## 注」里没有这一条")
    for r in notes:
        if r not in refs: errs.append(f"「## 注」里有 [^{r}]，正文里没有这个记号")
    for r in refs:
        if r.isdigit() and (r not in en_notes or f"[^{r}]" not in en_text):
            errs.append(f"[^{r}] 不是这一页 Shorey 正文里的脚注（自己加的注编号用 [^z1] [^z2]…）")
    for s in got:
        for l in lines.get(s, []):
            if '"' in l:
                errs.append(f"[{s}] 里有英文直引号 \"，引号用 “ ” 和 ‘ ’：{l[:30]}")
                break
    return lines, notes, refs, errs


def fn_btn(num):
    return f'<button type="button" class="fn" aria-expanded="false" aria-controls="n{num}">{num}</button>'


def render_en(raw, nmap):
    """Shorey 一节 → HTML 段落。nmap {Shorey 注号: 本页编号}：只显示被译者选中的。"""
    def inline(s):
        s = re.sub(r"\s*\[cit\. [^\]]*\]\s*", " ", s)
        s = esc(s)
        s = re.sub(r"\[\^(\d+)\]", lambda m: fn_btn(nmap[m.group(1)]) if m.group(1) in nmap else "", s)
        s = re.sub(r"(?<![\[\w])\^(\d+)", r"<sup>\1</sup>", s)
        return re.sub(r"\s{2,}", " ", s).strip()
    out = []
    for para in re.split(r"\n\s*\n", raw.strip()):
        prose, verse = [], []
        def flush_prose():
            if prose:
                t = inline(" ".join(prose))
                if t: out.append(f"<p>{t}</p>")
                prose.clear()
        def flush_verse():
            if verse:
                out.append('<p class="verse">' + "<br>".join(inline(v) for v in verse) + "</p>")
                verse.clear()
        for l in para.split("\n"):
            if l.startswith("> "):
                flush_prose(); verse.append(l[2:])
            elif l.strip():
                flush_verse(); prose.append(l.strip())
        flush_prose(); flush_verse()
    return "\n".join(out)


def render_zh(lines, nmap):
    def inline(s):
        s = esc(s.strip())
        return re.sub(r"\[\^(\d+|z\d+)\]", lambda m: fn_btn(nmap[m.group(1)]), s)
    out, verse, gap = [], [], False
    def flush():
        nonlocal gap
        if verse:
            out.append(f'<p class="verse{" pb" if gap and out else ""}">' + "<br>".join(inline(v) for v in verse) + "</p>")
            verse.clear(); gap = False
    for l in lines:
        if not l.strip():
            flush(); gap = True
        elif l.startswith(">"):
            verse.append(l[1:].lstrip())
        else:
            flush()
            cls = ' class="pb"' if gap and out else ""
            out.append(f"<p{cls}>{inline(l)}</p>")
            gap = False
    flush()
    return "\n".join(out)


def build(pid, zh_file=None, en_only=False):
    """返回 (HTML 块, 统计)；有问题抛 Bad。"""
    book, secs = page_secs(pid)
    en = shorey(book, secs)
    en_notes = shorey_notes(book, secs)
    zf = zh_file or zh_path(pid)
    have_zh = not en_only and os.path.exists(zf)
    zl, notes, refs, errs = ({}, {}, [], [])
    if have_zh:
        zl, notes, refs, errs = parse_zh(rd(zf), secs, " ".join(en.values()), en_notes)
    marks = {}
    if os.path.exists(marks_path(pid)):
        for i, l in enumerate(rd(marks_path(pid)).splitlines(), 1):
            if not l.strip() or l.lstrip().startswith("#"):
                continue
            m = re.fullmatch(r"\s*(\d{3}[a-e])\s*\|\s*(.+?)\s*", l)
            if not m:
                errs.append(f"text/marks/{pid}.txt 第 {i} 行：应为「节号 | 文字」"); continue
            if m.group(1) not in secs:
                errs.append(f"text/marks/{pid}.txt 第 {i} 行：{m.group(1)} 不在这一页 {secs[0]}–{secs[-1]} 里"); continue
            marks.setdefault(m.group(1), []).append(m.group(2))
    if errs:
        raise Bad("\n".join(errs))
    nmap = {r: str(i) for i, r in enumerate(refs, 1)}
    en_map = {r: n for r, n in nmap.items() if r.isdigit()}
    where = {}   # 注号 → 它的注文放在哪一节下面（中文记号所在的节）
    for s in secs:
        for r in re.findall(r"\[\^(\d+|z\d+)\]", "\n".join(zl.get(s, []))):
            where[r] = s
    zw = 0
    out = [f'{BEGIN}（tools/gen_text.py 生成，不要手改：改译文改 text/zh/{pid}.txt，改路标改 text/marks/{pid}.txt，然后重跑） -->',
           f'<article class="fulltext" id="text" data-page="{pid}" data-from="{secs[0]}" data-to="{secs[-1]}" data-zh="{1 if have_zh else 0}" data-src="{fingerprint(pid, zh_file, en_only)}">',
           '<div class="ft-bar"></div>', HOW]
    if not have_zh:
        out.append('<p class="ft-wait">这一段的中文译文还在译，先放英文。</p>')
    for s in secs:
        for mk in marks.get(s, []):
            out.append(f'<aside class="mark" role="note"><span class="mark-tag">导读</span>{esc(mk)}</aside>')
        out.append(f'<section class="st" id="s{s}"><a class="st-n" href="#s{s}">{s}</a>')
        if have_zh:
            z = render_zh(zl[s], nmap)
            zw += len(re.findall(r"[一-鿿]", re.sub(r"<[^>]+>", "", z)))
            out.append(f'<div class="zh" lang="zh-CN">\n{z}\n</div>')
        out.append(f'<div class="en" lang="en">\n{render_en(en[s], en_map)}\n</div>')
        ns = [r for r in refs if where.get(r) == s]
        if ns:
            out.append('<div class="st-notes">' + "".join(
                f'<p class="fn-t" id="n{nmap[r]}" hidden><b>{nmap[r]}</b>{esc(notes[r])}</p>' for r in ns) + "</div>")
        out.append("</section>")
    out += [CREDIT, "</article>", END]
    w = sum(len(re.sub(r"\[\^\d+\]|\[cit\. [^\]]*\]", " ", en[s]).split()) for s in secs)
    return "\n".join(out), {"n": len(secs), "w": w, "zw": zw, "notes": len(refs), "marks": sum(map(len, marks.values())), "zh": have_zh}


def write_page(path, block):
    t = rd(path)
    i, j = t.find(BEGIN), t.find(END)
    if i < 0 or j < i:
        raise Bad(f"{os.path.relpath(path, ROOT)} 里没有一对 {BEGIN} -->…{END} 标记")
    new = t[:i] + block + t[j + len(END):]
    if new != t:
        open(path, "w", encoding="utf-8").write(new)


def page_block(t):
    i, j = t.find(BEGIN), t.find(END)
    return t[i:j + len(END)] if 0 <= i < j else None


def update_js(pid, st):
    p = os.path.join(ROOT, "assets/chapters.js")
    s = rd(p)
    s2, k = re.subn(r'(\{ id: "%s", book: \d+, from: "\w+", to: "\w+", )n: \d+, w: \d+, zw: \d+' % re.escape(pid),
                    lambda m: f'{m.group(1)}n: {st["n"]}, w: {st["w"]}, zw: {st["zw"]}', s)
    if k != 1:
        raise Bad(f"chapters.js 里页 {pid} 那一行的格式认不出（要有 n: …, w: …, zw: …）")
    if s2 != s:
        open(p, "w", encoding="utf-8").write(s2)


def main():
    a = sys.argv[1:]
    def opt(name):
        if name in a:
            i = a.index(name); v = a[i + 1]; del a[i:i + 2]; return v
        return None
    def flag(name):
        if name in a:
            a.remove(name); return True
        return False
    zh_file, out_file = opt("--zh"), opt("--out")
    en_only, check, all_ = flag("--en-only"), flag("--check"), flag("--all")
    if "--slice" in a:
        i = a.index("--slice"); pid, d = a[i + 1], a[i + 2]
        book, secs = page_secs(pid)
        en = shorey(book, secs)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, f"shorey-{pid}.txt"), "w", encoding="utf-8") as f:
            f.write("\n\n".join(f"[{s}] {en[s].strip()}" for s in secs) + "\n")
        with open(os.path.join(d, f"notes-{pid}.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(shorey_notes(book, secs).values()) + "\n")
        return 0
    ids = list(pages()) if all_ else a
    if not ids:
        print(__doc__); return 1
    bad, msgs = 0, []
    for pid in ids:
        try:
            if check:
                path = os.path.join(ROOT, f"chapters/{pid}.html")
                blk = page_block(rd(path)) if os.path.exists(path) else None
                m = re.search(r'data-src="(\w+)"', blk or "")
                ok = m and m.group(1) == fingerprint(pid)
                if not ok: bad += 1; msgs.append(f"{pid} 全文块过期或没有，重跑 python3 -I tools/gen_text.py {pid}")
                else: msgs.append(f"{pid} ✓")
                continue
            block, st = build(pid, zh_file, en_only)
            path = out_file or os.path.join(ROOT, f"chapters/{pid}.html")
            write_page(path, block)
            if not out_file:
                update_js(pid, st)
            msgs.append(f"{pid} {st['n']} 节" + (f"，中文 {st['zw']} 字，注 {st['notes']} 条" if st["zh"] else "，只有英文（还没有 text/zh/%s.txt）" % pid if not en_only else "，只有英文（--en-only）")
                        + (f"，路标 {st['marks']} 条" if st["marks"] else ""))
        except Bad as e:
            bad += 1
            print(f"✗ {pid}\n    " + str(e).replace("\n", "\n    "))
    if not bad:
        print("✓ 全文块 " + "；".join(msgs))
    elif check:
        print("✗ " + "；".join(msgs))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
