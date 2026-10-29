#!/usr/bin/env python3
"""从 Calibre 书库里的两份 epub（只读）提取文本到 source/text/。
  source/calibre/*.epub      Fooled by Randomness, Updated Second Edition（2004；Random House 平装本，Calibre 从 MOBI 转的）
  source/calibre-tw/*.epub   《隨機騙局》（羅耀宗 譯，大塊文化 2014，据第二版）。读者读的是这个繁体本。
                             （source/calibre-zh 是简体《随机漫步的傻瓜》，据第一版、有缺，用户 2026-10-29 定了不用，不提取。）

产出：
  text/00.txt        正文前：Preface、Acknowledgments for the Updated Second Edition、Chapter Summaries、Prologue，加上书后的 Acknowledgments for the First Edition。`## ` 分篇，段号连续。
  text/01–14.txt     一章一个文件。Part I/II/III 的篇首语放在 01、08、12 的开头（`## PART …`）。
  text/14.txt        第 14 章，末尾并进 Epilogue（Solon Told You So，原书只有一个小标题）作 §4，译本同样并进「後記：梭倫說過」。16.txt Postscript。
                     `# NN 章名`；`## ` 是原书全大写的小标题，`### ` 是斜体的小小标题；每行一段，行首 [段号]（每章连续编号）。
                     段里的 {注K} 是原书的星号脚注，章末 `## 脚注` 收 `[nK] …`。
  text/notes.txt     书后的 A Trip to the Library（按页码的尾注和书目），正文里没有链接。
  text/index.tsv     章、段数、词数、小标题数、章名。
  text/zh/00–16.txt  繁体译本，章号和英文一一对应（Part 篇首语也在 01、08、12 开头）。`# ` 章题、`## ` 小标题、`### ` 小小标题，
                     `{Q}` 楷体的引文和章旨，`{F}` 图表的标题；正文每行一段（不编段号），繁体照原样。
  text/zh/notes.txt  译本的「註釋」。zh/ 只给作者对照和 lint 核对「译本译法」。

段落标记：{Q} 缩进的引文（含各章开头的章旨）；{T} 表格的一行（格之间用 | 分开）；{F} 原书的图（不复刻）。*词* 是原书的斜体。
epub 是从扫描版转的，有连字符断词（empiri-cism）和粘连（whospen），照原样保留：读者屏幕上也是这样。"""
import glob, html, os, re, sys, zipfile
from html.parser import HTMLParser

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "source/text")


def epub(link):
    e = glob.glob(os.path.join(ROOT, "source", link, "*.epub"))
    if len(e) != 1: sys.exit(f"source/{link}/ 里要正好一个 epub，现在是 {e}")
    return zipfile.ZipFile(e[0])


BLOCK = {"p", "blockquote", "table", "tr", "div", "h1", "h2", "h3"}


class Blocks(HTMLParser):
    """把一个 html 文件拆成块：(kind, cls, text, bold, italic, notes, plain)。
    kind 是 p / q（在 blockquote 里）/ t（表格行）/ f（图）；bold、italic 是这一块九成以上的字是不是粗体 / 斜体。"""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.buf, self.stack, self.sp = [], [], [], []
        self.nb = self.ni = self.nt = 0; self.notes = []; self.cls = ""; self.inref = 0
    def flush(self):
        s = re.sub(r"\s+", " ", "".join(self.buf)).strip().replace("* *", " ").replace("**", "")
        s = re.sub(r"\*\s+([.,;:!?’”)])", r"*\1", s)
        s = re.sub(r" {2,}", " ", s)
        if s.strip("| "):
            kind = "t" if "tr" in self.stack else "q" if "blockquote" in self.stack else "p"
            plain = re.sub(r"\x01\w+\x01|\*", "", s).strip()
            self.out.append((kind, self.cls, s, self.nt > 0 and self.nb >= self.nt * 0.9,
                             self.nt > 0 and self.ni >= self.nt * 0.9, self.notes, plain))
        self.buf, self.notes = [], []; self.nb = self.ni = self.nt = 0
    def handle_starttag(self, tag, a):
        a = dict(a); c = a.get("class", "")
        if tag in BLOCK: self.flush(); self.cls = c
        if tag == "br": self.buf.append(" "); return
        if tag == "img":
            self.flush(); self.out.append(("f", "", "{F} {图：" + os.path.basename(a.get("src", "")) + "}", 0, 0, [], "")); return
        self.stack.append(tag)
        if tag == "td": self.buf.append(" | ")
        elif tag == "span":
            self.sp.append(c)
            if c == "italic": self.buf.append("*")
        elif tag == "a":
            m = re.search(r"index_split_036\.html#(filepos\d+)", a.get("href", ""))
            if m: self.notes.append(m.group(1)); self.buf.append("\1" + m.group(1) + "\1"); self.inref = 1
    def handle_startendtag(self, tag, a):
        if tag in ("br", "img"): self.handle_starttag(tag, a)
    def handle_endtag(self, tag):
        if tag == "span" and self.sp:
            if self.sp.pop() == "italic":     # 斜体里的尾随空格挪到 * 外面：*word,* next
                last = self.buf[-1] if self.buf else ""
                if last != last.rstrip(): self.buf[-1] = last.rstrip(); self.buf += ["*", " "]
                else: self.buf.append("*")
        if tag == "a": self.inref = 0
        if tag in BLOCK: self.flush()
        while self.stack:
            if self.stack.pop() == tag: break
    def handle_data(self, d):
        if self.inref: return
        n = len(d.strip())
        if n:
            self.nt += n
            if "bold" in self.sp: self.nb += n
            if "italic" in self.sp: self.ni += n
        self.buf.append(d)


