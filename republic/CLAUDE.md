# 理想国（Plato, Republic）· 全文对照＋导读

- 书：柏拉图《理想国》十卷，斯特方码 327a–621d。**书库里没有这本书**，没有 `source/calibre`；底本是网上取的公版文本，放在 `source/raw/`（`new-book.sh` 没跑，目录是手建的）。
- 网址 https://t.miaowuao.cn/republic/ ，目录 `republic/`，localStorage 键前缀 `rp-`，共享脚本 `assets/rp.js`（E 步建）。
- 和以前的站不一样：**站上放整本英中对照全文**（公版），导读穿插在旁边。全文翻译没有现成流程，在第一卷上试出来。
- 参考书：书库里有余纪元《〈理想国〉讲演录》（id 6657，AZW3，有版权），要用时挂成 `source/calibre-ref`，只当导读作者的背景，不搬内容。

## 版权

- 能整本放：希腊文原文；Shorey 英译（Loeb 1930/1935，译者 1934 年去世）；Jowett 英译（1892 第三版）。各来源的许可原话见 `source/reports/extract.md`。
- 中文全文是本站新译：以 Shorey 为底本，对 Jowett，关键词和有疑问处对希腊文。站上写明「从英译转译、对过希腊文，不是学术译本」。
- **译者、作者、审读员都不看有版权的译本**（中文：郭斌和 / 张竹明、王太庆、顾寿观等；英文：Bloom、Grube / Reeve、Griffith 等），译文只从上面三份公版文本来。
- `overlap.py` 和 lint 的引用上限是为有版权的书设的：全文页要豁免（E 步定参数），导读页引的是公版文本，也不设上限。

## 用户的回答（2026-11-16，B 步）

- 卡在哪（四样都选）：**论证绕、跟不上**（给每段论证画路线：谁主张什么、苏格拉底怎么反驳、走到哪一步）；**希腊背景不熟**（人物卡、雅典当时的情况、荷马和神话典故）；
  **概念抽象**（大白话和图）；**不知道今天怎么看**（每页「今天怎么看」和「本站怎么看」，记忆 views-with-commentary、reader-for-joy）。
- 提前知道内容：没坏处（主编定的，没问），不设分界线。
- 怎么读：**直接在站上读新译全文**，手上没有中译本，不做译本对照和勘误。
- 英译底本：**Shorey 为主**整本放，Jowett 只在名段作对照。
- 英文词条：**不要**，不接词本。
- 部署：**第一卷做完直接上线**，做完告诉用户（首页卡片、同步白名单、推送；这个授权只管这本书）。
- 范围：**先只做第一卷**（327a–354c：全文对照＋导读 2–3 页）。上线后用户看成品、看用量，再定后九卷是全做还是只做导读加名段。
- 谁来做：**活都派 Opus 子代理**（用户说主会话太贵）。样板页也派 Opus 写，主编只定方案、跑检查、验收。Agent 调用要写 `model: "opus"`。

## 原书材料

- `python3 -I tools/extract.py` 生成 `source/text/` 的全部内容，不手改；格式写在脚本开头。
  `NN.txt` Shorey 正文（`[327a]` 斯特方码标记）、`notes/NN.txt` Shorey 脚注、`grc/NN.txt` 希腊文、`jowett/NN.txt`、`index.tsv` 一节一行。
- 来源：Shorey 和希腊文（Burnet）是 PerseusDL `canonical-greekLit` 的 TEI XML（`tlg0059.tlg030.perseus-eng2 / grc2`），**CC BY-SA 4.0，要署 Perseus 并链到它和源仓库**（页脚或「关于底本」里写）；Jowett 是古腾堡 #1497。
- 十卷 1355 个斯特方节：Shorey 12.4 万词＋脚注 2767 条，希腊文 8.8 万词，Jowett 11.8 万词。第一卷 327a–354c 共 136 节，Shorey 1.36 万词、脚注 208 条。
- 对照只能**按斯特方节对齐**：Shorey 第一卷只有 26 段，希腊文和 Jowett 各约 490 段；Jowett 不带斯特方码。Shorey 的节号有时比希腊文早或晚半句（331c、338c）。
- Shorey 的引号是提取脚本加的（XML 里只有 `<q>`）；`[cit. …]` 是 Perseus 加的出处，不是 Shorey 的文字，站上不显示。XML 没有逐句的说话人标注。

## 页表、怎么改、怎么验

- 页表在 `assets/chapters.js` 的 `RP_PAGES`：`01a` 327a–331d 克法洛斯、`01b` 331e–336a 玻勒马霍斯、`01c` 336b–347e 色拉叙马霍斯上、`01d` 348a–354c 色拉叙马霍斯下；`00` 开读之前是主编页。往后加卷就加行。没有模拟器、没有揭晓页。
- 一页九节：读之前三节（这一段在争什么、出场的人、需要的背景）→ 全文 → 论证路线、概念 → 今天怎么看 → 本站怎么看 → 精彩回顾。样板页 `chapters/01a.html`。
- **翻译流程**：译者照 `tools/TRANSLATE.md` 写 `text/zh/<页>.txt`（按斯特方节，末尾 `## 注`）→ 译文审读员照 `tools/TR-REVIEW.md` 直接改 → 新译名并进 `GLOSSARY.md`。一页一位译者、一位审读，都是 Opus。
- **全文块**由 `python3 -I tools/gen_text.py <页>` 生成进章节页的 `TEXT:BEGIN/END` 之间，不手改；译文或路标（`text/marks/<页>.txt`）改了就重跑，否则 lint 报过期。它会改 `assets/chapters.js`，**只由主编跑**。
- 导读作者照 `source/BRIEF.md`、审读员照 `source/REVIEW.md`（`source/` 不入库，丢了照 `_tools/templates/` 重建）。阅读包 `sh tools/pack.sh [--review] <页>`。
- 每页三项检查：`python3 -I tools/lint.py chapters/<页>.html`、`python3 -I tools/overlap.py chapters/<页>.html`（小壳：跳过全文块，不限引用处数）、`node tools/check.mjs chapters/<页>.html`。
- 进度 `sh tools/status.sh`；验收看节 `python3 -I tools/peek.py chapters/<页>.html`、`tools/accept.py`。

## 上线（2026-11-16，第一卷）

- 首页卡片在 `~/tutorials-home/index.html`（`data-progress="rp-done-:5"`，四页＋00）；`rp-` 在 `sync.js` 的 `PREFIXES`、`sync_server.py` 的 `KEY_RE`。不接词本。
- 改了页面：三项检查都过再 `git add republic/` 提交推送，`gh run watch` 不接管道，最后 `~/tutorials-deploy/scripts/check-site.sh republic index.html chapters/<页>.html`。
- 加页以后：首页卡片的页数和条数（注、论证路线步数、今天怎么看张数）、00 页「现在做到哪」要跟着改。
- `GLOSSARY.md` 和 `text/` 会部署出去（本站自己的译文，CC BY-SA，无妨）。

进度和待办在 `NEXT_STEPS.md`。
