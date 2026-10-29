# 导读站总仓库

2026-10-18 起，新书的导读站都放在这里，一本书一个目录，不再为每本书单建 GitHub 仓库、部署密钥和 Secret。
之前的 13 个站仍在各自的仓库里，不搬（见 `~/tutorials-deploy/README.md` 的教程表）。

```
my_book_companion/
  .github/workflows/deploy.yml   推送到 main → 把改动过的书 rsync 到 t.miaowuao.cn/<目录名>/
  _tools/                        仓库自己的工具，不部署
    calibre.py                   在 Calibre 书库里查书、挂软链接（只读）
    new-book.sh                  开一本书的目录骨架
  <目录名>/                      一本书一个目录，网址就是 /<目录名>/
    index.html chapters/ assets/ 部署
    AUTHORING.md tools/          不部署
    source/calibre -> /mnt/d/calibre/books/<作者>/<书名 (id)>/   不入库、不部署
```

## 书单

| 书 | 目录 / 网址 | 键前缀 | Calibre id | 状态 |
|---|---|---|---|---|
| Paris to the Moon（Adam Gopnik） | `paris/` · https://t.miaowuao.cn/paris/ | `pm-` | 6412 | 2026-10-19 上线：24 页，核查和词条审读都做过 |
| Flowers for Algernon（Daniel Keyes），附回忆录 Algernon, Charlie, and I | `algernon/` · https://t.miaowuao.cn/algernon/ | `al-` | 2262（回忆录 5575，中译本 6838） | 2026-10-19 上线：小说 18 页＋回忆录 7 页＋开读之前＋中篇和长篇对照，核查和词条审读都做过 |
| On Borrowed Time（Harald Weinrich，Rendall 英译） | `borrowed/` · https://t.miaowuao.cn/borrowed/ | `bt-` | 6053 | 2026-10-19 上线：19 页＋开读之前，审读轮（核查和词条审读合一）做过 |
| Up from the Projects（Walter E. Williams 自传） | `projects/` · https://t.miaowuao.cn/projects/ | `up-` | 5613 | 2026-10-20 上线：12 页＋开读之前，审读轮做过；和 Odyssey、Letters 互链 |
| Darwin's Worms（Adam Phillips），附达尔文 1881 年蚯蚓书专页 | `worms/` · https://t.miaowuao.cn/worms/ | `dw-` | 5612 | 2026-10-20 上线：9 页＋开读之前＋蚯蚓书专页，审读轮做过；页面「原典」整段放达尔文、弗洛伊德的公有领域原文 |
| The Selfish Gene（Richard Dawkins，30 周年版），对照中译本 40 周年增订版 | `selfish/` · https://t.miaowuao.cn/selfish/ | `sg-` | 2218（译本 6839） | 2026-10-21 上线：22 页＋开读之前，审读轮做过；5 个模拟器，每页尾注导读和逐段译本勘误，另有对照今天、译本勘误两个汇总页 |
| 国富论（Adam Smith，Cannan 1904 年版），对照杨敬年中译本 | `wealth/` · https://t.miaowuao.cn/wealth/ | `wn-` | 6844、6845（译本 6840） | 2026-10-21 上线：28 页＋开读之前（9 核心、19 轻量），核心页做过收窄审读；节分先读 / 有空 / 可跳过，全书最短读法；每条论点标今天怎么看；逐段译本勘误；2 个模拟器 |
| Uncontrolled（Jim Manzi，2012） | `uncontrolled/` · https://t.miaowuao.cn/uncontrolled/ | `uc-` | 6452 | 2026-10-22 上线：20 页＋开读之前，样板审读、底稿核对、审读轮都做过；节就是原书小标题，节分先读 / 有空 / 可跳过和全书最短读法；5 个模拟器；对照今天只用出版后的证据 |
| Impro（Keith Johnstone，1979），对照饶昊鹏中译本 | `impro/` · https://t.miaowuao.cn/impro/ | `im-` | 6413（译本 6846） | 2026-10-22 上线：18 页＋开读之前，每页一位审读员全审；游戏卡 73 张（`games.html`），逐段译本勘误 332 条（`zh.html`），2 个模拟器，节分先读 / 有空 / 可跳过和全书最短读法；页头和分节地图以译本为主 |
| The Making of a Manager（Julie Zhuo，2019），对照許恬寧繁体译本 | `manager/` · https://t.miaowuao.cn/manager/ | `mm-` | 6847（译本 6848） | 2026-10-27 上线：11 页＋开读之前，英文纸书为主、对着繁体译本逐段读；情境卡 38 张（`cases.html`）、原创判断题 32 道（`drills.html`）、词条 587 条接词本、逐段译本勘误 84 条（`zh.html`）；节分先读 / 有空 / 可跳过和全书最短读法；6 位审读员两页一人审完 |
| Fooled by Randomness（Nassim Nicholas Taleb，2004 增订第二版），对照羅耀宗繁体译本 | `fooled/` · https://t.miaowuao.cn/fooled/ | `fb-` | 6352（译本 6851） | 2026-10-29 上线：19 页＋开读之前，繁体译本为主、对着英文读；页中间「先停下，去读原书」的分界，线以下默认收起；5 个模拟器（蒙特卡洛、看盘频率、偏态、抛硬币的经理、体检假阳性）；词条 341 条接词本、逐段译本勘误 163 条（`zh.html`，开头有繁简术语对照）；节分先读 / 有空 / 可跳过和全书最短读法；每页一位审读员 |

