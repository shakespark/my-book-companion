#!/usr/bin/env python3
"""从 Calibre 书库里的两份 epub（只读）提取文本到 source/text/。
  source/calibre/*.epub      Thinking in Systems: A Primer（Chelsea Green 2008，Diana Wright 编）
  source/calibre-zh/*.epub   《系统之美》（邱昭良 译，浙江人民出版社 2012，湛庐文化电子版；用户 2026-11-15 从 AZW3 转的）。读者读的是这个。

产出：
  text/00.txt        正文前：A Note from the Author、A Note from the Editor（末尾是书前 Pirsig 的题词）、Introduction: The Systems Lens。
  text/01–07.txt     一章一个文件。`# NN 章名`；`## ` 小标题，`### ` 第 2 章各模型的小标题；每行一段，行首 [段号]（每章连续编号）。
  text/08.txt        Appendix（术语表、原理汇总、陷阱对策、杠杆点、生活准则、模型方程）。
  text/back.txt      书末：Bibliography、Editor’s Acknowledgments、About the Author（译本都没有）。
  段里的 {注K} 是书后 Notes 的注号（原书正文上标），章末 `## 注释` 收 `[nK] …`（译本没有译这些注）。
  text/index.tsv     一节一行：章、节、段、词、原书小标题、译本小标题、en（原书这一节开头几个词）、字（译本字数）、zs（译本开头 16 字）。
  text/chapters.tsv  一章一行。
  text/zh/00–08.txt  译本，章号、节号和英文一一对应（两边小标题前都标 §k）。`# ` 章题、`## ` 小标题；正文每行一段（不编段号）。
                     章末 `## 译者注` 收译本的「——译者注」。
  text/img/、text/zh/img/  两边 epub 里的图（作者对照图上的标签用；不复刻、不上页面）。
                     译本有三张图是文字表格（附录术语表两张、第 7 章一张），转写在 source/imgtext/zh-<图号>.txt，提取时以 {T} 行并在 {图：…} 后面。
  text/zh/front.txt  译本独有的：各方赞誉、导读「决策者的系统思考」。zh/back.txt：译者后记。

段落标记（英文）：{Q} 题词和它的出处；{Q} 按位置认（看 mark_epigraphs）；{S} 页边的金句（原书排在页边、加粗，正文里多半有同一句）；{B} 灰底方框（THINK ABOUT THIS、
A NOTE ON …、第 5 章的 THE TRAP / THE WAY OUT），方框标题写成 {B} **标题**；{I} 插话（INTERLUDE • …，标题和正文都标）；{F} 图注；{图：文件名} 原书的图（不复刻）。
*词* 是原书的斜体；† 是原书的字面星号（第 1 章「A system† is」，页脚「† Definitions of words in bold face can be found in the Glossary」）。
原书正文里加粗的词是术语表里有的词，提取时没保留粗体（术语表在 08 §1）。
段落标记（译本）：{B} 译本排成缩进块的段（题词、出处、译本加的「系统之思」「系统多棱镜」标签和方框、部分例子；译本不区分这几种）；
{C} 居中的字（图上的说明、「典型代表：……」）；{F} 图注（「图2—1 ……」）；{图：文件名}；{R} 右对齐（署名）。

分节：节 = 有正文的那一级小标题，没有正文的小标题并进下一节。英文的小标题写死在 HEADS 里（原书的标签很乱：h8、h17、h191、tx9、tx12 都有）。
  00：原书 §1 作者说明 = 译本「前言」（译本把 Pirsig 题词放在前言开头，原书排在编者说明之后），§2 编者说明 = 译本「献词 献给世界的复杂性」（戴安娜·莱特署名），
      §3–§5 引言：原书没有小标题，按译本的三个小标题（无处不在的系统 / 重塑系统，发现更大的世界 / 找到属于你的系统之美）本站分，节名用译本的。
  第 2 章：「One-Stock Systems」「Two-Stock Systems」没有正文，并进下一节（和译本「单存量系统」「双存量系统」一样）。
  第 6 章：最后一节「进入谦卑的『空』」原书没有小标题，在「There is so much that could be said」本站分（看 SPLIT）。"""
import glob, html, os, re, sys, zipfile
from html.parser import HTMLParser

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "source/text")


