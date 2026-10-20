#!/usr/bin/env python3
"""从 Calibre 书库里的 epub（source/calibre/*.epub，只读）提取文本到 source/text/NN.txt（NN = 篇号 01–04）。
01 Prologue、02 Darwin Turns the Worm、03 The Death of Freud、04 Epilogue。这个 epub 是 Calibre 从 AZW3 转的，
有少量扫描识别的错字（in. the trees、heirarchy、a’continental），文本照原样保留，读者电子书里看到的就是这些字（.loc 要照抄）。

每个文件：`# NN 篇名`，然后 `> 题词` 一行；`## §k` 是原书的空行分隔（epub 里上边距 1em 的 noindent 段，没有小标题），
k 在篇内编号。每行一段，行首 [段号]（每篇连续编号）。
段落标记：{Q} 缩进的引文（blockquote，几段连着的引文各占一行）；{C} 引文后不缩进的段（原书里是同一段的接续，
本站仍单独编号）；{D} 剧本台词。*词* 是原书的斜体。全书的节目和词数另存 source/text/index.tsv。"""
import glob, html, os, re, sys, zipfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
epubs = glob.glob(os.path.join(ROOT, "source/calibre/*.epub"))
if len(epubs) != 1: sys.exit(f"source/calibre/ 里要正好一个 epub，现在是 {epubs}")
Z = zipfile.ZipFile(epubs[0])
read = lambda n: Z.read(n).decode("utf-8")

# 篇号 → (题词所在文件, 正文文件)
PARTS = [(f"text/part{i:04d}_split_000.html", f"text/part{i:04d}_split_001.html") for i in range(6, 10)]
QUOTE = {"blockquote", "blockquote1"}
DIALOG = {"calibre26", "calibre27", "calibre28"}


def clean(s):
    s = re.sub(r'<br[^>]*/>', " ", s)
    s = re.sub(r"<i[^>]*>(.*?)</i>", r"*\1*", s, flags=re.S)
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    s = re.sub(r"\s+", " ", s).strip()
    return s.replace("* *", " ").replace("**", "")


out_dir = os.path.join(ROOT, "source/text")
os.makedirs(out_dir, exist_ok=True)
index = []
for n, (head_f, body_f) in enumerate(PARTS, 1):
    h = read(head_f)
    title = clean(re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S).group(1))
    epi = [clean(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", h, re.S)]
    body = read(body_f)
    lines, k, sec, words, sw, sk = [f"# {n:02d} {title}", "> " + " — ".join(epi), ""], 0, 0, 0, 0, 0
    for m in re.finditer(r'<p class="([^"]+)"[^>]*>(.*?)</p>', body, re.S):
        cls, txt = m.group(1), clean(m.group(2))
        if not txt: continue
        if cls == "noindent":
            if sec: index.append(f"{n:02d}\t{sec}\t{sk}\t{sw}"); sw = sk = 0
            sec += 1
            lines.append(f"## §{sec}")
        k += 1; sk += 1; sw += len(txt.split()); words += len(txt.split())
        mark = "{Q} " if cls in QUOTE else "{D} " if cls in DIALOG else "{C} " if cls == "calibre25" else ""
        lines.append(f"[{k}] {mark}{txt}")
    index.append(f"{n:02d}\t{sec}\t{sk}\t{sw}")
    open(os.path.join(out_dir, f"{n:02d}.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"{n:02d}  {sec:2d} 节  {k:3d} 段  {words:5d} 词  {title}")

open(os.path.join(out_dir, "index.tsv"), "w", encoding="utf-8").write("篇\t节\t段数\t词数\n" + "\n".join(index) + "\n")
