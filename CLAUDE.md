# 导读站总仓库

2026-10-18 起，新书的导读站都放在这个仓库里，一本书一个一级目录，部署到 `https://t.miaowuao.cn/<目录名>/`。
本仓库的结构和部署方式见 `README.md`。做书的依据是下面三份，**按阶段读，用到哪份读哪份**（三份加起来约 100KB，主会话每一轮都要重读上下文，不要一上来全读）：

- `~/tutorials-deploy/PLAYBOOK.md`：选型表。一本书该做成什么样，靠四个问题来定。**B、E 步读。**
- `~/tutorials-deploy/AUTHORING-COMMON.md`：章节页的公共规范，包括版权红线、页面约定、自检、报告格式。**E、F 步读。**
- `~/tutorials-deploy/README.md`：服务器、同步、首页、取图、踩过的坑。最上面的表是 13 个老站。
  **A 步只 grep 教程表查书名；D 步读「踩过的坑」里提取那几条；I、J 步读「新增一个教程」和同步、词本几节。** G、H 步用不着。

`_tools/templates/` 里是每本书都一样的说明模板（`source/` 不入库，所以放这里）：`BRIEF-common.md`（作者怎么干活、交稿前自查、报告）、`REVIEW.md`（审读说明）。

## 会话怎么分（省额度）

2026-11-15 量过 Fooled by Randomness 一本书的用量：作者约 56%，主会话约 21%，审读约 13%，底稿约 10%。
主会话的花费七八成是「每一轮把整个上下文重读一遍」，所以**每轮的价钱和当时的上下文长度成正比**；E、F 两步挤在一个会话里那次，上下文涨到 36 万 token，一个会话花了主会话总量的三分之一。
2026-11-15 又量了 Thinking in Systems（新流程第一本）：每页 3.8M → 2.8M 当量，作者每位 −38%，审读每位 −30%；A–F 这几个固定阶段没省（约 7M），底稿每页涨了五成。
量的时候注意：调了 advisor 的那一轮，usage 顶层是两次请求相加，上下文峰值要看 `iterations` 里单次的（以前写的「62 万」就是这样多算的）；advisor 自己的用量只在 `iterations` 里，不在顶层合计里。

- **一个阶段一个会话**：A–D，E，F，G＋H（一批 3–6 页，一批一个会话；Systems 一个会话做 6 页，主会话峰值才 126k），I–J。阶段做完就把下一步写进这本书的 `NEXT_STEPS.md`，告诉用户开新会话接着做，不要顺手做下一阶段。用户说「把剩下的都做了」时照做。
- **阶段中途也可以停**：读了很多大文件、来回改了很多轮之后，先把进度落到 `NEXT_STEPS.md`，建议用户开新会话。
- **主会话不整份读大文件**：页面用 `tools/peek.py` 看指定的几节，原文用 `grep -n`、`sed -n` 看要对的那几段，不 `cat` 整页、整章。别的书的页面、规范只在 E 步照着搭骨架时读；E 步也不整份读 `lint.py` 和上一本的 `AUTHORING.md`（Systems 的 E 会话这两份就是 44k 字符），复制过来用 `grep -n` 找要改的地方。
  自己写的脚本（`gen_chapters.py` 之类）正常时只打印一行，出错才打印细节：Systems 跑 6 次进了 26k 字符。
- **能一起发的工具调用一起发**，对主会话和代理都一样。
- **作者、底稿代理不调 advisor**（2026-11-15 用户定的）：每调一次，整个上下文不走缓存地发给另一个模型，Systems 里作者平均 1.7 次，约等于作者自己花费的三成。写进 `BRIEF.md` 和 `LINE-TASK.md`。主会话和审读员照常。
- 新会话接手一本书：读它的 `CLAUDE.md`（固定信息）和 `NEXT_STEPS.md` 的「现在」一节，跑 `tools/status.sh`，就够了。

## 用户报一个书名时

先判断这本书属于哪种情况：

1. **老站已经做过**：书名出现在 `~/tutorials-deploy/README.md` 的教程表里。去那个目录（如 `~/ddia`）干活，不在这里新建。
2. **本仓库已有它的目录**：读 `<目录名>/CLAUDE.md` 和 `<目录名>/NEXT_STEPS.md` 的「现在」一节，看做到哪一步，接着做。（2026-11-15 以前的书没有 `NEXT_STEPS.md`，进度写在 `CLAUDE.md` 里，不用回头拆。）
3. **都不是**：这是新书，按下面的流程从头做。

**只做用户点名的那一本。** Calibre 书库里大部分书不做，不要扫书库批量建目录，也不要顺手给别的书开头。

## 新书的流程

