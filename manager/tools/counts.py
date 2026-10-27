#!/usr/bin/env python3
"""数全站的条目，给首页卡片的标签用：python3 -I tools/counts.py"""
import glob, re
n = {"页": 0, "游戏卡": 0, "概念": 0, "译本勘误": 0, "今天怎么看": 0, "看法": 0, "关键句": 0, "理解题": 0, "照片": set()}
for f in sorted(glob.glob("chapters/0[1-5]*.html")):
    t = open(f, encoding="utf-8").read(); n["页"] += 1
    n["游戏卡"] += t.count('<div class="game"'); n["概念"] += t.count('<div class="concept"'); n["译本勘误"] += t.count('<div class="zherr"')
    n["今天怎么看"] += t.count('<div class="today"'); n["看法"] += t.count('<div class="views">'); n["关键句"] += t.count('<div class="entry"')
    n["理解题"] += len(re.findall(r'class="check"', t)); n["照片"] |= set(re.findall(r'src="\.\./assets/img/([^"]+)"', t))
n["照片"] = len(n["照片"])
print(n)
