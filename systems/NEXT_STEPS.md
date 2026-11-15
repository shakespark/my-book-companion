# Thinking in Systems · 进度

## 现在

- **G＋H 全部做完（2026-11-15）**：十四页加 00 开读之前都已收稿（TS_READY 15 项），验收记录在 `source/ACCEPTANCE.md`。汇总页 index / recap / terms / drills / today / zh 的 check 都过。
- **下一个会话：I（上线，用户已授权直接做，做完告诉用户），再做 J。** 第一件事：读本目录 `CLAUDE.md`，`sh tools/status.sh`，然后照仓库 `CLAUDE.md` 的 I 步：
  首页卡片（`~/tutorials-home/index.html`，`data-progress="ts-done-:14"`，页数按 TS_PAGES 核一遍）、同步白名单（`sync.js` 的 `PREFIXES`、`sync_server.py` 的 `KEY_RE`，`scripts/sync-apply.sh`）、
  英文词条接词本（`words.html` 的 `BOOKS` 和两处前缀正则）、`git add systems/` 提交推送、`gh run watch`、`check-site.sh systems index.html chapters/01a.html`。
- 00 页「三十年以后」「你手边这本译本」里的条数（今天怎么看 29 条、勘误 321 处）是 2026-11-15 统计的，以后改了页面要跟着改。
- J：补全 `CLAUDE.md`，仓库 `README.md` 书单，`~/tutorials-deploy/README.md` 踩坑和 PLAYBOOK 表；模板教训见下面的记录。

## 记录

### 2026-11-15 A–D

- A：书库 6852（英文 EPUB）、5631（译本 AZW3＋EPUB，EPUB 是用户当天转的）。用户确认这两本。
- B：四个问题都选了推荐项，部署和样板「都不用停」。读法：系统之美电子书＋纸书。详见 `CLAUDE.md`。
- C：目录 `systems`，前缀 `ts-`；`new-book.sh systems 6852`，`calibre.py link systems 5631 calibre-zh`；`source/.venv` 装了 Pillow。
- D：`tools/extract.py` 是新写的（只照 `fooled/` 的分节和 index.tsv 的套路）。原书的标签很乱（同一级小标题有 h8、h17、h191、tx9、tx12），小标题写死在 `HEADS`；
  引言、第 6 章末节原书没有小标题，照译本的小标题本站分（`SPLIT`）。题词按位置认（`mark_epigraphs`），`index.tsv` 的 en 列和 zs 列 73 行逐行对过，指的是同一段。
  转写了译本三张文字表格图（00054、00055、00056）；别的译本图看过几张（00002、00050、00051、00053），是带中文标签的示意图。

### 2026-11-15 E

- 页表 14 页（`in` 01a 01b 02a 02b 03 04a 04b 05a 05b 06a 06b 07 08），73 节全落到页上；拆页看主题（浴缸 / 回路，单存量 / 双存量，杠杆点 12–7 / 6–1），07 虽 7000 词不拆（16 条短准则）。
- 模拟器 5 个，4 页（02a 两个）；后几章不做模拟器，用情境题。
- 用户补答：英文词条照 Fooled 要；「路线」「人和背景」不做。小节十三个；没有分界线和剧透名单。
- 建了：`AUTHORING.md`（20KB）、`assets/ts.js`（照 fb.js，去 gate，加 drills 汇总和画曲线的 `TS.chart`，手机上按容器宽度画）、`style.css`（加情境题、曲线图）、
  `index/recap/terms/today/zh/drills.html`（check 都过）、`tools/gen_chapters.py`、`lint.py`（加情境题、sim2、轻量页，五类「嫌疑」）、`pack.sh`、`status.sh`、`peek.py`、`accept.py`，`overlap.py` 引用上限改 2，
  `source/SECS.tsv`（73 行空表，只填了 08 §2 的 zs）、`source/ACCEPTANCE.md`。

### 2026-11-15 F

- 填了 `SECS.tsv` 第 1 章 6 行。写 `chapters/01a.html`、`tools/sim01a.mjs`、`source/reports/01a.md`；三项检查和 sim 都过，400 / 1100 深浅截图看过。
- 浴缸模拟器：附录写的流入时段按字面会停在 20，原书图 7 是 25，照图 7（流入从第 5 分钟那一步起打开）。
- 共享文件：`TS.chart` 的竖线标记离纵轴 90px 以内时放进图里（原来和纵轴名叠）；`pack.sh` 给模拟器页加附录方程（作者、审读都有），作者包再加 01a 的模拟器脚本和 `sim01a.mjs`；`style.css` 情境题选项改成 A/B/C，「今天怎么看」卡片不再被长网址撑出边框（手机上看出来的，check 查不出，记进了仓库 README）。`AUTHORING.md` 两处旧指向改了（`#c-stock-flow`、`sim01a.mjs`）。
- 主编核了报告里原先凭记忆写的三条（1996 停产 CFC、约 30 万亿个细胞、Jevons 1865），都对，补了网址。汇总页 index / recap / terms / drills / today / zh 有了 01a 的内容，check 都过。
- 写了 `source/REVIEW.md`（照模板）、`source/BRIEF.md`（模板公共几节＋读者＋样板踩坑＋样板审读分类；各页提示待 G）。
- 审读（Opus 一位）改 7 处，3 处会读歪：范围说大 3、归属 3（译本加的话混进「读完」）、图注和图对不上 1；勘误、词条、模拟器、卡片没改。都写不成 lint 规则。记在 `source/ACCEPTANCE.md`。