def epub(link):
    e = glob.glob(os.path.join(ROOT, "source", link, "*.epub"))
    if len(e) != 1: sys.exit(f"source/{link}/ 里要正好一个 epub，现在是 {e}")
    return zipfile.ZipFile(e[0])


BLOCK = {"p", "div", "h1", "h2", "h3", "h4", "table", "tr", "li", "blockquote"}   # td 里没有 <p>，整行当一块


class Blocks(HTMLParser):
    """把一个 html 文件拆成块：(cls, divs, text, plain, notes)。divs 是外层 div 的 class 列表，notes 是这一块里的注的 id。"""
    def __init__(self, noteref):
        super().__init__(convert_charrefs=True)
        self.noteref = noteref
        self.out, self.buf, self.notes, self.divs, self.stack = [], [], [], [], []
        self.cls = ""; self.inref = 0
    def flush(self):
        s = "".join(self.buf)
        s = re.sub(r"\s+", " ", s).strip().replace("**", "").replace("* *", " ")
        s = re.sub(r"\*\s+([.,;:!?’”)])", r"*\1", s); s = re.sub(r" {2,}", " ", s)
        plain = re.sub(r"\x01\w+\x01|\*", "", s).strip()
        if plain or "\x02" in s:
            self.out.append((self.cls, list(self.divs), s.replace("\x02", ""), plain.replace("\x02", ""), self.notes))
        self.buf, self.notes = [], []
    def handle_starttag(self, tag, a):
        a = dict(a); c = a.get("class", "") or ""
        if tag == "br": self.buf.append(" "); return
        if tag == "img":
            self.flush(); self.out.append(("img", list(self.divs), "{图：" + os.path.basename(a.get("src", "")) + "}", "", [])); return
        if tag in BLOCK: self.flush(); self.cls = "tr" if tag == "tr" else c
        if tag == "div": self.divs.append(c)
        if tag == "td" and "".join(self.buf).strip(): self.buf.append(" | ")
        self.stack.append(tag)
        if tag in ("i", "em"): self.buf.append("*")
        elif tag == "a":
            m = self.noteref(a)
            if m: self.notes.append(m); self.buf.append("\x01" + m + "\x01"); self.inref = 1
    def handle_startendtag(self, tag, a):
        if tag in ("br", "img"): self.handle_starttag(tag, a)
    def handle_endtag(self, tag):
        if tag in ("i", "em"):
            last = self.buf[-1] if self.buf else ""
            if last != last.rstrip(): self.buf[-1] = last.rstrip(); self.buf += ["*", " "]
            else: self.buf.append("*")
        if tag == "a": self.inref = 0
        if tag in BLOCK: self.flush()
        if tag == "div" and self.divs: self.divs.pop()
        while self.stack:
            if self.stack.pop() == tag: break
    def handle_data(self, d):
        if self.inref: return
        if d.strip() == "*": d = d.replace("*", "†")
        d = re.sub(r"^(\s*)\* ", r"\1† ", d)
        self.buf.append(d)


def enref(a):
    m = re.search(r"chap23_\S*#(d\d+)$", a.get("href", ""))
    return m.group(1) if m else None


def blocks(src, ref=enref):
    b = Blocks(ref); b.feed(src); b.flush(); return b.out


E = epub("calibre")
efile = lambda n: next(x for x in E.namelist() if os.path.basename(x).startswith(f"chap{n}_thinking"))
eread = lambda n: E.read(efile(n)).decode("utf-8")
os.makedirs(os.path.join(OUT, "zh"), exist_ok=True)

# 书后 Notes：<a href="…#d47751a" id="d47751">1</a>. 文字
NOTE = {}
for m in re.finditer(r'<p class="tx12a"><a href="[^"]*" id="(d\d+)">\d+</a>\.(.*?)</p>', eread(23), re.S):
    NOTE[m.group(1)] = blocks("<p>" + m.group(2) + "</p>")[0][2]

