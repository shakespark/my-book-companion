# Engineering: A Very Short Introduction · 导读

- 书：David Blockley, *Engineering: A Very Short Introduction*（Oxford University Press, 2012）。Calibre id **6148**（EPUB），`source/calibre`。
  书库里的 id 2226 是同一版的 MOBI（ASIN 相同），不用。
- 网址 https://t.miaowuao.cn/eng/ ，目录 `eng/`，localStorage 键前缀 `eg-`，共享脚本 `assets/eg.js`。骨架照 Systems（`systems/`：概念块、模拟器、英文词条、今天怎么看 / 本站怎么看、pack.sh），去掉译本；「书里的人和项目」照 Uncontrolled。
- 原书结构：Preface 加 6 章（1 From idea to reality；2–6 是重力、热、电磁、信息、系统五个「时代」），约 3.6 万词，每章 4200–6800 词；
  **章内没有小标题**，分节由本站按段号定。书末有 Glossary（35 条）、References（按章）、Further reading。全书 20 张图，1 个方框（第 1 章 Box 1）。

## 用户的回答（2026-11-19）

- 卡在哪：**机制和概念、英文语言、人物项目和历史背景、今天怎么看，四样都要**。
  - 机制和概念：力和能量、热机、电磁、信息、系统和风险，用「先用中文过一遍」的概念块，加几个能改参数的模拟器（全书定好数量）。
  - 英文：英文伴读，有词条，「记下」接跨书词本。
  - 背景：书里的工程师、发明和项目（桥、蒸汽机、电网……），配维基照片。
  - 今天怎么看：2012 年成书，讲之后的变化，加「本站怎么看」（记忆 views-with-commentary、reader-for-joy）。
- 怎么读：**英文 Kindle / 电子书**，不对着译本读，不做译本勘误。`.loc` 要和原文一字不差（读者会拿它搜）；词条只收词典帮不上忙的。
- 提前知道内容：**没坏处，不设分界线**；只有模拟器和题目先猜、答案折叠。
- 原书是商业出版物，全套版权红线。
- 部署：**到 I 步直接做，做完告诉用户**（首页卡片、同步白名单、接词本、推送；这个授权只管这一本书）。
- 样板和额度 B 步没另问，照仓库默认：F 步写完样板等用户认可再铺开；G＋H 一批 3–6 页、一批一个会话。

## 页表、怎么改、怎么验

- 页（`tools/gen_chapters.py` 的 `PAGES`）：`01`（第 1 章）、`02`、`03a`（[1–22]）`03b`（[23–38]）、`04a`（[1–25]）`04b`（[26–45]）、`05`、`06a`（[1–18]）`06b`（[19–35]）；`00` 开读之前是主编页，含 Preface 讲了什么。
- 模拟器 6 个：02 推秋千、03a 卡诺上限、04a 高压送电、05 蜂窝复用、06a 安全系数和失效概率、06b 瑞士奶酪。样板页 `chapters/02.html`（主编写）。小节十二个，见 `AUTHORING.md`。
- 节是本站分的（原书章内无小标题）：`source/SECS.tsv`（章 节 段 节名 档 line en，62 节，先读 35%）由底稿 `source/line/` 的 TSV 合并；改了跑 `python3 -I tools/gen_chapters.py`。`assets/chapters.js` 是生成的，不手改（t、d、`EG_READY` 由 `tools/accept.py` 填）。
- 每页三项检查：`python3 -I tools/lint.py`、`python3 -I tools/overlap.py`（引用上限 2）、`node tools/check.mjs`；模拟器页加 `node tools/sim<页>.mjs`。lint 的「？」是嫌疑，作者在报告里逐条答。
- 阅读包：`sh tools/pack.sh <页>`（作者）、`sh tools/pack.sh --review <页>`（审读员），输出在 `source/pack/`。进度：`sh tools/status.sh`；验收看节：`python3 -I tools/peek.py chapters/<页>.html`。

## 文件

- `tools/extract.py` → `source/text/00–06.txt`（`[k]` 每章段号；`{Q}` 引文、`{B}` 方框、`{F}` 图注带 `[img N]`；上标 `^`、下标 `_`）、
  `glossary.txt`、`refs.txt`、`index.tsv`。Box 1 里原书的粗体标成 `{b:…}`。`source/epub/` 是解开的 epub（`images/00003–00022.jpg` 是图 1–20），图的描述在 `source/FIGS.md`。
- 底稿 `source/line/01–06.md`（`source/LINE-TASK.md` 派的，不上页面；拆页的章按 `# 03a` 一级标题分页，`pack.sh` 只给作者自己那页）。
## 上线（2026-11-19）

- 首页卡片 `data-progress="eg-done-:10"`（9 页＋00），卡片标签里的条数：概念 43、人和工程 41、词条 163、今天 21、看法 25、理解题 63，增删要跟着改首页和 00 页的「今天怎么看」条数。
- 同步白名单 `eg-`（`sync.js`、`sync_server.py`），词本 `words.html` 的 `BOOKS.eg`。
- 进度和待办在 `NEXT_STEPS.md`。
