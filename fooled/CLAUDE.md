# Fooled by Randomness · 导读

- 书：Nassim Nicholas Taleb, *Fooled by Randomness: The Hidden Role of Chance in Life and in the Markets*，增订第二版（2004；这份 EPUB 是 Random House 平装本，含 Preface、Acknowledgments for the Updated Second Edition、Chapter Summaries、Prologue、14 章、Epilogue、Postscript「Three Afterthoughts in the Shower」、A Trip to the Library 和 Notes）。
  Calibre id **6352**（EPUB、MOBI），`source/calibre`。
- **译本（读者读的）**：繁体《隨機騙局》，**羅耀宗 譯**，大塊文化 2014（据 2004 年第二版），Calibre id **6851**（EPUB），`source/calibre-tw`。
  全书都译了：章節摘要、序「不必把知識看得那麼重」、更新第二版謝辭、前言「雲中的清真寺」、附筆「沖澡時想到的三件事」、第一版謝辭、註釋與書單；
  小标题和原书一一对应（目录 197 条逐条对得上），各章 1.55–1.65 字一词，很匀，没有看出删节。「譯註」夹在正文括号里。
  Nero Tulip 译作「尼洛．屠利普」，Part I「梭倫的警世之言」，Part II「打字機前的猴子」，Part III「在耳中塞蠟」。
- 简体本不用（用户 2026-10-29：「就按繁体为主，不管简体版了」）。书库里的《随机漫步的傻瓜》（盛逢时 译，中信 2012；id 6184 和 6850 是同一译文的两份电子书）
  版权页写第二版，其实是据 2001 年第一版译的：没有 2004 年的序、章节摘要、Postscript，第 11 章第二版扩写的部分也没有。`source/calibre-zh` 还挂着，不提取、页面不提。
- 网址 https://t.miaowuao.cn/fooled/ ，目录 `fooled/`，localStorage 键前缀 `fb-`，共享脚本 `assets/fb.js`。骨架照 Impro（`impro/`：以译本为主指路、逐段勘误、模拟器），词条和「记下」照 Manager（`manager/`），读前 / 读后分界照 Free to Choose 的 `div.gate`（本站加了默认收起）。

## 用户的回答（2026-10-29）

- 卡在哪：**概率直觉、主线和结构、背景和人物、现代视角的评论，四样都要**。
  - 概率直觉：偏态、蒙特卡洛、噪声和信息、幸存者偏差、遍历性。配几个能改参数的模拟器（全书定好数量，不为交互而交互）。
  - 主线：随笔式写法，常从交易室扯到梭伦、波普尔、蒙田，配分节地图。
  - 背景：华尔街交易、1998 年 LTCM 和新兴市场危机，书里的哲学家、作家。用户对经济学了解不多（见记忆 user-econ-novice），金融概念要从头讲。
  - 现代评论：2004 年成书，之后有 2008 年金融危机、《黑天鹅》和塔勒布后来的立场。每页写「主流看法 / 作者看法 / 本站评论」，末尾加「读完：作者到底说了什么」和「本站怎么看」（见记忆 views-with-commentary）。
- 怎么读：**繁体译本为主，对着英文原版读**（B 步答的是「简体译本为主」，用户找到繁体本后改成繁体为主）。
  页头和分节地图以译本的章名、小标题为主（照 `impro/`；繁体本小标题和原书一一对应，两边都能给），人名、术语用译本的译法；
  页面正文用简体和大陆说法，引译本时照抄繁体，一字不差（照 `manager/`）；每页一节逐段「译本勘误」，全站汇总（见记忆 translation-errata）；有少量英文词条，接词本。
- 提前知道内容：**没有坏处，但想先自己想**。页面中间设一道「先停下，去读原书」的分界，作者的完整论证和本站结论放在读后；Nero 和 John 两个交易员的结局不提前说。
- 原书和译本都是商业出版物，全套版权红线。
- 部署：**到时候直接做，做完告诉用户**（首页卡片、同步白名单、推送上线；这个授权只管这一本书）。
- 额度（2026-10-29）：**每个会话约 3 页**（照 Manager）：做完记待办，用户开新会话接着做（记忆 pace-one-page）。
- 样板（2026-10-29）：**不看，写完直接铺开**。样板照样审读，审读结果写进 `source/BRIEF.md`，不停下等用户（记忆 skip-sample-review）。

