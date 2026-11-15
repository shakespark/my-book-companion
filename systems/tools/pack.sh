#!/bin/sh
# 阅读包：把一位代理动笔前要读的东西切成小份，放进 source/pack/<页>/（source/ 不入库），打印清单。
#   sh tools/pack.sh <页>            作者的：公共规范、AUTHORING.md、样板页（去图和脚本）、LINE.md、这一章的底稿、这一页的取图清单、这一页那几节的原文和译本、章末注释；模拟器页加附录的模型方程、样板的模拟器脚本和 sim01a.mjs
#   sh tools/pack.sh --review <页>   审读员的：AUTHORING.md、LINE.md、作者报告、这一页（整页，含 SVG 和模拟器脚本）、原文和译本那几节、章末注释；模拟器页加附录的模型方程
# 还不存在的文件（LINE.md、底稿、取图清单、样板页）自动跳过。代理第一轮跑它，第二轮一条消息并行 Read 清单上全部文件。
# 切分用的是 ../_tools/pack.py（用法见它开头）。
cd "$(dirname "$0")/.." || exit 1
SAMPLE=01a
mode=author; [ "$1" = "--review" ] && { mode=review; shift; }
id=$1; [ -n "$id" ] || { echo "用法：sh tools/pack.sh [--review] <页>"; exit 1; }
# 页 → 章号、第一节、最后一节、这一章最后一节（从 assets/chapters.js 读）
set -- $(python3 -I - "$id" <<'PY'
import json, re, sys
js = open("assets/chapters.js", encoding="utf-8").read()
m = re.search(r'\{ id: "%s", ch: (\d+), secs: (\[[^\]]*\])' % re.escape(sys.argv[1]), js)
if not m: sys.exit("chapters.js 里没有页 " + sys.argv[1])
ch, secs = int(m.group(1)), [int(x) for x in json.loads(m.group(2))]
last = max(int(k) for k in re.findall(r'"k": "(\d+)"', re.search(r'"%02d": \[(.*?)\n  \]' % ch, js, re.S).group(1)))
print(f"{ch:02d}", secs[0], secs[-1], last)
PY
) || exit 1
ch=$1; a=$2; b=$3; last=$4
sim=$(grep -o "{ id: \"$id\", [^}]*need: \[[^]]*\"sim" assets/chapters.js)   # 模拟器页加附录的模型方程（08 §6）
en="source/text/$ch.txt@^#+ §$a ..^#+ §$((b+1)) |^## 注释"
zh="source/text/zh/$ch.txt@^## §$a ..^## §$((b+1)) |^## 译者注"
notes=""; grep -q '^## 注释' "source/text/$ch.txt" && notes="source/text/$ch.txt@^## 注释"
zhn=""; grep -q '^## 译者注' "source/text/zh/$ch.txt" && zhn="source/text/zh/$ch.txt@^## 译者注"
have() { [ -f "$1" ] && printf '%s\n' "$2"; }
if [ $mode = author ]; then
  list=$( { echo "$HOME/tutorials-deploy/AUTHORING-COMMON.md"; echo AUTHORING.md
            [ "$id" != $SAMPLE ] && have chapters/$SAMPLE.html "chapters/$SAMPLE.html#html"
            have source/LINE.md source/LINE.md; have source/line/$ch.md source/line/$ch.md; have source/img/$id.md source/img/$id.md
            echo "$en"; echo "$zh"; [ -n "$notes" ] && echo "$notes"; [ -n "$zhn" ] && echo "$zhn"
            [ -n "$sim" ] && echo "source/text/08.txt@^## §6 "
            [ -n "$sim" ] && [ "$id" != $SAMPLE ] && { echo "chapters/$SAMPLE.html@^<script>\$..^</script>\$"; echo tools/sim$SAMPLE.mjs; }
            [ -n "$sim" ] && for f in source/line/sim$id.py source/line/sim$ch.py; do have $f $f; done; } )
  out=source/pack/$id
else
  list=$( { echo AUTHORING.md; have source/LINE.md source/LINE.md; have source/reports/$id.md source/reports/$id.md
            have chapters/$id.html chapters/$id.html
            echo "$en"; echo "$zh"; [ -n "$notes" ] && echo "$notes"; [ -n "$sim" ] && echo "source/text/08.txt@^## §6 "
            [ -n "$sim" ] && for f in source/line/sim$id.py source/line/sim$ch.py; do have $f $f; done; } )
  out=source/pack/review-$id
fi
rm -rf "$out"
printf '%s\n' "$list" | tr '\n' '\0' | xargs -0 python3 -I ../_tools/pack.py --out "$out"
