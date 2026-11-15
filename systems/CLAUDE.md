# Thinking in Systems · 导读

- 书：Donella H. Meadows, *Thinking in Systems: A Primer*，Diana Wright 编（Chelsea Green 2008；初稿 1993）。Calibre id **6852**（EPUB），`source/calibre`。
- **译本（读者读的）**：《系统之美：决策者的系统思考》，**邱昭良 译**，浙江人民出版社 2012 年 8 月纸版，湛庐文化电子版。Calibre id **5631**（EPUB 是用户 2026-11-15 从 AZW3 转的），`source/calibre-zh`。
  译本多出的：各方赞誉、邱昭良的「导读 决策者的系统思考」、译者后记（`source/text/zh/front.txt`、`back.txt`）。
  原书的编者说明在译本里是「献词 献给世界的复杂性」（戴安娜·莱特署名）；原书书后 Notes、Bibliography、编者致谢、作者简介译本都没有。
  译本给每章加了自拟的章名（「系统之奇：系统的6大障碍」），引言加了三个原书没有的小标题，页边金句前加「系统之思」、方框前加「系统多棱镜」；附录术语表和第 7 章一张表排成图片（已转写）。
- 网址 https://t.miaowuao.cn/systems/ ，目录 `systems/`，localStorage 键前缀 `ts-`，共享脚本 `assets/ts.js`。骨架照 Fooled（`fooled/`：以译本为主指路、逐段勘误、模拟器、英文词条、今天怎么看 / 本站怎么看），去掉了分界线；情境题照 Manager 的 `drills.html`。

## 用户的回答（2026-11-15，B 步）

- 卡在哪（四样都要）：
  - **机制**：存量、流量、反馈回路、延迟，光读文字建立不起直觉。做能改参数、先猜再跑的模拟器（第 2 章「系统大观园」的几个模型、附录的模型方程是现成的骨架；全书定好数量，不为交互而交互）。
  - **概念和术语**：每页「先用中文过一遍」的概念块，汇总成全书术语页；术语用译本的译法（附录术语表），译得不好的另说。
  - **认得出、用得上**：8 个陷阱、12 个杠杆点、15 条法则，做原创情境题（给场景，问是哪个陷阱、杠杆点在哪），答案折叠。
  - **现代视角的评论**：2008 年出版、1993 年初稿，背后是《增长的极限》。每页「今天怎么看」和「本站怎么看」（记忆 views-with-commentary、reader-for-joy）。
- 提前知道内容：**没坏处**，不设「先停下」的线；只有模拟器和情境题先猜，答案折叠。
- 怎么读：**《系统之美》电子书为主，手上的纸书是英文原版**（2026-11-15 用户补充）。页头和分节地图两边都给：译本的章名、小标题和开头几个字为主，
  再给原书的小标题和段落开头几个英文词（照着翻英文纸书）；不写页码。每页一节逐段「译本勘误」，全站汇总（记忆 translation-errata）；**勘误以中文电子书为准**。
- 原书和译本都是商业出版物，全套版权红线。
- 部署：**到时候直接做，做完告诉用户**（首页卡片、同步白名单、推送上线；这个授权只管这一本书）。
- 样板：**不看，写完直接铺开**。样板照样审读，审读结果写进 `source/BRIEF.md`，不停下等用户。
- 额度：一个阶段一个会话，G＋H 每批约 3 页（记忆 pace-one-page）。
- E 步补问（2026-11-15）：**英文词条要，照 Fooled**（每页 6–20 条、trap 三分之一以上、「记下」接跨书词本，I 步要接 `words.html`）；**「路线」「书里的人和背景」两节不做**，背景放进概念块和今天怎么看。

## 原书材料

- `python3 -I tools/extract.py` 生成 `source/text/` 的全部内容，不手改；用法和标记写在脚本开头。
  00（作者说明、编者说明、引言）、01–07 七章、08 附录；原书和译本 **73 节一一对上**，两边小标题前都标 `§k`；`index.tsv` 一节一行。
  正文约 6.3 万词（最长 05 章 1.1 万，最短 03 章 3800）；译本各节 1.6–2.1 字一词，很匀，没看出整节删节。
- 译本三张文字表格图的转写在 `source/imgtext/zh-<图号>.txt`（主编照图转写），提取时并进去。两边的图拷在 `source/text/img/`、`text/zh/img/`，勘误要对着核图上的标签。
- 底稿 `source/line/00–07.md`（`source/LINE-TASK.md` 派的，不上页面）；`source/LINE.md` 是全站分工：概念归哪页、统一用词、模拟器的裁定。照片清单 `source/img/<页>.md`（`source/IMG-TASK.md`）。

## 页表、怎么改、怎么验

- 页（`tools/gen_chapters.py` 的 `PAGES`）：`in`（00 §1–§5）、`01a`（§1–§3）`01b`（§4–§6）、`02a`（§1–§4）`02b`（§5–§6）、`03`、`04a`（§1–§4）`04b`（§5–§7）、
  `05a`（§1–§5）`05b`（§6–§9）、`06a`（§1–§7，杠杆点 12–7）`06b`（§8–§14，6–1）、`07`（16 节）；`08` 附录是主编最后写的轻量页（need `light`），`00` 开读之前是主编页。
  译本的赞誉、邱昭良导读、译者后记（`zh/front.txt`、`back.txt`）不做页，00 页提一句。
- 模拟器 5 个：01a 浴缸、01b 两种回路（咖啡 / 存款）、02a 恒温器和汽车库存（一页两个，need `sim2`）、02b 石油和渔场。照附录 08 §6 的方程，画图用 `TS.chart`。
- 样板页 `chapters/01a.html`（主编写）。小节十三个，见 `AUTHORING.md`；没有分界线、没有剧透名单。
- `source/SECS.tsv`（本站节名、档、line、zs 覆盖）填好后跑 `python3 -I tools/gen_chapters.py`；`assets/chapters.js` 的节表是生成的，不手改（t、d、`TS_READY` 由 `tools/accept.py` 填）。
- 每页三项检查：`python3 -I tools/lint.py`、`python3 -I tools/overlap.py`（引用上限 2）、`node tools/check.mjs`；模拟器页加 `node tools/sim<页>.mjs`。lint 的「？」是嫌疑，作者在报告里逐条答。
- 阅读包：`sh tools/pack.sh <页>`（作者）、`sh tools/pack.sh --review <页>`（审读员），输出在 `source/pack/`。进度：`sh tools/status.sh`；验收看节：`python3 -I tools/peek.py chapters/<页>.html`。

## 上线（2026-11-15）

- 首页卡片在 `~/tutorials-home/index.html`（`data-progress="ts-done-:15"`，14 页＋00）；`ts-` 在 `sync.js` 的 `PREFIXES`、`sync_server.py` 的 `KEY_RE`；词本 `words.html` 的 `BOOKS.ts`（页名表）和两处前缀正则。
- 改了页面：三项检查都过再 `git add systems/` 提交推送，`gh run watch` 不接管道，最后 `~/tutorials-deploy/scripts/check-site.sh systems index.html chapters/<页>.html`。
- 卡片和 00 页里的条数（勘误 321、今天怎么看 29、情境题 48、概念 50、词条 235）是上线时统计的，增删了要跟着改。

进度和待办在 `NEXT_STEPS.md`。