## 进度

- [x] A 找书　[x] B 问用户　[x] C 开目录（2026-10-29）
- [x] D 提取（2026-10-29）：`tools/extract.py`（照 `selfish/` 改）→ `source/text/00–16.txt`、`notes.txt`、`index.tsv`，译本（繁体）`source/text/zh/00–16.txt`、`zh/notes.txt`，章号和英文一一对应。
  - 英文：00 是 Preface、Acknowledgments for the Updated Second Edition、Chapter Summaries、Prologue、Acknowledgments for the First Edition；Part I/II/III 的篇首语在 01、08、12 开头；15 Epilogue、16 Postscript。`## ` 全大写小标题、`### ` 小小标题（以 toc.ncx 为准，197 条全对上），`[k]` 每章段号，`{Q}` 引文和章旨、`{T}` 表格行、`{F}` 图，`{注K}` 星号脚注（全书只有第 7 章两条），`notes.txt` 是书后按页码的尾注（正文没有链接）。
  - 字数：正文约 9.3 万词；最长 11 章 1.14 万词、03 章 8500 词，最短 14 章 1450 词、15 章 280 词。
  - epub 是从 MOBI 转的扫描版，有断词和粘连（empiri-cism、whospen），照原样保留。
  - 译本：`#` 章题和篇名、`##` 小标题、`###` 小小标题，`{Q}` 楷体（引文、章旨、篇的副题），`{F}` 图表标题，正文不编段号，繁体照原样。
  - 分节（2026-10-29 E 步开头补的）：节 = 有正文的那一级小标题，原书和译本 **171 节一一对上**，两边文本里小标题前都标了 `§k`；`index.tsv` 一节一行（章、节、段、词、原书小标题、译本小标题、en、译本字数、zs），章级的表改名 `chapters.tsv`。
    清掉的脏数据：`Part I/II/III` 段删了（01、08、12 的段号因此少 1）；Table/Figure 标题和第 11 章「Number of afflicted…」不再当小标题（改成不编号的 `{F}`、`{T}` 行）；11 章「We Do Not Understand Confidence Levels」挪到两张图后面；没有正文的大标题并进下一节；章首无小标题的正文是「（章首）」节；01 的 §1、08 和 12 的 §1–§4 是篇首语（08、12 的章旨在 §4 末尾）。
- [x] E 规范和骨架（2026-10-29）
  - 页（19 页加 00「开读之前」）：pr（00 §1–§6 序 + §11 前言）、01、02、03a（§1–§9）、03b（§10–§13）、04、05、06、07、08、09a（§1–§11）、09b（§12–§21）、10、11a（§1–§9）、11b（§10–§24）、12、13、14（含 15 后记）、16。
  - 模拟器 5 个：03a 平行的历史（蒙特卡洛，轮盘 vs 牙医；带「一千人各玩一次 / 一人连玩一百次」切换，演作者后来说的遍历性）、03b 看盘频率（噪声和信息）、06 偏态、09a 一万个抛硬币的经理（幸存者偏差、回归、本书说的遍历性）、11b 体检假阳性（基础比率）。
  - 底稿：5 位代理照 `source/LINE-TASK.md` 写 `source/line/NN.md`（a: 00 01 02；b: 03 04 05；c: 06 07 08；d: 09 10 12 13；e: 11 14 16）。
  - 后记并进第 14 章作 §4（段 13–15，提取时并的，照 Manager 把结语并进第 10 章），不再有 15.txt；页 14 的节是 1–4。
  - 已建（2026-10-29）：`AUTHORING.md`（十五节，第 9 节之后 `<div class="gate"></div>`；样板定为 `chapters/06.html`）、`assets/fb.js`（分界线之后包进 `section.after` 默认收起，`fb-open-页` 记展开；词条「记下」存 `fb-star-页-词条`）、
    `assets/style.css`（照 Impro，末尾加 gate、zhtitle、linechs）、`tools/gen_chapters.py`（读 index.tsv 和 `source/SECS.tsv` 生成 `assets/chapters.js`；SECS.tsv 第 6 列 zs 可省，译本开头会剧透时换一截）、
    `tools/lint.py`（照 Impro 改：去游戏卡和 landing，词条照 Manager 6–20 条、trap ≥ 1/3，查 gate 位置，译本 12 字重合繁体和转简体后各查一遍，`SPOIL` 剧透名单，照 `source/LINE.md`）、`tools/accept.py`、`tools/peek.py`、`overlap.py` 引用上限 2、
    `index.html`、`recap.html`、`terms.html`、`today.html`、`zh.html`；`source/.venv`（Pillow、opencc-python-reimplemented，lint 用它繁转简）。
  - 底稿 5 位都交了（`source/line/`，不上页面，作者动笔前读自己那章的）。主编据此写了 `source/LINE.md`（页表、概念分工、全站术语表、剧透名单和揭晓页的写法、跨页要知道的事）和 `source/SECS.tsv`（171 节的节名、档、line；14 §4 的 zs 换了一截不剧透的），lint 的 `SPOIL` 填好了，`gen_chapters` 跑通：19 页 166 节，先读约 35%。
  - 剧透：John 揭晓在 01 §9、Carlos 在 05 §2、Nero 的秘密在 11 §2（页 11a）、Nero 的结局在 14 §4。**揭晓页线以上也不说**（AUTHORING 和 LINE.md 一致）。
  - 模拟器能复现的数都在底稿末尾「模拟器」一节（03a、03b 在 03.md，06 在 06.md，09a 在 09.md，11b 在 11.md）。
  - I 步要记得：`~/tutorials-home/words.html` 的页 id 正则（`\d\d[a-z]?|m\d|in`）不认 `pr`，接词本时加上。
