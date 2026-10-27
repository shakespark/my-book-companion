# The Making of a Manager · 导读

- 书：Julie Zhuo, *The Making of a Manager: What to Do When Everyone Looks to You*（Portfolio / Penguin, 2019）。
  Calibre id **6847**（EPUB），`source/calibre`。商业出版物，全套版权红线。
- 结构：引言、十章（What Is Management? / Your First Three Months / Leading a Small Team / The Art of Feedback / Managing Yourself /
  Amazing Meetings / Hiring Well / Making Things Happen / Leading a Growing Team / Nurturing Culture）、结语，章末有原书注释。
  每章开头有一张「AVOID / ASPIRE」手绘图（引言和结语是「THE MYTH / THE REALITY」），文字只在图里。
- 中译本：繁体《當上主管後，難道只能默默崩潰？：Facebook產品設計副總打造和諧團隊的領導之路》，卓茱莉著，**許恬寧譯**，
  時報文化 2020（ISBN 978-957-13-8158-9），Calibre id **6848**（EPUB），`source/calibre-zh`。注释在每章末尾。
  - 书库里还有简体《硬核晋升》（陈黎译，中信 2020，id 6849），**不用**：2026-10-27 抽查 8 处，简体本几处意思译反
    （「尽快给反馈」成「尽可能地提供」、长者优惠那个例子读反、weepier 成「笨拙」），章名被出版社改写；繁体本意译过头、偶有添字，但没那么伤。
- 网址 https://t.miaowuao.cn/manager/ ，目录 `manager/`，localStorage 键前缀 `mm-`，共享脚本 `assets/mm.js`。
  骨架照 Impro（`impro/`，有逐段译本勘误、卡片汇总页）和 Uncontrolled（`uncontrolled/`，英文为主、节就是原书小标题）。

## 用户的回答（2026-10-27）

- 卡在哪（多选）：**四样都要**。
  - 现代视角的评论：2019 年的书、硅谷大公司视角；之后有远程办公、裁员潮、AI，管理界看法变了。每个观点给主流看法 / 作者看法 / 本站评论（记忆 views-with-commentary、reader-for-joy）。
  - 遇到问题会查：情境手册（第一次一对一、给差评、招错人……），每条指回书里那一节；每章一两张能带走的工具卡。
  - 判断力练习：原创情境题，给一段对话或邮件，先判断经理哪里做错，再看答案。
  - 英文口语和背景：硅谷行话、美式口语、流行文化梗，Facebook 早年的人和事。
- 提前知道内容：没问（管理书，按 PLAYBOOK 无害、不分界；判断题的答案折叠）。
- 怎么读：**英文纸书为主**，**对着繁体本逐段读**，要逐段译本勘误（记忆 translation-errata，门槛照 reader-for-joy 放高：只收会让人读歪的）。
  繁体读得顺。页面按英文原书定位（小标题、段首几个词），译本的章名和译法在勘误里给。
- 和管理的关系：**以前带过 / 可能要带**：既能回想，也为以后准备；实操和好读两头兼顾。
- 部署：**不看样板，写完直接上线**。样板照样审读，审读结果写进 BRIEF；首页卡片、同步白名单、推送上线到时候直接做。授权只管这一本书。
- 搜索：grok 周额度用完，不用 grok（记忆 no-grok-search）。

## 进度

- [x] A 找书（2026-10-27）：原书 6847，繁体译本 6848。
- [x] B 问用户（2026-10-27）：见上。
- [x] C 开目录（2026-10-27）：`_tools/new-book.sh manager 6847`，译本 `calibre.py link manager 6848 calibre-zh`。
- [x] D 提取（2026-10-27）：`tools/extract.py` → `source/text/00–10.txt`（结语并进 10，是 §6）、`source/zh/00–10.txt`、`source/img/`。
- [x] E 规范和骨架（2026-10-27）：`AUTHORING.md`、`source/LINE.md`（概念 / 情境卡分工、术语表）、`source/SECS.tsv`（节名、档）；骨架照 Impro。
- [x] F 样板（2026-10-27）：`chapters/04.html` 主编写，三项检查过，已进 `MM_READY`。样板审读 4 处必改、十来处可改都已改；
  教训写进 `source/BRIEF.md`「样板页审读时抓到的错」。用户说不看样板，没给用户看。
- [x] G 铺开（2026-10-27，两个会话）：in、01–10 全部收齐，都在 `MM_READY`。验收记录在 `source/ACCEPTANCE.md`，作者报告在 `source/reports/`。
- [x] 00 开读之前（主编页，2026-10-27 第二个会话写好）：作者是谁、好在哪窄在哪、2019 年以后（26 条今天怎么看的统计和四件大变化，事实都取自各页已核过的「今天怎么看」）、全书地图、译本须知（97 处勘误的五类）、最短读法（`#path`）。只跑 overlap 和 check。
- [x] H 审读（2026-10-27 第二个会话）：6 位 Opus 审读员，说明 `source/REVIEW.md`（核查和词条审读合一）。约 80 处改动，真会读歪的 19 处；勘误 97→84；trap 去 64。主编收尾（in/01 情境卡和判断题去重、06 今天卡、00 总数）见 `source/ACCEPTANCE.md` 末尾。
- [ ] I 上线
- [ ] J 收尾

## 怎么改、怎么验

- 每页三项检查：`python3 -I tools/lint.py chapters/NN.html`、`python3 -I tools/overlap.py chapters/NN.html`、`node tools/check.mjs chapters/NN.html --shots source/shots/NN`。
- `assets/chapters.js` 由 `tools/gen_chapters.py` 生成（读 `source/SECS.tsv`），节表别手改；每页的 t、d 和 `MM_READY` 用 `python3 -I tools/accept.py <页> "<标题>" "<一句话>"` 填。
- 页码（纸书 p.）全由 `mm.js` 按 `MM_PG` 补，页面里只写 `data-p` 段号。

## 待办（2026-10-27 第二个会话结束时写；下个会话从这里接着做）

正文 11 页（in、01–10）和 00 开读之前都收了，H 审读轮也做完了，下一步是 I 上线（用户已授权，直接做）。还没提交、没上线，`manager/` 整个目录还没入库。

3. 档已调过（2026-10-27）：06 §4、09 §6 升「先读」；07 §4、09 §4、10 §5 从「可跳过」改「有空」。全书先读 22/61。01 §5 没升（第 1 章已有三节先读）。
4. **I 上线**（用户已授权，不用再问）：首页卡片 `data-progress="mm-done-:11"`（11 = in + 10 章；00 算不算进去看 Impro 怎么做）；`mm-` 加进 `~/tutorials-home/sync.js` 的 `PREFIXES` 和 `~/tutorials-deploy/sync/sync_server.py` 的 `KEY_RE`，`scripts/sync-apply.sh`；`words.html` 的 `BOOKS` 加 `mm: {dir:"manager", …}`，两个前缀正则加 `mm`；`git add manager/` 提交推送，`gh run watch`，`check-site.sh manager index.html chapters/04.html`。
5. **J 收尾**：本仓库 README 书单、`~/tutorials-deploy/README.md` 踩坑、PLAYBOOK 一行。

以后要再派代理，先把 `source/BRIEF.md`、`source/REVIEW.md` 里的 scratchpad 路径换成新会话的。
J 收尾时给 `~/tutorials-deploy/README.md` 记的教训：主编页（00）汇总各页时只看了页面上的转述，两处把话安错了人，写 00 也要回原文；trap 里字面就能猜对的（zoom out、resonate）作者仍常标，审读轮去掉 64 个。
