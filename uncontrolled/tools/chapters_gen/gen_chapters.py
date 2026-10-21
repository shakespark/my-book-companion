# 一次性：从 source/SECS.tsv 和 source/line/NN.md 的节表生成 assets/chapters.js 的节数据；之后 chapters.js 手工维护。
import os, re, sys, json
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..")
secs = {}
for row in open(f"{R}/source/SECS.tsv", encoding="utf-8").read().splitlines()[1:]:
    ch, k, p, w, t0, en = row.split("\t")
    a, b = p.split("–")
    secs.setdefault(ch, {})[int(k)] = dict(k=int(k), p=[int(a), int(b)], t=t0, en=en, w=int(w), tier="", line="")
for ch in list(secs):
    f = f"{R}/source/line/{ch}.md"
    if not os.path.exists(f): continue
    body = open(f, encoding="utf-8").read()
    tab = body.split("## 节", 1)[1].split("\n## ", 1)[0]
    rows = [r for r in tab.splitlines() if re.match(r"\| \d", r)]
    if ch == "00": secs[ch] = {}
    for r in rows:
        c = [x.strip() for x in r.strip("|").split("|")]
        k = int(c[0]); a, b = c[1].split("–")
        d = secs[ch].setdefault(k, dict(k=k, p=[int(a), int(b)], w=int(c[2]), en=c[7] if len(c) > 7 else ""))
        d.update(t=c[4], tier=c[5], line=c[6])
# 主编改的档和英文开头
OVR = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else {}
for key, v in OVR.items():
    ch, k = key.split("§"); secs[ch][int(k)].update(v)
out = []
for ch in sorted(secs):
    out.append(f'  "{ch}": [')
    for k in sorted(secs[ch]):
        s = secs[ch][k]
        out.append(f'    {{ k: {k}, p: [{s["p"][0]}, {s["p"][1]}], t: "{s["t"]}", en: "{s["en"]}", w: {s["w"]}, tier: "{s["tier"]}", line: "{s["line"]}" }},')
    out.append("  ],")
print("\n".join(out))