# 小标题（按出现顺序；前缀匹配，忽略大小写和空白）。("##", 文字) 或 ("###", 文字)
H2 = lambda *xs: [("##", x) for x in xs]
HEADS = {
    "00": H2("A NOTE FROM THE AUTHOR", "A NOTE FROM THE EDITOR"),
    "01": H2("More Than the Sum of Its Parts", "Look Beyond the Players to the Rules of the Game", "Bathtubs 101",
             "How the System Runs Itself", "Stabilizing Loops", "Runaway Loops"),
    "02": [("##", "One-Stock Systems"), ("###", "A Stock with Two Competing Balancing Loops"),
           ("###", "A Stock with One Reinforcing Loop and One Balancing Loop"), ("###", "A System with Delays"),
           ("##", "Two-Stock Systems"), ("###", "A Renewable Stock Constrained by a Nonrenewable Stock"),
           ("###", "Renewable Stock Constrained by a Renewable Stock")],
    "03": H2("Resilience", "Self-Organization", "Hierarchy"),
    "04": H2("Beguiling Events", "Linear Minds in a Nonlinear World", "Nonexistent Boundaries", "Layers of Limits",
             "Ubiquitous Delays", "Bounded Rationality"),
    "05": H2("Policy Resistance", "The Tragedy of the Commons", "Drift to Low Performance", "Escalation",
             "Success to the Successful", "Shifting the Burden to the Intervenor", "Rule Beating", "Seeking the Wrong Goal"),
    "06": H2(*[f"{n}. " for n in range(12, 0, -1)]),
    "07": H2("Get the Beat of the System", "Expose Your Mental Models", "Honor, Respect, and Distribute Information",
             "Use Language with Care", "Pay Attention to What Is Important", "Make Feedback Policies",
             "Go for the Good of the Whole", "Listen to the Wisdom of the System", "Locate Responsibility in the System",
             "Stay Humble", "Celebrate Complexity", "Expand Time Horizons", "Defy the Disciplines",
             "Expand the Boundary of Caring", "Don’t Erode the Goal of Goodness"),
    "08": H2("System Definitions: A Glossary", "Summary of Systems Principles", "Springing the System Traps",
             "Places to Intervene in a System", "Guidelines for Living in a World of Systems", "Model Equations"),
}
# 原书没有小标题、本站照译本分节的地方：(章, 这一段的开头) → 节名（用译本的）
SPLIT = {("00", "Managers are not confronted"): "（引言）无处不在的系统",
         ("00", "Because of feedback delays within complex systems"): "（引言）重塑系统，发现更大的世界",
         ("00", "When our small research group moved"): "（引言）找到属于你的系统之美",
         ("06", "There is so much that could be said to qualify this list"): "（本站分）进入谦卑的“空”"}
PLAN = [("00", "Front matter and Introduction", [8, 9, 10, 11]), ("01", None, [12, 13]), ("02", None, [14]),
        ("03", None, [15, 16]), ("04", None, [17]), ("05", None, [18]), ("06", None, [19, 20]), ("07", None, [21]),
        ("08", "Appendix", [22])]
TITLES = {"01": "The Basics", "02": "A Brief Visit to the Systems Zoo", "03": "Why Systems Work So Well",
          "04": "Why Systems Surprise Us", "05": "System Traps . . . and Opportunities",
          "06": "Leverage Points—Places to Intervene in a System", "07": "Living in a World of Systems"}
norm = lambda t: re.sub(r"\s+", "", t).upper()
NOTEPI = ("Because of feedback delays", "According to the competitive exclusion", "A diverse system with multiple")
ATTR = lambda b: re.match(r"\*?—", b) and len(b) < 250       # 题词的出处行：「—Wendell Berry, writer」


def mark_epigraphs(L):
    """题词按位置认（class 太乱）：章首或原书小标题之后往下读，读到出处行（— 开头的短段），它和它前面读过的段都是题词；
    接着再读，后面还可以有第二段题词（第 1 章 §6、第 5 章 §7 各两段）。读过的段超过 12 段或 300 词还没碰到出处，就是正文开始了。
    诗（第 3 章 §4、第 4 章 §2）和卡尔文的对白（第 5 章 §8）一行一段，所以段数放得宽。
    NOTEPI 里的段是正文：引言「Because of feedback delays…」后面跟一句谚语，不是题词。"""
    out = list(L); i = 0
    while i < len(out):
        if i == 0 or re.match(r"#{2,3} ", out[i]):
            js, words, j = [], 0, i + 1
            while j < len(out) and not out[j].startswith("#") and len(js) <= 12 and words <= 300:
                m = re.match(r"\[(\d+)\] (.*)$", out[j])
                if m and not re.match(r"\{[SBFTI]\}|\{图", m.group(2)):
                    body = re.sub(r"^\{Q\} ", "", m.group(2))
                    if body.startswith(NOTEPI): break
                    js.append(j); words += len(body.split())
                    if ATTR(body):
                        for q in js:
                            if " {Q} " not in out[q]: out[q] = re.sub(r"^(\[\d+\]) ", r"\1 {Q} ", out[q])
                        js, words = [], 0
                j += 1
        i += 1
    return out