**A. 在书库里找到这本书。** 运行 `python3 _tools/calibre.py find <书名或作者>`。
查出多个版本、多种格式，或者一本都没查到，就问用户。查到了也要把书名、作者、格式、id 报给用户确认。

**B. 一次问清用户（用 AskUserQuestion）。** 先按书的类型和 PLAYBOOK 里各站的答案，替每个问题标好推荐项。要问的是：

- PLAYBOOK 的四个问题：读者卡在哪、提前知道内容有没有害处、怎么读（纸书 / Kindle / 有声书 / 中译本）、是不是商业出版物。
- 手上有没有中译本，是哪个译本，有没有电子版。有电子版的话，也要放进 `source/` 供对照，见 README 踩坑记录里 Free to Choose 那条。
- 部署这一步（首页卡片、同步白名单、推送上线）能不能到时候直接做。用户说可以，就写进这本书的 `CLAUDE.md`。这个授权只管这一本书。

**C. 开目录。**

- 目录名就是网址：英文小写、短，比如 `ftc`、`sysperf`。不能和老站重名，`new-book.sh` 会查线上有没有被占。
- localStorage 键前缀用两个字母，不能和现有的冲突。现有的写在 `~/tutorials-home/sync.js` 的 `PREFIXES` 里。
- 运行 `_tools/new-book.sh <目录名> <id>`，会建好 `tools/` 和 `source/calibre`（软链接到书库）。
- **书库里没有 EPUB**（只有 AZW3、MOBI、PDF）：请用户在 Windows 的 Calibre 里把这本书转成 EPUB。转出的文件会放进书库里同一个目录，软链接自动就能看到。
  这台 WSL 调不了 Windows 的程序，`ebook-convert.exe` 跑不起来，所以这一步只能用户自己做。
- 要从维基取照片的话，建 `source/.venv` 并装 Pillow，`fetch_img.py` 要用。
- 建这本书的 `CLAUDE.md` 和 `NEXT_STEPS.md`（见下面「每本书的两份记录」）。

**D. 提取原文。** 从最像这本书的老站复制 `tools/extract.py` 改：

- O'Reilly 的 epub 照 `~/ddia/tools/extract.py`。
- Pearson / Addison-Wesley 的 epub 照 `~/systems_performance/tools/extract.py`。
- 一般商业书照 `~/creating_modern_capitalism/tools/extract.py` 或 `~/free_to_choose/tools/extract.py`。

产出 `source/text/NN.txt`，一章一个文件。README 踩坑记录里有几条提取的坑：`<br>` 要换成空格、上标会丢、自闭合的 span。

**E. 规范和骨架。**

- 写 `AUTHORING.md`：开头一句「公共部分见 `~/tutorials-deploy/AUTHORING-COMMON.md`」，然后填它的参数表，再写这本书的差异。
- 从最像的老站复制骨架：`index.html`、`assets/style.css`、共享脚本、`chapters.js`、`recap.html`、`tools/lint.py`。
- 共享脚本改名成 `<前缀>.js`，里面的 localStorage 前缀全部换掉。
- 页脚要有备案号；共享脚本末尾要有加载 `/_home/sync.js` 的那一行。
- **阅读包**：写 `tools/pack.sh <页>`，里面调 `python3 -I ../_tools/pack.py --out <目录> <条目>…`（用法见脚本开头），把这一页的作者要读的东西切成小份：
  公共规范、`AUTHORING.md`、样板页（条目末尾加 `#html`，去掉图和脚本）、`source/LINE.md`、这一章的底稿、这一页那几节的原文和译本（`文件@起..止` 按节取）。
  `tools/pack.sh --review <页>` 给审读员：`AUTHORING.md`、`LINE.md`、作者报告、这一页、原文和译本那几节。输出目录用 `source/pack/<页>/`（`source/` 不入库）。
  作者和审读员第一轮跑它、第二轮一条消息并行 Read 全部。Fooled 的作者没有它时，动笔前中位数走了 47 轮。
- **`AUTHORING.md` 只写这本书的参数和差异**，不抄公共规范和上一本书里一样的话（规范从 16KB 涨到过 34KB，每位作者都要全读）。上一本书的教训，已经做成 lint 规则的就不再写成文字。
- `tools/status.sh`（照 `fooled/tools/status.sh`）、`tools/peek.py`、`tools/accept.py` 一起建好。
- lint 里要有：位置词和节号标签（`data-p` 跨节而标签只写一节）、「今天」栏里早于出版年的年份、卡片标题两句并列、「是一回事 / 同一件事」这类等同词、
  页面写「没给出处 / 没点名」时提示查书后注释。这几类只报嫌疑，作者在报告里逐条答；审读员不再管位置和节号。
