#!/usr/bin/env python3
"""从 Calibre 书库里的 epub（只读）提取文本到 source/text/。
  source/calibre/*.epub   Uncontrolled（Basic Books 2012；Calibre 从 AZW3 转的）

产出：
  text/00.txt        导言（Introduction）。
  text/01–15.txt     一章一个文件：`# NN 章名`，`## 小标题`（原书每章有 2–7 个小标题），每行一段，行首 [段号]（每章连续编号）。
                     原书没有页码锚点（Kindle 转出的），不写页码。
                     章末 `## 书后注释`：原书 NOTES 里这一章的条目，每条一行 `[nj] 页码 锚词: 出处……`，几乎全是出处，
                     页码是纸书页码（Kindle 读者看不到）。只供作者查出处，不讲。
  text/index.tsv     章、段数、词数、小标题。

段落标记：{Q} 缩进的引文；{E} 章首或部首的题词；{A} 题词的出处行；{L} 编号列表的一项；{F} 图（原书 8 张图，在 source/img/ 里，按 {图N} 编号）。
*词* 是原书的斜体。部首（PART I/II/III）的题词并进那一部第一章的开头，标 `## 部首题词`。"""
import glob, html, os, re, sys, zipfile
from html.parser import HTMLParser

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "source/text")

e = glob.glob(os.path.join(ROOT, "source/calibre/*.epub"))
if len(e) != 1: sys.exit(f"source/calibre/ 里要正好一个 epub，现在是 {e}")
E = zipfile.ZipFile(e[0])
read = lambda n: E.read(n).decode("utf-8")

# 块级元素的 class → 段落标记。不在表里的 div（calibre3、centeraligned 之类的容器）不另起段。
BLOCK = {"fmtx": "", "fmtx1": "", "lsl": "{L} ", "tx": "{Q} ", "tx1": "{Q} ",
         "pepiv": "{E} ", "peps": "{A} ", "h": "## ", "aph": "## ", "fmht": "#"}


class Blocks(HTMLParser):
    """按层级拆段：正文段落里嵌着引文时，引文前后的正文各成一段。"""
    def __init__(self):
        super().__init__(convert_charrefs=True); self.stack = []; self.buf = []; self.out = []; self.imgs = []
    def flush(self):
        s = re.sub(r"\s+", " ", "".join(self.buf)).strip().replace("* *", " ").replace("**", "")
        self.buf = []
        cls = next((c for c in reversed(self.stack) if c in BLOCK), None)
        if s and s != "*" and cls: self.out.append(BLOCK[cls] + s)
    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag in ("div", "h1", "h2"):
            self.flush(); self.stack.append(a.get("class", ""))
        elif tag in ("i", "em"): self.buf.append("*")
        elif tag == "br": self.buf.append(" ")
        elif tag == "img":
            self.flush(); self.imgs.append(os.path.basename(a["src"])); self.out.append(f"{{F}} {{图{a['src']}}}")
    def handle_startendtag(self, tag, a):
        if tag in ("div", "h1", "h2"): return
        self.handle_starttag(tag, a)
    def handle_endtag(self, tag):
        if tag in ("div", "h1", "h2"):
            self.flush()
            if self.stack: self.stack.pop()
        elif tag in ("i", "em"): self.buf.append("*")
    def handle_data(self, d):
        self.buf.append(d)


def blocks(names):
    p = Blocks()
    for n in names:
        src = read(n); p.feed(src[src.index("<body"):])
    p.flush()
    return p.out


ncx = read("toc.ncx")
toc = [(html.unescape(m.group(1)), m.group(2).split("#")[0])
       for m in re.finditer(r"<text>([^<]*)</text>\s*</navLabel>\s*<content src=\"([^\"]+)\"", ncx)]
spine = [n for n in sorted(E.namelist()) if re.match(r"text/part\d{4}(_split_\d{3})?\.html$", n)]


def files(start, stop):
    a = spine.index(start); b = spine.index(stop) if stop else len(spine)
    return spine[a:b]


