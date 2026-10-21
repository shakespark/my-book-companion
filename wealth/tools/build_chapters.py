#!/usr/bin/env python3
"""生成 assets/chapters.js（全站目录数据，wn.js 和 tools/lint.py 都从这里读）。不要手改 chapters.js，改输入再跑一遍：

- source/pages.json：页表（主编手改）。id、kind（core / light）、chs（这一页包含的原书章号）、part（一章拆几页时写哪一部分）、
  need（sim：必写模拟器）、t（本站标题，≤10 字）、d（一句话，≤24 字）；ready（已写好的页）；extra（主编页 00）。
- source/line/<页>.md 的「## 节」表：k、章、段、词、档、节名、en、zh（底稿代理写，主编改定）。可以多一列 line（这一节的作用，≤30 字）。
- source/text/index.tsv：章号、英文章名、杨译章名。

每节的英文词数 w 按段号从 source/text/<章>.txt 数；译本字数 zc 从 source/text/zh/<章>.txt 里这一节的地标数到下一节的地标（或章末）。
找不到地标、段号不连续的，报出来并以非零状态退出。

运行：python3 -I tools/build_chapters.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT = ROOT / "source" / "text"
LINE = ROOT / "source" / "line"

BOOKS = [
    {"n": 0, "t": "全书引言", "zh": "引言和本书计划", "s": ""},
    {"n": 1, "t": "卷一", "zh": "论劳动生产力改进的原因，兼论劳动产品在不同阶级的人民间自然分配的顺序", "s": "分工、价格、工资、利润、地租"},
    {"n": 2, "t": "卷二", "zh": "论资财的性质、积累和使用", "s": "资本怎样积累、怎样使用"},
    {"n": 3, "t": "卷三", "zh": "论各国财富增长的不同途径", "s": "罗马以后的欧洲经济史"},
    {"n": 4, "t": "卷四", "zh": "论各种政治经济学体系", "s": "驳重商主义，评重农学派"},
    {"n": 5, "t": "卷五", "zh": "论君主或国家的收入", "s": "政府该做什么，钱从哪来"},
]

ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10, "XI": 11}


def words(s):
    s = re.sub(r"\{M:[^}]*\}|\{n\d+\}|\{T\}", " ", s)
    return len(s.split())


def load_en(ch):
    paras = {}
    for line in (TEXT / f"{ch}.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("## 注"):
            break
        m = re.match(r"^\[(\d+)\] (.*)$", line)
        if m:
            paras[int(m.group(1))] = m.group(2)
    return paras


def load_zh(ch):
    out = []
    for line in (TEXT / "zh" / f"{ch}.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("## 译注"):
            break
        out.append(line)
    return out


def zh_find(lines, mark):
    """地标在第几行：{M} 小标题一字不差，或者正文行以它开头（地标末尾的 … 去掉）。"""
    key = mark.rstrip("…").rstrip(".").strip()
    for i, l in enumerate(lines):
        if l.startswith("{M} ") and l[4:].strip() == key:
            return i
    for i, l in enumerate(lines):
        body = l[4:] if l.startswith("{M} ") else l
        if body.startswith(key) or (len(key) >= 8 and key in body):
            return i
    return None


def cjk(lines):
    return len(re.findall(r"[一-鿿]", "".join(l for l in lines if not l.startswith("{M} "))))


def parse_line_table(path):
    rows = []
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^## 节\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return rows
    head = None
    for l in m.group(1).splitlines():
        if not l.startswith("|"):
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if head is None:
            head = cells
            continue
        if set(cells[0]) <= set("-: "):
            continue
        rows.append(dict(zip(head, cells)))
    return rows


def main():
    errs = []
    cfg = json.loads((ROOT / "source" / "pages.json").read_text(encoding="utf-8"))
    chapters = []
    for l in (TEXT / "index.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        key, en, zh = l.split("\t")[:3]
        b, n = map(int, key.split("-"))
        m = re.match(r"CHAPTER ([IVX]+): (.*)", en)
        en_t = m.group(2) if m else en
        en_t = en_t[:1] + en_t[1:].lower() if en_t.isupper() else en_t
        chapters.append({"key": key, "book": b, "n": n, "en": en_t, "zh": zh})
    secs = {}
    for p in cfg["pages"]:
        f = LINE / f"{p['id']}.md"
        if not f.exists():
            continue
        rows = parse_line_table(f)
        out = []
        for r in rows:
            try:
                k = int(r["k"])
                ch = r["章"]
                ab = [int(x) for x in re.split(r"[–-]", r["段"])]
                a, b = ab[0], ab[-1]
            except Exception as e:
                errs.append(f"{p['id']}: 节表这一行读不懂：{r}（{e}）")
                continue
            if ch not in p["chs"]:
                errs.append(f"{p['id']} §{k}: 章 {ch} 不在这一页的 chs 里")
                continue
            en = load_en(ch)
            w = sum(words(en.get(i, "")) for i in range(a, b + 1))
            missing = [i for i in range(a, b + 1) if i not in en]
            if missing:
                errs.append(f"{p['id']} §{k}: {ch} 没有第 {missing[:3]} 段")
            tier = r.get("档", "")
            if tier not in ("先读", "有空", "可跳过"):
                errs.append(f"{p['id']} §{k}: 档「{tier}」不是 先读 / 有空 / 可跳过")
            s = {"k": k, "ch": ch, "p": [a, b], "t": r.get("节名", ""), "en": r.get("en", "").rstrip("…").strip(), "zh": r.get("zh", ""), "w": w, "zc": 0, "tier": tier}
            if r.get("line"):
                s["line"] = r["line"]
            out.append(s)
        # 段号首尾相接（同一章之内）
        for x, y in zip(out, out[1:]):
            if x["ch"] == y["ch"] and y["p"][0] != x["p"][1] + 1:
                errs.append(f"{p['id']}: §{x['k']} 到 §{y['k']} 段号不连续（{x['p']} → {y['p']}）")
        # 译本字数：按地标切
        for ch in dict.fromkeys(s["ch"] for s in out):
            zl = load_zh(ch)
            these = [s for s in out if s["ch"] == ch]
            pos = []
            for s in these:
                i = zh_find(zl, s["zh"]) if s["zh"] else None
                if i is None:
                    errs.append(f"{p['id']} §{s['k']}: 杨译地标「{s['zh']}」在 zh/{ch}.txt 里找不到")
                pos.append(i)
            # 一章被拆到几页时，这一页的开头和结尾不一定是章首章尾：开头用第一节的地标，结尾用下一页第一节的地标
            first_en = min(s["p"][0] for s in these)
            for j, s in enumerate(these):
                start = pos[j] if pos[j] is not None else 0
                if j == 0 and first_en == 1:
                    start = 0
                end = None
                for q in pos[j + 1:]:
                    if q is not None:
                        end = q
                        break
                if end is None:
                    end = next_page_mark(cfg, p, ch, zl) or len(zl)
                s["zc"] = cjk(zl[start:end])
        secs[p["id"]] = out
    js = ["// 全站目录。tools/build_chapters.py 生成，不要手改：改 source/pages.json 或 source/line/<页>.md 的节表，再跑一遍。",
          "// WN_BOOKS 五卷；WN_CHAPTERS 原书的章（key 章号，en 英文章名，zh 杨译章名）；",
          "// WN_SECS 每页的节（k 节号，ch 章号，p 段号范围，t 本站节名，en 英文开头几个词，zh 杨译里的地标，w 英文词数，zc 杨译汉字数，tier 先读/有空/可跳过）；",
          "// WN_PAGES 页（kind core/light，chs 包含的章，need 必写的可省小节，t 标题，d 一句话）；WN_EXTRA 主编页；WN_READY 已写好的页。",
          "window.WN_BOOKS = " + json.dumps(BOOKS, ensure_ascii=False) + ";",
          "window.WN_CHAPTERS = [", *[f"  {json.dumps(c, ensure_ascii=False)}," for c in chapters], "];",
          "window.WN_SECS = {"]
    for pid, ss in secs.items():
        js.append(f'  "{pid}": [')
        js += [f"    {json.dumps(s, ensure_ascii=False)}," for s in ss]
        js.append("  ],")
    js += ["};", "window.WN_PAGES = ["]
    js += [f"  {json.dumps(p, ensure_ascii=False)}," for p in cfg["pages"]]
    js += ["];", "window.WN_EXTRA = " + json.dumps(cfg["extra"], ensure_ascii=False) + ";",
           "window.WN_READY = " + json.dumps(cfg["ready"]) + ";", ""]
    (ROOT / "assets" / "chapters.js").write_text("\n".join(js), encoding="utf-8")
    tot = {t: sum(s["zc"] for ss in secs.values() for s in ss if s["tier"] == t) for t in ("先读", "有空", "可跳过")}
    print(f"写了 {len(secs)} 页的节；先读 {tot['先读']} 字，有空 {tot['有空']} 字，可跳过 {tot['可跳过']} 字")
    for e in errs:
        print("✗", e)
    sys.exit(1 if errs else 0)


def next_page_mark(cfg, p, ch, zl):
    """同一章拆到下一页时，这一页在译本里到下一页第一节的地标为止。"""
    ids = [x["id"] for x in cfg["pages"]]
    i = ids.index(p["id"])
    if i + 1 >= len(ids):
        return None
    nxt = cfg["pages"][i + 1]
    if ch not in nxt["chs"]:
        return None
    f = LINE / f"{nxt['id']}.md"
    if not f.exists():
        return None
    rows = [r for r in parse_line_table(f) if r.get("章") == ch]
    if not rows:
        return None
    return zh_find(zl, rows[0].get("zh", ""))


if __name__ == "__main__":
    main()
