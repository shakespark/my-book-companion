#!/usr/bin/env python3
"""从 Calibre 书库里的两份 epub（只读）提取文本到 source/text/。
  source/calibre/*.epub      The Selfish Gene, 30th Anniversary edition（OUP 2006；Calibre 从 AZW3 转的）
  source/calibre-zh/*.epub   《自私的基因：40周年增订版》（卢允中等译，中信 2018）

产出：
  text/00.txt        正文前的四篇：30 周年版导言、第二版序、第一版 Trivers 的序（Foreword）、第一版序。`## ` 分篇，段号连续。
  text/01–13.txt     一章一个文件：`# NN 章名`，每行一段，行首 [段号]（每章连续编号），段号后的 (pN) 是这一段开头在原书（OUP 2006 纸书）的页码。
                     段里的 {注K} 是原书正文的星号 *，指向书后的尾注 K（1989 年第二版加的）。
                     章末 `## 尾注`：`### 注K（第 k 段，p. N）标题`，下面每段一行，行首 [nK.j]。
  text/index.tsv     章、段数、词数、尾注数、页码范围。
  text/zh/00.txt、01–13.txt、notes.txt   译本，正文每行一段（不编段号）。`{译注}` 是译者的脚注。只给作者对照和 lint 核对「译本译法」。
                     译本另有第 14、15 章和 40 周年版的说明、序言，英文版没有，不提取。

段落标记：{Q} 缩进的引文；{A} 引文的出处行；{F} 图注（原书第 12 章四张收益矩阵是图，不复刻）。*词* 是原书的斜体。
原书的分数和算式在 epub 里是小图片，这里按 FRAC 换成文字（5/12、(1/2)^3 …）。epub 自己有几处用错了图（读者 Kindle 上看到的也一样），
照原样换，并在 source/IMG_ERRATA.md 列出，作者别把它当成作者的笔误。overlap.py 只读 text/ 顶层的 *.txt，zh/ 不参与英文比对。"""
import glob, html, os, re, sys, zipfile
from html.parser import HTMLParser

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "source/text")


def epub(link):
    e = glob.glob(os.path.join(ROOT, "source", link, "*.epub"))
    if len(e) != 1: sys.exit(f"source/{link}/ 里要正好一个 epub，现在是 {e}")
    return zipfile.ZipFile(e[0])


# 图片 → 文字。主编逐张看过（2026-10-20）。
FRAC = {"00002": "{图：Necker 立方体}", "00003": "5/12", "00004": "7/12", "00005": "6 1/4", "00006": "1/6", "00007": "5/6",
        "00008": "16 2/3", "00009": "7/12", "00010": "1/2", "00011": "1/2 × 1/2 × 1/2", "00012": "(1/2)^3", "00013": "(1/2)^g",
        "00014": "2 × (1/2)^4 = 1/8", "00015": "1 × (1/2)^3 = 1/8", "00016": "(relatedness = 2 × (1/2)^3 = 1/4)",
        "00017": "(relatedness = 1 × (1/2)^2 = 1/4)", "00018": "(2 × (1/2)^8 = 1/128)", "00019": "(relatedness = 1/32)",
        "00020": "(1/8)", "00021": "(1/2)", "00022": "1/4", "00023": "1/16",
        "00024": "(1 × 12) + (1/2 × 12) + (1/8 × 12) + (0 × 12) = +19 1/2", "00025": "3/8",
        "00026": "1/10 × 1/2 + 9/10 × 1/4 = 0.275", "00027": "1/4", "00028": "1/3", "00029": "5/8", "00030": "3/4",
        "00035": "עלמה", "00036": "בתולה", "00037": "1/8", "00038": "3/8"}
