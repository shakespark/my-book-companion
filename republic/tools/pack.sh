#!/bin/sh
# 阅读包：把一位代理动笔前要读的东西切成小份，放进 source/pack/<页>/（source/ 不入库），打印清单。
#   sh tools/pack.sh <页>            导读作者的：公共规范、AUTHORING.md、GLOSSARY.md、样板页（去掉全文块、图和脚本）、LINE.md、这一页的取图清单、
#                                    这一页的 Shorey 正文和 Shorey 脚注（按斯特方节切准）、中文译文、译者报告、已有的路标
#   sh tools/pack.sh --review <页>   审读员的：AUTHORING.md、GLOSSARY.md、LINE.md、作者报告、这一页（去掉全文块）、路标、Shorey 正文和脚注、中文译文
# 还不存在的文件（LINE.md、取图清单、译文、报告、样板页）自动跳过。代理第一轮跑它，第二轮一条消息并行 Read 清单上全部文件。
# Jowett 不放（要对照时自己 grep source/text/jowett/NN.txt）。切分用 ../_tools/pack.py（用法见它开头），Shorey 按节切用 tools/gen_text.py --slice。
cd "$(dirname "$0")/.." || exit 1
SAMPLE=01a
mode=author; [ "$1" = "--review" ] && { mode=review; shift; }
id=$1; [ -n "$id" ] || { echo "用法：sh tools/pack.sh [--review] <页>"; exit 1; }
src=source/pack/.src/$id
python3 -I tools/gen_text.py --slice "$id" "$src" || exit 1
have() { [ -f "$1" ] && printf '%s\n' "${2:-$1}"; }
page() {   # 页面去掉全文块：全文块之前一份、之后一份（#html 去掉图和脚本）
  [ -f "chapters/$1.html" ] || return 0
  if grep -q '^<!-- TEXT:BEGIN' "chapters/$1.html"; then
    echo "chapters/$1.html@^<!doctype..^<!-- TEXT:BEGIN$2"; echo "chapters/$1.html@^<!-- TEXT:END$2"
  else echo "chapters/$1.html$2"; fi
}
if [ $mode = author ]; then
  list=$( { echo "$HOME/tutorials-deploy/AUTHORING-COMMON.md"; echo AUTHORING.md; echo GLOSSARY.md
            [ "$id" != $SAMPLE ] && page $SAMPLE "#html"
            have source/LINE.md; have source/img/$id.md
            have text/marks/$id.txt; echo "$src/shorey-$id.txt"; echo "$src/notes-$id.txt"
            have text/zh/$id.txt; have source/reports/tr-$id.md; } )
  out=source/pack/$id
else
  list=$( { echo AUTHORING.md; echo GLOSSARY.md; have source/LINE.md; have source/reports/$id.md
            page $id; have text/marks/$id.txt
            echo "$src/shorey-$id.txt"; echo "$src/notes-$id.txt"; have text/zh/$id.txt; } )
  out=source/pack/review-$id
fi
rm -rf "$out"
printf '%s\n' "$list" | tr '\n' '\0' | xargs -0 python3 -I ../_tools/pack.py --out "$out"
