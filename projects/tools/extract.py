#!/usr/bin/env python3
"""从 Calibre 书库里的 epub（source/calibre/*.epub，只读）提取文本到 source/text/NN.txt（01–07 = 第 1–7 章；序言并在 01 的最前面，记作 §0）。
这个 epub 是用户 2026-10-20 从 MOBI 转的，文字是扫描识别出来的：数字里混着字母（i98os、8o percent），
词粘在一起（asafull-time、somewhatornate），破折号成了连字符。文本照原样保留，不改错字，读者 Kindle 里看到的就是这些字。
章名和章号是图片；第 7 章开头一句的前几个字丢了（文本从 NTY-FOUR 起），读者那里也一样。

每个文件：`# NN 章名`；`## §k 节名` 是原书的小标题（k 在章内编号；章首到第一个小标题之间是 §1「（开头）」；01 的 §0 是序言）。每行一段，行首 [段号]（每章连续编号，01 从序言起算）。
段落标记：{Q} 缩进的引文（blockquote）；{CAP} 照片的图注；{IMG 00008} 书里的图片（照片、剪报、文件），
  后面跟着 source/imgtext/00008.txt 里的转写或描述（没有就只有标记）；`[· · ·]` 是花饰。
第 6 章末 `## 注` 是书后的脚注。全书的节目和词数另存 source/text/index.tsv。"""
import glob, html, os, re, sys, zipfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
epubs = glob.glob(os.path.join(ROOT, "source/calibre/*.epub"))
if len(epubs) != 1: sys.exit(f"source/calibre/ 里要正好一个 epub，现在是 {epubs}")
Z = zipfile.ZipFile(epubs[0])
read = lambda n: Z.read(n).decode("utf-8")

# index_split_004 是序言，005–011 是第 1–7 章，012 是索引（图片）和脚注
BODY = [f"index_split_{i:03d}.html" for i in range(4, 12)]  # BODY[0] 序言，BODY[n] 第 n 章
NOTES = "index_split_012.html"
TITLES = ["Preface", "Starting Out", "Rudderless and Drifting", "In the Army Now", "Heading West for Opportunity",
          "Heading East for Opportunity", "Teaching and Preaching", "Afterthoughts"]
CAPTION = {"calibre_15", "calibre_25", "calibre_42", "calibre_47", "calibre_77"}


def text(s):
    s = re.sub(r"<br\s*/?>", " ", s)
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    return re.sub(r"\s+", " ", s).strip()


def img_size(name):
    b = Z.read(name)
    i = 2
    while i < len(b):
        if b[i] != 0xFF: break
        m = b[i + 1]
        if m in (0xC0, 0xC1, 0xC2):
            return int.from_bytes(b[i + 7:i + 9], "big"), int.from_bytes(b[i + 5:i + 7], "big")
        i += 2 + int.from_bytes(b[i + 2:i + 4], "big")
    return 0, 0


out_dir = os.path.join(ROOT, "source/text")
os.makedirs(out_dir, exist_ok=True)
imgtext_dir = os.path.join(ROOT, "source/imgtext")
index, problems, allimgs = [], [], []

notes = [text(m.group(1)) for m in re.finditer(r"<p[^>]*>(.*?)</p>", read(NOTES), re.S)]
notes = [n for n in notes if n]

def parts(fname):
    body = read(fname)
    return body[body.find("<body"):]


for cno in range(1, 8):
    ctitle = TITLES[cno]
    # 第 1 章前面接上序言（§0）
    segs = [(BODY[0], 1, "Preface"), (BODY[1], 2, "（开头）")] if cno == 1 else [(BODY[cno], 2, "（开头）")]
    k, words = 0, 0
    lines, sec_titles, sec_words, sec_paras, first = [], [], [], [], len(segs) == 1
    for fname, skip, start in segs:
     nimg = 0
     sec_titles.append(start); sec_words.append(0); sec_paras.append(0)
     lines.append(f"## §{len(sec_titles) - (0 if first else 1)} {start}")
     for m in re.finditer(r"<(p|blockquote)([^>]*)>(.*?)</\1>", parts(fname), re.S):
         tag, attrs, inner = m.groups()
         cls = (re.search(r'class="([^"]+)"', attrs) or [None, ""])[1]
         imgs = re.findall(r'<img src="([^"]+)"', inner)
         t = text(inner)
         for src in imgs:
             nimg += 1
             if nimg <= skip:
                 continue  # 章首的章号图、章名图
             w, h = img_size(src)
             n = os.path.splitext(os.path.basename(src))[0]
             if w < 60 and h < 60 and t:
                 continue  # 首字下沉的字母（Buckley 专栏开头的 I），字母本身丢了，读者看到的是图
             if w < 200:
                 lines.append("[· · ·]"); continue
             k += 1
             f = os.path.join(imgtext_dir, n + ".txt")
             tr = open(f, encoding="utf-8").read().strip().replace("\n", " / ") if os.path.exists(f) else ""
             lines.append(f"[{k}] {{IMG {n}}} {tr}".rstrip())
             allimgs.append(f"{cno:02d}\t{n}\t{w}x{h}")
             sec_paras[-1] += 1
         if not t or (imgs and len(t) < 3): continue
         nw = len(t.split())
         head = cls == "calibre_14" or (cls == "calibre_16" and nw <= 10 and not t.startswith(("Source", "By ")))
         if head:
             sec_titles.append(t); sec_words.append(0); sec_paras.append(0)
             lines.append(f"## §{len(sec_titles) - (0 if first else 1)} {t}")
             continue
         k += 1
         mark = "{Q} " if tag == "blockquote" else "{CAP} " if (cls in CAPTION and nw < 30) or t.startswith("Source:") else ""
         words += nw; sec_words[-1] += nw; sec_paras[-1] += 1
         lines.append(f"[{k}] {mark}{t}")
    if 0 in sec_paras:
        problems.append(f"{cno:02d} 有空节：{[t for t, n in zip(sec_titles, sec_paras) if not n]}")
    head = [f"# {cno:02d} {ctitle}", ""]
    tail = (["", "## 注"] + notes) if cno == 6 else []
    open(os.path.join(out_dir, f"{cno:02d}.txt"), "w", encoding="utf-8").write("\n".join(head + lines + tail) + "\n")
    for j, (st, sw, sp) in enumerate(zip(sec_titles, sec_words, sec_paras), 1 if first else 0):
        index.append(f"{cno:02d}\t{j}\t{st}\t{sp}\t{sw}")
    print(f"{cno:02d}  {len(sec_titles):2d} 节  {k:3d} 段  {words:5d} 词  {ctitle}")

open(os.path.join(out_dir, "index.tsv"), "w", encoding="utf-8").write(
    "章\t节\t节名\t段数\t词数\n" + "\n".join(index) + "\n")
open(os.path.join(out_dir, "images.tsv"), "w", encoding="utf-8").write("章\t图\t尺寸\n" + "\n".join(allimgs) + "\n")
for p in problems: print("！", p)
