#!/usr/bin/env python3
"""从 Calibre 书库里的 epub（source/calibre/*.epub，只读）提取文本到 source/text/NN.txt（NN = 章号 01–10，10 是尾声）。
这个 epub 是扫描识别出来的（转自 MOBI）：没有斜体，破折号成了连字符，注号直接粘在句尾（antiquity.13），德文变音常丢。
文本照原样保留，不改错字，读者电子书里看到的就是这些字（.loc 要照抄）。

每个文件：`# NN 章名`；`## §k 节名 • 人名` 是原书目录里的一节（k 在章内编号，9 章共 50 节，尾声不分节）。每行一段，行首 [段号]（每章连续编号）。
段落标记：{Q} 缩进的引文（blockquote）；{IMG 00065} 排成图片的引文或诗，读者电子书里也是图片、搜不到，
  后面跟着 source/imgtext/00065.txt 里的转写（没有转写就只有标记）；`[· · ·]` 是节内的花饰分隔。
章末 `## 注` 是书后尾注里这一章的部分（注号照原书）。全书的节目和词数另存 source/text/index.tsv。"""
import glob, html, os, re, sys, zipfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
epubs = glob.glob(os.path.join(ROOT, "source/calibre/*.epub"))
if len(epubs) != 1: sys.exit(f"source/calibre/ 里要正好一个 epub，现在是 {epubs}")
Z = zipfile.ZipFile(epubs[0])
read = lambda n: Z.read(n).decode("utf-8")

# 正文：index_split_004–013 依次是第 1–9 章和第 10 章（尾声）；003 是目录页，014 是尾注。
BODY = [f"index_split_{i:03d}.html" for i in range(4, 14)]
TOC, NOTES = "index_split_003.html", "index_split_014.html"


def text(s):
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    return re.sub(r"\s+", " ", s).strip()


def key(s):
    return re.sub(r"[^A-Z]", "", s.upper())


def img_size(name):
    # 宽图（590 宽）是排成图片的引文；窄图（一百来像素）是花饰
    b = Z.read(name)
    i = 2
    while i < len(b):
        if b[i] != 0xFF: break
        m = b[i + 1]
        if m in (0xC0, 0xC1, 0xC2):
            return int.from_bytes(b[i + 7:i + 9], "big"), int.from_bytes(b[i + 5:i + 7], "big")
        i += 2 + int.from_bytes(b[i + 2:i + 4], "big")
    return 0, 0


# 目录页：「数字 章名」起一章，「节名 • 人名」是一节
chapters = []
prefix = "OEBPS/" if any(n.startswith("OEBPS/") for n in Z.namelist()) else ""
for m in re.finditer(r"<(p|blockquote)[^>]*>(.*?)</\1>", read(prefix + TOC), re.S):
    t = text(m.group(2))
    if re.match(r"\d+ [A-Z]", t):
        chapters.append((t.split(" ", 1)[1], []))
    elif "•" in t and chapters:
        title, who = (x.strip() for x in t.split("•", 1))
        chapters[-1][1].append((title, who))
    elif t in ("Notes", "Index"):
        break
assert len(chapters) == 10 and chapters[-1][0].startswith("EPILOGUE"), [c[0] for c in chapters]
assert sum(len(c[1]) for c in chapters) == 50, [(c[0], len(c[1])) for c in chapters]
out_dir = os.path.join(ROOT, "source/text")
os.makedirs(out_dir, exist_ok=True)
imgtext_dir = os.path.join(ROOT, "source/imgtext")
index, problems = [], []

# 尾注：按章名（全大写那一行）切开
notes_txt = [text(m.group(1)) for m in re.finditer(r"<p[^>]*>(.*?)</p>", read(prefix + NOTES), re.S)]
notes, cur = {}, 0
for t in notes_txt:
    if not t or t.startswith("Chapter "): continue
    hit = [i for i, (ct, _) in enumerate(chapters, 1) if key(t) == key(ct)]
    if hit: cur = hit[0]; notes[cur] = []; continue
    if cur: notes[cur].append(t)

for cno, fname in enumerate(BODY, 1):
    ctitle, secs = chapters[cno - 1]
    body = read(prefix + fname)
    body = body[body.find("<body"):]
    lines, k, sec, words, si = [], 0, 0, 0, 0
    sec_words, sec_paras = [], []
    if not secs:  # 尾声没有分节
        sec = 1; lines.append("## §1 " + ctitle.title()); sec_words.append(0); sec_paras.append(0)
    for m in re.finditer(r"<(p|blockquote)([^>]*)>(.*?)</\1>", body, re.S):
        tag, attrs, inner = m.groups()
        imgs = re.findall(r'<img src="([^"]+)"', inner)
        t = text(inner)
        if imgs and not t:
            for src in imgs:
                w, h = img_size(prefix + src)
                n = os.path.splitext(os.path.basename(src))[0]
                if w < 300:
                    lines.append("[· · ·]"); continue
                if k == 0 and sec <= 1 and not lines[1:]:
                    continue  # 章首的章名图
                k += 1
                f = os.path.join(imgtext_dir, n + ".txt")
                tr = open(f, encoding="utf-8").read().strip().replace("\n", " / ") if os.path.exists(f) else ""
                lines.append(f"[{k}] {{IMG {n}}} {tr}".rstrip())
                if sec: sec_paras[-1] += 1
            continue
        if not t or re.fullmatch(r"\w", t): continue  # 空段、识别成单个字符的章号
        if si < len(secs) and key(t).startswith(key(secs[si][0])[:25]):
            title, who = secs[si]
            si += 1; sec += 1
            lines.append(f"## §{sec} {title} • {who}")
            sec_words.append(0); sec_paras.append(0)
            continue
        if not sec:
            problems.append(f"{cno:02d} 第一节标题之前有正文：{t[:60]}")
            sec = 1; lines.append("## §1 ?"); sec_words.append(0); sec_paras.append(0)
        k += 1
        n = len(t.split()); words += n; sec_words[-1] += n; sec_paras[-1] += 1
        lines.append(f"[{k}] {'{Q} ' if tag == 'blockquote' else ''}{t}")
    if si < len(secs):
        problems.append(f"{cno:02d} 没找到的节：{[s[0] for s in secs[si:]]}")
    name = ctitle.title() if cno < 10 else "Epilogue on the Sense of Time"
    head = [f"# {cno:02d} {name}", ""]
    tail = ["", "## 注"] + notes.get(cno, [])
    open(os.path.join(out_dir, f"{cno:02d}.txt"), "w", encoding="utf-8").write("\n".join(head + lines + tail) + "\n")
    titles = [s[0] for s in secs] or [name]
    for j, (st, sw, sp) in enumerate(zip(titles, sec_words, sec_paras), 1):
        index.append(f"{cno:02d}\t{j}\t{st}\t{(secs[j - 1][1] if secs else '')}\t{sp}\t{sw}")
    print(f"{cno:02d}  {sec:2d} 节  {k:3d} 段  {words:5d} 词  {name}")

open(os.path.join(out_dir, "index.tsv"), "w", encoding="utf-8").write(
    "章\t节\t节名\t人名\t段数\t词数\n" + "\n".join(index) + "\n")
for p in problems: print("！", p)
