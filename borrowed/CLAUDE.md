# On Borrowed Time · 导读

- 书：Harald Weinrich, *On Borrowed Time: The Art and Economy of Living with Deadlines*，Steven Rendall 英译（University of Chicago Press，2008；德文原书 *Knappe Zeit: Kunst und Ökonomie des befristeten Lebens*，C.H. Beck，英译本版权页写 © 2005）。
  Calibre id **6053**（EPUB 是用户 2026-10-19 从 MOBI 转的），`source/calibre`。不用的：6064（TPZ）、6803（Z-Library 的 PDF）。
- 全书 9 章共 50 节（书自己的目录页；epub 的 toc.ncx 漏了每章第一节，别信它），加第 10 章尾声（不分节），正文约 7.7 万词，书后尾注约 8000 词。每节讲一两位作家（从塞涅卡、但丁、歌德到马尔克斯、《罗拉快跑》）怎么看有限的时间和期限。
- EPUB 的文字有扫描识别的痕迹：破折号成了连字符（`Roman times-before Galen`），注号粘在句尾（`antiquity.13`），个别错字（`Die Bilrgschaft`），正文里约 110 张图是**排成图片的引文和诗**（第 2 章就有 55 张），其余是花饰「· · ·」和书后索引页。
- 网址 https://t.miaowuao.cn/borrowed/ ，目录 `borrowed/`，localStorage 键前缀 `bt-`，共享脚本 `assets/bt.js`。骨架照 Paris（`paris/`），字母页号照 Algernon。

## 用户的回答（2026-10-19）

- 卡在哪：**哲学概念、作品和作家背景、主线、语言，四样都要**。用户特别说「这本书哲理性很强，需要增加更多说明」。
  - 哲学概念：每节先用中文把概念讲清（塞涅卡、帕斯卡、海德格尔、布鲁门贝格、马夸德……），再说作者拿它做什么。
  - 作品和作家背景：书里五十来位作家和作品大多没读过，要交代作品讲什么、这人是谁、作者为什么挑这一段。
  - 主线：一节换一个作家，读着散。要有贯穿全书的一条线，标出每节在线上的位置。
  - 语言：德译英的学术英语，夹拉丁、法、德、意引文。
- 提前知道内容：**没有害处，不分读前读后**。
- 每页要有「这一章到底说了什么」（用户 2026-10-19 看样板页前提的：「否则我可能读完都不知道作者想表达什么」）：
  做成「读完：作者到底说了什么」一节，3–5 条论点按逻辑重组、标段号，加一句「合起来」；一章拆成几页的，最后一页再加「第 N 章合起来」。lint 查条数、字数、段号在不在这一页。
- 怎么读：**英文电子书，就是书库里这一本**（MOBI 转的，用户 2026-10-19 确认，诗在读者屏幕上也是图片）。
  用户搜过三段扫描错字（`Roman times-before Galen`、`Roman antiquity.13`、`island of Kos, around 40o BC`）都搜得到：**`.loc` 照这本的字原样抄，错字、连字符、粘着的注号都不改**。
  **`.loc` 和分节地图的 `.en` 不含引号**（读者电子书里是直引号，页面只能写弯引号；带引号的能不能搜到没验证过，2026-10-19 定为避开，lint 查）。
  单个生词一般不收（长按能查）。**例外：图片里的引文和诗**（旁路提醒，用户转来，2026-10-19 采纳）：长按查不了、也搜不到，而且是全书最难懂的地方，要逐句给中文意思，生词也收；`.loc` 不能指向图片里的字。
- 译本：**没有中译本**，页面不写译本译法。
- 原书：商业出版，全套版权红线。
- 部署：**到时候直接做，做完告诉用户**（首页卡片、同步白名单、推送上线；只限这本书）。

## 页和节

- 19 页，一页是一章里连续的几节（3000–5500 词，不拆节）：01a 01b 02a 02b 02c 02d 03a 03b 04 05 06a 06b 07 08a 08b 09a 09b 09c 10，外加主编写的 00「开读之前」。
  页表在 `assets/chapters.js` 的 `BT_PAGES`，lint 从那里读。节号用原书的（02b 是 §3–§5），段号在一章之内连续。
