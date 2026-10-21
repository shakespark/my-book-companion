#!/usr/bin/env python3
"""与英文长片段的重合检查：python3 -I tools/overlap.py 文件…
实现在 ~/tutorials-deploy/scripts/overlap.py（所有伴读站共用），这里只是转调。
比对的是 source/text/*.txt：斯密原文（公版）和海尔布罗纳《俗世哲人》第 2、3 章（wp-02、wp-03，有版权）。
斯密的原文只能放在「原典」的 <blockquote class="pd-orig"> 里（那一块不参与比对，另由 lint 核对一字不差），别处不能有 12 词以上的连续原文；
海尔布罗纳的英文一处都不能长段照抄。本站不用 <blockquote class="quote">（斯密的话进原典），所以引用上限是 0。
中文和杨译、海尔布罗纳中译本的重合，由 tools/lint.py 查。"""
import os, runpy, sys
if "--max-quotes" not in sys.argv: sys.argv += ["--max-quotes", "0"]
if "--skip-class" not in sys.argv: sys.argv += ["--skip-class", "pd-orig"]
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.argv[1:] = [os.path.relpath(os.path.abspath(a), root) if os.path.exists(a) else a for a in sys.argv[1:]]
os.chdir(root)
runpy.run_path(os.path.expanduser("~/tutorials-deploy/scripts/overlap.py"), run_name="__main__")