heads = [(t, f) for t, f in toc if re.match(r"(CHAPTER \d+|PART |Introduction|Acknowledgments|NOTES)", t)]
order = {f: i for i, (_, f) in enumerate(heads)}
os.makedirs(OUT, exist_ok=True)
imgdir = os.path.join(ROOT, "source/img"); os.makedirs(imgdir, exist_ok=True)
fig = {}            # epub 里的图片文件名 → 全书图号
part_epi = []       # 部首题词，并进下一章
index = ["章\t段数\t词数\t小标题"]
chap_files = {}
for i, (t, f) in enumerate(heads):
    nxt = heads[i + 1][1] if i + 1 < len(heads) else None
    if t in ("Acknowledgments", "NOTES"): continue
    B = blocks(files(f, nxt))
    if t.startswith("PART "):
        part_epi = ["", f"## 部首题词（{t}）"] + [b for b in B if b.startswith(("{E}", "{A}"))]; continue
    m = re.match(r"CHAPTER (\d+) - (.*)", t)
    n, title = (int(m.group(1)), m.group(2)) if m else (0, "Introduction")
    chap_files[n] = files(f, nxt)
    L = [f"# {n:02d} {title}"] + part_epi; part_epi = []
    k, words, subs = 0, 0, []
    for b in B:
        if b.startswith("#"):
            if b.startswith("## "): L += ["", b]; subs.append(b[3:])
            continue                                  # fmht：章号和章名，已在 # 行
        if b == "## ": continue
        if b.startswith("{F}"):
            src = re.search(r"\{图(.*?)\}", b).group(1); name = os.path.basename(src)
            fig.setdefault(name, len(fig) + 1)
            b = f"{{F}} {{图{fig[name]}}}（source/img/fig{fig[name]}{os.path.splitext(name)[1]}）"
        k += 1; words += len(re.sub(r"^\{\w\} ", "", b).split())
        L.append(f"[{k}] {b}")
    for j in range(1, len(L)):          # 图紧前面的短行是图题：原书有的排成引文、有的排成正文
        if "{F} {图" in L[j] and (m := re.match(r"(\[\d+\] )(\{Q\} )?(.*)", L[j - 1])) and len(m.group(3).split()) < 15:
            L[j - 1] = f"{m.group(1)}{{F}} {m.group(3)}"
    index.append(f"{n:02d}\t{k}\t{words}\t{' | '.join(subs)}")
    open(os.path.join(OUT, f"{n:02d}.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"{n:02d}  {k:3d} 段  {words:6d} 词  {len(subs)} 个小标题  {title}")

# 图片：原样拷出，供作者看（不复刻进页面）
for name, j in fig.items():
    with open(os.path.join(imgdir, f"fig{j}{os.path.splitext(name)[1]}"), "wb") as w: w.write(E.read(f"images/{name}"))

# 书后注释：`Chapter N: 标题` 分章，每条以纸书页码开头
notes_files = files(dict(heads)["NOTES"], dict(toc)["INDEX"])
cur, per = None, {}
for b in blocks(notes_files):
    b = re.sub(r"^\{\w\} ", "", b)
    m = re.match(r"(?:## )?(Introduction|Chapter (\d+))", b)
    if m and len(b) < 120:
        cur = int(m.group(2) or 0); per[cur] = []; continue
    if cur is not None and not b.startswith("#"): per[cur].append(b)
for n, items in sorted(per.items()):
    p = os.path.join(OUT, f"{n:02d}.txt")
    with open(p, "a", encoding="utf-8") as w:
        w.write("\n## 书后注释\n" + "".join(f"[n{j}] {s}\n" for j, s in enumerate(items, 1)))
open(os.path.join(OUT, "index.tsv"), "w", encoding="utf-8").write("\n".join(index) + "\n")
print("图：", {f"fig{j}": n for n, j in fig.items()}, "  注释：", {n: len(v) for n, v in sorted(per.items())})
