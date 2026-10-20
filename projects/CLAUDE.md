# Up from the Projects · 导读

- 书：Walter E. Williams, *Up from the Projects: An Autobiography*（Hoover Institution Press，2010）。Calibre id **5613**，`source/calibre`。
  书库里原只有 MOBI，EPUB 是用户 2026-10-20 在 Calibre 里转的。用户的 Kindle 版和书库这本一致（用户说的）。
  扫描识别的文字：数字混字母（i98os、8o）、词粘连、直引号、无斜体；章名是图片；第 7 章开头一句丢了前几个字（从 NTY-FOUR 起）。
- 网址 https://t.miaowuao.cn/projects/ ，目录 `projects/`，localStorage 键前缀 `up-`，共享脚本 `assets/up.js`。
- 骨架照 On Borrowed Time（`borrowed/`），对照今天照 Free to Choose，出场的人照 Odyssey。

## 用户的回答（2026-10-20）

- 卡在哪：**四样都要**：
  - 语言：口语、俚语、熟词生义，1940–60 年代费城黑人街区和军队的说法。
  - 时代和人物背景：种族隔离、征兵和驻韩美军、民权运动、UCLA 经济系，书里出场的人。
  - 经济学观点：他讲最低工资、执照、福利、歧视的经济学时，论证怎么走，先用中文讲清，再对照今天。
  - 情感和讨论：读后有话可说。
  - 外加**和 Sowell 的书对照**（用户在「卡在哪」里自己补的）。
- 提前知道内容：**没影响**，不分读前读后。
- 和姊妹站：**要互链**：两边说到同一件事，就链到 Odyssey（`~/a_personal_odyssey`，/odyssey/）或 A Man of Letters（`~/a_man_of_letters`，/letters/）；两边说法不一致时并排摆出来，不裁决。
- 怎么读：**英文 Kindle**，就是书库里这一本。`.loc` 必须一字不差；单个生词一般不收（长按能查）。
- 译本：没有（用户只有电子书）。页面不写译本译法。
- 原书：商业出版，全套版权红线。
- 部署：**到时候直接做，做完告诉用户**（首页卡片、同步白名单、推送上线；只限这本书）。
- 样板页：**用户 2026-10-20 说「不用给我看样板了，直接做完吧」**。样板页照常过三项检查和审读，不等用户认可。

## 页和节

- 12 页（一页是一章里连续的几个原书小标题）：01a 01b 02 03a 03b 04a 04b 05a 05b 06a 06b 07，外加主编写的 00「开读之前」。页表在 `assets/chapters.js` 的 `UP_PAGES`（`need` 是这一页必写的可省小节：econ / sowell / today）。
- 原文一章一个文件 `source/text/01–07.txt`，序言并在 01 的最前面记作 §0；章首到第一个小标题记作 §1。`{IMG}` 后面是 `source/imgtext/` 的转写（36 张，22 张是剪报、文件、信）。
- 每页十四节，见 `AUTHORING.md`。`terms.html` 汇总经济学概念块，`recap.html` 汇总精彩回顾。
- 底稿：`source/PLAN.md`（通读全书，主编用）、`source/SOWELL.md`（和 Odyssey、Letters 的 37 条对照；老站没有锚点，只链到页）。

## 进度

- [x] A 找书　[x] B 问用户　[x] C 开目录（2026-10-20）
- [x] D 提取：`tools/extract.py` → `source/text/`、`index.tsv`、`images.tsv`；图片转写 `source/imgtext/`
- [x] E 规范和骨架：`AUTHORING.md`、`assets/up.js`、`style.css`、`chapters.js`、`index.html`、`recap.html`、`terms.html`、`tools/lint.py`、`source/REVIEW.md`
- [ ] F 样板页 `chapters/01a.html`：三项检查通过，审读中
- [ ] G 铺开　[ ] H 审读　[ ] I 上线　[ ] J 收尾

## 怎么验

```sh
python3 -I tools/lint.py chapters/<页>.html
python3 -I tools/overlap.py chapters/<页>.html --max-quotes 2
node tools/check.mjs chapters/<页>.html --shots source/shots
```
`source/text/`、`index.tsv`、`images.tsv` 是 `tools/extract.py` 生成的，不手改；`UP_SECS` 的节名和词数从 index.tsv 生成。
