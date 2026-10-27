#!/usr/bin/env python3
"""从 Calibre 书库里的 epub（只读）提取文本到 source/text/ 和 source/zh/。
  source/calibre/*.epub      The Making of a Manager（Portfolio / Penguin 2019，出版社原版 epub，带纸书页码）
  source/calibre-zh/*.epub   繁体译本《當上主管後，難道只能默默崩潰？》（許恬寧譯，時報 2020）

产出：
  text/00.txt        引言（Introduction: Great Managers Are Made, Not Born）。
  text/01–10.txt     一章一个文件。结语（Epilogue）并进 10.txt，作为最后一节（见文件末尾）。
                     `# NN 章名`，`## 小标题`（原书 head-a），`### 小小标题`（head-b），`#### `（head-c）。
                     每行一段，行首 [段号 p页码]：段号每章连续，页码是这一段开头所在的纸书页（epub 的 pagebreak 标记，和纸书一致）。
                     章末 `## 脚注`：原书页脚的 * 注（几条笑话和补充），正文里标 {*N}。
                     章末 `## 书后注释`：原书 Notes 里这一章的条目，每条一行 `[nj] 锚词: 出处`，几乎全是出处，只供作者查。
  text/index.tsv     章、段数、词数、起止页、小标题。
  zh/00–10.txt       译本对应的章（结语同样并进 10），`## 小節`、`### `，每行一段 [段号]（每章连续，和原书段号不对应）；章末 `## 注`（译本的注，含译注）。
  img/               原书的插图（每章开头两张漫画，图题 AVOID / ASPIRE，在 epub 里排在图的前面，引言和结语是 THE MYTH / THE REALITY；文字只在图里），
                     按 {图N} 编号，供作者看，不复刻进页面。

段落标记：{Q} 缩进的引文和示范（反馈范例、邮件、对话）；{L} 列表的一项；{F} 图或图题。*词* 是原书的斜体，**词** 是粗体。"""
import glob, html, os, re, sys, zipfile
from html.parser import HTMLParser

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = os.path.join(ROOT, "source")


def epub(d):
    e = glob.glob(os.path.join(SRC, d, "*.epub"))
    if len(e) != 1: sys.exit(f"source/{d}/ 里要正好一个 epub，现在是 {e}")
    return zipfile.ZipFile(e[0])


BLOCK_TAGS = ("p", "h1", "h2", "h3", "h4", "li")