## 新增一本书

完整流程（问用户什么、样板页、派作者、核查、上线）见 `CLAUDE.md`「新书的流程」。下面只是开目录这一步。

只给决定要做的书开目录，书库里其他书不碰。

1. 查书的 id：`python3 _tools/calibre.py find "Free to Choose"`
2. 开目录：`_tools/new-book.sh ftc2 1288`（目录名不能和线上已有的站重名，脚本会查）。
   得到 `ftc2/tools/`（三个共用检查脚本的小壳）和 `ftc2/source/calibre`（指向书库里这本书的目录）。
   提取的文本照老站的做法放在 `ftc2/source/text/`，同样不入库。
   一本导读要用到第二、三本书（译本、姊妹篇）时，给链接名再挂一次：`python3 _tools/calibre.py link ftc2 <id> calibre-zh`（`algernon/` 就是这样挂了回忆录和译本）。
3. 后面照 `~/tutorials-deploy/README.md`「新增一个教程」的第 0、1、7、8、9 步：定策略、写规范、备案号页脚、localStorage 前缀、
   线上检查、首页卡片、同步白名单。**第 2–5 步（workflow、建仓库、部署密钥、推送设置）不用做了**，提交推送本仓库即可：
   ```sh
   git add ftc2/ && git commit -m "…" && git push
   ```

## 部署怎么走

- 一级目录里名字不以 `_` 或 `.` 开头、含 `index.html` 的算一本书。
- 普通推送只部署这次改动过的书；手动触发（`gh workflow run deploy`）、首次推送、强推或改了 workflow 时全部重推。
- 一本书一本书地 `rsync --delete` 到 `deploy@t.miaowuao.cn:<目录名>/`。**绝不能把仓库根目录 `--delete` 到服务器根目录**，那会删光首页和老站。
- 和老站重名的目录不推（workflow 里的 `reserved`），老站新增时把名字加进去。
- 整个仓库只用一把部署钥匙（服务器 `authorized_keys` 里注释为 `github-actions-deploy@books`）。

## 注意

- **从仓库里删掉一本书，服务器上的目录不会跟着删**，要手动清：`ssh root@t.miaowuao.cn rm -r /var/www/tutorials/<目录名>`（先确认）。
- **几个会话同时写不同的书**：只 `git add <目录名>/`。推送被拒（别的会话先推了）就 `git pull --rebase` 再推。
- `source/calibre` 是软链接：在 Calibre 里改了书名或作者，书的目录会改名，链接就断了，删掉重新 `calibre.py link`。
