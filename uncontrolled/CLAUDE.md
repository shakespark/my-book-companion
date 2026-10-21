# Uncontrolled · 导读

- 书：Jim Manzi, *Uncontrolled: The Surprising Payoff of Trial-and-Error for Business, Politics, and Society*（Basic Books 2012）。
  Calibre id **6452**（AZW3、EPUB；EPUB 是 2026-10-21 用户转出的），`source/calibre`。商业出版物，全套版权红线。
- 结构：导言 + 15 章，分三部（I Science 1–8、II Social Science 9–12、III Political Action 13–15），每章有小标题；正文约 8.5 万词，书后注释约 7 千词。
- 中译本：书库里没有，用户没提，不用。
- 网址 https://t.miaowuao.cn/uncontrolled/ ，目录 `uncontrolled/`，localStorage 键前缀 `uc-`，共享脚本 `assets/uc.js`（待建）。骨架照 The Selfish Gene（`selfish/`）。

## 用户的回答（2026-10-21）

- 卡在哪：**方法概念、论证主线、经济学和政策背景、英文语言，四样都要**。
  - 方法概念：随机对照试验、因果推断、回归、外部效度、因果密度等，先用中文讲，配能调参数的模拟器。
  - 论证主线：从科学哲学讲到商业试验再讲到政策，线长易丢：分节地图、全书的线、最短读法。
  - 经济学和政策背景：美国福利改革、教育、犯罪等项目评估，经济模型之争；用户是经济学新手（记忆 user-econ-novice）。
- 提前知道内容：**无害**，不设读前 / 读后分界。
- 怎么读：**英文 Kindle**（这份 EPUB）。单个生词一般不收；`.loc` 一字不差，要能在 Kindle 上搜到。
- 部署：**到时候直接做，做完告诉用户**（首页卡片、同步白名单、推送上线；授权只管这一本书）。
- 默认要做的（用户在前几本书里每次都要）：每页末尾「读完：作者到底说了什么」和「本站怎么看」（记忆 views-with-commentary）；
  书 2012 年出版，做「对照今天」（复现危机、科技公司大规模 A/B 测试、2019 年诺奖的随机试验等）；每章「精彩回顾」和 `recap.html`。
- **写完直接上线，不用给用户看**（用户 2026-10-21 原话：「写完后可以直接上线，不用给我看」）。样板页不等用户认可；照「用户不看样板时」那条坑，样板照样审读，审读结果写进作者任务说明。

## 页和节

- 页：00（开读之前，主编页）、in（导言）、01–09、10a 10b、11a 11b、12a 12b、13、14、15a 15b。模拟器：01 07 08 10b 11a。
- 十四节，见 `AUTHORING.md`；没有译本、没有作者尾注。

## 进度

- [x] A–F（2026-10-21/22）：见上；样板 `chapters/07.html`。用户说写完直接上线，没等认可。
- [x] G 铺开（2026-10-22）：一章一个作者（拆两页的章同一人写两页），两批 15 位 Opus 作者，全部交齐并由主编读过收下；作者报告 `source/reports/`，验收 `source/ACCEPTANCE.md`。
- [x] H 审读（2026-10-22）：样板加 8 位审读员审完 20 页（核查和词条审读合一，`source/REVIEW.md`），每页改动记在报告末尾和 ACCEPTANCE。
  写到一半 WebSearch 全会话 200 次额度用完、grok 402；之后限每页搜 6 次，能直接打开的原页用 curl 看。
- [x] I 上线（2026-10-22）：首页卡片 `uc-done-:20`；sync.js PREFIXES 和 sync_server.py KEY_RE 加 uc-（已 sync-apply）；words.html 的 `uc`（页 id 含 `in`）和两处前缀正则。
- [x] J 收尾：本仓库 README 书单、tutorials-deploy README（教程表、踩坑四条）、PLAYBOOK 各站答案。

**全书完成。** 以后用户报 Uncontrolled 多半是要改某一页：照下面「怎么验」跑检查，改完 `git add uncontrolled/` 提交推送即部署。

## 页和节

- 页：00（开读之前，主编页）、in（导言）、01–09、10a 10b、11a 11b、12a 12b、13、14、15a 15b。模拟器：01 07 08 10b 11a。
- 节就是原书小标题（导言本站分 4 节），档 先读约 39%，00 页和首页的 `#path` 自动拼出全书最短读法（`uc.js` 的 `mountPath`，每分钟 150 词估时间）。
- 十四节，见 `AUTHORING.md`；没有译本、没有作者尾注。概念分工和术语表 `source/LINE.md`（作者自加的几个 id 已登记）。

## 怎么验

```sh
python3 -I tools/lint.py chapters/<页>.html        # 00 不跑 lint
python3 -I tools/overlap.py chapters/<页>.html
node tools/check.mjs chapters/<页>.html --shots source/shots/<页>
node tools/sim07.mjs                                # 07 模拟器照「试试看」连点（别页照它改）
```

- `assets/chapters.js` 手工维护：收稿用 `python3 -I tools/accept.py <页> "<标题>" "<一句话>"` 填 t、d、加进 UC_READY。节表要重算才跑 `tools/chapters_gen/assemble.py keep`（读 `source/SECS.tsv`、`source/line/` 和 `override.json`，保留 t、d、READY）。
- `source/text/`、`index.tsv`、`source/img/` 由 `tools/extract.py` 生成，不手改。`source/.venv` 装了 Pillow。
- 汇总页都是自动的：`terms.html` 收概念块，`today.html` 收对照今天，`recap.html` 收精彩回顾和本站的总体看法。
- 对照今天的「今天」只用 2012 年以后的证据（06、10a 各删过一张只有出版前证据的卡）。