def blocks(src):
    b = Blocks(); b.feed(src); b.flush(); return b.out


E = epub("calibre")
read = lambda n: E.read(n).decode("utf-8")
os.makedirs(os.path.join(OUT, "zh"), exist_ok=True)

# 脚注：split_036 里每条以 <small id="fileposN"> 开头
FOOT = {}
for m in re.finditer(r'<p class="calibre_9"><sup[^>]*><small id="(filepos\d+)"[^>]*>.*?</sup>(.*?)<br', read("index_split_036.html"), re.S):
    t = blocks("<p>" + m.group(2) + "</p>")[0][2]
    FOOT[m.group(1)] = t

NUM = "One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Thirteen Fourteen".split()
# (文件号, 起点 filepos 或 None) → 章；Part 篇首语并进下一章
PLAN = [("00", "Front matter", [4, 5, 6, 7, 30]),
        ("01", None, [8, 9, 10]), ("02", None, [11]), ("03", None, [12]), ("04", None, [13]), ("05", None, [14]),
        ("06", None, [15]), ("07", None, [16]), ("08", None, [17, 18, 19]), ("09", None, [20]), ("10", None, [21]),
        ("11", None, [22]), ("12", None, [23, 24, 25]), ("13", None, [26]), ("14", None, [27, 28]),
        ("16", "Postscript: Three Afterthoughts in the Shower", [29])]
TOC = {}
for m in re.finditer(r"<text>(\w+) ([^<]+)</text>", read("toc.ncx")):
    if m.group(1) in NUM and NUM.index(m.group(1)) + 1 not in TOC: TOC[NUM.index(m.group(1)) + 1] = html.unescape(m.group(2)).strip()

# toc.ncx 里的条目都算小标题：有几个斜体小标题和篇的副题没有加粗，光看粗体会漏
hnorm = lambda t: re.sub(r"\s+([:’])", r"\1", re.sub(r"\s+", " ", t)).upper().strip()
TOCSET = {hnorm(html.unescape(t)) for t in re.findall(r"<text>([^<]*)</text>", read("toc.ncx"))}
index, allfoot, EN = [], set(), {}
for num, title, files in PLAN:
    title = title or TOC[int(num)]
    L, k, nsec, words, fn = [f"# {num} {title}", ""], 0, 0, 0, []
    for i in files:
        if num == "14" and i == 28: L.append("## EPILOGUE: SOLON TOLD YOU SO")
        bs = blocks(read(f"index_split_{i:03d}.html"))
        for kind, cls, s, bold, ital, notes, plain in bs:
            if plain in ("•", "", "Fooled by Randomness") and kind != "f": continue
            if re.fullmatch(r"Part I{1,3}", plain): continue          # 篇的序号，篇名在下一行
            if re.match(r"(Table|Figure) [P\d]+\.?\d*\b", plain) and kind in ("p", "q") and len(plain) < 120 and (bold or hnorm(plain) in TOCSET):
                L.append(f"{{F}} {plain}"); continue                   # 表和图的标题，不是小标题
            if plain.startswith("Number of afflicted persons"):
                L.append(f"{{T}} {plain}"); continue
            if kind == "p" and (bold and cls in ("calibre_", "calibre_3", "calibre_26") and len(plain) < 120 or hnorm(plain) in TOCSET):
                if re.fullmatch(r"(One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve|Thirteen|Fourteen)", plain): continue
                if num != "00" and plain.upper() == title.upper().replace("–", "—"): continue
                if num == "16" and plain.upper() in title.upper(): continue
                if num == "14" and i == 28 and plain.upper() in "EPILOGUE: SOLON TOLD YOU SO": continue
                if plain.upper() == plain or plain.startswith("PART"):
                    L.append(f"## {plain}"); nsec += 1
                else:
                    L.append(f"### {plain}")
                continue
            for fp in notes:
                fn.append(fp); s = s.replace("\1" + fp + "\1", f"{{注{len(fn)}}}")
            k += 1
            mark = {"q": "{Q} ", "t": "{T} ", "f": ""}.get(kind, "")
            L.append(f"[{k}] {mark}{s}")
            words += len(plain.split())
    if fn:
        L += ["", "## 脚注"]
        for j, fp in enumerate(fn, 1):
            L.append(f"[n{j}] {FOOT.get(fp, '（找不到）')}"); allfoot.add(fp)
    EN[num] = L
    index.append(f"{num}\t{k}\t{words}\t{nsec}\t{title}")
    print(f"{num}  {k:3d} 段  {words:6d} 词  小标题 {nsec:2d}  脚注 {len(fn)}  {title}")