IMG_ERRATA = """# epub 里用错的分数图

原书的分数在 epub 里是小图片，`tools/extract.py` 按看到的图换成文字。下面几处 epub 用错了图或印错了数（读者的 Kindle 上也是这样），
提取文本照原样保留；作者写页面时按原书的逻辑讲，不照抄这几个数，可以在页面上提醒读者一句。主编对着 source/text 核过（2026-10-20）。

- 05.txt 第 21 段：「behaving like a hawk, namely 16 2/3 in our particular example」——概率不可能是 16 2/3，
  按上下文（第 18 段的稳定比例 7/12 hawks）应是 7/12；16 2/3 是第 19 段「1/6 鹰 5/6 鸽」的平均收益，epub 把那张图用到了这里。
- 06.txt 第 27 段（净收益的加权算式）：「(1/8) Benefit to other brother」应是 1/2，「1/2 Risk to first cousin」应是 1/8：epub 把两张图对调了（译本这里是对的）。
- 06.txt 第 33 段：「Their relatedness is either (1/2) or 1/2」——半同胞和全同胞，应是 1/4 或 1/2（同段的平均数 3/8 也证明了这一点）。

- 06.txt 注 32 第一段（n32.1）引第一版原话「second cousins should tend to receive A as much altruism」：A 应是 1/16（epub 里这里就是字母 A，不是图片）。

另有两处是扫描识别把数字 1 认成了字母 I（读者屏幕上也是 I）：06.txt 第 27 段「relatedness with himself is I」、第 33 段「only I in 10」。

段号是 source/text 每行开头的 [k]，不是文件的行号。
"""


class Para(HTMLParser):
    """把一段 <p> 的内部转成纯文本：<em>/<i> → *x*，<img> → FRAC，<br> → 空格，尾注链接 → {注K}，记下页码锚点。"""
    def __init__(self):
        super().__init__(convert_charrefs=True); self.out = []; self.pages = []; self.notes = []; self.skip = 0
    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag in ("em", "i"): self.out.append("*")
        elif tag == "br": self.out.append(" ")
        elif tag == "img":
            k = os.path.splitext(os.path.basename(a.get("src", "")))[0]
            self.out.append(FRAC.get(k, "{图}"))
        elif tag == "a":
            i = a.get("id", "")
            if i.startswith("page_"): self.pages.append(i[5:]); self.out.append("\0")
            m = re.search(r"#ien(\d+)$", a.get("href", ""))
            if m: self.notes.append(int(m.group(1))); self.out.append(f"{{注{m.group(1)}}}"); self.skip = 1
    def handle_startendtag(self, tag, a):
        self.handle_starttag(tag, a)
        if tag == "a": self.skip = 0
    def handle_endtag(self, tag):
        if tag in ("em", "i"): self.out.append("*")
        elif tag == "a": self.skip = 0
    def handle_data(self, d):
        if not self.skip: self.out.append(d)
    def text(self):
        s = "".join(self.out)
        lead = s.split("\0")[0].strip() == ""          # 页码锚点在段首
        s = re.sub(r"\s+", " ", s.replace("\0", "")).strip()
        s = s.replace("* *", " ").replace("**", "")
        return s, lead


def para(inner):
    p = Para(); p.feed(inner); s, lead = p.text()
    return s, p.pages, p.notes, lead


MARK = {"blockquote": "{Q} ", "attribute": "{A} ", "caption": "{F} ", "right": "{A} "}
E = epub("calibre")
read = lambda n: E.read(n).decode("utf-8")
os.makedirs(os.path.join(OUT, "zh"), exist_ok=True)

FRONT = [("text/part0004.html", "Introduction to 30th anniversary edition"), ("text/part0005.html", "Preface to second edition"),
         ("text/part0006.html", "Foreword to first edition (Robert L. Trivers)"), ("text/part0007.html", "Preface to first edition")]
CHAPS = [f"text/part{i:04d}.html" for i in range(8, 21)]
note_where = {}     # 尾注号 → (章, 段号)
page = ["?"]


# 排版上没有缩进、实际是别人原话的段落（第 12 章一战亲历者的回忆，转引自 Axelrod），按开头几个词标 {Q}
QUOTE_START = ("We go out at night in front of the trenches", "I was having tea with A company",
               "At seven it came", "So regular were they [the Germans]")


