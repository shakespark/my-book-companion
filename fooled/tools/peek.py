#!/usr/bin/env python3
"""主编验收用：打印一页的几节正文（去标签）。python3 -I tools/peek.py chapters/09.html [节名…]"""
import re, sys
t = open(sys.argv[1], encoding="utf-8").read()
t = re.sub(r"<svg.*?</svg>|<script>.*?</script>", "[图]", t, flags=re.S)
names = sys.argv[2:] or ["这一页在做什么", "读之前：这一页在全书的哪里", "这一页的路线", "读完：作者到底说了什么", "今天怎么看", "本站怎么看"]
for n in names:
    i = t.find(f"<h2>{n}</h2>")
    if i < 0: continue
    j = t.find("<h2>", i + 5)
    body = re.sub(r"<[^>]+>", "", t[i:j if j > 0 else len(t)])
    print("=====", n); print(re.sub(r"\n\s*\n+", "\n", body).strip())
