#!/usr/bin/env python3
"""从 Calibre 书库里的两份 epub（只读）提取文本到 source/text/。
  source/calibre/*.epub      Impro（Keith Johnstone；Taylor & Francis / Routledge 2012 电子版）
  source/calibre-zh/*.epub   《即兴》（饶昊鹏译，后浪 / 贵州人民出版社 2020）

产出：
  text/01.txt   Introduction（序言，Irving Wardle 写的）＋ Notes on Myself（关于我自己）
  text/02.txt   Status（姿态）            text/03.txt   Spontaneity（自发性）
  text/04.txt   Narrative Skills（叙事技巧）  text/05.txt   Masks and Trance（面具与催眠）＋ Appendix（附录）
                `# NN 篇名`；`## §N 小标题`：原书的编号小节。01 篇：§1 是序言，§2 是 Notes on Myself 没有小标题的开头，§3–§15 是它的 13 个小标题；
                05 篇：§1–§14 是原书的编号小节，§15 是附录（写的是流浪儿面具，并在这里，方便和 §9 放在一页）；
                `### 小标题`：编号小节里的小标题（游戏名多在这一级）。每行一段，行首 [段号]（每篇连续编号）。
                篇末 `## 注`：原书的作者注（各部分的注接着编号），一条注的第一段 [nK]，接着的段落（引文、表格）[nK.1]、[nK.2]…
  text/index.tsv  篇、节、段号范围、词数、小标题、这一节开头几个词。
  text/zh/01–05.txt  译本，和英文同样分 `## §N`、`### 小标题`（译本的节和原书一一对应），正文每行一段，不编段号。
                `{译注}` 是译本的脚注（译注、编注），`{原注}` 是译本里作者自己的注（原书篇末的 Notes），译本把它们集中放在一篇的后面几节末尾。
                `*词*` 是译本的强调（em）。只给作者对照和 lint 核对。

段落标记：{D} 对话或台词（`说话人: 台词`，原书排成两栏的表）；{S} 对话里方括号的旁白（多是作者的评点）；
{Q} 缩进的引文（多是别人的话）；{V} 诗行；{L} 编号列表的一项；{T} 表格的一行（单元格用 ` | ` 隔开）；{A} 署名。
`{注K}` 是正文里作者注的注号（原书是上标），注的内容在篇末 `## 注`。*词* 是原书的斜体。overlap.py 只读 text/ 顶层的 *.txt，zh/ 不参与英文比对。"""
import glob, html, os, re, sys, zipfile
from html.parser import HTMLParser

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "source/text")


def epub(link):
    e = glob.glob(os.path.join(ROOT, "source", link, "*.epub"))
    if len(e) != 1: sys.exit(f"source/{link}/ 里要正好一个 epub，现在是 {e}")
    return zipfile.ZipFile(e[0])


# ---------- 英文 ----------
EN = epub("calibre")
TITLES = ["Introduction", "Notes on Myself", "Status", "Spontaneity", "Narrative Skills", "Masks and Trance", "Appendix"]
FILES = ["OEBPS/part%04d.xhtml" % i for i in range(6, 13)]

# 块级 div 的 class → 段落标记；None 表示标题、不另成段（另行处理）。
BLOCK = {"class_para": "", "class_para1": "", "class_parat": "", "class_para3": "", "class_noindent2": "{S} ",
         "class_fnpara": "", "class_para2": "{L} ", "class_sig": "{A} ", "class_sig1": "{A} ", "class_sig2": "{A} ",
         "class_sig3": "{A} ", "class_sig4": "{A} ", "class_series3": "{N} "}
for k in range(0, 6): BLOCK["class_verse" + (str(k) if k else "")] = "{V} "
HEAD = re.compile(r"class_h\d*$")
SKIP = {"class_chtitle", "class_chtitle1", "class_fntitle"}


