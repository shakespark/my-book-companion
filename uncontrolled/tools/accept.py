#!/usr/bin/env python3
"""主编收稿：python3 -I tools/accept.py <页id> "<标题>" "<一句话>" —— 填 chapters.js 里这一页的 t、d，并把页加进 UC_READY。"""
import os, re, sys
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets/chapters.js")
pid, t, d = sys.argv[1:4]
s = open(p, encoding="utf-8").read()
s, n = re.subn(r'(\{ id: "%s",.*?t: )"[^"]*", d: "[^"]*"' % re.escape(pid), lambda m: f'{m.group(1)}"{t}", d: "{d}"', s)
if n != 1 and pid != "00": sys.exit(f"UC_PAGES 里找不到页 {pid}")
m = re.search(r"window\.UC_READY = \[(.*?)\];", s)
ready = [x.strip().strip('"') for x in m.group(1).split(",") if x.strip()]
if pid not in ready: ready.append(pid)
order = ["00"] + re.findall(r'\{ id: "(\w+)", ch:', s)
ready.sort(key=order.index)
s = s.replace(m.group(0), "window.UC_READY = [" + ", ".join(f'"{x}"' for x in ready) + "];")
open(p, "w", encoding="utf-8").write(s)
print("READY:", " ".join(ready))
