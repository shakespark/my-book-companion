# Darwin's Worms · 导读

- 书：Adam Phillips, *Darwin's Worms: On Life Stories and Death Stories*（Faber 1999；这份电子书是 Basic Books 版）。
  Calibre id **5612**（有 EPUB，是 Calibre 从 AZW3 转的），`source/calibre`。
- 正文四篇：01 Prologue（7776 词）、02 Darwin Turns the Worm（7328）、03 The Death of Freud（11911）、04 Epilogue（5556），共约 3.3 万词。
  原书没有小标题，只有空行分隔（epub 里上边距 1em 的 `noindent` 段），提取成 24 节：7 / 5 / 8 / 4。节名由本站起。
- EPUB 有少量扫描识别错字（`in. the trees`、`heirarchy`、`a’continental scale`、`an, insufficiently`），文本照原样保留。
- 网址 https://t.miaowuao.cn/worms/ ，目录 `worms/`，localStorage 键前缀 `dw-`，共享脚本 `assets/dw.js`。骨架照 On Borrowed Time（`borrowed/`）。

## 用户的回答（2026-10-20）

- 卡在哪：**概念、人和作品背景、主线、语言，四样都要**（和 On Borrowed Time 一样）。
- 用户另外问：「是否可以结合达尔文自己研究蚯蚓的著作？这个著作应该是公开版权了吧」。
  是：1881 年的 *The Formation of Vegetable Mould through the Action of Worms* 公有领域（达尔文 1882 年去世）。
  公有领域原典放在 `source/pd/`（Gutenberg 2355 蚯蚓书、2010 自传 1887 版、1228 物种起源第 1 版；其余由代理收集，见 `source/pd/INDEX.md`）。
- 怎么读：**Kindle**（这份 EPUB）。单个生词一般不收；`.loc` 一字不差、能搜。
- 译本：**没有中译本**，页面不写译本译法。
- 提前知道内容：**没影响，不分读前读后**。
- 原书：商业出版，全套版权红线。
- 部署：**到时候直接做，做完告诉用户**（首页卡片、同步白名单、推送上线；只限这本书）。
- **每页最后要讲清「作者到底说了什么」，并给出本站自己的观点**（用户 2026-10-20 开工后补的，原话：「这本书哲理性较强，我需要你给我更多的帮助，比如在每章最后增加一节作者到底说了什么，你是什么观点的讨论，否则我很容易陷入到文字中」）。
  做成两节：「读完：作者到底说了什么」（3–5 条论点按逻辑重组、合起来；一篇最后一页加「X 篇合起来」）和「本站怎么看」（2–3 块 `div.views`：主流看法 / 作者的看法 / 本站的评论，最后 `p.verdict` 本站的总体看法）。lint 都查。

## 页和节

- 9 页：01a 01b 02a 02b 03a 03b 03c 04a 04b（一页是一篇里连续的几节，2200–4600 词），外加主编页 00「开读之前」和 vm「达尔文的蚯蚓书」（1881 年那本书本身，公有领域，排在 02b 之后）。页表在 `assets/chapters.js` 的 `DW_PAGES`（`need: ["pd"]` 的页必写原典一节），lint 从那里读。
- 每页十三节：这一页在做什么 / 读之前 / 路线 / 分节地图 / 先用中文过一遍：概念 / 书里的人和作品 / 原典：达尔文和弗洛伊德的原文 / 词与短语 / 值得停下来的句子 / 读完：作者到底说了什么 / 本站怎么看 / 检查一下理解 / 精彩回顾。
- **原典**：`source/pd/` 是公有领域原文（达尔文英文原文；弗洛伊德德文原文，Strachey 英译有版权不用）。页面 `<blockquote class="pd-orig">` 整段放原文配本站全译，lint 核对原文一字不差出自 `source/pd/*.txt`；overlap 用 `--skip-class pd-orig` 跳过这一块（2026-10-20 给共用的 `~/tutorials-deploy/scripts/overlap.py` 加的参数）。
- 全书的线：`DW_STAGES`（四段 = 四篇）和 `DW_SECS` 每节的 `t`（本站节名）、`en`（开头几个词）、`line`，主编写；依据和概念分工、每页提示在 `source/LINE.md`。
- `.loc` 和分节地图的 `.en` 不含引号（Kindle 上不好打字搜）；错字照抄。

## 进度

- [x] A 找书　[x] B 问用户　[x] C 开目录（2026-10-20）
- [x] D 提取（2026-10-20）：`tools/extract.py` → `source/text/01–04.txt`、`index.tsv`
- [x] E 规范和骨架（2026-10-20）：`AUTHORING.md`、`assets/dw.js`、`assets/style.css`（照 borrowed，末尾加原典块和看法块）、`assets/chapters.js`、`index.html`、`recap.html`、`terms.html`、`tools/lint.py`、`tools/overlap.py`；`source/LINE.md`、`source/REVIEW.md`
- [ ] F 样板页 `chapters/02b.html`（达尔文篇 §3–§5，主编写）：三项检查通过，审读中；**等用户认可**
- [ ] G 铺开　[ ] H 审读轮　[ ] I 上线　[ ] J 收尾

## 怎么验

```sh
python3 -I tools/lint.py chapters/<页>.html
python3 -I tools/overlap.py chapters/<页>.html
node tools/check.mjs chapters/<页>.html --shots source/shots
```
`source/text/`、`index.tsv` 是 `tools/extract.py` 生成的，不手改。`source/.venv` 装了 Pillow（取图）。