- [x] F 样板页（2026-10-29）：`chapters/06.html`（主编写；偏态，带模拟器「赢的次数和赚的钱」，`tools/sim06.mjs` 连点）。三项检查过，`accept.py` 收了（t「偏态：次数和大小」，d「赢的次数多，不等于赚钱」）。
  派审读前请顾问看过（改 4 处），审读员 r06（Opus，照 `source/REVIEW.md`）改 11 处、删勘误 1 条，约 4 处会读歪；记录在 `source/reports/06.md` 末尾和 `source/ACCEPTANCE.md`。
  据此：`source/BRIEF.md` 写好（作者任务说明，「样板页审读时抓到的错」十一类）；AUTHORING 加了「节号标签列全」「不写相对位置」「别被带歪框可说证据方向」；lint 加了「读完」和 `.at` 的节号标签查全。用户说不看样板，没等认可。
- [x] G 铺开：**2026-10-29 用户说「这次（只这次）把所有页都派出并发」，18 页作者一次派出**（Opus，名字 a<页>，pr 的叫 apr）。交稿的页逐页验收，验收一页就记 ACCEPTANCE 并在这里打勾。
  **2026-10-29 18 页作者全部交稿**（报告都是「状态：已交稿」，交稿时主编复跑过检查）。**下一步：逐页验收**，每个会话约 3 页，先看各报告末尾的「主编批注」（交稿时主编定下的事和验收要做的）。
  建议顺序：揭晓页 01 05 11a 14 先验（线以上剧透）；模拟器页 03a 03b 09a 11b 要亲手跑 `node tools/sim<页>.mjs`；成对的 03a/03b、09a/09b、11a/11b 同一会话验，对一遍两页的「读完」和「这一章合起来」。
  交稿期间主编改过的共享文件：`fb.js`（只有一章的段渲染出 "null"；不满 100 字的节显示「约 0 字」），`SECS.tsv`（12 §3 维特根斯坦、16 §5 line、2 §8 节名），`LINE.md`（賽局文獻 11b 和 13 各报；杠杆归 05 c-margin-call），`BRIEF.md`（报告落文件、SVG 黑白反色、通用 User-Agent），`zh.html`（术语对照）。
  作者自起的概念 id 很多（见各报告），验收时登记进 LINE.md 的分工表，并查有没有两页讲同一个概念。
  **新会话接手**：先跑 `tools/status.sh`，它列出每页有没有稿子、报告第一行的状态（`写作中` / `已交稿`）、ACCEPTANCE 收了没有。作者的报告全在 `source/reports/<页>.md`，不靠对话记录。
  「已交稿」没「收了」的，就是待验收的页，一个会话验收约 3 页。「写作中」的：派出它的会话还开着，就是作者还在写；那个会话已经关了，作者就停了，写了一半的页删掉（`chapters/<页>.html`、`assets/img/<页>-*`、CREDITS.md 里那几行、报告）再重派。
  报告文件的格式写在 BRIEF 末尾。
  **待办（a08 2026-10-29 提的）**：`SECS.tsv` 的 line 显示在线以上（`linehere` 条带），有的直接说出了这一节的论证或结论（如 8 §11「只拿活下来的基金回测，必然得出『买输家』」）。读者想先自己想：找个会话把 166 条 line 过一遍，改成只说「这一节讲什么、起什么作用」，不说结论；改完 `python3 -I tools/gen_chapters.py`。不急，上线前做完即可。
  **待办（多位作者提的）**：SVG 在 400 宽下是 560px、横滑，有几张图的要紧部分要滑过去才看得到（12 尺子图右栏、11a 参照点曲线「赚」的一半）。验收时看截图，逐张决定改成上下排还是不动。
  **验收进度（2026-10-29 第一个验收会话）**：收了 01 05 14（揭晓页，线以上按没读过的读者读过），审读员 r01 r05 r14 派出。
  主编验收时改的：01 §9「故事的转折」改「很短，只有两段」（页面、SVG、SECS.tsv）；05 Henry 卡补「十个西格玛」一句；zh.html 补 Nero Tulip、衍生性證券；LINE.md 登记 05、14 的自起概念和 c-sigma-event（归 13）。
  `tools/status.sh` 加了「审读」一栏：ACCEPTANCE 那行写「派出」= 派出了，报告里有「## 审读」= 审完。派出了没审完、会话已关的，重派审读员。审完的页，主编看一眼审读节、把改了几处 / 会读歪填进 ACCEPTANCE 那一行。
  r01 r05 r14 都审完了（2026-10-29），结果记进 ACCEPTANCE；01 审读发现作者常把「书里没给出处」说成事实，其实书后 Notes 有，已加进 REVIEW.md。
  收了 11a 11b（2026-10-29，同一会话接着做），审读员 r11a r11b 派出；四个揭晓页都验完了。11a 主编改 1 处（「经济学整个是规范科学」把作者说重了）。
  r11a r11b 审完（11a 改 7、11b 改 10）；两页的「今天怎么看」各有一张卡标题两句并列，审读员都没收窄，主编收的：这一类每页都要主编自己看。
  收了 03a 03b（2026-10-29），审读员 r03a r03b 派出；两个模拟器主编逐项手算过。
  r03a r03b 审完（03a 改 9、03b 改 6）。
  收了 09a 09b（2026-10-29），审读员 r09a r09b 派出；09a 模拟器主编逐项手算过。几页之间重复讲的概念（多重比较四遍、统计显著两遍、结果偏差五遍）记在 LINE.md 末尾，全站过一遍时合并。
  收了 pr 02 04（2026-10-29），审读员 rpr r02 r04 派出（r02 复算 9/11 波动卡）。04 主编改 2 处（卡标题收窄、[11] 改标译反）。
  r09a r09b 审完。收了 07 08 10（2026-10-29），审读员 r07（核 Niederhoffer 讣闻）r08 r10 派出；10 的章名「輸家通賠」译反，在「读之前」和 zh.html 补了说明。
  **下一个会话**：pr–11b、14 都已验收、审完、填进 ACCEPTANCE（2026-10-29）。验 12 13 16（最后三页）。验 13 时统一「西格玛」。之后是 G 步收尾：SVG 窄屏那条待办、166 条 line 改写、LINE.md 末尾的重复合并，再进 H。
  验 13 时：全页 16 处「希格玛」统一成「西格玛」（05 已改）。全站过一遍时：结果偏差 Baron 和 Hershey 1988 五页重复（见 LINE.md c-outcome-bias）。
  验收流程：主编读「读完」「本站怎么看」「译本勘误」和线以上的剧透，三项检查，登记新概念和术语，`accept.py`，记 ACCEPTANCE，再派审读（Opus，名字 r<页>，`读 source/REVIEW.md，照它审读 <ID>`，揭晓页加一句剧透提示）。审读员交回后主编打开改过的「今天怎么看」卡看一眼：r14 把标题改成了两句并列，和 REVIEW.md「把标题收窄」那条相反；不只信报告。REVIEW.md 里的 scratchpad 路径每个会话改成本会话的。
  **G 收尾（2026-10-29 最后一个会话，用户说「把剩下的工作都做了」）**：收了 12 13 16，r12 r13 r16 审完（12 改 5、13 改 4、16 改 11）。13 全页统一「西格玛」「维特根斯坦」「马科维茨」。
  166 条 line 改写了 123 条（只说这一节讲什么，不说结论；改前的版本在本会话 scratchpad，不留）。SVG 窄屏：不重画，`style.css` 给横滑的图加了一行「图比屏幕宽，左右滑动看全图」（sticky，截图看过）。
  LINE.md 末尾的重复看过：结果偏差在 01 02 03a 07 14 各只一句、各撑本页的卡，多重比较各有各的例子，**不合并**。
  全站查了一遍「今天」栏里 2004 年以前的研究（r12 在 12 抓到的一类）：05（IMF 1999 年调查）、10（Liebowitz 和 Margolis 1990）挪进「当时」，标签不变。