def body(fname, lines, k, ch):
    src = read(fname)
    held = ""
    for m in re.finditer(r'<p class="([^"]+)"[^>]*>(.*?)</p>', src, re.S):
        cls, inner = m.group(1), m.group(2)
        if cls == "image": continue
        s, pages, notes, lead = para(inner)
        if cls == "pub-image":            # 第 12 章的莎士比亚那一行：并进紧接着的出处行，不另占段号
            held = s; continue
        if held: s, cls, held = f"{held} — {s}", "blockquote", ""
        if any(s.startswith(q) for q in QUOTE_START): cls = "blockquote"
        if not s:
            if pages: page[0] = pages[-1]
            continue
        start = pages[0] if pages and lead else page[0]
        if pages: page[0] = pages[-1]
        k += 1
        for n in notes: note_where[n] = (ch, k)
        lines.append(f"[{k}] (p{start}) {MARK.get(cls, '')}{s}")
    return k


index = []
lines, k = ["# 00 Front matter", ""], 0
for f, title in FRONT:
    m = re.search(r'<a id="page_(\w+)"', read(f)); page[0] = m.group(1) if m else "?"
    lines.append(f"## {title}"); k = body(f, lines, k, 0)
open(os.path.join(OUT, "00.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
# 章名用 toc.ncx 的写法（第 7 章起正文标题是全大写）
TOC = {int(m.group(1)): html.unescape(m.group(2)) for m in re.finditer(r"<text>(\d+)\. ([^<]+)</text>", read("toc.ncx"))}
chap_lines, titles = {}, {}
for n, f in enumerate(CHAPS, 1):
    src = read(f)
    h = re.search(r"<h2[^>]*>(.*?)</h2>", src, re.S).group(1)
    page[0] = re.findall(r'id="page_(\w+)"', src[:src.index("<p ")])[-1]   # 第 1 章前面还有一个空白页 xxiv
    titles[n] = TOC[n]
    L = [f"# {n:02d} {titles[n]}", ""]
    chap_lines[n] = (L, body(f, L, 0, n), page[0])

# 尾注：每条以 <p class="no-indent"> 里的 「p. N」链接 + 斜体标题开头
notes = {}
cur = None
for f in sorted(n for n in E.namelist() if n.startswith("text/part0021_split_")):
    src = read(f)
    for m in re.finditer(r'<p class="([^"]+)"[^>]*>(.*?)</p>', src, re.S):
        cls, inner = m.group(1), m.group(2)
        hm = re.search(r'id="ien(\d+)"', inner)
        s, _, _, _ = para(inner)
        if not s or cls == "pagebreak": continue
        if hm:
            K = int(hm.group(1)); pm = re.match(r"p\. (\w+)\s*(.*)", s)
            cur = notes.setdefault(K, {"page": pm.group(1) if pm else "?", "head": pm.group(2) if pm else s, "paras": []})
        elif cur is not None:
            cur["paras"].append(MARK.get(cls, "") + s)

for n, (L, k, last) in chap_lines.items():
    mine = sorted(K for K, (c, _) in note_where.items() if c == n)
    if mine: L += ["", "## 尾注"]
    words = sum(len(re.sub(r"^\[\d+\] \(p\w+\) ", "", x).split()) for x in L if x.startswith("["))
    nw = 0
    for K in mine:
        nt = notes.get(K)
        if not nt: print(f"  第 {n} 章的注 {K} 在尾注里找不到"); continue
        L.append(f"### 注{K}（第 {note_where[K][1]} 段，p. {nt['page']}）{nt['head']}")
        for j, p in enumerate(nt["paras"], 1):
            L.append(f"[n{K}.{j}] {p}"); nw += len(p.split())
    first = re.search(r"\(p(\w+)\)", L[2]).group(1)
    index.append(f"{n:02d}\t{k}\t{words}\t{len(mine)}\t{nw}\tp{first}–p{last}\t{titles[n]}")
    open(os.path.join(OUT, f"{n:02d}.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"{n:02d}  {k:3d} 段  {words:6d} 词  尾注 {len(mine):2d} 条 {nw:5d} 词  p{first}–p{last}  {titles[n]}")
lost = sorted(set(notes) - set(note_where))
if lost: print("  正文里没有链接的尾注：", lost)
open(os.path.join(OUT, "index.tsv"), "w", encoding="utf-8").write(
    "章\t段数\t词数\t尾注数\t尾注词数\t页码\t章名\n" + "\n".join(index) + "\n")
open(os.path.join(ROOT, "source", "IMG_ERRATA.md"), "w", encoding="utf-8").write(IMG_ERRATA)

# 译本
Z = epub("calibre-zh")
zread = lambda n: Z.read(n).decode("utf-8")


# 译本的分数和算式也是小图片（class="calibre16"），主编逐张看过（2026-10-20），换成文字；其余图片是各章的装饰插画，丢掉。
# 2026-10-20 之前这里把图片一律删掉，各页曾误以为「译本的分数只剩空白」，审读轮发现后改正。
ZFRAC = {"Image00009": "5/12 : 7/12", "Image00010": "7/12", "Image00011": "5/12", "Image00012": "6 1/4", "Image00013": "1/6",
         "Image00014": "5/6", "Image00015": "16 2/3", "Image00017": "2 × (1/2)^4 = 1/8", "Image00018": "1 × (1/2)^3 = 1/8",
         "Image00019": "2 × (1/2)^3 = 1/4", "Image00020": "1 × (1/2)^2 = 1/4", "Image00021": "2 × (1/2)^8 = 1/128",
         "Image00022": "1/32", "Image00023": "1/8", "Image00024": "1/16", "Image00025": "1/10",
         "Image00026": "1/10 × 1/2 + 9/10 × 1/4 = 0.275", "Image00029": "1/5", "Image00031": "5/8", "Image00039": "1/500",
         "Image00046": "3/8", "Image00043": "עלמה", "Image00044": "בתולה", "Image00045": "παρθένος"}


def ztext(inner):
    inner = re.sub(r'<img[^>]*src="(Image\d+)\.jpg"[^>]*>', lambda m: f" {ZFRAC[m.group(1)]} " if m.group(1) in ZFRAC else "", inner)
    s = re.sub(r"<sup[^>]*>.*?</sup>", "", inner, flags=re.S)
    s = re.sub(r"<br[^>]*>", "", s)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


spine = [n for n in sorted(Z.namelist()) if re.match(r"OEBPS/text\d+\.html$", n)]
zh, cur = {}, None
for f in spine:
    src = zread(f)
    h = re.search(r"<h1[^>]*>(.*?)</h1>", src, re.S)
    if h:
        t = ztext(re.sub(r"<br[^>]*>", " ", h.group(1)))
        m = re.match(r"第(\d+)章", t)
        cur = (f"{int(m.group(1)):02d}" if m and int(m.group(1)) <= 13 else None) if m else \
              ("00" if t in ("30周年版简介", "第2版前言", "序言", "前言") else "notes" if t == "尾注" else None)
        if cur: zh.setdefault(cur, []).extend(["", f"# {t}"])
    if not cur: continue
    for m in re.finditer(r'<(p|h3|h4)( class="([^"]*)")?[^>]*>(.*?)</\1>', src, re.S):
        tag, cls, inner = m.group(1), m.group(3) or "", m.group(4)
        s = ztext(inner)
        if not s: continue
        zh[cur].append(f"## {s}" if tag in ("h3", "h4") else s)
    for m in re.finditer(r'<div class="fnote1?">(.*?)</div>', src, re.S):
        s = ztext(m.group(1))
        if s: zh[cur].append("{译注} " + s)
for k, L in zh.items():
    open(os.path.join(OUT, "zh", f"{k}.txt"), "w", encoding="utf-8").write("\n".join(L).strip() + "\n")
print("译本：zh/" + " ".join(sorted(zh)) + "，" + " ".join(f"{k}:{sum(len(x) for x in L)}字" for k, L in sorted(zh.items())))
