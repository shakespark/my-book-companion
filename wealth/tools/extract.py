#!/usr/bin/env python3
"""从书库的 EPUB 提取《国富论》原文和杨敬年译本，写到 source/text/。

英文：Cannan 版（Liberty Fund 在线图书馆的 EPUB，source/calibre 上册、source/calibre-v2 下册）。
  source/text/<章>.txt，章号形如 1-01（卷一第 1 章）、2-00（卷二引言）、0-00（全书引言和计划）。
  每行一段：[段号] 正文。段号一章之内连续。
  {M:…} 是 Cannan 的页边小结，插在它在原书里的位置；{nK} 是脚注号（K 一章之内连续）。
  ## 开头的行是章内的小标题（PART I、Digression……）。
  章末「## 注」下面是脚注：[nK] {S} 斯密自己的注，{C} Cannan 的编者注（原书用方括号括起的）。
  表格每行一个 {T} 开头的段。
中文：杨敬年译本（source/calibre-zh）。
  source/text/zh/<章>.txt：正文，每行一段，不编段号；{M} 开头的行是混在正文里的小标题（Cannan 页边小结的译文，脚本按「短、句末没有标点」认的）；
  ［K］是译注号，章末「## 译注」。
  source/text/zh/daodu/<章>.txt：各编、各章前面的「导读」；source/text/zh/front.txt：译者导言等书前材料。
另写 source/text/index.tsv：章号、英文章名、杨译章名、英文词数、译本汉字数、小标题和它们的段号范围。

运行：python3 -I tools/extract.py
"""
import html
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source"
OUT = SRC / "text"

ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10, "XI": 11}


def epub_main(path):
    z = zipfile.ZipFile(path)
    name = [n for n in z.namelist() if n.startswith("Smith_0206")][0]
    return z.read(name).decode("utf-8")


def clean_inline(s):
    """一段 HTML → 纯文字，保留 {M:…} 和 {nK} 标记。"""
    s = re.sub(r'<span class="pb">.*?</span></span>', "", s)  # 页码
    s = re.sub(r'<span class="type-margin"><span>(.*?)</span></span>', lambda m: "{M:" + re.sub(r"<[^>]+>", "", m.group(1)).strip() + "}", s)
    s = re.sub(r'<a href="#([^"]+)" id="[^"]+_ref" class="footnote-link type-footnote">[^<]*</a>', lambda m: "{fn:" + m.group(1) + "}", s)
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def split_chapters(doc):
    """按 h2 切块：返回 [(kind, title, body_html)]，kind 是 div 的 class。"""
    heads = list(re.finditer(r'<div id="[^"]+" class="(type-[a-z]+)">\s*<h2[^>]*>(.*?)</h2>', doc))
    out = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(doc)
        title = re.sub(r"<a [^>]*>.*?</a>", "", m.group(2))
        title = html.unescape(re.sub(r"<[^>]+>", "", title)).strip()
        out.append((m.group(1), title, doc[m.end():end]))
    return out


def chapter_key(book, kind, title):
    if kind == "type-introduction":
        return f"{book}-00"
    m = re.match(r"CHAPTER ([IVX]+)", title)
    if kind == "type-chapter" and m:
        return f"{book}-{ROMAN[m.group(1)]:02d}"
    return None


