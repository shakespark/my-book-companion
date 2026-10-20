# The Selfish Gene · 导读

- 书：Richard Dawkins, *The Selfish Gene*, 30th Anniversary edition（Oxford University Press 2006；正文是 1989 年第二版，含作者 1989 年的尾注和 2006 年的 30 周年导言）。
  Calibre id **2218**（AZW3、EPUB、MOBI；EPUB 是 2026-10-20 用户转出的），`source/calibre`。
- 中译本：《自私的基因：40周年增订版》，卢允中等译，中信出版社 2018，Calibre id **6839**（EPUB），`source/calibre-zh`。
  第 1–13 章和尾注与英文版一一对应；译本另有第 14、15 章（取自 *The Extended Phenotype*）和 40 周年版的说明、序言，英文版没有这些。
- 正文 13 章约 11.5 万词（每章 3500 到 14300 词，第 12、13 章最长），书后尾注约 3 万词（index.tsv 的数）。
- 网址 https://t.miaowuao.cn/selfish/ ，目录 `selfish/`，localStorage 键前缀 `sg-`，共享脚本 `assets/sg.js`。骨架照 Darwin's Worms（`worms/`），模拟器的写法照 DDIA（`~/ddia`），译本检查照 Flowers for Algernon（`algernon/`），对照今天照 Up from the Projects（`projects/`）。

## 用户的回答（2026-10-20）

- 卡在哪：**概念和机制、论证主线和争议、英文语言、人物和研究背景，四样都要**。
  - 机制：ESS、鹰鸽博弈、亲缘系数、重复囚徒困境等概念，配可以调参数的小模拟器（全书定好数量，不为交互而交互）。
  - 论证和争议：基因视角到底主张什么、书名常被怎样误读；「对照今天」：1976 年和 1989 年的说法后来哪些成立、哪些被改写。
- 怎么读：**英文 Kindle**（这份 EPUB）。单个生词一般不收；`.loc` 一字不差，要能在 Kindle 上搜到。
- 译本：**有电子版**，用 40 周年增订版（6839）对照。章名、人名、术语照这个译本的译法，译本漏译、误译的地方要提示（参照 Free to Choose 的做法）。
- 提前知道内容：科普书，按无害处理，不分读前读后（主编默认，告诉过用户）。
- 原书是商业出版物，全套版权红线。
- 部署：**到时候直接做，做完告诉用户**（首页卡片、同步白名单、推送上线；授权只管这一本书）。
- **会对着译本读**（用户 2026-10-20，看了代理报的错译漏译后说「会对着译本读，所以这个译本勘误很有必要」）：每页加一节「译本勘误」，逐段对照译本，误译、意思译反、漏译、术语、数字错一条一块，引译本原句 ≤20 字兼作搜索定位；全站汇总在 `zh.html`。
- 默认每页末尾加「读完：作者到底说了什么」和「本站怎么看」两节（见记忆 views-with-commentary，用户在前几本书里每次都要）。

## 进度

- [x] A 找书　[x] B 问用户　[x] C 开目录（2026-10-20）
- [x] D 提取（2026-10-20）：`tools/extract.py` → `source/text/00–13.txt`（00 是导言和三篇序；每行一段，`[k] (p页码)`，`{注K}` 是原书星号，章末 `## 尾注` 收 1989 年的尾注 `[nK.j]`）、`index.tsv`；
  译本 `source/text/zh/00–13.txt`、`notes.txt`（不编段号，`{译注}`）。原书分数是图片，脚本按 FRAC 换成文字；epub 用错图的三处记在 `source/IMG_ERRATA.md`。
  原书各章**没有小标题**，第 12、13 章（1989 年新加）没有尾注。