def en_lines(num, files):
    title = TITLES.get(num, dict((p[0], p[1]) for p in PLAN)[num])
    heads = list(HEADS.get(num, [])); L = [f"# {num} {title}", ""]; k = 0; fn = []; seen_head = False; inter = False
    for i in files:
        for cls, divs, s, plain, notes in blocks(eread(i)):
            if plain in ("Thinking in Systems", "_____________", "") and cls != "img": continue
            if cls == "h9" and not (heads and norm(plain).startswith(norm(heads[0][1]))): continue   # 章号（作者、编者说明的标题也是 h9）
            if num == "00" and plain.upper().startswith("INTRODUCTION: THE SYSTEM"): continue
            if re.fullmatch(r"PART (ONE|TWO|THREE)", plain.strip()) or plain.strip() in (
                    "System Structure and Behavior", "Systems and Us", "Creating Change—in Systems and in Our Philosophy"): continue
            if cls == "h7" and norm(plain) == norm(title): continue
            if heads and norm(plain).startswith(norm(heads[0][1])) and len(plain) < 200 and "a1" not in divs:
                lv, _ = heads.pop(0); L.append(f"{lv} {plain}"); seen_head = True; continue
            sp = next((v for (c, a), v in SPLIT.items() if c == num and plain.startswith(a)), None)
            if sp: L.append(f"## {sp}")
            for nid in notes:
                fn.append(nid); s = s.replace("\x01" + nid + "\x01", f"{{注{len(fn)}}}")
            s = re.sub(r"\x01\w+\x01", "", s)
            if "a2" not in divs: inter = False                            # 插话和页边金句排在同一种 a2 框里：INTERLUDE 开头的那一串是插话
            elif plain.startswith("INTERLUDE"): inter = True
            if cls == "img": mark = ""
            elif cls == "tr": mark = "{T} "
            elif "a2" in divs and inter: mark = "{I} "
            elif "a2" in divs: mark = "{S} "
            elif "a1" in divs:
                mark = "{B} "
                if cls.startswith("h") and len(plain) < 120: s = f"**{plain}**"
            elif cls.startswith("h") and plain.upper().startswith(("THE TRAP", "THE WAY OUT")): mark = "{B} "; s = f"**{plain}**"
            elif plain.startswith("INTERLUDE"): mark = "{I} "
            elif cls == "tx000" or re.match(r"Figure \d+\.", plain): mark = "{F} "
            elif i == 10: mark = "{Q} "                                   # 书前 Pirsig 的题词（一个文件）
            elif plain.startswith(("—", "— ")) and len(plain) < 160: mark = "{Q} "
            else: mark = ""
            k += 1; L.append(f"[{k}] {mark}{s}")
    L = mark_epigraphs(L)
    if heads: print(f"  {num}: 没找到的小标题 {heads}")
    if fn:
        L += ["", "## 注释"] + [f"[n{j}] {NOTE.get(nid, '（找不到）')}" for j, nid in enumerate(fn, 1)]
    return L, k, fn


EN, chap_rows, allnotes = {}, [], set()
for num, title, files in PLAN:
    L, k, fn = en_lines(num, files); EN[num] = L; allnotes |= set(fn)
    words = sum(len(re.sub(r"^\[\d+\] (\{\w\} )?", "", x).replace("*", "").split()) for x in L if re.match(r"\[\d+\]", x) and "{图" not in x)
    chap_rows.append(f"{num}\t{k}\t{words}\t{L[0][5:]}")
    print(f"{num}  {k:3d} 段  {words:6d} 词  注 {len(fn):2d}  {L[0][5:]}")
lost = set(NOTE) - allnotes
if lost: print("  正文里没链到的注：", sorted(lost))
open(os.path.join(OUT, "chapters.tsv"), "w", encoding="utf-8").write("章\t段数\t词数\t章名\n" + "\n".join(chap_rows) + "\n")

