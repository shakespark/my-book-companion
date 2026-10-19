#!/usr/bin/env python3
"""从 Calibre 书库里的三个 epub（只读）提取文本到 source/text/。运行：python3 -I tools/extract.py
  source/calibre/*.epub          小说 Flowers for Algernon（Mariner 版，17 篇进步报告）
  source/calibre-memoir/*.epub   回忆录 Algernon, Charlie, and I（23 章加后记，书末附 1959 年的原版中篇）
  source/calibre-zh/*.epub       中译本《献给阿尔吉侬的花束》（陈澄和译）

产出（一页一个文件，页 id 见 PAGES / MEMOIR，和 assets/chapters.js、tools/lint.py 用同一套）：
  text/<页 id>.txt   小说各页：`# 页 id 报告 N[–M]`，`> 原书标题`，`## §k 报告 N · 日期` 是一条带日期的报告（或报告里 *** 之后的一段），
                     页内 §k 和 [段号] 都从 1 起。日期从段首拿掉，段落从日期后的正文开始（读者在 Kindle 里搜的是正文）。
  text/m1.txt …      回忆录各页：`## §k 第 N 章 标题`，章内空行分隔之后是 `## §k 第 N 章（续）`。
  text/nv.txt        1959 年的原版中篇（回忆录书末），`## §k` 是一篇报告。
  text/00.txt        小说的献词和柏拉图题记。
  text/zh/rNN.txt    译本，一篇报告一个文件：`## 日期`，正文每行一段（不编段号），`{注}` 是编者注。只给作者对照和 lint 核对「译本译法」。
  text/index.tsv     各页的报告、节数、段数、词数。
段落标记：{Q} 是缩进的引文（剪报、信、书里的书）。*词* 是原书的斜体。overlap.py 只读 text/ 顶层的 *.txt，中文在 zh/ 里不参与英文比对。"""
import glob, html, os, re, sys, zipfile
from html.parser import HTMLParser

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "source/text")

def epub(sub):
    f = glob.glob(os.path.join(ROOT, f"source/{sub}/*.epub"))
    if len(f) != 1: sys.exit(f"source/{sub}/ 里要正好一个 epub，现在是 {f}")
    return zipfile.ZipFile(f[0])

# 小说的页：页 id → 报告，以及拆页从哪一条开始（日期或 ***，按出现顺序数，0 起）。
# 报告 1–6 很短，合成一页；7、8 合一页；11、13、14、16、17 太长，按日期拆。
PAGES = [("01", [1, 2, 3, 4, 5, 6], None), ("07", [7, 8], None), ("09", [9], None), ("10", [10], None),
         ("11a", [11], (0, 5)), ("11b", [11], (5, None)), ("12", [12], None),
         ("13a", [13], (0, 5)), ("13b", [13], (5, None)),
         ("14a", [14], (0, 3)), ("14b", [14], (3, 8)), ("14c", [14], (8, None)),
         ("15", [15], None),
         ("16a", [16], (0, 6)), ("16b", [16], (6, 14)), ("16c", [16], (14, None)),
         ("17a", [17], (0, 9)), ("17b", [17], (9, None))]
# 一整页只有一条长日记、原书没有分隔的，本站按场面分节：页 id → 第 2、3… 节从哪一段开始。这些节标「（本站分）」。
# 16c 是 9 月 27 日一条（约 5300 词）：到 Marks Street / 门口和锁上的门 / 进屋，母亲清醒的一会儿 / Norma 回来 / 刀和离开。
SPLIT = {"16c": [9, 31, 61, 95]}
# 回忆录的页：页 id → 章号（24 是后记）
MEMOIR = [("m1", [1, 2, 3]), ("m2", [4, 5]), ("m3", [6, 7, 8]), ("m4", [9, 10]), ("m5", [11, 12, 13, 14]),
          ("m6", [15, 16, 17, 18]), ("m7", [19, 20, 21, 22, 23, 24])]


