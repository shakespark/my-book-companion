# Impro · 导读

- 书：Keith Johnstone, *Impro: Improvisation and the Theatre*（1979 年 Faber 初版；书库这份是 Taylor & Francis / Routledge 2012 电子版）。
  Calibre id **6413**（EPUB、KFX），`source/calibre`。商业出版物，全套版权红线。
- 结构：序言（Introduction，约 1 千词）、Notes on Myself（约 9 千词）、四篇长文 Status（1.7 万）、Spontaneity（1.26 万）、Narrative Skills（1.3 万）、Masks and Trance（2.9 万），附录（约 900 词）。全书约 8.2 万词；每篇有编号小节和小标题。
- 中译本：《即兴》，基思·约翰斯通著，**饶昊鹏译**，后浪 / 贵州人民出版社 2020（ISBN 978-7-221-15741-6），Calibre id **6846**（EPUB，用户 2026-10-22 加进书库），`source/calibre-zh`。
  章名：序言 / 关于我自己 / 姿态（= Status）/ 自发性 / 叙事技巧 / 面具与催眠 / 附录，另有推荐语、出版后记。
- 网址 https://t.miaowuao.cn/impro/ ，目录 `impro/`，localStorage 键前缀 `im-`，共享脚本 `assets/im.js`（待建）。骨架照 The Selfish Gene（`selfish/`，有译本勘误）和 Uncontrolled（`uncontrolled/`，最新）。

## 用户的回答（2026-10-22）

- 卡在哪（多选）：**概念和机制、动手练、背景和现代评论、英文语言，四样都要**。
  - 概念和机制：地位（status，译本作「姿态」）、接受和拒绝（offer / block）、自发性、叙事里的「重新纳入」、面具和出神。先用中文讲，配图解，必要时小模拟。
  - 动手练：书里的课堂游戏整理成「怎么玩、几个人、看什么」，能和朋友或一个人试；全站汇总一页。
  - 背景和现代评论：1950–70 年代英国戏剧（Royal Court、George Devine）、书里的心理学说法；今天的即兴戏剧和商业培训怎么用它，哪些说法（出神、面具附身）站不住。
  - 英文语言：**少量，只收关键句**（译本传不出的双关、行话、名句，附英文原句方便翻原书），不做完整词条、不接词本（待定：接不接词本到 I 步再看词条数量）。
- 提前知道内容：**没有害处，但游戏先别揭底**。不设整页的读前 / 读后分界，但「这个练习会发生什么」放在一道线后面，先猜再看。
- 怎么读：**中译本（饶昊鹏译）为主，有电子版**。**会对着译本逐段读，要逐段译本勘误**（记忆 translation-errata，门槛照 reader-for-joy 放高：只收会让人读歪的）。
  页面按内容地标和译本的章名、小标题指路，不写页码；章名、人名、术语用这个译本的译法（勘误里指出译法不妥的）。
- 部署：**写完直接上线**（用户原话选项「写完直接上线」：样板照样审读，但不停下等用户看；分批派作者，一路做到上线）。首页卡片、同步白名单、推送上线到时候直接做。授权只管这一本书。
- 默认要做的（前几本每次都要）：每页末尾「读完：作者到底说了什么」和「本站怎么看」（记忆 views-with-commentary）；
  1979 年的书，做「今天怎么看」（现代视角的评论分量要重，记忆 reader-for-joy）；每页「精彩回顾」和 `recap.html`。
- 搜索：**grok 周额度用完，不用 grok**（记忆 no-grok-search）。WebSearch 用完时改用 web-fetch 读已知网址，再不行列进「拿不准」。

## 进度

- [x] A 找书（2026-10-22）：原书 6413，译本 6846。
- [x] B 问用户（2026-10-22）：见上。
- [x] C 开目录（2026-10-22）：`_tools/new-book.sh impro 6413`，译本 `calibre.py link impro 6846 calibre-zh`。
- [x] D 提取（2026-10-22）：`tools/extract.py` → `source/text/01–05.txt`（序言并进 01，附录并进 05 §15）、`index.tsv`、`zh/01–05.txt`。
  踩过的坑：原书篇末注的延续段（护士技术表、引文）一开始混进了正文，改成 Notes 标题之后全归 `## 注`；正文注号 `{注K}`；
  译本的作者注是 `aside.number`（标 `{原注}`），译本有两处盗版水印（`[书籍分享V信…]`）已滤掉；原书电子版不标引文，很多段以引号开头是别人的话。
- [x] 底稿（2026-10-22）：6 位代理读原文和译本写 `source/line/01、02、03、04、05-1、05-2.md`（任务 `source/LINE-TASK.md`，不联网）。
- [x] E 规范和骨架（2026-10-22）：`AUTHORING.md`（十六节）、`assets/im.js`、`style.css`（加 zherr、game、zhh）、`tools/lint.py`、`tools/gen_chapters.py`、`source/SECS.tsv`、`source/LINE.md`（概念分工、术语表）、`index.html` 和五个汇总页。
- [x] F 样板 `chapters/02a.html`（主编写，三项检查过，`tools/sim02a.mjs` 连点过）。审读员 r02a 改 20 处（记录在 `source/reports/02a.md` 末尾），
  主编分类：约 6 处真会读歪（批评柏格森没查他原著、[52] 方向写反、把作者一个例子写成通则、勘误说过头、「试试看」步骤不全、拜昂的事实错），约 9 处丢限定词，其余是位置、措辞。十类错已写进 `source/BRIEF.md`。用户说写完直接上线，没等认可。
