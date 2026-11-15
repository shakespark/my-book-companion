#!/bin/sh
# 铺开进度：每页的稿子、报告状态、验收、审读（报告里有「## 审读」就是审完）。node/python 都不用，新会话第一条命令跑它。
cd "$(dirname "$0")/.." || exit 1
printf '%-4s %-6s %-12s %-6s %s\n' 页 稿子 报告 验收 审读
for id in in 01a 01b 02a 02b 03 04a 04b 05a 05b 06a 06b 07 08; do
  page=—; [ -f "chapters/$id.html" ] && page=有
  rep=—; [ -f "source/reports/$id.md" ] && { l=$(head -1 "source/reports/$id.md"); case "$l" in 状态：*) rep=${l#状态：};; *) rep=有（无状态行）;; esac; }
  acc=—; grep -q "^| $id |" source/ACCEPTANCE.md && acc=收了
  rev=—; grep -q "^| $id |.*派出" source/ACCEPTANCE.md && rev=派出
  grep -q "^## 审读" "source/reports/$id.md" 2>/dev/null && rev=审完
  printf '%-4s %-6s %-12s %-6s %s\n' "$id" "$page" "$rep" "$acc" "$rev"
done
