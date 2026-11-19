#!/bin/sh
# 阅读包：把一位代理动笔前要读的东西切成小份，放进 source/pack/<页>/（source/ 不入库），打印清单。
#   sh tools/pack.sh <页>            作者的：公共规范、AUTHORING.md、样板页（去图和脚本）、LINE.md、这一页的底稿（拆页的章只给共用部分和自己那页）、
#                                    FIGS.md 里这一页的图、取图清单、这一页那几段的原文（01 加 Preface）；模拟器页加样板的模拟器脚本和 sim<样板>.mjs
#   sh tools/pack.sh --review <页>   审读员的：AUTHORING.md、LINE.md、作者报告、这一页（整页，含 SVG 和模拟器脚本）、原文那几段（01 加 Preface）
# 还不存在的文件（LINE.md、底稿、取图清单、样板页、报告）跳过并在最后提示。代理第一轮跑它，第二轮一条消息并行 Read 清单上全部文件。
# 页的段号范围从 assets/chapters.js（EG_PAGES 的 secs、EG_SECS 的 p）算。底稿 source/line/NN.md 里 `# 03a` 这样的一级标题下是那一页自己的，别的一级标题下是共用的。
# 切分用的是 ../_tools/pack.py（用法见它开头）。
cd "$(dirname "$0")/.." || exit 1
SAMPLE=02            # 样板页的页 id（F 步定）
mode=author; [ "$1" = "--review" ] && { mode=review; shift; }
id=$1; [ -n "$id" ] || { echo "用法：sh tools/pack.sh [--review] <页>"; exit 1; }
list=$(python3 -I - "$id" "$mode" "$SAMPLE" <<'PY'
import json, os, re, sys
pid, mode, sample = sys.argv[1:4]
js = open("assets/chapters.js", encoding="utf-8").read()
m = re.search(r'\{ id: "%s", ch: (\d+), secs: (\[[^\]]*\]), need: (\[[^\]]*\])' % re.escape(pid), js)
if not m: sys.exit("chapters.js 里没有页 " + pid)
ch, secs, need = int(m.group(1)), json.loads(m.group(2)), json.loads(m.group(3))
sm = re.search(r'"%02d": \[\n(.*?)\n  \]' % ch, js[js.index("window.EG_SECS"):], re.S)
if not secs or not sm: sys.exit(f"页 {pid} 还没有节（先写 source/SECS.tsv，再跑 tools/gen_chapters.py）")
rng = lambda p: tuple(map(int, p.split("–"))) if "–" in p else (int(p), int(p))
tab = {r["k"]: rng(r["p"]) for r in (json.loads(x.strip().rstrip(",")) for x in sm.group(1).splitlines())}
a, b = tab[secs[0]][0], tab[secs[-1]][1]
out, miss = [], []
def have(f, spec=None):
    if os.path.exists(f): out.append(spec or f)
    else: miss.append(f)

# 原文：[a] 到 [b+1] 之前（从第一段起的页带上章名行）；{F} 图注行跟着它前面的段
text = f"source/text/{ch:02d}.txt"
lines = open(text, encoding="utf-8").read().split("\n")
no = {int(x.group(1)): i for i, l in enumerate(lines, 1) if (x := re.match(r"\[(\d+)\] ", l))}
lo = 1 if a == 1 else no[a]
hi = no[b + 1] - 1 if b + 1 in no else len(lines)
while hi > lo and not lines[hi - 1].strip(): hi -= 1
src = [f"{text}:{lo}-{hi}"]   # Preface（00.txt）不归任何作者页，放在主编写的 00「开读之前」

# FIGS.md：章对得上，且正文提到它的段在 a–b 里，或者图注行落在这一页的原文里
figs = []
if os.path.exists("source/FIGS.md"):
    fl = open("source/FIGS.md", encoding="utf-8").read().split("\n")
    heads = [i for i, l in enumerate(fl, 1) if l.startswith("## ")]
    for n, i in enumerate(heads):
        h = re.match(r"## 图 \d+（章 (\d+)，第 (\d+) 行[^）]*）", fl[i - 1])
        if not h or int(h.group(1)) != ch: continue
        ps = [int(x) for x in re.findall(r"\[(\d+)\]", fl[i - 1].split("）")[0])]
        if any(a <= p <= b for p in ps) or lo <= int(h.group(2)) <= hi:
            end = heads[n + 1] - 1 if n + 1 < len(heads) else len(fl)
            figs.append(f"source/FIGS.md:{i}-{end}")
    if figs and heads: figs.insert(0, f"source/FIGS.md:1-{heads[0] - 1}")

# 底稿：一级标题 `# 03a` 这类是某一页的，只给自己那页；别的一级标题下（含开头）是共用的
line = f"source/line/{ch:02d}.md"
draft = []
if mode == "author" and os.path.exists(line):
    ll = open(line, encoding="utf-8").read().split("\n")
    h1 = [i for i, l in enumerate(ll, 1) if re.match(r"# ", l)]
    bounds = [1] + [i for i in h1 if i > 1] + [len(ll) + 1]
    keep = []
    for s, e in zip(bounds, bounds[1:]):
        pm = re.match(r"# (\d\d[a-z])\b", ll[s - 1])
        if pm and pm.group(1) != pid: continue
        if keep and keep[-1][1] == s - 1: keep[-1][1] = e - 1
        else: keep.append([s, e - 1])
    draft = [line] if keep == [[1, len(ll)]] else [f"{line}:{s}-{e}" for s, e in keep]
    if re.search(r"\d$", pid) is None and not any(re.match(r"# %s\b" % pid, l) for l in ll):
        print(f"注意：{line} 里没有「# {pid}」一级标题，整份给了", file=sys.stderr)
elif mode == "author": miss.append(line)

sim = any(x.startswith("sim") for x in need)
if mode == "author":
    out += [os.path.expanduser("~/tutorials-deploy/AUTHORING-COMMON.md"), "AUTHORING.md"]
    if pid != sample: have(f"chapters/{sample}.html", f"chapters/{sample}.html#html")
    have("source/LINE.md"); out += draft; out += figs; have(f"source/img/{pid}.md"); out += src
    if sim and pid != sample and os.path.exists(f"chapters/{sample}.html") and re.search(r"^<script>$", open(f"chapters/{sample}.html", encoding="utf-8").read(), re.M):
        out.append(f"chapters/{sample}.html@^<script>$..^</script>$"); have(f"tools/sim{sample}.mjs")
else:
    out.append("AUTHORING.md"); have("source/LINE.md"); have(f"source/reports/{pid}.md"); have(f"chapters/{pid}.html"); out += src
for f in miss: print(f"跳过（还没有）：{f}", file=sys.stderr)
print("\n".join(out))
PY
) || exit 1
out=source/pack/$id; [ $mode = review ] && out=source/pack/review-$id
rm -rf "$out"
printf '%s\n' "$list" | tr '\n' '\0' | xargs -0 python3 -I ../_tools/pack.py --out "$out"