# 书末（译本没有）
B = []
for n in (24, 25, 26):
    for cls, divs, s, plain, notes in blocks(eread(n)):
        if plain in ("Thinking in Systems", "_____________"): continue
        B.append(("## " if cls.startswith("h") else "") + re.sub(r"\x01\w+\x01", "", s))
open(os.path.join(OUT, "back.txt"), "w", encoding="utf-8").write("\n".join(B) + "\n")

# ── 译本：calibre 从 AZW3 转的，h1 篇、h2 章、h3 小标题；p.block 缩进块，p.center 居中（图和图上的字），p.img 图注，p.note 译者注，p.right 署名 ──
Z = epub("calibre-zh")
zread = lambda n: Z.read(f"text/{n}.html").decode("utf-8")
ZPLAN = {"00": ["part0006", "part0003", "part0007_split_000", "part0007_split_001", "part0008", "part0009"],
         **{f"{c:02d}": [f"part{c + 9:04d}"] for c in range(1, 8)},
         "08": ["part0017_split_000", "part0017_split_001", "part0018", "part0019", "part0020", "part0021"],
         "front": ["part0002", "part0004"], "back": ["part0022"]}
zt = lambda x: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"<br[^>]*>", " ", x)))).strip()
ZH = {}
for num, files in ZPLAN.items():
    L, notes = [], []
    for f in files:
        src = zread(f); src = src[src.index("<body"):]
        for m in re.finditer(r'<(h[1-4]|p)\b([^>]*)>(.*?)</\1>', src, re.S):
            tag, attrs, inner = m.groups()
            cls = (re.search(r'class="([^"]*)"', attrs) or [None, ""])[1]
            imgs = re.findall(r'<img[^>]*src="([^"]+)"', inner)
            inner = re.sub(r'<a id="w\d+"></a><a href="[^"]*#m(\d+)">.*?</a>', r"[译注\1]", inner)
            t = zt(inner)
            for im in imgs:
                L.append("{图：" + os.path.basename(im) + "}")
                tr = os.path.join(ROOT, "source/imgtext", "zh-" + os.path.splitext(os.path.basename(im))[0] + ".txt")
                if os.path.exists(tr): L += [x for x in open(tr, encoding="utf-8").read().splitlines() if x.startswith("{T}")]
            if not t: continue
            if tag == "h1":
                if re.match(r"第.部分|附录$", t): continue
                L.append(f"# {t}")
            elif tag == "h2": L.append(f"## {t}" if num == "08" else f"# {t}")   # 附录各篇是 h2
            elif tag in ("h3", "h4"): L.append(f"## {t}")
            elif cls == "note": notes.append(t)
            elif cls == "img": L.append("{F} " + t)
            elif cls == "center": L.append("{C} " + t)
            elif cls == "right": L.append("{R} " + t)
            elif cls == "block": L.append("{B} " + t)
            else: L.append(t)
    # 页眉一样的重复标题（引言、前言在文件开头各有一次）去掉
    L = [x for j, x in enumerate(L) if not (x.startswith("# ") and j and L[j - 1] == x)]
    ZH[num] = (L, notes)
for nm in ("front", "back"):
    open(os.path.join(OUT, "zh", f"{nm}.txt"), "w", encoding="utf-8").write("\n".join(ZH[nm][0]) + "\n")


# 图拷出来给作者看（勘误要对着两边的图核标签）：text/img/、text/zh/img/
for zf, pre, dst in ((E, "OEBPS/images/", "img"), (Z, "images/", "zh/img")):
    os.makedirs(os.path.join(OUT, dst), exist_ok=True)
    for n in zf.namelist():
        if n.startswith(pre) and not n.endswith("/"):
            open(os.path.join(OUT, dst, os.path.basename(n)), "wb").write(zf.read(n))


# ── 分节 ──
def sections(L, zh):
    items = []
    for x in L[1:]:
        if not x.strip(): continue
        if x.startswith("## 注释"): break
        m = re.match(r"(#{1,3}) (.*)$", x)
        if m and not (zh and m.group(1) == "#"): items.append(("H", len(m.group(1)), m.group(2)))
        elif zh and m: continue                      # 译本里的章题、前言 / 献词 / 引言的大标题
        else: items.append(("P", x))
    secs = []
    for it in items:
        if it[0] == "H":
            if secs and not secs[-1]["paras"]: secs[-1]["path"].append(it[2]); secs[-1]["lv"].append(max(it[1], 2))
            else: secs.append(dict(path=[it[2]], lv=[max(it[1], 2)], paras=[]))
        else:
            if not secs: secs.append(dict(path=[], lv=[], paras=[]))
            secs[-1]["paras"].append(it[1])
    # 章首只有题词的，并进下一节
    if len(secs) > 1 and not secs[0]["path"] and all(re.match(r"(\[\d+\] )?\{[QBC]\}", p) for p in secs[0]["paras"]):
        secs[1]["paras"] = secs[0]["paras"] + secs[1]["paras"]; secs.pop(0)
    return secs