- [x] 00 开读之前（主编页，2026-10-29）：作者、和《黑天鹅》等后几本的关系、好在哪 / 要打折扣、二十多年以后（今天怎么看 51 条：成立 25、部分成立 18、被改写 5、有争议 3）、全书地图、译本须知（勘误 163 条：误译 107、术语 29、译反 14、漏译 9、数字 4）、最短读法（`#path`）。作者生平只写各页已核过的（沃顿 MBA、巴黎博士、Empirica 1999）。只跑 overlap 和 check。
- [x] H 核查、词条审读：**不另开一轮**。照记忆 review-not-academic，核查和词条审读合一，验收时每页派了一位审读员（r<页>，19 页全审），记录在 `source/ACCEPTANCE.md` 和各报告末尾「## 审读」。
- [x] I 上线（2026-10-29）：首页卡片 `fb-done-:19`；`sync.js` PREFIXES 和 `sync_server.py` KEY_RE 加 `fb-`（sync-apply 过）；词本 `words.html` 的 BOOKS 加 `fb`（页 id 含 `pr`），两个前缀正则加 `fb`、页 id 正则加 `pr`。
- [x] J 收尾（2026-10-29）：本仓库 README 书单；tutorials-deploy README 教程表和踩坑、PLAYBOOK 一行。

