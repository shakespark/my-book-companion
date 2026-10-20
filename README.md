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
