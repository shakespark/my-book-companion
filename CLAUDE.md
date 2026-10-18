# 导读站总仓库

2026-10-18 起，新书的导读站都放在这个仓库里，一本书一个一级目录，部署到 `https://t.miaowuao.cn/<目录名>/`。
部署架构、服务器、踩过的坑见 `~/tutorials-deploy/README.md`，写作的公共规范见 `~/tutorials-deploy/AUTHORING-COMMON.md`，**先读这两份**。本仓库的结构和步骤见 `README.md`。

工作约定：
- **只给用户点名的书做导读。** Calibre 书库（`/mnt/d/calibre/books`）里大部分书不做；不要扫书库批量建目录。
- **对 Calibre 书库只读。** 只通过 `_tools/calibre.py` 查和挂软链接，不往书库里写、不改 `metadata.db`。
- **提交只加自己那本书的目录**：`git add <目录名>/`，不要 `git add .` / `git add -A`。几个会话同时写不同的书是常态，共用一个工作区。
- 原书材料在各书的 `source/` 里（软链接和提取的文本），不入库、不部署。
- 每本书的页面要有备案号页脚；localStorage 键带这本书的前缀，并照 `~/tutorials-deploy/README.md`「跨设备同步」加进白名单。
- 目录名不能和老站重名（workflow 里有 `reserved` 名单），也不以 `_` 开头（`_` 开头的是仓库自己的工具目录，不部署）。
- 改了部署方式或踩了新坑，更新本仓库 `README.md`，必要时也更新 `~/tutorials-deploy/README.md`。