class Blocks(HTMLParser):
    """块级元素逐个成段；记下每段开头所在的纸书页、引用的脚注。mark(cls, tag) 返回段落前缀，None 表示丢掉这一块。"""
    def __init__(self, mark, page=None):
        super().__init__(convert_charrefs=True)
        self.mark = mark; self.out = []; self.buf = []; self.cur = None; self.page = page; self.bpage = page
        self.stack = []; self.skip = 0; self.notes = []
    def flush(self):
        if self.cur is None: return
        s = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        s = re.sub(r"\*\*\s*\*\*|(?<!\*)\*\s*\*(?!\*)", " ", s).strip()
        pre = self.mark(*self.cur)
        if s and pre is not None: self.out.append((self.bpage, pre + s))
        self.buf = []; self.cur = None
    def handle_starttag(self, tag, a):
        a = dict(a); cls = a.get("class", "")
        if a.get("type") == "pagebreak" or (tag == "span" and a.get("epub:type") == "pagebreak"):
            self.page = a.get("title");
            if self.cur is not None and not "".join(self.buf).strip(): self.bpage = self.page
            return
        if tag in BLOCK_TAGS:
            self.flush(); self.cur = (cls, tag); self.bpage = self.page; return
        if tag == "blockquote": self.stack.append("bq")
        if tag == "img":
            self.flush(); self.out.append((self.page, f"{{F}} {{IMG {a.get('src') or a.get('xlink:href')}}}")); return
        if tag == "image":
            self.flush(); self.out.append((self.page, f"{{F}} {{IMG {a.get('xlink:href')}}}")); return
        if tag == "a" and (a.get("type") == "noteref" or a.get("epub:type") == "noteref" or cls == "ref"):
            self.skip += 1; self.notes.append(a.get("href", "")); self.buf.append(f"{{*{a.get('href', '')}}}"); return
        if tag in ("i", "em") or "italic" in cls: self.buf.append("*")
        if tag in ("b", "strong") or "bold" in cls: self.buf.append("**")
        if tag == "br": self.buf.append(" ")
        self.stack.append((tag, cls))
    def handle_startendtag(self, tag, a):
        if tag in ("img", "image", "br") or dict(a).get("type") == "pagebreak": self.handle_starttag(tag, a)
    def handle_endtag(self, tag):
        if tag in BLOCK_TAGS: self.flush(); return
        if tag == "a" and self.skip: self.skip -= 1; return
        if tag == "blockquote":
            while self.stack and self.stack[-1] != "bq": self.stack.pop()
            if self.stack: self.stack.pop()
            return
        if self.stack and isinstance(self.stack[-1], tuple) and self.stack[-1][0] == tag:
            t, cls = self.stack.pop()
            if tag in ("i", "em") or "italic" in cls: self.buf.append("*")
            if tag in ("b", "strong") or "bold" in cls: self.buf.append("**")
    def handle_data(self, d):
        if self.skip: return
        if self.cur is None and d.strip(): self.cur = ("", "p"); self.bpage = self.page
        self.buf.append(d)


def parse(E, names, mark, page=None):
    p = Blocks(mark, page)
    for n in names:
        s = E.read(n).decode("utf-8"); p.feed(s[s.index("<body"):])
    p.flush()
    return p.out, p.page


# ---------- 原书 ----------
E = epub("calibre")
opf_dir = "text/"
spine = sorted(n for n in E.namelist() if re.match(r"text/part\d{4}\.html$", n))
ncx = E.read("toc.ncx").decode("utf-8")
toc = [(html.unescape(m.group(1)), m.group(2).split("#")[0])
       for m in re.finditer(r"<text>([^<]*)</text>\s*</navLabel>\s*<content src=\"([^\"]+)\"", ncx)]
heads = [(t, f) for t, f in toc if re.match(r"(Introduction|Chapter |Epilogue|Acknowledgments|Notes)", t)]


def en_mark(cls, tag):
    if tag == "h1" or cls.startswith("x13-bm-head") or "x03-co-hd" in cls or "x02-" in cls: return None
    if tag == "h2" or "head-a" in cls: return "## "
    if tag == "h3" or "head-b" in cls: return "### "
    if tag == "h4" or "head-c" in cls: return "#### "
    if "caption" in cls: return "{F} "
    if "extract" in cls: return "{Q} "
    if tag == "li" or "list" in cls: return "{L} "
    if "footnote" in cls: return ""
    return ""


def files(start, stop):
    a = spine.index(start); b = spine.index(stop) if stop else len(spine)
    return spine[a:b]


OUT = os.path.join(SRC, "text"); os.makedirs(OUT, exist_ok=True)
IMG = os.path.join(SRC, "img"); os.makedirs(IMG, exist_ok=True)
fig = {}
index = ["章\t段数\t词数\t页\t小标题"]
WORDNUM = {w: i for i, w in enumerate("One Two Three Four Five Six Seven Eight Nine Ten".split(), 1)}
foot_all = {}          # 脚注文件名#id → 文本
for n in spine:
    s = E.read(n).decode("utf-8")
    for m in re.finditer(r'<div class="footnote"[^>]*id="([^"]+)"[^>]*>(.*?)</div>', s, re.S):
        t = html.unescape(re.sub(r"<[^>]+>", "", m.group(2)))
        foot_all[os.path.basename(n) + "#" + m.group(1)] = re.sub(r"\s+", " ", t).strip().lstrip("* ").strip()

