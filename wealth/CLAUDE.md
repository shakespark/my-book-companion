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

## 进度（handoff，2026-10-21 晚）

- [x] A–F 完成。样板页 01（核心）、02（轻量）用户看过，让继续。
- [ ] G 铺开，**已上线 25 页**：00 01–22 25（核心页 9 个全部完成）。
  **还剩 5 个轻量页**：卷五 23、24、26、27、28（5-02 赋税 4 万词，页 27 可单独派一人）。用户按卷下令（「可以开始处理卷X」）。
- [x] I 上线收尾（2026-10-21）：首页卡片已加（`~/tutorials-home/index.html`，`data-progress="wn-done-:28"`；标签里的数字等全书写完再补），`wn-` 已进同步白名单（sync.js PREFIXES、sync_server.py KEY_RE，已 sync-apply）。不接 words.html。
- [ ] J 收尾：本仓库 README 书单、`~/tutorials-deploy/README.md` 踩坑记录和教程表、PLAYBOOK 各站答案。

## 怎么接着做（用户定的规矩）

- **额度有 5 小时窗口**：一批写完、验收完、上线后，把结果和 token 用量报给用户，**等用户说话再派下一批**。用户说「开始处理卷X」就做那一卷。
- **轻量页两页派一个 Opus 作者**（一人约 35 万 token、25–30 分钟），任务说明照之前的写法：读 `source/BRIEF.md`（<ID> 换页号）、样板 `chapters/02.html` 和已验收的轻量页（03、06、09–13 都写得好）、`source/LINE.md` 的概念分工；交代这一卷「今天怎么看」的要点、别把斯密说绝对再反驳；两页报告写进 `source/reports/<页>.md`；只碰自己的文件。很长的章（4-07 殖民地 3.7 万词、5-02 赋税 4 万词）可以单独派一人。
- **轻量页不派审读员**：主编验收时读原典的本站译（对着英文）和「今天怎么看」两节，跑三项检查，`source/pages.json` 填 t、d、加进 ready，`python3 -I tools/build_chapters.py`，记 `source/ACCEPTANCE.md`。核心页（已全部完成）才派收窄版审读（`source/REVIEW.md`）。
- 作者报告里新起的概念 id 要登记进 `source/LINE.md`；勘误收不收、节名统一等拍板记 `source/DECISIONS.md` 或 ACCEPTANCE。
- 提交只加 `wealth/`（有作者在写时只加已验收页的文件），推送后 `gh run watch` 再 `~/tutorials-deploy/scripts/check-site.sh wealth chapters/<页>.html`（刚推完偶尔 404，等部署跑完再查）。
- 已定的译名：settlement laws =「定居法」（注杨译「户籍法」）；police 按上下文译治理、政策；projector 搞新计划的人。术语表在 `source/LINE.md` 第 5 节。

## 页和节

- 28 页 + 主编页 00（开读之前）。核心页 9 个：01 04 05 07 08 16 17 21 25；其余 19 个轻量页。页表 `source/PAGES.md`、`source/pages.json`。
- 节分三档：先读 / 有空 / 可跳过。全书先读约 10.3 万字（杨译），`wn.js` 按每分钟 300 字估时间，00 页的 `#path` 自动列出全书最短读法。
- 核心页十四节、轻量页九节，见 `AUTHORING.md`；`tools/lint.py` 按 `kind` 分别检查。正文里指路用的杨译小标题写 `<span class="zh">…</span>`（lint 核对）。
- 模拟器 2 个：01 别针厂、04 价格回摆。

## 怎么验

```sh
python3 -I tools/build_chapters.py        # 改了 pages.json 或底稿节表后
python3 -I tools/lint.py chapters/<页>.html
python3 -I tools/overlap.py chapters/<页>.html
node tools/check.mjs chapters/<页>.html --shots source/shots/<页>
```
