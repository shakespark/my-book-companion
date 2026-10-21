import os, re, subprocess, sys
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..")
B = os.path.dirname(os.path.abspath(__file__))
secs = subprocess.run(["python3", "-I", f"{B}/gen_chapters.py", f"{B}/override.json"], capture_output=True, text=True, check=True).stdout
secs = re.sub(r"\[(\d+)\]\s*[–-]\s*\[(\d+)\]\s*", r"第 \1–\2 段", secs)
secs = re.sub(r"\[(\d+)\]\s*", r"第 \1 段", secs).replace("＝", " = ")
words = {}
for m in re.finditer(r'"(\d\d)": \[(.*?)\n  \]', secs, re.S):
    words[m.group(1)] = {int(k): int(w) for k, w in re.findall(r"k: (\d+),.*?w: (\d+),", m.group(2))}
PAGES = [("in", 0, [1, 2, 3, 4]), *[(f"{n:02d}", n, None) for n in range(1, 10)], ("10a", 10, [1, 2]), ("10b", 10, [3]),
         ("11a", 11, [1, 2]), ("11b", 11, [3, 4, 5]), ("12a", 12, [1, 2, 3]), ("12b", 12, [4, 5, 6, 7]), ("13", 13, None), ("14", 14, None),
         ("15a", 15, [1, 2]), ("15b", 15, [3, 4])]
SIM = {"01", "07", "08", "10b", "11a"}
old = open(f"{R}/assets/chapters.js", encoding="utf-8").read() if len(sys.argv) > 1 else ""
td = dict(re.findall(r'\{ id: "(\w+)",.*?t: "([^"]*)", d: "([^"]*)"', old) and [(i, (t, d)) for i, t, d in re.findall(r'\{ id: "(\w+)",.*?t: "([^"]*)", d: "([^"]*)"', old)])
lines = []
for pid, ch, ss in PAGES:
    ss = ss or sorted(words[f"{ch:02d}"])
    w = sum(words[f"{ch:02d}"][k] for k in ss)
    t, d = td.get(pid, ("", ""))
    need = '"sim"' if pid in SIM else ""
    lines.append(f'  {{ id: "{pid}", ch: {ch}, secs: [{", ".join(map(str, ss))}], need: [{need}], words: {w}, t: "{t}", d: "{d}" }},')
head = open(f"{B}/head.js", encoding="utf-8").read()
ready = re.search(r"window\.UC_READY = \[.*?\];", old)
js = head.replace("//SECS", secs.rstrip()).replace("//PAGES", "\n".join(lines)).replace("//READY", ready.group(0) if ready else "window.UC_READY = [];")
open(f"{R}/assets/chapters.js", "w", encoding="utf-8").write(js)
print("ok", len(lines), "pages")
