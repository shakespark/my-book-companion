#!/usr/bin/env python3
"""从 Calibre 书库里的 epub（只读）提取文本到 source/text/。
  source/calibre/*.epub   David Blockley, Engineering: A Very Short Introduction（OUP 2012；Calibre 从 MOBI 转的，index_split_NNN.html）

产出：
  text/00.txt          Preface（含致谢），`# 00 Preface`，每行一段，行首 [段号]。
  text/01–06.txt       一章一个文件：`# NN 章名`，每行一段，行首 [段号]（每章连续编号）。原书章内没有小标题，分节由本站在 chapters.js 里按段号定。
  text/glossary.txt    书末 Glossary，一行一条：`词 — 释义`。
  text/refs.txt        书末 References（`## Chapter N` 分章，按出现顺序，没有页码和注号；有几条是作者的补充说明）和 Further reading。
  text/index.tsv       章、段数、词数（不含图注）、章名。

段落标记：{Q} 缩进的引文（原书的引文段，出处多在前后正文里）；{B} 方框（Box）里的段，方框标题行是 `{B} Box N 标题`；
{b:…} 方框里原书的粗体（Box 1 的六大门类）；{F} 图注，形如 `{F} 3. Timeline [img 00004]`（原书 20 张图，图不复刻）。*词* 是原书的斜体。
上标写成 ^（10^3、r^2），下标写成 _（T_1、q_2）；原书小型大写的 BC / AD 照写。"""
import glob, html, os, re, sys, zipfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "source/text")
e = glob.glob(os.path.join(ROOT, "source/calibre/*.epub"))
if len(e) != 1: sys.exit(f"source/calibre/ 里要正好一个 epub，现在是 {e}")
Z = zipfile.ZipFile(e[0])
read = lambda n: Z.read(n).decode("utf8")


def text(inner):
    s = re.sub(r"<br[^>]*>", " ", inner)
    s = re.sub(r"<sup[^>]*>(.*?)</sup>", lambda m: "^" + m.group(1) if len(m.group(1)) == 1 else "^(" + m.group(1) + ")", s, flags=re.S)
    s = re.sub(r"<sub[^>]*>(.*?)</sub>", r"_\1", s, flags=re.S)
    s = re.sub(r"<img[^>]*src=\"images/(\d+)\.[a-z]+\"[^>]*>", r"[img \1]", s)
    s = re.sub(r"</?em[^>]*>", "*", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = s.replace("**", "")  # 相邻斜体合并
    return re.sub(r"\s+", " ", s).strip()


def blocks(src):
    """按顺序给出 (类型, 文本)：p 正文、q 引文、b 方框、f 图注、i 只有图片的段。"""
    # 章里的 blockquote 只有第 1 章的 Box 1（外面包着 div.calibre_18），所以 blockquote 一律算方框
    for m in re.finditer(r'<(blockquote|p)( class="([^"]*)")?[^>]*>(.*?)</\1>', src, re.S):
        tag, cls, inner = m.group(1), m.group(3) or "", m.group(4)
        if tag == "blockquote":
            inner = re.sub(r"^\s*<p[^>]*>|</p>\s*$", "", inner.strip())
            if "Box " not in inner[:80]:   # Box 1 正文里的粗体（六大门类）标成 {b:…}
                inner = re.sub(r'<strong[^>]*>(.*?)</strong>', r"{b:\1}", inner, flags=re.S)
        s = text(inner)
        if not s: continue
        if re.fullmatch(r"\[img \d+\]", s): yield "i", s; continue
        if re.match(r'(<a[^>]*></a>)*\s*<strong class="calibre14">\d+\. ', inner): yield "f", s; continue
        if tag == "blockquote": yield "b", s; continue
        yield ("q" if cls == "calibre10" else "p"), s


os.makedirs(OUT, exist_ok=True)
rows = []
FILES = {0: "index_split_006.html", 1: "index_split_008.html", 2: "index_split_009.html", 3: "index_split_010.html",
         4: "index_split_011.html", 5: "index_split_012.html", 6: "index_split_013.html"}
for ch, fn in FILES.items():
    src = read(fn)
    h = re.search(r"<h2[^>]*>(.*?)</h2>", src, re.S)
    title = text(re.sub(r"^.*?<br[^>]*>", "", h.group(1), flags=re.S)) if ch else "Preface"
    src = src[h.end():]
    out, k, words, pend_img = [f"# {ch:02d} {title}"], 0, 0, None
    for typ, s in blocks(src):
        if typ == "i": pend_img = s; continue
        if ch == 0 and typ == "q": typ = "p"  # 序言整篇是 calibre10
        if typ == "f":
            line = "{F} " + s + (" " + pend_img if pend_img else "")
            pend_img = None
            out.append(line); continue
        k += 1
        mark = {"p": "", "q": "{Q} ", "b": "{B} "}[typ]
        out.append(f"[{k}] {mark}{s}")
        words += len(s.split())
    if pend_img: out.append("{F} " + pend_img)
    open(os.path.join(OUT, f"{ch:02d}.txt"), "w").write("\n".join(out) + "\n")
    rows.append(f"{ch:02d}\t{k}\t{words}\t{title}")
open(os.path.join(OUT, "index.tsv"), "w").write("章\t段\t词\t章名\n" + "\n".join(rows) + "\n")

# Glossary
src = read("index_split_014.html")
gl = []
for m in re.finditer(r'<p class="calibre_19">(?:<a></a>)?<strong[^>]*>(.*?)</strong>(.*?)</p>', src, re.S):
    head, rest = text(m.group(1)), text(m.group(2))
    two = re.match(r"([a-z]+) (.*)", rest)   # epub 只把两词词头的第一个词标了粗体（systems complexity、systems thinking、thermionic emission）
    if two and head in ("systems", "thermionic"): head, rest = f"{head} {two.group(1)}", two.group(2)
    gl.append(f"{head} — {rest}")
open(os.path.join(OUT, "glossary.txt"), "w").write("# Glossary\n" + "\n".join(gl) + "\n")

# References + Further reading
ref = ["# References"]
for fn, head in (("index_split_015.html", None), ("index_split_016.html", "# Further reading")):
    src = read(fn)
    if head: ref.append(head)
    src = src[re.search(r"</h2>", src).end():]
    for m in re.finditer(r'<(h3|p)( class="([^"]*)")?[^>]*>(.*?)</\1>', src, re.S):
        s = text(m.group(4))
        if not s: continue
        ref.append(f"## {s}" if m.group(1) == "h3" else s)
open(os.path.join(OUT, "refs.txt"), "w").write("\n".join(ref) + "\n")
print(f"提取 {len(rows)} 份正文、术语 {len(gl)} 条、参考 {len(ref)} 行 → source/text/")
