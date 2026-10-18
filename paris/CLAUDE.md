# Paris to the Moon · 导读

- 书：Adam Gopnik, *Paris to the Moon: A Family in France*（Quercus 2011 年版 epub，约 11 万词）。Calibre id 6412，`source/calibre` 指向书库。
- 网址 https://t.miaowuao.cn/paris/ ，目录 `paris/`，localStorage 键前缀 `pm-`。
- 全书是《纽约客》专栏文章的合集：4 部分，23 篇（含 4 篇 Christmas Journal），约 11.7 万词，写 1995–2000 年一家人住在巴黎的日子。
- 读者的译本（待用户确认）：台湾马可孛罗版《巴黎到月球》，李桂蜜译（2008 年二版）。

## 用户的回答（2026-10-18）

- 卡在哪：**主线和语言分量相当**。主线：一篇随笔从小事扯到大道理，读完说不清在说什么。语言：熟词生义、典故、法国背景。
- 怎么读：**台湾译本纸书为主**，英文电子书辅助。本站没有译本文本：页面不写「译本译作」，不猜译本页码，按篇名和内容地标指路。
- 提前知道内容：**没有害处**，不设分界。
- 原书：商业出版，全套版权红线。
- 部署：**到时候直接做，做完告诉用户**（只限这本书）。

## 进度

- [x] A 找书　[x] B 问用户　[x] C 开目录
- [x] D 提取（`tools/extract.py` → `source/text/NN.txt`，篇号 01–23；`index.tsv` 是篇目和词数）
- [x] E 骨架（照 CMC：`assets/pm.js`、`chapters.js`、`style.css`、`index.html`、`recap.html`、`tools/lint.py`）；`AUTHORING.md` 已写（2026-10-18）
- [x] F 样板页 `chapters/03.html`（The Strike），用户 2026-10-18 认可（「照这个样板铺开」）
- [x] G 铺开：22 位作者（Opus）各写一篇，任务说明 `source/BRIEF.md`；主编逐页验收，记录在 `source/ACCEPTANCE.md`
- [ ] H 核查：7 位核查员（`source/FACTCHECK.md`，收件箱 `source/factcheck-inbox.md`），另加一轮词条审读（`source/ENTRYREVIEW.md`）：验收时多数页只读了上半页，词条只有作者看过
- [ ] I 上线（首页卡片、同步白名单、词本；`tutorials-home`、`tutorials-deploy` 的代码改动已做好未推）　[ ] J 收尾

## 版式要点（样板页定下的）

- 十节，`<h2>` 一字不差：这一篇在做什么 / 读之前：这篇的来历 / 这一篇的路线 / 分节地图 / 背景：作者默认你知道的事 / 词与短语 / 后来（可省）/ 值得停下来的句子 / 检查一下理解 / 精彩回顾。
- 读者以译本为主：分节地图的 `<b>` 是中文地标（读译本时认得出的场面），`.en` 是英文那一节开头 4–7 个词（电子书里搜）；不写英文页码。
- 「路线」防止写成摘要：一张 SVG、一段说怎么走，结论只在 `p.landing` 里说一次；lint 限字数。
- 词条只收中文传不出原味的：熟词生义、反话挖苦、典故、夹着的法文；每千词至少 4 条、一页最多 70 条、trap 至少三分之一。
- 没有原书分隔的长篇（02 Private Domain、15 The Rookie、17 The Balzar Wars、21 Like a king）由主编在 `tools/extract.py` 里按段号分节，标「本站分」，页面上 `<li class="ours">`。10 Trouble at the Tower 只有 800 词，不分。
- 《纽约客》刊期查不到可靠出处就不写（`chapters.js` 的 `ny` 留空）。
- 检查：`python3 -I tools/lint.py chapters/NN.html`、`python3 -I tools/overlap.py chapters/NN.html`、`node tools/check.mjs chapters/NN.html --shots source/shots`。