- **2026-10-22 会话因用量上限中断时的状态**（下次接着做，先核对）：
  - 已收稿（`IM_READY`）：00 01a 01b 02a 02b 02c 02d 03b 04a 04b 04c 05b 05d 05f（05f 的审读等 05a、05c、05e 交了再派）。限额恢复后（同日晚）已让中断的 11 个代理接着做，并派了 05b 的审读。审读做完：02a 01a 02d 04a 02b（记录在各自 `source/reports/<页>.md` 末尾和 `source/ACCEPTANCE.md`）。
  - 中断时还在跑的（后台代理可能已经写完）：作者 03a 03c 05a 05b 05c 05e 05f；审读 01b 03b 04b 04c 02c 05d。
    接手时：`ls chapters/` 看哪些作者页已在；`grep -l "## 审读" source/reports/*.md` 看哪些审完。作者页在、但没有报告或三项检查不过的，重派那一页；审读没写记录的，重派审读。
  - 收稿流程：三项检查 → 读「读完」「本站怎么看」→ `tools/accept.py` → 派审读（`读 source/REVIEW.md，照它审读 <ID>`）→ 审完在 ACCEPTANCE 记改了几处、几处会读歪。
  - 各页审读至今：每页改 9–20 处，约四分之一到三分之一真会读歪。
- [x] G 铺开（2026-10-22，两批 17 位作者，全部交齐、主编读过收下，记录 `source/ACCEPTANCE.md`）：照 `source/BRIEF.md` 派 17 位 Opus 作者，一页一人，任务说明就是「读 source/BRIEF.md，照它写页 <ID>」。分两批：
  第一批 01a 01b 02b 02c 02d 03a 03b 03c 04a；第二批 04b 04c 05a 05b 05c 05d 05e 05f。交稿后主编逐页读「读完」「本站怎么看」「译本勘误」再收（`tools/accept.py`），记 `source/ACCEPTANCE.md`。
  搜索额度按会话算（2026-10-22 用户提议过新开会话来避开限制，最后选在原会话接着派）。
- [x] H 审读（2026-10-22 全部审完）：用户看了样板的审读结果（20 处，约 6 处会读歪）后定：**照样板全审**，一页一个审读员，查 REVIEW.md 的全部五项（2026-10-22）。作者交稿、主编收下就派。说明在 `source/REVIEW.md`。
- [x] 00 开读之前（主编页，2026-10-22 写好）：作者是谁（Johnstone 1933–2023、Royal Court、Theatresports）、全书五篇的地图、最短读法（`<div id="path">`）、译本须知（「姿态」「催眠」、作者注混在译注里、段落和原书不完全对应）、术语表摘要。
- **（已做）全部审完以后要做**：结论图例的「被改写」改成「后来的研究推翻了它、换了一种说法，或者情况变了」（today.html 和各页「今天怎么看」的 `ul.verdicts`；r05d 建议，审读还在改页面时不动）；`tools/counts.py` 数出首页卡片的数字，替换 `~/tutorials-home/index.html` 里的 COUNT_*。
- 2026-10-22 全书审完后第一次提交上线。
- [x] I 上线（2026-10-22）：总仓库提交 cea4e0c，部署 13 分钟（首次传图）；`check-site.sh impro` 全部正常；首页卡片 `im-done-:18`（tutorials-home be2aa0b）；sync.js PREFIXES 和 sync_server.py KEY_RE 加 `im-`，已 sync-apply；不接词本（关键句没有「记下」按钮）。
- [x] J 收尾（2026-10-22）：本仓库 README 书单；tutorials-deploy README 教程表和踩坑八条、PLAYBOOK 一行。

**全书完成。** 以后用户报 Impro 多半是要改某一页：照「怎么验」跑检查，改完 `git add impro/` 提交推送即部署。用户读到哪段想要准确译法，可以单段对照原文给（不整本翻译）。

## 页和节

- 页：00（开读之前，主编页）、01a 01b、02a–02d、03a–03c、04a–04c、05a–05f，共 18 页加 00。全部 `need: game`；02a、03b 加 `sim`。
- 节就是原书和译本的编号小节，04 篇 §3 拆成 3a、3b。档：先读约 39%（按译本字数），05 §8 主编降为有空。
- 十六节，见 `AUTHORING.md`。

## 怎么验

```sh
python3 -I tools/lint.py chapters/<页>.html        # 00 不跑 lint
python3 -I tools/overlap.py chapters/<页>.html
node tools/check.mjs chapters/<页>.html --shots source/shots/<页>
node tools/sim02a.mjs                               # 02a 模拟器照「试试看」连点
```

- `assets/chapters.js` 由 `python3 -I tools/gen_chapters.py` 生成（读 index.tsv、zh 文本、`source/SECS.tsv`，页表在脚本里），保留每页 t、d 和 IM_READY；收稿用 `python3 -I tools/accept.py <页> "<标题>" "<一句话>"`。
- `source/text/` 由 `tools/extract.py` 生成，不手改。`source/.venv` 装了 Pillow。
- 汇总页都是自动的：`terms.html` 收概念块，`games.html` 收游戏卡，`today.html` 收今天怎么看，`zh.html` 收译本勘误，`recap.html` 收精彩回顾和本站的总体看法。
- 如果用户在 Calibre 里改了译本的书名，`source/calibre-zh` 会断，重挂：`python3 _tools/calibre.py link impro 6846 calibre-zh`（先删旧链接）。