lost = set(FOOT) - allfoot
if lost: print("  正文里没链到的脚注：", sorted(lost))
# index.tsv 在下面分节之后写
open(os.path.join(OUT, "chapters.tsv"), "w", encoding="utf-8").write("章\t段数\t词数\t小标题数\t章名\n" + "\n".join(index) + "\n")

# 书后尾注（A Trip to the Library … Notes），正文里没有链接，原样给作者查出处
NL = []
for kind, cls, s, bold, ital, notes, plain in blocks(read("index_split_032.html")):
    NL.append(("## " if bold and len(plain) < 80 else "") + s)
open(os.path.join(OUT, "notes.txt"), "w", encoding="utf-8").write("\n".join(NL) + "\n")

# 繁体译本：Sigil 做的，h1 篇、h2 章、h3 小标题、h4 小小标题，class 带 kai 的是楷体（引文、章旨、篇的副题），div.photo 是图表
Z = epub("calibre-tw")
zread = lambda n: Z.read("OEBPS/Text/" + n).decode("utf-8")
ZPLAN = {"00": ["front-matter", "foreword_01", "foreword_02", "foreword_03", "acknowledgment"],
         **{f"{c:02d}": [f"01-0{c}"] for c in range(1, 8)}, **{f"{c:02d}": [f"02-0{c - 7}"] for c in range(8, 12)},
         **{f"{c:02d}": [f"03-0{c - 11}"] for c in range(12, 14)}, "14": ["03-03", "afterword"], "16": ["back-matter"], "notes": ["comment_02"]}
for num, part in (("01", "01"), ("08", "02"), ("12", "03")):
    ZPLAN[num] = [f"chapter_{part}", f"{part}-00"] + ZPLAN[num]
zt = lambda x: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"<br[^>]*>", " ", x)))).strip()
ZH = {}
for num, files in ZPLAN.items():
    L = []
    for f in files:
        src = zread(f + ".xhtml"); src = src[src.index("<body"):]
        for m in re.finditer(r'<(h[1-4]|p)\b([^>]*)>(.*?)</\1>', src, re.S):
            tag, attrs, inner = m.groups()
            if tag == "h1": inner = re.sub(r'<span class="num1">', " ", inner)
            t = zt(inner); cls = (re.search(r'class="([^"]*)"', attrs) or [None, ""])[1]
            if not t: continue
            if tag in ("h1", "h2"): L.append(f"# {t}")
            elif tag == "h3": L.append(f"## {t}")
            elif tag == "h4": L.append(f"### {t}")
            elif "caption" in cls: L.append("{F} " + t)
            elif "kai" in cls: L.append("{Q} " + t)
            else: L.append(t)
    ZH[num] = L
    en = next((int(x.split("\t")[2]) for x in index if x.startswith(num + "\t")), 0)
    n = sum(len(re.findall(r"[一-鿿]", x)) for x in L)
    print(f"zh/{num:5s} {n:6d} 字" + (f"  {n / en:.2f} 字/词" if en else "") + f"  小标题 {sum(x.startswith('## ') for x in L):2d}  {L[0] if L else ''}")