def write_secs(head, secs, tail):
    out = [head, ""]
    for k, s in enumerate(secs, 1):
        path, lv = (s["path"], s["lv"]) if s["path"] else (["（章首）"], [2])
        for j, h in enumerate(path):
            out.append("#" * lv[j] + " " + (f"§{k} " if j == len(path) - 1 else "") + h)
        out += s["paras"]
    return "\n".join(out + tail) + "\n"


def zh_00(L):
    """译本 00：前言、献词、引言各自的 # 标题当节；引言的「# 引言 系统多棱镜」下面紧跟 ## 无处不在的系统。"""
    out = []
    for x in L:
        if x in ("# 前言", "# 献词 献给世界的复杂性"): out.append("#" + x)
        elif x == "# 引言 系统多棱镜": out.append("## （引言）无处不在的系统")
        elif x == "# 无处不在的系统": continue
        elif x in ("# 重塑系统，发现更大的世界", "# 找到属于你的系统之美"): out.append("## （引言）" + x[2:])
        elif x.startswith("# "): continue
        else: out.append(x)
    return ["# 00 正文前和引言"] + out


rows, bad = [], []
for num in EN:
    L = EN[num]; Lz, znotes = ZH[num]
    if num == "00": Lz = zh_00(Lz)
    if num == "08": Lz = ["# 附录"] + Lz
    es, zs = sections(L, False), sections(Lz, True)
    print(f"  {num}: 原书 {len(es)} 节，译本 {len(zs)} 节" + ("" if len(es) == len(zs) else "  ← 对不上"))
    if len(es) != len(zs):
        bad.append(num)
        for j in range(max(len(es), len(zs))):
            a = " › ".join(es[j]["path"]) if j < len(es) else "—"; b = " › ".join(zs[j]["path"]) if j < len(zs) else "—"
            print(f"      §{j + 1}  {a[:50]:50s} | {b}")
        continue
    foot = L[L.index("## 注释") - 1:] if "## 注释" in L else []
    ztail = (["", "## 译者注"] + znotes) if znotes else []
    open(os.path.join(OUT, f"{num}.txt"), "w", encoding="utf-8").write(write_secs(L[0], es, foot))
    zhead = Lz[0]
    open(os.path.join(OUT, "zh", f"{num}.txt"), "w", encoding="utf-8").write(write_secs(zhead, zs, ztail))
    for k, (e, z) in enumerate(zip(es, zs), 1):
        ps = [int(m.group(1)) for p in e["paras"] for m in [re.match(r"\[(\d+)\]", p)] if m]
        body = [re.sub(r"^\[\d+\] (\{\w\} )?", "", p) for p in e["paras"] if re.match(r"\[\d+\]", p) and "{图" not in p]
        w = sum(len(b.replace("*", "").split()) for b in body)
        first = next((re.sub(r"^\[\d+\] ", "", p) for p in e["paras"] if re.match(r"\[\d+\] [^{]", p)), body[0] if body else "")
        zb = [p for p in z["paras"] if not p.startswith("{")]
        zw = sum(len(re.findall(r"[一-鿿]", p)) for p in z["paras"])
        rows.append("\t".join([num, str(k), f"{min(ps)}–{max(ps)}" if ps else "", str(w), " › ".join(e["path"]) or "（章首）",
                               " › ".join(z["path"]) or "（章首）", " ".join(re.sub(r"\{注\d+\}|\*", "", first).split()[:6]),
                               str(zw), zb[0][:16] if zb else ""]))
open(os.path.join(OUT, "index.tsv"), "w", encoding="utf-8").write("章\t节\t段\t词\t原书小标题\t译本小标题\ten\t字\tzs\n" + "\n".join(rows) + "\n")
print(f"index.tsv：{len(rows)} 节" + (f"；对不上的章 {bad}" if bad else ""))