class Blocks(HTMLParser):
    """一个块一段；表格一行一段（对话行标 {D}，其他标 {T}）。"""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []; self.buf = []; self.out = []; self.row = None; self.cell = None; self.italic = 0
    def emit(self, cls, s):
        s = re.sub(r"\s+", " ", s).strip().replace("* *", " ").replace("**", "")
        if not s: return
        if cls == "class_fntitle": self.out.append(("NT", s)); return
        if cls in SKIP: return
        if HEAD.match(cls or ""): self.out.append(("H", s)); return
        if cls in BLOCK: self.out.append(("P", BLOCK[cls] + s))
    def flush(self):
        if self.row is not None: return          # 表格里的 div 不断段，整行一起出
        s = "".join(self.buf); self.buf = []
        cls = next((c for c in reversed(self.stack) if c in BLOCK or c in SKIP or HEAD.match(c or "")), None)
        self.emit(cls, s)
    def handle_starttag(self, tag, a):
        a = dict(a); c = a.get("class", "")
        if tag == "tr": self.flush(); self.row = []; return
        if tag == "td" and self.row is not None: self.cell = []; return
        if tag == "div":
            self.flush(); self.stack.append(c)
        elif tag == "span":
            self.stack.append("@i" if c == "class" else "@s")
            if c == "class": (self.cell if self.cell is not None else self.buf).append("*")
        elif tag in ("i", "em"): (self.cell if self.cell is not None else self.buf).append("*")
        elif tag == "br": (self.cell if self.cell is not None else self.buf).append(" ")
        elif tag == "a" and c == "class4": self.stack.append("@n"); (self.cell if self.cell is not None else self.buf).append(" {注")
    def handle_endtag(self, tag):
        if tag == "td" and self.row is not None and self.cell is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip().replace("**", "")); self.cell = None; return
        if tag == "tr" and self.row is not None:
            cells = [x for x in self.row if x]; self.row = None
            if len(cells) == 2 and cells[0].endswith(":") and len(cells[0]) < 40:
                self.out.append(("P", "{D} " + cells[0] + " " + cells[1]))
            elif cells: self.out.append(("P", "{T} " + " | ".join(cells)))
            return
        if tag == "div":
            if self.row is None: self.flush()
            if self.stack: self.stack.pop()
        elif tag == "span" and self.stack and self.stack[-1] in ("@i", "@s"):
            if self.stack.pop() == "@i": (self.cell if self.cell is not None else self.buf).append("*")
        elif tag in ("i", "em"): (self.cell if self.cell is not None else self.buf).append("*")
        elif tag == "a" and self.stack and self.stack[-1] == "@n": self.stack.pop(); (self.cell if self.cell is not None else self.buf).append("}")
    def handle_data(self, d):
        (self.cell if self.cell is not None else self.buf).append(d)


def en_blocks(name):
    src = EN.read(name).decode("utf-8")
    p = Blocks(); p.feed(src[src.index("<body"):]); p.flush()
    return p.out


