#!/bin/sh
# 铺开进度：每页的稿子、报告状态、验收、审读（报告里有「## 审读」就是审完）。只用 sh 和 grep，新会话第一条命令跑它。
# 页表从 assets/chapters.js 的 EG_PAGES 读（00 是主编页，另列）。
cd "$(dirname "$0")/.." || exit 1
printf '%-4s %-6s %-12s %-6s %s\n' 页 稿子 报告 验收 审读
for id in 00 $(sed -n '/EG_PAGES/,/^\];/s/.*{ id: "\([0-9a-z]*\)".*/\1/p' assets/chapters.js); do
  page=—; [ -f "chapters/$id.html" ] && page=有
  rep=—; [ -f "source/reports/$id.md" ] && { l=$(head -1 "source/reports/$id.md"); case "$l" in 状态：*) rep=${l#状态：};; *) rep=有（无状态行）;; esac; }
  acc=—; grep -q "^| $id |" source/ACCEPTANCE.md 2>/dev/null && acc=收了
  rev=—; grep -q "^| $id |.*派出" source/ACCEPTANCE.md 2>/dev/null && rev=派出
  grep -q "^## 审读" "source/reports/$id.md" 2>/dev/null && rev=审完
  printf '%-4s %-6s %-12s %-6s %s\n' "$id" "$page" "$rep" "$acc" "$rev"
done