- 用户要的东西从一开始就做上：每章一节「精彩回顾」，外加汇总全书的 `recap.html`（他隔几周回来时靠它回忆）。
  交互组件要用大白话写清该填什么、每一列是什么。「成立 / 被改写」这类结论标签要有图例，并写明判的是哪句话。

**F. 样板页。**

- 主编自己写一章做样板，`check.mjs`、`overlap.py`、`lint.py` 三项检查都要跑通。
- 样板页照样派一位审读员（先写好 `source/REVIEW.md`）。审读抓到的错按类写进 `source/BRIEF.md` 和 `REVIEW.md` 末尾；能写成 lint 规则的写成规则。
  把这一页的审读分类记下来（改了几处、几处会读歪、哪几类），用户问审读值不值时拿它回答。
- 用样板页把 `tools/pack.sh` 跑一遍，看清单上每份都读得完、节取得对。
- **写完给用户看，等用户认可了再铺开。** 用户说过不看样板的（记忆 skip-sample-review，只管那一本书），不停下等，审读照做。

**G. 铺开。** 一批 3–6 页，一批一个会话（记忆 pace-one-page）；用户说可以多派时照用户说的。

- 写 `source/BRIEF.md`：`_tools/templates/BRIEF-common.md` 的几节原样放进去，再加这本书的读者、样板审读抓到的错、各页提示。
  写 `source/REVIEW.md`：照 `_tools/templates/REVIEW.md` 改，末尾填样板审读抓到的几类。
  两份里都**不写死 scratchpad 路径**，让代理用自己系统提示里的。
- 派之前先把任务说明里每章的提示和原文对一遍：CMC 那次就有几条提示写错了。
- **底稿**（有译本或内容密的书）：几位代理照 `source/LINE-TASK.md` 写 `source/line/NN.md`，主编据此写 `source/LINE.md`（页表、概念分工、术语表、剧透名单）。
  **底稿按页分节**（一章拆成几页的，每页一节，跨页共用的放最前面一节），`pack.sh` 用 `文件@起..止` 只给作者他那一页的节和共用节：Systems 把整章底稿（约 72KB）发给了只写半章的作者。
  底稿末尾加一节「要的图」：这一章每页想放哪几张照片（人、地方、物件），写成维基共享资源的搜索词。
- **取图单独派一位代理**，在作者之前：照底稿的「要的图」，一张一张串行跑 `fetch_img.py`（维基的额度是共用的，不并行），看过画面，
  把清单写进 `source/img/<页>.md`（文件名、画面、出处、图注能写什么）。作者照清单用图，不自己找。取图代理不读原文和规范，上下文小，一轮比作者便宜得多。
- 作者用 Opus（2026-10-14 用户定的，不换 Sonnet）。一页派一位作者，派出的消息只写：读 `source/BRIEF.md`，你写 <页>。
- 任务说明里要写明工作目录是 `/home/lee/my_book_companion/<目录名>`，先用 `pwd` 确认。
- 作者只写自己那一页，不做 git 操作，不再派子代理；临时文件放 scratchpad 里自己的子目录。
- 搜索：WebSearch 额度是所有代理共用的，会中途用完。搜索结果是作者上下文里最大的一项（Systems 每位 3.5–10 万字符，比原文那一章还多）：每页不超过 8 次，只查「今天怎么看」和书里、底稿里没有的事实；底稿已带出处的不重查。grok 不用（记忆 no-grok-search）；搜不了就列进「拿不准」，不写进页面。
- 报告落文件 `source/reports/<页>.md`，第一行是状态（`写作中` / `已交稿`）；作者最后一条消息只写一两句。
- 作者交稿后就停笔，不再给已交稿的作者派活，免得一页两个人改。

**H. 审读和验收**（和 G 同一个会话、一页一页接着做，不另开一轮）。

顺序是**作者交稿 → 审读 → 主编验收**（2026-11-15 用户定的；以前是主编先读一遍再派审读、审完再看一遍）。Fooled 里主编每页只改 0–3 处，审读员改 2–11 处，主编读两遍不值。

1. **作者交稿**：主编跑三项检查（只看有没有过），不读页面，马上派审读员：Opus，一页一位，消息只写「读 `source/REVIEW.md`，审读 <页>」，揭晓页加一句剧透提示。
   核查和词条审读是合一的一轮（记忆 review-not-academic）。技术书的命令，审读员要真的在本机跑一遍。
