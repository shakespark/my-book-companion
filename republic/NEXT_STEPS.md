# 理想国 · 进度

## 现在

- **第一卷已上线（2026-11-16）**：`00` 开读之前＋`01a`–`01d` 四页（327a–354c），https://t.miaowuao.cn/republic/ ；首页卡片、同步白名单（`rp-`）都接了。A–I 对第一卷都做完。
- **等用户决定后九卷**：全做（全文对照＋导读），还是只做导读加名段。用户看过线上成品、看过下面的用量再定。**没说之前不动后九卷。**
- 接着做的话，一卷的流程（都派 `model: "opus"`，主会话只派活、跑 `gen_text.py`、验收）：
  1. 按论证把这一卷切成页，`grep -n` 核切点，加进 `assets/chapters.js` 的 `RP_PAGES`、建页壳（照 01b 复制，清空八节）。
  2. 每页一位译者（`tools/TRANSLATE.md`）→ 一位译文审读（`tools/TR-REVIEW.md`）→ 新译名并进 `GLOSSARY.md` → `gen_text.py`。
  3. 每页一位导读作者（`source/BRIEF.md`，各页提示要先写）→ 主编 `gen_text.py`＋三项检查 → 一位审读（`source/REVIEW.md`）→ 主编 peek 验收、`accept.py`、记 `source/ACCEPTANCE.md`。
  4. 改首页卡片的页数（`rp-done-:N`）和条数，00 页「现在做到哪」，提交推送。
- 待办：
  - 铺到卷六以后之前，核实 Loeb 第二册（卷六到卷十，1935）的公版状态。
  - 第 7 卷 Shorey 源文件有 3 处少标收引号（`extract.py` 没修）。
  - 没有 `source/.venv`，要放照片先建（现在四页都没照片，图是内联 SVG）。
  - J 步没做：总仓库 `README.md` 书单、`~/tutorials-deploy/README.md` 踩坑和 PLAYBOOK 表、模板里要不要加「全文翻译」的流程——等后九卷定了一起写。
- **第一卷的用量**（各子代理任务通知里的 `subagent_tokens` 相加，约 284 万；和总仓库 `CLAUDE.md` 里的「当量」不是一个口径，没含主会话）：
  导读作者 4 位 77 万 · 译者 4 位 53 万 · 导读审读 4 位 52 万 · 译文审读 4 位 50 万 · 搭骨架 29 万 · 提取 12 万 · 开读之前 10 万。
  骨架和提取是一次性的；每页（译＋审＋导读＋审）约 58 万。

## 记录

### 2026-11-16 A–D

- A：书库里没有《理想国》（只有余纪元讲演录 6657）。用户确认要做，范围是全文英中对照加导读，先做第一卷。
- B：回答见 `CLAUDE.md`。用户另说：活派 Opus 子代理做，主会话太贵。
- C：目录 `republic`，前缀 `rp-`。没有 Calibre id，`new-book.sh` 没跑，手建 `tools/`（三个检查脚本）和 `source/`。
- D：一位 Opus 代理取了三份底本、写了 `tools/extract.py`，报告在 `source/reports/extract.md`（约 12 万 token）。主编抽看了第一卷开头的 Shorey、希腊文、脚注和 `index.tsv`。

### 2026-11-16 E–I（同一个会话，用户说「这次先继续做」）

- E：一位 Opus 搭骨架（照 `systems/`）：九节页壳、`gen_text.py`（全文块生成）、lint / pack / status / peek / accept。主编修了两处：lint 数论证路线步数把 SVG 的 `<line>` 算进去；`rp.js` 的 `mountRecap` 在章节页的 `#recap` 标题上也跑。
- 翻译：四位译者并行，四位译文审读。主编定：跨节引号（后一节开头补前引号）、331d 跟 Shorey 加注、hexis 译「品质」。译文审读共改 27 处，15 处会读歪。
- F：样板页 01a 由 Opus 写（用户说活都派 Opus），审读改 4 处、2 处会读歪，四类错写进 `source/BRIEF.md`。
- G＋H：01b、01c、01d 三位作者并行，各一位审读；00 页一位 Opus 写，主编读一遍。细节见 `source/ACCEPTANCE.md`。
- I：首页卡片（`rp-done-:5`）、`sync.js` 的 `PREFIXES`、`sync_server.py` 的 `KEY_RE`；先 `sync-apply.sh` 再推站、再推首页（服务器遇到不认识的键会拒掉整个请求）。`tools/TRANSLATE.md`、`tools/TR-REVIEW.md` 放在 `tools/` 里是为了不部署。
