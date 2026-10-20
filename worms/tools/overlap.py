#!/usr/bin/env python3
"""与原书的英文长片段重合检查：python3 -I tools/overlap.py 文件… [--n 12]
实现在 ~/tutorials-deploy/scripts/overlap.py（所有伴读站共用），这里只是转调。本书每页至多 2 处引用；
<blockquote class="pd-orig">（达尔文、弗洛伊德的公有领域原文）不参与比对，出处由 tools/lint.py 对 source/pd/ 核对。"""
import os, runpy, sys
if "--max-quotes" not in sys.argv: sys.argv += ["--max-quotes", "2"]
sys.argv += ["--skip-class", "pd-orig"]
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.argv[1:] = [os.path.relpath(os.path.abspath(a), root) if os.path.exists(a) else a for a in sys.argv[1:]]
os.chdir(root)
runpy.run_path(os.path.expanduser("~/tutorials-deploy/scripts/overlap.py"), run_name="__main__")
