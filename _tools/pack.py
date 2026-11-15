#!/usr/bin/env python3
"""阅读包：把代理动笔前要读的文件切成 Read 一次读得完的小份，放进一个目录，打印清单。

代理拿到清单后，在**一条消息里并行 Read 全部**，两三轮就读完；不要一轮 cat 一个文件
（超长输出会被截断存盘，还得再读一遍）。

用法：python3 -I _tools/pack.py --out <目录> [--max 15000] <条目>…
条目：
  路径                    整个文件
  路径:120-340            只要第 120–340 行
  路径@起..止             从第一处匹配「起」的行，到其后第一处匹配「止」的行之前（正则；止可省，到文件末尾）
                          例：source/text/03.txt@§1 ..§10    取 §1–§9
  条目末尾加 #html        HTML 页当样板读：去掉 <svg>、<script> 的内容和空行，只留结构和文字

输出文件按条目顺序编号（01-…、02-…），超过 --max（估算 token）的按行切成 .p1 .p2。
原书材料只出现在 --out 里：--out 要放在 scratchpad 或 source/ 下，不入库。
"""
import os, re, sys


def est(s):
    cjk = len(re.findall(r"[⺀-鿿豈-﫿＀-￯]", s))
    return int(cjk * 1.3 + (len(s) - cjk) / 3)


def load(spec):
    html = spec.endswith("#html")
    if html:
        spec = spec[:-5]
    path, rng, mark = spec, None, None
    if "@" in spec:
        path, mark = spec.split("@", 1)
    else:
        m = re.match(r"^(.*):(\d+)-(\d+)$", spec)
        if m:
            path, rng = m.group(1), (int(m.group(2)), int(m.group(3)))
    text = open(os.path.expanduser(path), encoding="utf-8").read()
    if html:
        text = re.sub(r"(<svg[^>]*>).*?(</svg>)", r"\1[图略]\2", text, flags=re.S)
        text = re.sub(r"(<script[^>]*>).*?(</script>)", r"\1[脚本略]\2", text, flags=re.S)
        text = re.sub(r"\n\s*\n+", "\n", text)
    lines = text.split("\n")
    if rng:
        lines = lines[rng[0] - 1:rng[1]]
    if mark is not None:
        a, _, b = mark.partition("..")
        i = next((k for k, l in enumerate(lines) if re.search(a, l)), None)
        if i is None:
            sys.exit(f"{path}: 找不到「{a}」")
        j = next((k for k in range(i + 1, len(lines)) if b and re.search(b, lines[k])), len(lines))
        lines = lines[i:j]
    return path, lines


def main():
    args = sys.argv[1:]
    out, cap, specs = None, 15000, []
    while args:
        a = args.pop(0)
        if a == "--out":
            out = args.pop(0)
        elif a == "--max":
            cap = int(args.pop(0))
        else:
            specs.append(a)
    if not out or not specs:
        sys.exit(__doc__)
    os.makedirs(out, exist_ok=True)
    made, total = [], 0
    for n, spec in enumerate(specs, 1):
        path, lines = load(spec)
        parts, cur, size = [], [], 0
        for l in lines:
            t = est(l) + 1
            if cur and size + t > cap:
                parts.append(cur)
                cur, size = [], 0
            cur.append(l)
            size += t
        if cur:
            parts.append(cur)
        base = re.sub(r"[^\w.-]+", "_", "_".join(os.path.normpath(path).split(os.sep)[-2:]))
        for k, p in enumerate(parts, 1):
            name = f"{n:02d}-{base}" + (f".p{k}" if len(parts) > 1 else "") + ".txt"
            body = "\n".join(p)
            with open(os.path.join(out, name), "w", encoding="utf-8") as f:
                f.write(f"【{spec}" + (f"　第 {k}/{len(parts)} 份" if len(parts) > 1 else "") + "】\n" + body + "\n")
            made.append((name, est(body)))
            total += est(body)
    print(f"阅读包 {len(made)} 份，约 {total:,} token。在一条消息里并行 Read 下面全部文件（不要 cat）：")
    for name, t in made:
        print(f"  {os.path.join(os.path.abspath(out), name)}　约 {t:,}")


if __name__ == "__main__":
    main()