TITLE = {re.sub(r"[^a-z0-9]", "", t.lower()): t for t, _ in toc}
page = None
chap_of_file = {}
for i, (t, f) in enumerate(heads):
    nxt = heads[i + 1][1] if i + 1 < len(heads) else None
    if t in ("Acknowledgments", "Notes"): continue
    if t.startswith("Introduction"): n, title = 0, t.split(": ", 1)[1]
    elif t.startswith("Epilogue"): n, title = 11, t.split(": ", 1)[1] if ": " in t else "Epilogue"
    else:
        m = re.match(r"Chapter (\w+): (.*)", t); n, title = WORDNUM[m.group(1)], m.group(2)
    fs = files(f, nxt)
    for x in fs: chap_of_file[os.path.basename(x)] = n
    B, page = parse(E, fs, en_mark, page)
    L = [f"# {n:02d} {title}"]
    k, words, subs, pages, foots = 0, 0, [], [], []
    for pg, b in B:
        if b.startswith("#"):
            if b.startswith("## "):          # 原书 head-a 排成全大写，照目录里的写法
                key = re.sub(r"[^a-z0-9]", "", b[3:].replace("*", "").lower())
                b = "## " + TITLE.get(key, b[3:])
            L += ["", b]
            if b.startswith("## "): subs.append(b[3:])
            continue
        if b.startswith("{F} {IMG"):
            src = re.search(r"\{IMG (.*?)\}", b).group(1); name = os.path.basename(src)
            fig.setdefault(name, len(fig) + 1)
            b = f"{{F}} {{图{fig[name]}}}（source/img/fig{fig[name]}{os.path.splitext(name)[1]}）"
        def fn(m):
            key = m.group(1).split("/")[-1]
            if key in foot_all:
                foots.append(foot_all[key]); return f"{{*{len(foots)}}}"
            return ""                        # 书后注释的锚（原书正文里不显示）
        b = re.sub(r"\{\*([^}]*)\}", fn, b)
        k += 1; words += len(re.sub(r"\{[^}]*\}", "", b).split())
        if pg: pages.append(int(pg))
        L.append(f"[{k} p{pg}] {b}")
    if foots: L += ["", "## 脚注"] + [f"[*{j}] {s}" for j, s in enumerate(foots, 1)]
    pr = f"{min(pages)}–{max(pages)}" if pages else ""
    index.append(f"{n:02d}\t{k}\t{words}\t{pr}\t{' | '.join(subs)}")
    open(os.path.join(OUT, f"{n:02d}.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"{n:02d}  {k:3d} 段  {words:6d} 词  p{pr:9s} {len(subs)} 个小标题  {title}")

for name, j in fig.items():
    with open(os.path.join(IMG, f"fig{j}{os.path.splitext(name)[1]}"), "wb") as w: w.write(E.read(f"images/{name}"))

# 书后注释：`CHAPTER X:` 分章；条目链回正文所在的文件，用它定章
notes = E.read(dict(heads)["Notes"]).decode("utf-8")
per = {}
for m in re.finditer(r'<p class="x13-bm-endnotes">(.*?)</p>', notes, re.S):
    href = re.search(r'href="([^"#]+)#', m.group(1))
    n = chap_of_file.get(href.group(1)) if href else None
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))).strip()
    per.setdefault(n, []).append(t)
for n, items in sorted(per.items(), key=lambda x: (x[0] is None, x[0])):
    if n is None: print("没定到章的注释：", items); continue
    with open(os.path.join(OUT, f"{n:02d}.txt"), "a", encoding="utf-8") as w:
        w.write("\n## 书后注释\n" + "".join(f"[n{j}] {s}\n" for j, s in enumerate(items, 1)))
open(os.path.join(OUT, "index.tsv"), "w", encoding="utf-8").write("\n".join(index) + "\n")
print("图：", len(fig), "  注释：", {n: len(v) for n, v in sorted(per.items(), key=lambda x: (x[0] is None, x[0]))})

