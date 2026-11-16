#!/usr/bin/env python3
"""主编收稿：python3 -I tools/accept.py <页id> "<标题>" "<一句话>" —— 填 chapters.js 里这一页的 t、d，并把页加进 RP_READY。
00（开读之前）只加进 RP_READY：python3 -I tools/accept.py 00"""
import os, re, sys
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets/chapters.js")
pid = sys.argv[1]
s = open(p, encoding="utf-8").read()
if pid != "00":
    t, d = sys.argv[2:4]
    if len(t) > 10 or len(d) > 24: sys.exit(f"标题不超过 10 个字（现在 {len(t)}），一句话不超过 24 个字（现在 {len(d)}）")
    if '"' in t + d: sys.exit("标题和一句话里不能有英文直引号")
    s, n = re.subn(r'(\{ id: "%s",[^}]*?t: )"[^"]*", d: "[^"]*"' % re.escape(pid), lambda m: f'{m.group(1)}"{t}", d: "{d}"', s)
    if n != 1: sys.exit(f"RP_PAGES 里找不到页 {pid}")
m = re.search(r"window\.RP_READY = \[(.*?)\];", s)
ready = [x.strip().strip('"') for x in m.group(1).split(",") if x.strip()]
if pid not in ready: ready.append(pid)
order = ["00"] + re.findall(r'\{ id: "(\w+)", book:', s)
ready.sort(key=order.index)
s = s.replace(m.group(0), "window.RP_READY = [" + ", ".join(f'"{x}"' for x in ready) + "];")
open(p, "w", encoding="utf-8").write(s)
print("READY:", " ".join(ready))