## 以后

**全书完成。** 以后用户报这本书，多半是要改某一页：照「怎么验」跑三项检查，改完 `git add fooled/` 提交推送即部署。
- 首页卡片上的数字是 2026-10-29 用脚本数的（今天怎么看按 `data-verdict`，勘误按 `.zherr .mark`，词条按 `.entry`，概念按 `.concept`，理解题按 `details.check`）。改了页面要更新卡片和 00 页的数时重新数。
- 以后要再派代理，先把 `source/BRIEF.md`、`source/REVIEW.md` 里的 scratchpad 路径换成新会话的。

## 怎么验
- `zh.html` 开头的「术语和人名对照」（2026-10-29 用户要的，英文 / 译本繁体 / 本站简体）是手写的静态表，不由脚本生成：只收繁简用词不同的，每条译法都在 `source/text/zh/` 里搜到过；另有一张「译本译得不对的几个术语」。
  验收时作者报告里新起的术语、人名，照这个格式补进去；本站一栏要和 `source/LINE.md` 的术语表一致。

- 改了 `tools/extract.py` 就重跑 `python3 -I tools/extract.py`，`source/text/` 全是它生成的，不手改。
- 节名、档、line 改 `source/SECS.tsv`，页表改 `tools/gen_chapters.py` 的 `PAGES`，然后 `python3 -I tools/gen_chapters.py`；`assets/chapters.js` 的节表是它生成的，不手改（每页的 t、d 和 `FB_READY` 重新生成时保留）。
- 06 的模拟器：`node tools/sim06.mjs`（照「试试看」连点，打印统计栏；别的模拟器页照它写 `tools/sim<页>.mjs`）。
- 每页：`node tools/check.mjs chapters/NN.html`、`python3 -I tools/overlap.py chapters/NN.html`、`python3 -I tools/lint.py chapters/NN.html`。
