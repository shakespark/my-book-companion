#!/bin/sh
# 为一本书开导读目录：建 <目录名>/tools/（共用检查脚本的转调小壳）和 <目录名>/source/calibre（指向书库）。
# 用法：_tools/new-book.sh <目录名> <Calibre 书 id>      书 id 用 _tools/calibre.py find <关键词> 查
# 只建骨架，不写任何页面。
set -eu
[ $# -eq 2 ] || { sed -n '2,4p' "$0"; exit 2; }
slug=$1; id=$2
root=$(cd "$(dirname "$0")/.." && pwd)
tpl=$HOME/tutorials-deploy/templates
case $slug in _*|*[!a-z0-9_-]*|'') echo "目录名只能用小写字母、数字、- 和 _，且不以 _ 开头"; exit 2;; esac
[ ! -e "$root/$slug" ] || { echo "$slug/ 已存在"; exit 1; }
code=$(curl -s -o /dev/null -w '%{http_code}' "https://t.miaowuao.cn/$slug/")
[ "$code" = 404 ] || { echo "线上 /$slug/ 返回 $code，已被别的站占用，换个名字"; exit 1; }

mkdir -p "$root/$slug/tools"
cp "$tpl/check.mjs" "$tpl/overlap.py" "$tpl/fetch_img.py" "$root/$slug/tools/"
python3 "$root/_tools/calibre.py" link "$slug" "$id"
echo "已建 $slug/。下一步：按 ~/tutorials-deploy/PLAYBOOK.md 定策略，写 $slug/AUTHORING.md；localStorage 键前缀和同步白名单照 README「新增一本书」。"
