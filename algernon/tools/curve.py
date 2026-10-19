#!/usr/bin/env python3
"""从提取好的小说文本（source/text/<页>.txt）算「查理的文字曲线」，写到 assets/curve.js（统计数，不含原文，可以部署）。
运行：source/.venv/bin/python -I tools/curve.py      （要 pyspellchecker 的英文词表：source/.venv/bin/pip install pyspellchecker）
每一条报告条目（分节地图的一个 §）一个点：
  miss   拼错的词占百分之几：不在词表里的小写词。书里大写出现过的人名地名不算；dont、im 这类丢了撇号的算错（查理早期就是这么写的）
  sent   平均每句多少词（按 . ! ? 断句）
  punct  每百词有几个逗号、分号、冒号、破折号
  long   九个字母以上的长词占百分之几
{Q} 段落（剪报、信、书里的书）不是查理写的，不算。assets/curve.js 是这个脚本生成的，不要手改。"""
import os, re, sys, unicodedata
from spellchecker import SpellChecker

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PAGES = ["01", "07", "09", "10", "11a", "11b", "12", "13a", "13b", "14a", "14b", "14c", "15", "16a", "16b", "16c", "17a", "17b"]
WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*")   # 带重音的字母（éclairs）也算在词里

entries = []   # (页, 节号, 报告, 日期, [段落文字…])
for pid in PAGES:
    for line in open(os.path.join(ROOT, f"source/text/{pid}.txt"), encoding="utf-8"):
        m = re.match(r"## §(\d+) 报告 (\d+) · (.*)$", line.rstrip("\n"))
        if m: entries.append((pid, int(m.group(1)), int(m.group(2)), m.group(3), [])); continue
        m = re.match(r"\[\d+\] (\{Q\} )?(.*)$", line.rstrip("\n"))
        if m and not m.group(1): entries[-1][4].append(m.group(2).replace("*", ""))

dic = SpellChecker()
# 词表里没有、但书里是正常写法的词（报告 10–16 里查出来的）：不算查理拼错
dic.word_frequency.load_words(["eclair", "eclairs", "retardate", "retardates", "cliche", "naivete", "lamplit", "gateleg", "uptilted",
    "psychophysical", "zagging", "photoeffect", "duncecap", "this'll", "what'd", "man'll",
    # 报告 14–17：书里正常的词、别人嘴里的话（Fay 的 cigareet、造词，喝醉时的 din't）、猴子叫声、连字符拆开的半个词（cul-de-sac、hi-fi、Mazel tov）、电子书断词（exten sion）
    "sneerer", "fairyish", "untidies", "upcurrent", "multipetaled", "undividing", "unclosing", "windowshade", "encl",
    "junkmobiles", "tincannia", "cigareet", "din't", "chee", "cheee", "cheeee", "cheeeee", "cul", "fi", "tov", "un", "exten"])
def known(w):
    w = unicodedata.normalize("NFKD", w.replace("’", "'")).encode("ascii", "ignore").decode()   # éclair → eclair
    return w in dic.word_frequency or (w.endswith("'s") and w[:-2] in dic.word_frequency)   # 所有格 men's、Donner's 不算错
# 全书里以大写开头、又不是词典词的（Kinnian、Nemur、Donner…），小写出现时也当专名，不算拼错
names = set()
for e in entries:
    for p in e[4]:
        for w in WORD.findall(p):
            if w[0].isupper() and not known(w.lower()): names.add(w.lower())

rows = []
for pid, k, r, date, paras in entries:
    text = " ".join(paras)
    ws = WORD.findall(text)
    if len(ws) < 20: continue
    low = [w for w in ws if not w[0].isupper() and w.lower() not in names]
    miss = sum(not known(w.lower()) for w in low) / max(1, len(low)) * 100
    sents = [s for s in re.split(r"[.!?]+", text) if WORD.search(s)]
    sent = len(ws) / max(1, len(sents))
    punct = len(re.findall(r"[,;:—]", text)) / len(ws) * 100
    long_ = sum(len(w) >= 9 for w in ws) / len(ws) * 100
    date = re.sub(r"（本站分）$", "", date)
    rows.append(f'  {{ p: "{pid}", s: {k}, r: {r}, d: "{date}", w: {len(ws)}, miss: {miss:.1f}, sent: {sent:.1f}, punct: {punct:.1f}, long: {long_:.1f} }}')

out = os.path.join(ROOT, "assets/curve.js")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w", encoding="utf-8").write(
    "// 查理的文字曲线：tools/curve.py 生成，不要手改。每条报告条目一个点。p 页 id，s 页内节号，r 报告号，d 日期，w 词数，\n"
    "// miss 拼错的词 %，sent 平均句长（词），punct 每百词的逗号分号冒号破折号，long 九个字母以上的长词 %。\n"
    "window.AL_CURVE = [\n" + ",\n".join(rows) + "\n];\n")
print(f"{len(rows)} 个点 → assets/curve.js")
for r in range(1, 18):
    sel = [x for x in rows if f" r: {r}," in x]
    vals = [re.search(r"miss: ([\d.]+), sent: ([\d.]+), punct: ([\d.]+), long: ([\d.]+)", x).groups() for x in sel]
    if vals: print(f"报告 {r:2d}  " + "  ".join(f"{n} {sum(float(v[i]) for v in vals) / len(vals):5.1f}" for i, n in enumerate(["拼错%", "句长", "标点", "长词%"])))