# ── 分节：原书和译本的小标题一一对应（toc 197 条），本站的节 = 有正文的那一级小标题 ──
# 没有正文、紧跟着下一级小标题的（NERO TULIP › Hit by Lightning）并进下一节；章首没有小标题的正文自成一节「（章首）」，
# 只有章旨 {Q} 的并进第一节。01、08、12 开头的篇首语（Part I/II/III）是 §1。表和图的标题不是小标题。
# 原书第 11 章「We Do Not Understand Confidence Levels」排在两张图前面，挪到图后面（译本也是图在前）。
def sections(L, zh):
    head, items = L[0], []                      # items: ("H", level, text) / ("P", line)
    for x in L[1:]:
        if not x.strip(): continue
        if x.startswith("## 脚注"): break
        m = re.match(r"(#{1,3}) (.*)$", x)
        if m and not (zh and re.match(r"# \d+ ", x)):   # 译本里篇首语后面的「# 1 章名」不算小标题
            items.append(("H", len(m.group(1)), m.group(2)))
        else: items.append(("P", x))
    # 小标题后面紧跟的全是图（[k] {F} {图…}、{F} 标题），把小标题挪到图后面
    i = 0
    while i < len(items):
        if items[i][0] == "H":
            j = i + 1
            while j < len(items) and items[j][0] == "P" and re.match(r"(\[\d+\] )?\{F\}", items[j][1]): j += 1
            if j > i + 1 and j < len(items) and items[j][0] == "P": items.insert(j - 1, items.pop(i)); continue
        i += 1
    secs, path = [], []
    for it in items:
        if it[0] == "H":
            if secs and not secs[-1]["paras"]: secs[-1]["path"].append(it[2]); secs[-1]["lv"].append(max(it[1], 2))
            else: secs.append(dict(path=[it[2]], lv=[max(it[1], 2)], paras=[]))
        else:
            if not secs: secs.append(dict(path=[], lv=[], paras=[]))
            secs[-1]["paras"].append(it[1])
    # 章首只有章旨的，并进下一节
    if len(secs) > 1 and not secs[0]["path"] and all(re.match(r"(\[\d+\] )?\{Q\}", p) for p in secs[0]["paras"]):
        secs[1]["paras"] = secs[0]["paras"] + secs[1]["paras"]; secs.pop(0)
    return head, secs


def write_secs(L, secs, foot):
    out = [L[0], ""]
    for k, s in enumerate(secs, 1):
        path, lv = (s["path"], s["lv"]) if s["path"] else (["（章首）"], [2])
        for j, h in enumerate(path):
            out.append("#" * lv[j] + " " + (f"§{k} " if j == len(path) - 1 else "") + h)
        out += s["paras"]
    return "\n".join(out + foot) + "\n"


ZORDER00 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 10, 11]   # 译本 00 的章節摘要排在最前面
rows, bad = [], []
for num in EN:
    L, Lz = EN[num], ZH[num]
    _, es = sections(L, False)
    if num == "00": Lz = ["# 00 正文前"] + Lz        # 译本 00 第一行就是「# 章節摘要」
    _, zs = sections(Lz, True)
    if num == "00":
        # 译本章節摘要里的 ##/### 是篇名、章名，不是小标题：并成一节
        summ = [s for s in zs if s["path"] and s["path"][0] == "章節摘要"]
        k = zs.index(summ[0]); n = 1
        while k + n < len(zs) and re.match(r"(第.部：|\d+ )", zs[k + n]["path"][0]): n += 1
        merged = dict(path=["章節摘要"], lv=[2], paras=sum((s["paras"] for s in zs[k:k + n]), []))
        zs[k:k + n] = [merged]
        zs = [zs[i] for i in ZORDER00]
    if num in ("01", "08", "12"): zs[0].update(path=[Lz[0][2:]], lv=[2])   # 篇首语：译本的篇名就是第一行
    if len(es) != len(zs):
        bad.append(f"{num}: 原书 {len(es)} 节，译本 {len(zs)} 节"); continue
    foot = L[L.index("## 脚注") - 1:] if "## 脚注" in L else []
    open(os.path.join(OUT, f"{num}.txt"), "w", encoding="utf-8").write(write_secs(L, es, foot))
    open(os.path.join(OUT, "zh", f"{num}.txt"), "w", encoding="utf-8").write(write_secs(Lz, zs, []))
    for k, (e, z) in enumerate(zip(es, zs), 1):
        ps = [int(m.group(1)) for p in e["paras"] for m in [re.match(r"\[(\d+)\]", p)] if m]
        body = [re.sub(r"^\[\d+\] (\{\w\} )?", "", p) for p in e["paras"] if re.match(r"\[\d+\]", p)]
        w = sum(len(re.sub(r"\*", "", b).split()) for b in body)
        first = next((b for p, b in zip([p for p in e["paras"] if re.match(r"\[\d+\]", p)], body) if not re.match(r"\[\d+\] \{[QFT]\}", p)), body[0] if body else "")
        zb = [p for p in z["paras"] if not p.startswith("{")]
        zw = sum(len(re.findall(r"[一-鿿]", p)) for p in z["paras"])
        zfirst = zb[0][:16] if zb else ""
        rows.append("\t".join([num, str(k), f"{min(ps)}–{max(ps)}" if ps else "", str(w), " › ".join(e["path"]) or "（章首）",
                               " › ".join(z["path"]) or "（章首）", " ".join(first.replace("*", "").split()[:6]), str(zw), zfirst]))
for b in bad: print("  节对不上：", b)
open(os.path.join(OUT, "index.tsv"), "w", encoding="utf-8").write("章\t节\t段\t词\t原书小标题\t译本小标题\ten\t字\tzs\n" + "\n".join(rows) + "\n")
print(f"index.tsv：{len(rows)} 节")