class Blocks(HTMLParser):
    """把一个 xhtml 拆成块：(标签, class, 文字, 是否在 blockquote 里, 段首的日期)。
    <br> 当空格；斜体包成 *…*；拆开排的小型大写（S<span>TADIUM</span>）原地拼回，不加空格；段首「斜体粗体」的 span 是日期。"""
    def __init__(self, italic):
        super().__init__(convert_charrefs=True)
        self.italic, self.blocks, self.buf, self.stack, self.bq, self.cls, self.tag, self.date = italic, [], [], [], 0, "", None, None
    def emit(self, tag=None, cls=None):
        s = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        s = re.sub(r"\*(\s*)\*", r"\1", s)                     # 相邻的两段斜体接起来
        s = re.sub(r"\*\s+([^*]*?)\*", r" *\1*", s); s = re.sub(r"\*([^*]*?)\s+\*", r"*\1* ", s)
        s = re.sub(r"\s+", " ", s).strip()
        if s or self.date or (tag or self.tag) == "p": self.blocks.append((tag or self.tag, cls if cls is not None else self.cls, s, self.bq > 0, self.date))
        self.buf, self.date = [], None
    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class") or ""
        if tag == "blockquote":
            if "".join(self.buf).strip(): self.emit()
            self.bq += 1
        elif tag in ("p", "h1", "h2", "h3"):
            if "".join(self.buf).strip(): self.emit()
            self.tag, self.cls, self.buf = tag, cls, []
        elif tag == "br": self.buf.append(" ")
        elif tag in ("span", "em", "i"):
            if "italic bold" in cls and not "".join(self.buf).strip() and self.tag == "p":
                self.stack.append("date"); self.buf.append("\0")
            elif self.italic(tag, cls): self.stack.append("*"); self.buf.append("*")
            else: self.stack.append("")
    def handle_startendtag(self, tag, attrs):
        if tag == "br": self.buf.append(" ")
    def handle_endtag(self, tag):
        if tag in ("span", "em", "i") and self.stack:
            m = self.stack.pop()
            if m == "*": self.buf.append("*")
            elif m == "date":
                s = "".join(self.buf); i = s.index("\0")
                d = re.sub(r"\s+", " ", s[i + 1:]).strip(); self.buf = [s[:i]]
                self.date = f"{self.date} {d}" if self.date else d     # 「5:30」「P.M.」是两个 span
        elif tag in ("p", "h1", "h2", "h3"): self.emit(tag); self.tag, self.cls = None, ""
        elif tag == "blockquote":
            if "".join(self.buf).strip(): self.emit("p")
            self.bq -= 1
    def handle_data(self, d): self.buf.append(d)

def blocks(z, name, italic):
    p = Blocks(italic); t = z.read(name).decode("utf-8"); p.feed(t[t.find("<body"):]); p.close()
    return p.blocks

def write(name, lines):
    open(os.path.join(OUT, name), "w", encoding="utf-8").write("\n".join(lines) + "\n")

os.makedirs(os.path.join(OUT, "zh"), exist_ok=True)
index = ["页\t类\t内容\t节数\t段数\t词数"]

# ---------- 小说 ----------
Z = epub("calibre")
nov_italic = lambda tag, cls: "italic" in cls.split()
T = lambda i: f"OEBPS/Text/Flowers_For_Algernon_split_{i:03d}.html"
front = [b for b in blocks(Z, T(0), nov_italic) if b[2]]
write("00.txt", ["# 00 献词和题记", ""] + [f"[{i}] {'{Q} ' if q else ''}{s}" for i, (_, _, s, q, _) in enumerate(front[2:], 1)])

reports = {}   # 报告号 → (原书标题, [ (日期或 ***, [(是否引文, 文字)…]) … ])
for r in range(1, 18):
    title, entries = None, []
    for tag, cls, s, q, date in blocks(Z, T(r + 2), nov_italic):
        if cls.startswith("calibre19") or cls.startswith("calibre17"):
            title = s; entries.append([None, []]); continue
        if cls == "calibre23": entries.append(["***", []]); continue
        if date:
            s = re.sub(r"^\s*[—-]\s*", "", s)
            if entries and entries[-1][0] is None and not entries[-1][1]: entries[-1][0] = date
            else: entries.append([date, []])
        if s: entries[-1][1].append((q, s))
    entries = [e for e in entries if e[1]]
    reports[r] = (title, entries)

for pid, rs, cut in PAGES:
    lines, k, n, words, titles = [], 0, 0, 0, []
    for r in rs:
        title, entries = reports[r]
        titles.append(title)
        a, b = cut or (0, None)
        last = title
        for i, (date, paras) in enumerate(entries):
            if date and date != "***": last = date
            if not a <= i < (b if b is not None else len(entries)): continue
            k += 1
            lines.append(f"## §{k} 报告 {r} · " + (f"{last}（*** 之后）" if date == "***" else date or title))
            for q, s in paras:
                if n + 1 in SPLIT.get(pid, ()):
                    k += 1; lines.append(f"## §{k} 报告 {r} · {last}（本站分）")
                n += 1; words += len(s.split())
                lines.append(f"[{n}] {'{Q} ' if q else ''}{s}")
    label = f"报告 {rs[0]}" + (f"–{rs[-1]}" if len(rs) > 1 else "")
    write(f"{pid}.txt", [f"# {pid} {label}", "> " + " / ".join(titles), ""] + lines)
    index.append(f"{pid}\t小说\t{label}\t{k}\t{n}\t{words}")
    print(f"{pid:4} {label:10} {k:3d} 节 {n:4d} 段 {words:6d} 词")

