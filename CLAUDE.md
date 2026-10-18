# 导读站总仓库

2026-10-18 起，新书的导读站都放在这个仓库里，一本书一个一级目录，部署到 `https://t.miaowuao.cn/<目录名>/`。
本仓库的结构和部署方式见 `README.md`。下面三份是做书的依据，动手前要读：

- `~/tutorials-deploy/README.md`：服务器、同步、首页、取图、踩过的坑。最上面的表是 13 个老站。
- `~/tutorials-deploy/PLAYBOOK.md`：选型表。一本书该做成什么样，靠四个问题来定。
- `~/tutorials-deploy/AUTHORING-COMMON.md`：章节页的公共规范，包括版权红线、页面约定、自检、报告格式。

## 用户报一个书名时

先判断这本书属于哪种情况：

1. **老站已经做过**：书名出现在 `~/tutorials-deploy/README.md` 的教程表里。去那个目录（如 `~/ddia`）干活，不在这里新建。
2. **本仓库已有它的目录**：读 `<目录名>/CLAUDE.md`，看做到哪一步，接着做。
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
- 用户要的东西从一开始就做上：每章一节「精彩回顾」，外加汇总全书的 `recap.html`（他隔几周回来时靠它回忆）。
  交互组件要用大白话写清该填什么、每一列是什么。「成立 / 被改写」这类结论标签要有图例，并写明判的是哪句话。

**F. 样板页。**

- 主编自己写一章做样板，`check.mjs`、`overlap.py`、`lint.py` 三项检查都要跑通。
- **写完给用户看，等用户认可了再铺开。**
- 样板页也要过事实核查轮。

**G. 铺开。**

- 写 `source/BRIEF.md` 作为作者任务说明，照 `~/systems_performance/source/BRIEF.md` 或 `~/free_to_choose/source/BRIEF.md` 改。
- 作者用 Opus（2026-10-14 用户定的）。一章派一个作者，十几个作者分两条消息派出。
- 任务说明里要写明工作目录是 `/home/lee/my_book_companion/<目录名>`，先用 `pwd` 确认。
- 作者只写自己那一章的页面和图片，不做 git 操作，不再派子代理。
- 派之前先把任务说明里每章的提示和原文对一遍：CMC 那次就有几条提示写错了。
- 主编逐页**读**交回的页面再验收，不能只信作者的报告。验收记录写在 `source/ACCEPTANCE.md`。

**H. 事实核查轮。**

- 核查说明写在 `source/FACTCHECK.md`，派 5、6 个核查员。
- 已经收进目录的页就可以开始核查，不必等最后几位作者交稿。一页只交给一个人改。
- 技术书的命令，核查员要真的在本机跑一遍。

**I. 接入和上线**（B 里没拿到授权的话，每一步先问）：

- 首页卡片：在 `~/tutorials-home/index.html` 复制一个 `.tut` 块，`data-progress="<前缀>-done-:<页数>"`。
- 同步白名单：把前缀加进 `~/tutorials-home/sync.js` 的 `PREFIXES` 和 `~/tutorials-deploy/sync/sync_server.py` 的 `KEY_RE`，后者用 `scripts/sync-apply.sh` 推到服务器。
- 英文伴读还要接词本：改 `~/tutorials-home/words.html` 的 `BOOKS`，以及 `words.html`、`index.html` 里匹配前缀的两个正则。
- 提交上线：`git add <目录名>/ && git commit && git push`，再 `gh run watch` 看部署，最后 `~/tutorials-deploy/scripts/check-site.sh <目录名> index.html <一个章节页>`。
- `tutorials-home` 和 `tutorials-deploy` 各自提交、推送。

**J. 收尾记录。**

- 补全 `<目录名>/CLAUDE.md`。
- 在本仓库 `README.md` 的书单里加一行。
- 在 `~/tutorials-deploy/README.md` 的踩坑记录里写这本书的新教训；PLAYBOOK「各站各自的答案」表里也加一行。

## 每本书的 `<目录名>/CLAUDE.md`

开目录时就建，每过一个阶段更新一次。它不部署。下次用户报同一个书名时，靠它接着做。要写的内容：

- 书名、作者、Calibre id，网址，键前缀，共享脚本叫什么，照哪个老站做的骨架。
- 用户在 B 里的回答：读者卡在哪、怎么读、用哪个译本、部署要不要问。
- 现在做到哪一步（A–J），下一步是什么；样板页是哪一页，用户认可了没有。
- 怎么改、怎么验：要跑哪几个检查，哪些文件是脚本生成的、不能手改。

## 硬性约定

- **对 Calibre 书库只读。** 只用 `_tools/calibre.py` 查书和挂软链接，不往书库里写，不改 `metadata.db`。
- **提交只加自己那本书的目录**：`git add <目录名>/`，不要 `git add .` 或 `git add -A`。几个会话同时写不同的书是常态，它们共用一个工作区。推送被拒就 `git pull --rebase` 再推。
- 原书材料（`source/` 里的软链接、提取的文本、译本）不入库、不部署。运行读这些文件的 Python 时加 `-I`。
- 目录名不以 `_` 开头：`_` 开头的是仓库自己的工具目录，不部署。
- 改了部署方式或踩了新坑，更新本仓库的 `README.md`，必要时也更新 `~/tutorials-deploy/README.md`。