- 原文是**一章一个文件** `source/text/NN.txt`，不按页拆（overlap 读整个目录，lint 按页表取节）。
- 每页十二节：这一页在做什么 / 读之前：这一页在全书的哪里 / 这一页的路线 / 分节地图 / 先用中文过一遍：这一页的概念 / 书里的人和作品 / 图里的引文（没有图片引文的页省掉）/ 词与短语 / 读完：作者到底说了什么 / 值得停下来的句子 / 检查一下理解（含「想一想」）/ 精彩回顾。
- 「全书的线」：`BT_STAGES`（五段）和 `BT_SECS` 每节的 `line`，主编写，页面「读之前」里的 `.linehere` 由 bt.js 画。依据是 `source/LINE.md`（通读全书的底稿 + 概念分工 + 主编核过的几处）。
- 概念块全站唯一，归哪页讲见 `source/LINE.md` 第 6 节；`terms.html` 自动汇总，`recap.html` 汇总精彩回顾。
- 图片引文：`source/imgtext/NNNNN.txt` 是两位代理看图转写的（118 张，含扉页），`tools/extract.py` 把它并进正文。一段引文（英译图 + 原文图）合成一块 `.imgq`，古人的诗据原作语言逐行译，在世或去世不到 70 年的只给大意。
- `source/raw/` 是 epub 解开的原样（看图用），`source/.venv` 装了 Pillow。

## 进度

- [x] A 找书　[x] B 问用户　[x] C 开目录（2026-10-19）
- [x] D 提取（2026-10-19）：`tools/extract.py` → `source/text/01–10.txt` 和 `index.tsv`；图片引文转写在 `source/imgtext/`
- [x] E 规范和骨架（2026-10-19）：`AUTHORING.md`、`assets/bt.js`、`assets/style.css`（照 Paris，末尾加本站组件）、`assets/chapters.js`、`index.html`、`recap.html`、`terms.html`、`tools/lint.py`；`source/LINE.md`
- [x] F 样板页 `chapters/01a.html`（第 1 章 §1）：三项检查通过，事实核查改了 19 处（`source/ACCEPTANCE.md`），后来按用户要求加了「读完：作者到底说了什么」。**用户 2026-10-19 认可**（「样板页可以，照这个铺开」）
- [x] G 铺开（2026-10-19）：18 位作者（Opus）一页一人，两批派出；中途额度用完暂停 20 分钟后恢复。主编逐页重跑三项检查、读概述/landing/读完后收下，作者报告摘要存 `source/reports/<页>.md`（「已核实的事实」带出处，审读不重查）。主编另写 `chapters/00.html`「开读之前」（全书的线 `#line`）
- [x] H 审读轮（2026-10-19 用户定：**核查和词条审读合成一轮**，一人审两三页，说明在 `source/REVIEW.md`；分寸是「只抓会误导读者的错」，用户原话「我不是搞学术的，真没必要那么认真」；作者报告里附了出处的事实不重查；**不换 Sonnet**）。2026-10-19 完成：9 位审读员审完 19 页 + 00，约 170 处修改（几乎都是说过头和口径不一），词条约 1400 条改约 30 条，记在 `source/ACCEPTANCE.md`　[ ] I 上线　[ ] J 收尾

## 怎么验

```sh
python3 -I tools/lint.py chapters/<页>.html
python3 -I tools/overlap.py chapters/<页>.html --max-quotes 2
node tools/check.mjs chapters/<页>.html --shots source/shots
```
`source/text/`、`index.tsv` 是 `tools/extract.py` 生成的，不手改；`BT_SECS` 的节名、词数也是从 index.tsv 生成的（line 是主编写的）。

## 以后改这本书

- 改哪一页就只动那一页；改完跑上面三项检查，`git add borrowed/` 提交推送即部署（GitHub Actions 有时排队十几分钟）。
- 加了新的概念块，`terms.html` 自动汇总；精彩回顾改了，`recap.html` 自动跟着变。
- `assets/chapters.js` 的 `BT_PAGES` 里 t、d 是主编从作者报告收的；`BT_SECS` 的 line 和 `BT_STAGES` 是主编写的「全书的线」（第 8 章第 4 节、第 10 章的 line 照审读改过）。`BT_SECS` 的节名和词数从 index.tsv 生成。
- 作者报告摘要在 `source/reports/<页>.md`，验收和审读记录在 `source/ACCEPTANCE.md`。
- 页名表改了的话，`~/tutorials-home/words.html` 里 bt 的 `pages` 也要跟着改。
