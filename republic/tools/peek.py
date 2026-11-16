#!/usr/bin/env python3
"""主编验收用：打印一页的几节正文（去标签，跳过全文块）。python3 -I tools/peek.py chapters/01a.html [节名…]
节名写 h2 的全名（「读完：论证路线」），不给就看「读完：论证路线」「今天怎么看」「本站怎么看」。看全文的某几节用 --text 起 止（如 --text 331a 331d），只打中文。"""
import re, sys
t = open(sys.argv[1], encoding="utf-8").read()
args = sys.argv[2:]
if args[:1] == ["--text"]:
    a, b = args[1], args[2] if len(args) > 2 else args[1]
    on = False
    for m in re.finditer(r'<section class="st" id="s(\w+)">(.*?)</section>', t, flags=re.S):
        on = on or m.group(1) == a
        if on:
            zh = re.search(r'<div class="zh"[^>]*>(.*?)</div>', m.group(2), flags=re.S)
            print(f"[{m.group(1)}]", re.sub(r"\n\s*\n+", "\n", re.sub(r"<button[^>]*>(\w+)</button>", r"[\1]", re.sub(r"<(?!button|/button)[^>]+>", "", zh.group(1) if zh else "（只有英文）"))).strip())
        if m.group(1) == b: break
    sys.exit()
t = re.sub(r"<!-- TEXT:BEGIN.*?<!-- TEXT:END -->", "[全文块]", t, flags=re.S)
t = re.sub(r"<svg.*?</svg>|<script>.*?</script>|<!--.*?-->", "", t, flags=re.S)
names = args or ["读完：论证路线", "今天怎么看", "本站怎么看"]
for n in names:
    m = re.search(r"<h2[^>]*>" + re.escape(n) + "</h2>", t)
    if not m: continue
    j = t.find("<h2", m.end())
    body = re.sub(r'<li data-kind="([^"]+)">', r"\n[\1] ", t[m.end():j if j > 0 else len(t)])
    body = re.sub(r'<div class="today" data-verdict="([^"]+)">', r"\n【\1】", body)
    body = re.sub(r"<[^>]+>", " ", body)
    print("=====", n); print(re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", body)).strip())
