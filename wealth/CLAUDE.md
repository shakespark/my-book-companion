# The Wealth of Nations · 导读

- 书：Adam Smith, *An Inquiry into the Nature and Causes of the Wealth of Nations*（1776；本站用 Edwin Cannan 编的版本，1904，Liberty Fund 在线图书馆的 EPUB，分两册）。
  Calibre id **6844**（上册，`source/calibre`）、**6845**（下册，`source/calibre-v2`）。公版书。
  全书五卷 32 章，约 38 万词。
- 中译本：《国富论》，杨敬年译，陕西人民出版社（电子版 2011），Calibre id **6840**（EPUB），`source/calibre-zh`。全译本，带格拉斯哥版注释和每章「导读」。商业出版物。
- 入门读物：Robert Heilbroner, *The Worldly Philosophers*（第七版）第 3 章，Calibre id **6841**（`source/calibre-wp`）；中译本《俗世哲學家》（商周，繁体）id **6842**（`source/calibre-wpzh`）。只用来写「开读之前」，读者不一定读。抽查过中译本第 3 章，误译较多，不推荐读者拿它当准。
- 网址 https://t.miaowuao.cn/wealth/ ，目录 `wealth/`，localStorage 键前缀 `wn-`，共享脚本 `assets/wn.js`（待建）。
- 2490、6798、6843 是古登堡计划的通行本，用户放弃格拉斯哥版（「就当只有 Cannan 版本」），都不用。

## 用户的回答（2026-10-21）

- 读者是对各种知识都好奇的门外汉，经济学了解不多。原话：「我不是专业读者，不用斤斤计较和比对。我只是想要作为一个对各种知识都感兴趣的门外汉，想要享受各种人类知识和智力的快乐。」
- 卡在哪：**经济学概念、主线和结构、18 世纪的英国、18 世纪英文**。另外的要求（原话）：「我不是为了学习这本书 18 世纪的书，而要从现代的角度看待这本书的观点，你要给出更多评论，不要让书把我带歪了。另外注意让我获得读书的快乐，而不是单纯的学知识。」
  → 每个观点都要有现代视角的评论（哪里对、哪里过时、被什么推翻）；页面要有故事、有惊喜、好读。
- 怎么读：**杨敬年译本为主，名段看英文原文**。导读按内容地标和杨译的章名、小标题指路，不写页码；译本勘误只收会把人读歪的（意思反了、关键术语错了，比如 police 译「警察」），门槛放高。
- 范围：**核心精读＋其余轻量**。「先读」那十来章每章一页讲透；其余章每章一页轻量页；全书地图标出最短读法。
- 提前知道内容：主编默认按无害处理，不设硬分界（告诉过用户）。
- 原书是公版：名段可以整段放英文原文，配本站白话译（照 Darwin's Worms 的「原典」）。杨译是商业出版物，引用受限。
- 部署：**到时候直接做，做完告诉用户**（首页卡片、同步白名单、推送上线；授权只管这一本书）。

## 进度

- [x] A 找书　[x] B 问用户　[x] C 开目录（2026-10-21）
- [x] D 提取（2026-10-21）：`tools/extract.py` → `source/text/<章>.txt`（章号 `1-08` 式，`[k]` 段号，`{M:…}` Cannan 页边小结，`{nK}` 脚注，章末 `## 注` 的 `{S}` 斯密注、`{C}` Cannan 注）、`index.tsv`；
  杨译 `source/text/zh/<章>.txt`（`{M}` 行是混在正文里的小标题，即 Cannan 页边小结的中译，有漂移）、`zh/daodu/`（各章导读）、`zh/front.txt`；
  `--wp` 另出 Heilbroner 第 2、3 章（`wp-02/03.txt`、`zh/wp-0*.txt`），只给 overlap 和 lint 查照抄用。
- [ ] E 规范和骨架（2026-10-21，大部分完成）：五位代理通读写底稿 `source/line/01–28.md`（任务 `source/LINE-TASK.md`）；主编的拍板记在 `source/DECISIONS.md`，**还要写 `source/LINE.md`（概念分工、术语表、全书的线）和 `source/BRIEF.md`**。
  已有：`AUTHORING.md`、`assets/wn.js`、`assets/style.css`、`assets/chapters.js`（`tools/build_chapters.py` 从 `source/pages.json` 和底稿节表生成，不手改）、`index.html`、`recap.html`、`terms.html`、`today.html`、`zh.html`、`tools/lint.py`、`tools/overlap.py`。
- [ ] F 样板页（2026-10-21 推上线，等用户认可）：核心页 `chapters/01.html`（全书引言和卷一第 1–3 章，别针厂模拟器），轻量页 `chapters/02.html`（卷一第 4 章，货币）。两页都过了审读（`source/ACCEPTANCE.md`）。首页卡片还没加。
- [ ] G 铺开　[ ] H 审读轮　[ ] I 上线　[ ] J 收尾

## 页和节

- 28 页 + 主编页 00（开读之前）。核心页 9 个：01 04 05 07 08 16 17 21 25；其余 19 个轻量页。页表 `source/PAGES.md`、`source/pages.json`。
- 节分三档：先读 / 有空 / 可跳过。全书先读约 10.3 万字（杨译），`wn.js` 按每分钟 300 字估时间，00 页的 `#path` 自动列出全书最短读法。
- 模拟器 2 个：01 别针厂、04 价格回摆。

## 怎么验

```sh
python3 -I tools/build_chapters.py        # 改了 pages.json 或底稿节表后
python3 -I tools/lint.py chapters/<页>.html
python3 -I tools/overlap.py chapters/<页>.html
node tools/check.mjs chapters/<页>.html --shots source/shots/<页>
```