# ---------- 译本 ----------
Z = epub("calibre-zh")
ZOUT = os.path.join(SRC, "zh"); os.makedirs(ZOUT, exist_ok=True)
zfiles = {0: ["preface03"], 11: ["epilogue01"]}
for n in range(1, 11):
    zfiles[n] = [f"ch{n:02d}-01t", f"ch{n:02d}-01"] if n == 10 else [f"ch{n:02d}-01"]


def zh_mark(cls, tag):
    if tag == "h1" or tag == "h2": return None
    if tag == "h3": return "## "
    if tag == "h4": return "### "
    if cls == "k": return "{Q} "
    if tag == "li": return "{L} "
    return ""


for n, fs in zfiles.items():
    names = [f"OEBPS/{x}.xhtml" for x in fs if f"OEBPS/{x}.xhtml" in Z.namelist()]
    B, _ = parse(Z, names, zh_mark)
    body = [re.sub(r"\{\*[^}]*\}", "", b) for _, b in B if not b.startswith("{F}")]
    # 注：p.footnote 的块在章末，以注号开头（[1] 是译注 / 原书的 * 注，1 是原书出处注）
    raw = "".join(Z.read(x).decode("utf-8") for x in names)
    notes = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))).strip()
             for m in re.finditer(r'<p class="footnote"[^>]*>(.*?)</p>', raw, re.S)]
    nset = set(notes)
    body = [b for b in body if b not in nset]
    # 第一行常是章名、引言标题（图片之外的文字），去掉和 h1/h2 重复的
    L = [f"# {n:02d}"]
    k = 0
    for b in body:
        if b.startswith("#"): L += ["", b]; continue
        k += 1; L.append(f"[{k}] {b}")
    if notes: L += ["", "## 注"] + notes
    open(os.path.join(ZOUT, f"{n:02d}.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"zh {n:02d}  {k:3d} 段  {sum(len(b) for b in body):6d} 字  {len(notes)} 条注")

# ---------- 结语并进第 10 章 ----------
# 结语只有五百多词，不单成一页：作为第 10 章最后一节 `## Epilogue: …`（译本 `## 結語：…`），段号接着第 10 章往下编。两边第 10 章、结语都没有注。
for d, head in (("text", "## Epilogue: "), ("zh", "## 結語：")):
    a, b = os.path.join(SRC, d, "10.txt"), os.path.join(SRC, d, "11.txt")
    L10 = open(a, encoding="utf-8").read().rstrip("\n").splitlines()
    L11 = open(b, encoding="utf-8").read().rstrip("\n").splitlines()
    k = max(int(m.group(1)) for x in L10 if (m := re.match(r"\[(\d+)[ \]]", x)))
    title = L11[0].split(" ", 2)[2] if d == "text" else "這趟旅程才完成1％"
    out = ["", head + title]
    for x in L11[1:]:
        if x.startswith("#"): continue
        m = re.match(r"\[(\d+)([ \]].*)$", x)
        if m: k += 1; out.append(f"[{k}{m.group(2)}")
    assert not any(x.startswith(("## 脚注", "## 书后注释", "## 注")) for x in L10 + L11)
    open(a, "w", encoding="utf-8").write("\n".join(L10 + out) + "\n"); os.remove(b)
idx = open(os.path.join(OUT, "index.tsv"), encoding="utf-8").read().splitlines()
r10 = idx[11].split("\t"); r11 = idx[12].split("\t")
r10[1] = str(int(r10[1]) + int(r11[1])); r10[2] = str(int(r10[2]) + int(r11[2]))
r10[3] = r10[3].split("–")[0] + "–" + r11[3].split("–")[1]; r10[4] += " | Epilogue"
open(os.path.join(OUT, "index.tsv"), "w", encoding="utf-8").write("\n".join(idx[:11] + ["\t".join(r10)]) + "\n")
print("结语已并进第 10 章")
