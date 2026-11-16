#!/bin/sh
# 进度：每页的译文、全文块、导读稿子、报告、验收、审读。新会话第一条命令跑它。页从 assets/chapters.js 读，往后加卷不用改这里。
#   译文：source/reports/tr-<页>.md 第一行的状态（没有报告但有 text/zh/<页>.txt 就是「有稿」）
#   全文块：页面里的全文块是不是最新的（tools/gen_text.py --check）
#   稿子：页面里还剩几节没写（p.wip）；报告：source/reports/<页>.md 第一行；验收、审读：source/ACCEPTANCE.md 里这一页那一行，报告里有「## 审读」就是审完
cd "$(dirname "$0")/.." || exit 1
printf '%-4s %-8s %-6s %-8s %-10s %-6s %s\n' 页 译文 全文块 稿子 报告 验收 审读
for id in 00 $(grep -o '{ id: "[0-9a-z]*", book:' assets/chapters.js | cut -d'"' -f2); do
  tr=—; [ -f "text/zh/$id.txt" ] && tr=有稿
  [ -f "source/reports/tr-$id.md" ] && { l=$(head -1 "source/reports/tr-$id.md"); tr=${l#状态：}; }
  blk=—; page=—
  if [ -f "chapters/$id.html" ]; then
    n=$(grep -c 'class="wip"' "chapters/$id.html"); [ "$n" -gt 0 ] && page="未写$n节" || page=写完
    if [ "$id" != 00 ]; then python3 -I tools/gen_text.py --check "$id" >/dev/null 2>&1 && blk=新 || blk=过期; fi
  fi
  rep=—; [ -f "source/reports/$id.md" ] && { l=$(head -1 "source/reports/$id.md"); case "$l" in 状态：*) rep=${l#状态：};; *) rep=有（无状态行）;; esac; }
  acc=—; grep -q "^| $id |" source/ACCEPTANCE.md 2>/dev/null && acc=收了
  rev=—; grep -q "^| $id |.*派出" source/ACCEPTANCE.md 2>/dev/null && rev=派出
  grep -q "^## 审读" "source/reports/$id.md" 2>/dev/null && rev=审完
  printf '%-4s %-8s %-6s %-8s %-10s %-6s %s\n' "$id" "$tr" "$blk" "$page" "$rep" "$acc" "$rev"
done