2. **审读员交回**：主编验收，**一页只读一遍**：
   - 报告里的「## 审读」一节：每处改动看得懂、站得住；标了要主编定的事，定掉。
   - `tools/peek.py` 看「读完」「今天怎么看」「本站怎么看」这几节（审读后的样子）。卡片标题是不是单句、标签对不对得上，主编自己逐张看：审读员常漏，也有把标题改成两句并列的。
   - 有不剧透要求的书：以没读过的读者身份读线以上。
   - 有模拟器的页：亲手跑 `node tools/sim<页>.mjs`。
   - 跨页的事：新起的概念登记进 `LINE.md`，术语和别的页统一，目录用的标题和一句话过剧透。
   - 三项检查，`tools/accept.py`，在 `source/ACCEPTANCE.md` 记一行：改了几处、几处会读歪、主编定了什么。
3. **审读只抓会让读者读歪的错。** 限定词只在方向或范围变了时改，差一档语气的不动；位置和节号归 lint。数据见 `_tools/templates/REVIEW.md` 开头。
4. 用户怀疑审读值不值时，不替他省掉：拿样板页的审读分类（几处、几处会读歪、哪几类）给他看，让他选。
5. 轻量页（国富论那种）不单派审读员，主编验收时多读两节。

**I. 接入和上线**（B 里没拿到授权的话，每一步先问）：

- 首页卡片：在 `~/tutorials-home/index.html` 复制一个 `.tut` 块，`data-progress="<前缀>-done-:<页数>"`。
- 同步白名单：把前缀加进 `~/tutorials-home/sync.js` 的 `PREFIXES` 和 `~/tutorials-deploy/sync/sync_server.py` 的 `KEY_RE`，后者用 `scripts/sync-apply.sh` 推到服务器。
  **服务器先推**（一个不认识的键整次拒收），再推 `tutorials-home`；`sync-apply.sh` 被自动模式拦就请用户 `! sh ~/tutorials-deploy/scripts/sync-apply.sh`。两个仓库别同时推（rrsync 撞锁），等前一个部署跑完。
- 英文伴读还要接词本：改 `~/tutorials-home/words.html` 的 `BOOKS`，以及 `words.html`、`index.html` 里匹配前缀的两个正则。
- 提交上线：`git add <目录名>/ && git commit && git push`，再 `gh run watch` 看部署，最后 `~/tutorials-deploy/scripts/check-site.sh <目录名> index.html <一个章节页>`。
- `tutorials-home` 和 `tutorials-deploy` 各自提交、推送。

**J. 收尾记录。**

- 补全 `<目录名>/CLAUDE.md`，`NEXT_STEPS.md` 的「现在」写成「全书完成」和以后改页面要注意的事。
- 这本书的 `BRIEF.md`、`REVIEW.md` 里有值得每本书都带上的新教训，就改 `_tools/templates/` 里的模板。
- 在本仓库 `README.md` 的书单里加一行。
- 在 `~/tutorials-deploy/README.md` 的踩坑记录里写这本书的新教训；PLAYBOOK「各站各自的答案」表里也加一行。

## 每本书的两份记录

开目录时就建，都不部署。下次用户报同一个书名时，靠它们接着做。分成两份，是因为 `CLAUDE.md` 每个会话、每位代理都会读到，流水账不该放在里面（Fooled 的写到了 19KB）。

**`<目录名>/CLAUDE.md`：固定信息，写好以后很少改，不超过 60 行。**

- 书名、作者、Calibre id，网址，键前缀，共享脚本叫什么，照哪个老站做的骨架。
- 用户在 B 里的回答：读者卡在哪、怎么读、用哪个译本、部署要不要问、额度怎么安排、看不看样板。
- 页表（哪几页、哪几页有模拟器、哪几页是揭晓页）。
- 怎么改、怎么验：要跑哪几个检查，哪些文件是脚本生成的、不能手改。
- 一句话：进度和待办在 `NEXT_STEPS.md`。

**`<目录名>/NEXT_STEPS.md`：进度。**

- 开头一节「现在」：做到哪一步（A–J），下一个会话第一件事做什么，待办。**每个会话结束前重写这一节**，不超过 20 行。
- 后面是按日期的简短记录：这个会话做了什么、定了什么。每页的验收细节记在 `source/ACCEPTANCE.md`，这里不重复。

## 硬性约定

- **对 Calibre 书库只读。** 只用 `_tools/calibre.py` 查书和挂软链接，不往书库里写，不改 `metadata.db`。
- **提交只加自己那本书的目录**：`git add <目录名>/`，不要 `git add .` 或 `git add -A`。几个会话同时写不同的书是常态，它们共用一个工作区。推送被拒就 `git pull --rebase` 再推。
- 原书材料（`source/` 里的软链接、提取的文本、译本）不入库、不部署。运行读这些文件的 Python 时加 `-I`。
- 目录名不以 `_` 开头：`_` 开头的是仓库自己的工具目录，不部署。
- 改了部署方式或踩了新坑，更新本仓库的 `README.md`，必要时也更新 `~/tutorials-deploy/README.md`。