### 2026-11-15 G（准备）

- 写 `source/LINE-TASK.md`，5 位底稿代理（a: 00 01；b: 02；c: 03 04；d: 05；e: 06 07）交回 `source/line/`，各章节表的 TSV 用脚本并进 `SECS.tsv`。先读原是 41%，把 04 §2、07 §1 降成有空，合 35%；08 六行主编填（§6 可跳过）。
- 模拟器裁定（详见 LINE.md）：咖啡照图 1—11（25%/分、dt 0.25），不照附录 10%；石油运营成本默认 1、给滑块；渔场 dt 0.25、150 年、价格表用底稿的「采用」行；库存的订货除以反应延迟。
- `extract.py`：插话（INTERLUDE）原来和页边金句一样标 `{S}`，改成整段标 `{I}`；段号没变。`pack.sh` 给模拟器页加了底稿的算数脚本。
- 写 `source/IMG-TASK.md`，取图代理（Sonnet）取了 12 页；04a 和 in、03 重复的两张主编删了，04b 的清单是催了才补的。

### 2026-11-15 G＋H 第一批（01b 02a 02b）

- 三位作者、三位审读（都 Opus）。审读改了 01b 2 处（1 处会读歪：勘误对图认错存量）、02a 0 处、02b 3 处（0 处会读歪）。
- 共享文件：补回 `source/line/curves.py`（底稿代理留在自己 scratchpad 里，sim02.py 跑不了）；SECS.tsv 02 §4 line 收窄范围。
- 删了站点根目录里取图代理误放的 `04b.md`（`source/img/04b.md` 的旧稿）。
- 坑：`status.sh` 的「审完」只看报告里有没有「## 审读」一节，审读员写到一半就显示「审完」。02a 因此提前验收了一次，审读又改了 1 处（日期）。**等审读员的消息再验收。**

### 2026-11-15 G＋H 第二批（03 04a 04b，同一会话接着做）

- 审读：03 改 3 处（2 处会读歪），04a 2 处（2，都是自画图），04b 2 处（1）。主编改了 04b 分节地图一处「最短的一节」。
- 04a 作者删了奥肯定律那张今天卡（失业是存量），同意；04b 作者把重复的扩缩容情境题换成缓存过期，[152] 气候卡没做（只有二手来源）。
- 两批的审读分类写进了 `source/BRIEF.md`、`source/REVIEW.md`（「第一、二批审读抓到的」）。

### 2026-11-15 G＋H 第三批

- 05a 05b 06a 三位作者并行，交稿即审读，审完验收。审读共改 8 处，2 处会读歪（分类写进 `BRIEF.md`「第三批审读抓到的」）。
- 主编定：05b 情境题 d-pe-exam 留；05b 本站总体看法的判据跟着审读改；`LINE.md` 术语表 policy resistance 一行改正（Fixes that Fail 是原书的副名，不是译本加的）。

### 2026-11-15 G＋H 第四批（06b、07）

- 两位作者并行，交稿即派审读。06b 审读改 1 处、07 改 3 处，都不会读歪。
- 主编定：06b 回路图和情境题 d-oncall-alerts 共用处境，不换题。07 小额贷款卡「当时」栏留着。

### 2026-11-15 G＋H 收尾（in、08、00）

- `in` 改成派作者写（原计划主编写；它是普通作者页，提示、底稿、取图清单都齐，主编写要把样板和规范读进主会话）。审读改 5 处，1 处会读歪（归属）。
- 08 主编写，不单派审读：附录 §1–§5 逐条对过，术语表对着译本图核；勘误 12 条。新发现：§2 末尾「心智和模型」三条整组漏译（EPUB 核过），术语表「反馈回路」因果方向译反，§4 标题漏「按效力递增」。§6 方程和图对不上的几处写在分节地图下面。
- 08 的 lint 坑：分节地图一节里不能有别的 `<li>`（附加说明用 `<p>`）；勘误 data-p 只能写一个段号；小标题不算段落，loc 要取那一节第一段的词。
- 00 主编写，照 Fooled 的 00；条数在 in 收稿后统计。
- 收尾时补：08 的图号改成译本编号（第 2 章原书图号减 14 就是译本的图2—N，和 02a、02b 一致）；§4 标题漏括号回 EPUB 核过；00 地图表 in、08 的标题照收稿的改，00 的《增长的极限》一句照 in 的今天卡对齐；00、08 截图（400 宽）裁原尺寸看过。