# ---------- 回忆录和原版中篇 ----------
M = epub("calibre-memoir")
mem_italic = lambda tag, cls: tag in ("em", "i")
names = sorted(n for n in M.namelist() if re.search(r"index_split_\d+\.html$", n))
chapters = {}  # 章号 → (标题, [(是否新的一节, 是否引文, 文字)…])
for name in names:
    bl = blocks(M, name, mem_italic)
    h = next((s for tag, _, s, _, _ in bl if tag == "h1"), "")
    m = re.match(r"(\d+)\. (.*)", h)
    if m: no, title = int(m.group(1)), m.group(2)
    elif h.startswith("Afterword") or any(s.startswith("My “What Would Happen If") or s.startswith('My "What Would Happen If') for _, _, s, _, _ in bl[:2]): no, title = 24, "Afterword"
    else: continue
    paras, brk = [], False
    raw = M.read(name).decode("utf-8")
    for tag, cls, s, q, _ in bl:
        if tag == "h1": continue
        if no == 24 and tag == "h2" and not paras: title = f"Afterword: {s}"; continue
        if not s: brk = True; continue
        paras.append((brk, q, s)); brk = False
    # 空段（<p><br/><br/></p>）是章内的分隔
    chapters[no] = (title, paras)
for pid, chs in MEMOIR:
    lines, k, n, words = [], 0, 0, 0
    for c in chs:
        title, paras = chapters[c]
        k += 1; lines.append(f"## §{k} " + ("后记" if c == 24 else f"第 {c} 章") + f" {title}")
        for brk, q, s in paras:
            if brk and n and not lines[-1].startswith("## "):
                k += 1; lines.append(f"## §{k} " + ("后记" if c == 24 else f"第 {c} 章") + "（续）")
            n += 1; words += len(s.split())
            lines.append(f"[{n}] {'{Q} ' if q else ''}{s}")
    label = f"第 {chs[0]}–{chs[-1]} 章" if chs[-1] != 24 else f"第 {chs[0]}–23 章和后记"
    write(f"{pid}.txt", [f"# {pid} 回忆录 {label}", ""] + lines)
    index.append(f"{pid}\t回忆录\t{label}\t{k}\t{n}\t{words}")
    print(f"{pid:4} {label:14} {k:3d} 节 {n:4d} 段 {words:6d} 词")

# 原版中篇：回忆录最后一个文件，一篇报告一节（标题是 calibre_5 那一行）
nv_name = next(n for n in reversed(names) if "THE ORIGINAL NOVELETTE" in M.read(n).decode("utf-8"))
lines, k, n, words = [], 0, 0, 0
for tag, cls, s, q, date in blocks(M, nv_name, mem_italic):
    if not s or s == "THE ORIGINAL NOVELETTE": continue
    if cls == "calibre_5":
        k += 1; lines.append(f"## §{k} {s.strip('*')}"); continue
    if not k: continue
    n += 1; words += len(s.split())
    lines.append(f"[{n}] {s}")
write("nv.txt", ["# nv 原版中篇（1959）", ""] + lines)
index.append(f"nv\t中篇\t原版中篇\t{k}\t{n}\t{words}")
print(f"nv   原版中篇       {k:3d} 节 {n:4d} 段 {words:6d} 词")

# ---------- 译本 ----------
C = epub("calibre-zh")
for r in range(1, 18):
    t = C.read(f"text/part{r + 5:04d}.html").decode("utf-8")
    t = re.sub(r'<span class="math-super\d*">.*?</span>', "", t, flags=re.S)
    out, title = [], None
    for m in re.finditer(r'<(h1|h3|p)[^>]*?(?:class="([^"]*)")?[^>]*>(.*?)</\1>', t, flags=re.S):
        tag, cls, inner = m.group(1), m.group(2) or "", m.group(3)
        note = 'id="note_' in inner
        s = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", inner))).strip()
        if not s: continue
        if tag == "h1": title = s; continue
        if tag == "h3": out.append(f"## {s}"); continue
        if note: out.append("{注} " + re.sub(r"^\[\d+\]", "", s)); continue
        out.append(("{Q} " if "kai" in cls else "") + s)
    write(f"zh/r{r:02d}.txt", [f"# 报告 {r} {title}", ""] + out)
print("译本：zh/r01.txt–r17.txt")
write("index.tsv", index)
