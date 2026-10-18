#!/usr/bin/env python3
"""从 Calibre 书库里的 epub（source/calibre/*.epub，只读）提取文本到 source/text/NN.txt（NN = 篇号 01–23，按原书顺序）。
每个文件：`# NN 篇名`，下一行 `> 第 k 部分 部分名`；`## §k p.页码` 是原书的分隔（epub 里的小花饰；没有分隔的篇只有 §1），
页码是这一节开头在原书纸本（Quercus 版 page-map）的页码。每行一段，行首 [段号]（每个文件内连续编号）。
段落标记：{Q} 缩进的引文或列表。*词* 是原书的斜体（多为法文）。全书的篇目和词数另存 source/text/index.tsv。"""
import glob, html, os, re, sys, zipfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
epubs = glob.glob(os.path.join(ROOT, "source/calibre/*.epub"))
if len(epubs) != 1: sys.exit(f"source/calibre/ 里要正好一个 epub，现在是 {epubs}")
Z = zipfile.ZipFile(epubs[0])

# 部分 → 篇所在的 epub 文件号（part00NN.xhtml）。0008、0013、0020、0026 是部分的扉页。
PARTS = [("The Winter Circus", range(9, 13)), ("Distant Errors", range(14, 20)),
         ("Lessons from Things", range(21, 26)), ("A Machine to Draw the World", range(27, 35))]
QUOTE = {"class_indentnumber", "class_indentnumber1"}
BREAK = {"class_image4"}
TITLE = {"class_h1", "class_h4"}

def clean(s):
    s = re.sub(r'<span class="class2">(.*?)</span>', r"*\1*", s, flags=re.S)
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    s = re.sub(r"\s+", " ", s).strip()
    return s.replace("* *", " ").replace("**", "")

def title_case(s):
    # 篇名里的 CHRISTMAS JOURNAL 是全大写排版，和目录页的写法统一
    return re.sub(r"CHRISTMAS JOURNAL", "Christmas Journal", s)

out_dir = os.path.join(ROOT, "source/text")
os.makedirs(out_dir, exist_ok=True)
index, n = [], 0
for pi, (pname, files) in enumerate(PARTS, 1):
    for fno in files:
        n += 1
        t = Z.read(f"OEBPS/part{fno:04d}.xhtml").decode("utf-8")
        body = t[t.find("<body"):]
        page = (re.search(r'<body[^>]*id="page_(\d+)"', body) or re.search(r'id="page_(\d+)"', body)).group(1)
        lines, k, sec, words, title = [], 0, 1, 0, None
        sec_lines = [f"## §1 p.{page}"]
        lines.extend(sec_lines)
        for m in re.finditer(r'<span id="page_(\d+)"></span>|<div[^>]*class="([^"]+)"[^>]*>(.*?)</div>', body, flags=re.S):
            if m.group(1): page = m.group(1); continue
            cls, inner = m.group(2), m.group(3)
            if cls in TITLE: title = title_case(clean(inner)); continue
            if cls in BREAK:
                # 分隔之后的第一个分页标记可能就在下一段开头，页码取下一段第一个出现的
                nxt = re.search(r'id="page_(\d+)"', body[m.end():m.end() + 400])
                sec += 1; lines.append(f"## §{sec} p.{nxt.group(1) if nxt else page}"); continue
            # 段落开头就跨页的，用段落里第一个页码之前的那页
            txt = clean(inner)
            if not txt: continue
            k += 1; words += len(txt.split())
            lines.append(f"[{k}] {'{Q} ' if cls in QUOTE else ''}{txt}")
            last = re.findall(r'id="page_(\d+)"', inner)
            if last: page = last[-1]
        head = [f"# {n:02d} {title}", f"> 第 {pi} 部分 {pname}", ""]
        open(os.path.join(out_dir, f"{n:02d}.txt"), "w", encoding="utf-8").write("\n".join(head + lines) + "\n")
        index.append(f"{n:02d}\t{pi}\t{title}\t{sec}\t{k}\t{words}\tpart{fno:04d}")
        print(f"{n:02d}  第{pi}部分  {sec:2d} 节  {k:3d} 段  {words:5d} 词  {title}")

open(os.path.join(out_dir, "index.tsv"), "w", encoding="utf-8").write("篇号\t部分\t篇名\t节数\t段数\t词数\tepub 文件\n" + "\n".join(index) + "\n")
