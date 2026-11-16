#!/usr/bin/env python3
"""与 Shorey 英译的长片段重合检查：python3 -I tools/overlap.py 文件…
实现在 ~/tutorials-deploy/scripts/overlap.py（所有伴读站共用），这里只是转调，并带上这本书的参数：
全书的底本都是公版，导读引原文不设上限，所以全文块（article.fulltext）和引用块（blockquote.quote）整块不查、引用不限处数和词数。
剩下查的是导读正文里有没有不加引用标记、整句照搬的英文（12 词以上）：不是版权问题，是写法问题，要么改成引用块，要么链到全文那一节。"""
import os, runpy, sys
for c in ("fulltext", "quote"):
    sys.argv += ["--skip-class", c]
if "--max-quotes" not in sys.argv: sys.argv += ["--max-quotes", "999"]
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.argv[1:] = [os.path.relpath(os.path.abspath(a), root) if os.path.exists(a) else a for a in sys.argv[1:]]
os.chdir(root)
runpy.run_path(os.path.expanduser("~/tutorials-deploy/scripts/overlap.py"), run_name="__main__")