def parse_body(body, notes_map):
    """一章（含它的小节）的 HTML → 段落列表和脚注列表。"""
    paras = []
    for m in re.finditer(r'(<h2[^>]*>.*?</h2>)|<p(?: class="([^"]*)")? id="Smith_[^"]+">(.*?)</p>|<table.*?</table>', body, re.S):
        if m.group(1):
            t = re.sub(r"<a [^>]*>.*?</a>", "", m.group(1))
            paras.append(("h", re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()))
        elif m.group(0).startswith("<table"):
            for row in re.findall(r"<tr.*?</tr>", m.group(0), re.S):
                cells = [clean_inline(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
                cells = [c for c in cells if c]
                if cells:
                    paras.append(("t", " | ".join(cells)))
        else:
            paras.append(("p", m.group(3)))
    return paras


def load_notes(doc):
    notes = {}
    for m in re.finditer(r'<div id="([^"]+_footnote_nt\d+)" class="type-footnote note">(.*?)</div>', doc, re.S):
        body = re.sub(r"^<a [^>]*>[^<]*</a>", "", m.group(2).strip())
        notes[m.group(1)] = clean_inline(body)
    return notes


def strip_notes(doc):
    return re.sub(r'<div id="[^"]+_footnote_nt\d+" class="type-footnote note">.*?</div>', "", doc, flags=re.S)


def english():
    chapters = {}
    order = []
    book = 0
    for vol in ("calibre", "calibre-v2"):
        epub = next((SRC / vol).glob("*.epub"))
        doc = epub_main(epub)
        notes = load_notes(doc)
        doc = strip_notes(doc)
        cur = None
        for kind, title, body in split_chapters(doc):
            mb = re.match(r"BOOK ([IVX]+)", title)
            if mb:
                book = ROMAN[mb.group(1)]
                cur = None
                if kind == "type-section":  # 下册把卷五的标题标成了 section
                    pass
                continue
            if kind in ("type-preface", "type-appendix", "type-colophon", "type-toc"):
                cur = None
                continue
            if kind == "type-introduction" and title.startswith("EDITOR"):
                cur = None
                continue
            if kind == "type-introduction" and title.startswith("INTRODUCTION AND PLAN"):
                key = "0-00"
            else:
                key = chapter_key(book, kind, title)
            if key:
                cur = key
                chapters[key] = {"title": title, "paras": [], "notes": notes}
                order.append(key)
                chapters[key]["paras"] += parse_body(body, notes)
            elif cur and kind == "type-section":
                chapters[cur]["paras"].append(("h", title))
                chapters[cur]["paras"] += parse_body(body, notes)
    index = {}
    for key in order:
        ch = chapters[key]
        lines, fns, secs = [], [], []
        k = 0
        sec = {"t": "（章首）", "p0": 1, "w": 0}
        for typ, content in ch["paras"]:
            if typ == "h":
                if not content or re.match(r"CHAPTER ", content):
                    continue
                if sec["w"]:
                    sec["p1"] = k
                    secs.append(sec)
                sec = {"t": content, "p0": k + 1, "w": 0}
                lines.append("## " + content)
                continue
            text = content if typ == "t" else clean_inline(content)
            if not text:
                continue

            def fn(m):
                fns.append(ch["notes"].get(m.group(1), ""))
                return "{n%d}" % len(fns)

            text = re.sub(r"\{fn:([^}]+)\}", fn, text)
            k += 1
            lines.append(f"[{k}] " + ("{T} " if typ == "t" else "") + text)
            sec["w"] += len(re.findall(r"[A-Za-z’']+", re.sub(r"\{[^}]*\}", "", text)))
        sec["p1"] = k
        secs.append(sec)
        lines.append("## 注")
        for i, n in enumerate(fns, 1):
            tag = "{C}" if n.startswith("[") else "{S}"
            lines.append(f"[n{i}] {tag} {n}")
        (OUT / f"{key}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        words = sum(s["w"] for s in secs)
        index[key] = {"title": ch["title"], "words": words, "secs": secs}
    return order, index


# 杨译的 spine 文件 → 章号。按书里的顺序，标题行认章。
ZH_HEAD = re.compile(r"^第([一二三四五六七八九十]+)章\s*(.*)$")
CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11}


def zh_lines(s):
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"</(p|h\d|div|li)>", "\n", s)
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    return [l.strip() for l in s.split("\n") if l.strip() and l.strip() != "国富论"]


def is_margin(l):
    return len(l) <= 40 and not re.search(r"[。！？：；”」）\]］]$", l) and not l.startswith("［")


def chinese():
    epub = next((SRC / "calibre-zh").glob("*.epub"))
    z = zipfile.ZipFile(epub)
    opf = [n for n in z.namelist() if n.endswith(".opf")][0]
    root = ET.fromstring(z.read(opf))
    base = opf.rsplit("/", 1)[0] + "/" if "/" in opf else ""
    man = {i.get("id"): i.get("href") for i in root.iter("{http://www.idpf.org/2007/opf}item")}
    spine = [man[it.get("idref")] for it in root.iter("{http://www.idpf.org/2007/opf}itemref")]
    (OUT / "zh" / "daodu").mkdir(parents=True, exist_ok=True)
    book = 0
    front = []
    titles = {}
    chars = {}
    for h in spine:
        ls = zh_lines(z.read(base + h).decode("utf-8", "ignore"))
        if not ls:
            continue
        first = ls[0]
        mb = re.match(r"^第([一二三四五])编$", first)
        if first.endswith("导读") and "编导读" in first:
            book = "一二三四五".index(first[1]) + 1
            (OUT / "zh" / "daodu" / f"{book}-book.txt").write_text("\n".join(ls) + "\n", encoding="utf-8")
            continue
        if first.endswith("导读"):
            m = re.match(r"^(?:第(.+)章|前三章)导读$", first)
            key = f"{book}-01" if first.startswith("前三章") else f"{book}-{CN[m.group(1)]:02d}"
            (OUT / "zh" / "daodu" / f"{key}.txt").write_text("\n".join(ls) + "\n", encoding="utf-8")
            continue
        if mb:
            book = "一二三四五".index(mb.group(1)) + 1
            continue
        if first in ("引言和本书计划",):
            key, title = "0-00", first
            body = ls[1:]
        elif first.replace(" ", "") == "引言":
            key, title = f"{book}-00", "引言"
            body = ls[1:]
        elif ZH_HEAD.match(first):
            m = ZH_HEAD.match(first)
            key = f"{book}-{CN[m.group(1)]:02d}"
            if m.group(2):
                title, body = m.group(2), ls[1:]
            else:
                title, body = ls[1], ls[2:]
            title = re.sub(r"［\d+］", "", title).strip()
        else:
            if book == 0:
                front += ["#### " + h] + ls
            continue
        # 正文和译注分开：译注是章末以「［K］」开头的行
        k = len(body)
        while k > 0 and re.match(r"^［\d+］", body[k - 1]):
            k -= 1
        # 有的译注跨行，往回找第一处「［1］」开头的行
        first_note = next((i for i in range(len(body)) if re.match(r"^［1］", body[i]) and i > 0 and not re.match(r"^［", body[i - 1])), None)
        if first_note is not None and first_note < k:
            k = first_note
        text, notes = body[:k], body[k:]
        out = [("{M} " + l) if is_margin(l) else l for l in text]
        out.append("## 译注")
        out += notes
        (OUT / "zh" / f"{key}.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
        titles[key] = title
        chars[key] = len(re.findall(r"[一-鿿]", "".join(l for l in text if not is_margin(l))))
    (OUT / "zh" / "front.txt").write_text("\n".join(front) + "\n", encoding="utf-8")
    return titles, chars


def main():
    (OUT / "zh").mkdir(parents=True, exist_ok=True)
    order, index = english()
    titles, chars = chinese()
    rows = ["章\t英文章名\t杨译章名\t英文词数\t译本汉字数\t小标题（段号范围，词数）"]
    for key in order:
        e = index[key]
        secs = "；".join(f"{s['t']}（{s['p0']}–{s['p1']}，{s['w']}）" for s in e["secs"])
        rows.append(f"{key}\t{e['title']}\t{titles.get(key, '？')}\t{e['words']}\t{chars.get(key, 0)}\t{secs}")
    (OUT / "index.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    missing = [k for k in order if k not in titles] + [k for k in titles if k not in index]
    print(f"英文 {len(order)} 章，共 {sum(e['words'] for e in index.values())} 词；译本 {len(titles)} 章，共 {sum(chars.values())} 字")
    if missing:
        print("两边对不上的章：", missing)
        sys.exit(1)


if __name__ == "__main__":
    main()


def heilbroner():
    """《俗世哲人》第 2、3 章（经济革命、斯密）：只给 lint 和 overlap 查「别照抄海尔布罗纳」用，00 页也参考它。
    英文 source/text/wp-02.txt、wp-03.txt（overlap.py 会拿它们比 12 词重合）；中文 source/text/zh/wp-02.txt、wp-03.txt。"""
    def spine_text(path):
        z = zipfile.ZipFile(path)
        opf = [n for n in z.namelist() if n.endswith(".opf")][0]
        root = ET.fromstring(z.read(opf))
        base = opf.rsplit("/", 1)[0] + "/" if "/" in opf else ""
        man = {i.get("id"): i.get("href") for i in root.iter("{http://www.idpf.org/2007/opf}item")}
        lines = []
        for it in root.iter("{http://www.idpf.org/2007/opf}itemref"):
            lines += zh_lines(z.read(base + man[it.get("idref")]).decode("utf-8", "ignore"))
        return lines
    en = spine_text(next((SRC / "calibre-wp").glob("*.epub")))
    zh = spine_text(next((SRC / "calibre-wpzh").glob("*.epub")))
    def cut(lines, start, stop):
        i = max(k for k, l in enumerate(lines) if l == start)  # 目录里也有章名，取正文里那一次
        j = next(k for k in range(i + 1, len(lines)) if lines[k] == stop)
        return lines[i:j]
    (OUT / "wp-02.txt").write_text("\n".join(cut(en, "The Economic Revolution", "The Wonderful World of Adam Smith")) + "\n", encoding="utf-8")
    (OUT / "wp-03.txt").write_text("\n".join(cut(en, "The Wonderful World of Adam Smith", "The Gloomy Presentiments of Parson Malthus and David Ricardo")) + "\n", encoding="utf-8")
    zs = [l.replace("　", " ").strip() for l in zh]
    i2 = max(k for k, l in enumerate(zs) if l.startswith("第二章"))
    i3 = max(k for k, l in enumerate(zs) if l.startswith("第三章"))
    i4 = max(k for k, l in enumerate(zs) if l.startswith("第四章"))
    (OUT / "zh" / "wp-02.txt").write_text("\n".join(zs[i2:i3]) + "\n", encoding="utf-8")
    (OUT / "zh" / "wp-03.txt").write_text("\n".join(zs[i3:i4]) + "\n", encoding="utf-8")


if __name__ == "__main__" and "--wp" in sys.argv:
    heilbroner()