os.makedirs(os.path.join(OUT, "zh"), exist_ok=True)
for old in glob.glob(os.path.join(OUT, "*.txt")) + glob.glob(os.path.join(OUT, "zh", "*.txt")): os.remove(old)
GROUP = {1: [0, 1], 2: [2], 3: [3], 4: [4], 5: [5, 6]}   # 本站的篇 → 原书的部分（序言并进 01，附录并进 05）
WHOLE = {0: "Introduction", 6: "Appendix"}                # 整个部分算一节
index = ["篇\t节\t段\t词\t小标题\ten"]
en_secs = {}                                              # 篇 → [§ 标题]，给译本核对节数
for n, parts in GROUP.items():
    L = [f"# {n:02d} {' + '.join(TITLES[x] for x in parts)}"]; notes = []; k = 0; sec = 0
    secs = []                                             # [§号, 标题, 首段, 末段, 词数, [小标题], 开头]
    def open_sec(name):
        global sec
        sec += 1; secs.append([sec, name, k + 1, k, 0, [], ""]); L.extend(["", f"## §{sec} {name}".rstrip()])
    for x in parts:
        B = en_blocks(FILES[x]); base = sec; pending_num = False; opened = False; in_notes = False
        if x in WHOLE: open_sec(WHOLE[x]); opened = True
        for kind, s in B:
            if kind == "NT": in_notes = True; continue
            if in_notes:                                  # 篇末「Notes」之后：{N} 起一条注，其余是这条注接着的段落（引文、表格）
                if s.startswith("{N} "): notes.append([re.sub(r"^\{N\} \**(\d+)\.?\**\.?\s*", "", s)])
                elif notes: notes[-1].append(s)
                continue
            if kind == "H":
                if x == 1: open_sec(s); opened = True; continue
                if x in WHOLE: L.extend(["", f"### {s}"]); secs[-1][5].append(s); continue
                m = re.match(r"(\d+)\s*(.*)$", s)
                if m:                                     # 编号小节，名字在同一行（Status）或下一行（只有 Masks：1 / George Devine）
                    if int(m.group(1)) != sec - base + 1: sys.exit(f"{TITLES[x]}: 节号跳了 {sec - base} → {s}")
                    open_sec(m.group(2)); opened = True; pending_num = x == 5 and not m.group(2); continue
                if pending_num:                           # 紧跟编号的那行标题是节名
                    secs[-1][1] = s; L[-1] = f"## §{sec} {s}"; pending_num = False; continue
                L.extend(["", f"### {s}"]); secs[-1][5].append(s); continue
            pending_num = False
            if not opened: open_sec("（篇首）"); opened = True
            k += 1; L.append(f"[{k}] {s}")
            S = secs[-1]; S[3] = k; S[4] += len(re.sub(r"^\{\w\} ", "", s).split())
            if not S[6]: S[6] = " ".join(re.sub(r"^\{\w\} ", "", s).replace("*", "").split()[:6])
    if notes: L += ["", "## 注"] + [f"[n{j}{'.' + str(i) if i else ''}] {s}" for j, ns in enumerate(notes, 1) for i, s in enumerate(ns)]
    open(os.path.join(OUT, f"{n:02d}.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    for S in secs:
        index.append(f"{n:02d}\t{S[0]}\t{S[2]}–{S[3]}\t{S[4]}\t{S[1]}{' / ' + ' | '.join(S[5]) if S[5] else ''}\t{S[6]}")
    en_secs[n] = [S[1] for S in secs]
    print(f"{n:02d}  {k:4d} 段  {sum(S[4] for S in secs):6d} 词  {len(secs):2d} 节  {len(notes)} 条注  {L[0][5:]}")
open(os.path.join(OUT, "index.tsv"), "w", encoding="utf-8").write("\n".join(index) + "\n")

# ---------- 译本 ----------
ZH = epub("calibre-zh")
zspine = sorted(n for n in ZH.namelist() if re.match(r"text/part\d{4}(_split_\d{3})?\.html$", n))
ZT = ["序言", "关于我自己", "姿态", "自发性", "叙事技巧", "面具与催眠", "附录"]


class ZBlocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.buf = []; self.out = []; self.tag = None; self.aside = False; self.ital = False
    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "aside": self.aside = "原注" if "number" in a.get("class", "") else "译注"   # aside.number 是作者的注，其余是译注、编注
        if tag == "em" and self.tag: self.buf.append("*")
        if tag in ("h1", "h2", "h3", "h4", "p"):
            self.buf = []; self.tag = tag
        if tag == "a" and a.get("epub:type") == "noteref" and not self.aside: self.buf.append("〔注〕")
        if tag == "br": self.buf.append(" ")
    def handle_endtag(self, tag):
        if tag == "aside": self.aside = False
        if tag == "em" and self.tag: self.buf.append("*")
        if tag == self.tag:
            s = re.sub(r"\s+", " ", "".join(self.buf)).strip(); self.tag = None
            s = re.sub(r"\[[^\]]*(?:分\s*享|V\s*信|zmxsh)[^\]]*\]", "", s).strip()   # 电子版里混进的水印
            if not s: return
            if tag.startswith("h"): self.out.append(("H", tag, s))
            elif self.aside: self.out.append(("N", self.aside, s))
            else: self.out.append(("P", "", s))
    def handle_data(self, d):
        if self.tag: self.buf.append(d)


def zh_blocks(names):
    out = []
    for nm in names:
        p = ZBlocks(); src = ZH.read(nm).decode("utf-8"); p.feed(src[src.index("<body"):]); out += p.out
    return out


starts = {}
for nm in zspine:
    src = ZH.read(nm).decode("utf-8")
    m = re.search(r"<h1[^>]*>(.*?)</h1>", src, re.S)
    if m:
        t = re.sub(r"<[^>]+>|\s", "", m.group(1))
        if t in ZT: starts[ZT.index(t)] = nm
stop = next(nm for nm in zspine if re.search(r"<h1[^>]*>\s*出版后记", ZH.read(nm).decode("utf-8")))
for n, parts in GROUP.items():
    L = [f"# {n:02d} {' + '.join(ZT[x] for x in parts)}"]; sec = 0; notes = []; nsecs = []
    def zsec(name):
        global sec, notes
        if notes: L.extend(f"{{{k}}} {x}" for k, x in notes); notes = []
        sec += 1; nsecs.append(name); L.extend(["", f"## §{sec} {name}".rstrip()])
    for x in parts:
        a = zspine.index(starts[x]); b = zspine.index(starts[x + 1]) if x + 1 in starts else zspine.index(stop)
        opened = False
        if x in WHOLE: zsec(ZT[x]); opened = True
        for kind, tag, s in zh_blocks(zspine[a:b]):
            if kind == "H":
                s2 = s.replace(" ", "") if len(s) <= 6 else s
                if tag == "h1": continue
                if x == 1: zsec(s2); opened = True; continue
                if x in WHOLE: L.extend(["", f"### {s2}"]); continue
                m = re.match(r"(\d+)\s*(.*)$", s)
                if m and tag == "h2": zsec(m.group(2).replace(" ", "") if len(m.group(2)) <= 6 else m.group(2)); opened = True; continue
                L.extend(["", f"### {s2}"]); continue
            if kind == "N": notes.append((tag, s)); continue
            if not opened: zsec("（篇首）"); opened = True
            L.append(s)
    if notes: L.extend(f"{{{k}}} {x}" for k, x in notes)
    if len(nsecs) != len(en_secs[n]): print(f"  !! 译本 {n:02d} 有 {len(nsecs)} 节，原书 {len(en_secs[n])} 节")
    open(os.path.join(OUT, "zh", f"{n:02d}.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"zh/{n:02d}  {len(nsecs):2d} 节  {sum(len(x) for x in L):6d} 字  {L[0][5:]}")