- [x] E 规范和骨架（2026-10-20）：四位代理通读全书写底稿 `source/line/00–13.md`（任务说明 `source/LINE-TASK.md`），主编据此定节和页，写 `source/LINE.md`（全书的线、概念分工、术语表、拍板的事）。
  `AUTHORING.md`、`assets/sg.js`、`assets/style.css`（末尾加尾注块、模拟器、`.zhv`、「有争议」标签）、`assets/chapters.js`（13 章 104 节、22 页）、`index.html`、`recap.html`、`terms.html`、`today.html`（对照今天汇总）、`tools/lint.py`、`tools/overlap.py`（引用上限 2）、`source/REVIEW.md`。
- [x] F 样板页 `chapters/05a.html`（第 5 章上半，鹰和鸽，带模拟器，主编写）：三项检查通过；审读员改 19 处（`source/ACCEPTANCE.md`），九类易犯的错写进 `source/BRIEF.md`；用户要求后加了「译本勘误」（11 条）。**用户 2026-10-20 认可**（「可以」）。派人前两位核对员把 13 章底稿对原文核了一遍，改 65 处（`source/ACCEPTANCE.md`）
- [x] G 铺开（2026-10-20，交回一位补派一位；21 页全部交齐并由主编读过收下）：第一批 01 02 03a 03b 04a 04b 05b 06a 06b 07 08a，第二批 08b 09a 09b 10a 10b 11 12a 12b 13a 13b；作者报告 `source/reports/`　
- [x] H 审读轮（2026-10-20，核查和词条审读合一，说明 `source/REVIEW.md`）：11 位审读员审完 23 页，记录和小结在 `source/ACCEPTANCE.md`。最大的问题是主编的译本提取把分数小图删掉，造出一批错勘误，已全部改正
- [ ] I 上线　[ ] J 收尾

## 页和节

- 22 页：01 02 03a 03b 04a 04b 05a 05b 06a 06b 07 08a 08b 09a 09b 10a 10b 11 12a 12b 13a 13b，外加主编页 00「开读之前」。页表在 `assets/chapters.js` 的 `SG_PAGES`（`need: ["sim"]` 的页必写模拟器），节在 `SG_SECS`（`p` 是段号范围，`en` 是节首几个词），lint 从那里读。
- 每页十六节：这一页在做什么 / 读之前 / 路线 / 分节地图 / 先用中文过一遍：概念 / 动手：模拟器（5 页）/ 书里的人和研究 / 词与短语 / 译本勘误 / 值得停下来的句子 / 作者 1989 年的尾注（有星号的页）/ 读完：作者到底说了什么 / 对照今天 / 本站怎么看 / 检查一下理解 / 精彩回顾。
- 模拟器：05a 鹰和鸽、06a 亲缘系数、09a 两性之战、10b 傻瓜骗子斤斤计较者、12a 重复囚徒困境锦标赛。页面末尾一段 `<script>`，`<head>` 里可加 `#sim-<页id>` 开头的 `<style>`。
- 尾注：正文星号 `{注K}`，每页「作者 1989 年的尾注」一个星号一块，lint 核对星号前的 4–7 个词。第 12、13 章没有尾注。
- 译本勘误：`<div class="zherr" data-p|data-n>`，类型 误译 / 译反 / 漏译 / 术语 / 数字，`p.loc` 英文定位、`p.zhq` 引译本原句（lint 核对），`zh.html` 自动汇总。
- 译本：只能写在 `<span class="zhv">译本：「…」</span>` 里（勘误以外每页 ≤6 处，≤20 字，lint 去 `zh/NN.txt` 和 `zh/notes.txt` 这一章那段核对），别处不能和译本连续 12 个汉字相同。

## 怎么验

```sh
python3 -I tools/lint.py chapters/<页>.html
python3 -I tools/overlap.py chapters/<页>.html
node tools/check.mjs chapters/<页>.html --shots source/shots/<页>
```
`source/text/`、`index.tsv`、`source/IMG_ERRATA.md` 是 `tools/extract.py` 生成的，不手改。`source/.venv` 装了 Pillow（取图）。
