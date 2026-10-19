// 全站目录。页 id 和 tools/extract.py 的 PAGES / MEMOIR、tools/lint.py 用同一套。主编维护，作者不改。
// kind：novel 小说页 / memoir 回忆录页 / extra 主编写的专页。
// 小说页：r 这一页包含的报告号；when 原书里这一页的日期范围（照书里的写法转成中文）；zh 中译本（陈澄和译）这几篇的标题。
// 回忆录页：ch 章号（24 是后记）。
// words 英文词数、secs 分节地图的节数（tools/extract.py 的输出，source/text/index.tsv）；t 本站给这一页起的标题（作者交稿后主编填，不剧透）；
// d 一句话（不超过 24 个字，不剧透，给目录用）。t、d 空着时目录只显示报告号。
window.AL_PAGES = [
  { id: "01", kind: "novel", r: [1, 2, 3, 4, 5, 6], when: "3 月 3 日–3 月 8 日", zh: "近步抱告—1 至 6", words: 3800, secs: 6, t: "墨迹、迷宫和兔脚", d: "手术前的六篇报告：一连串看不懂的测验" },
  { id: "07", kind: "novel", r: [7, 8], when: "3 月 11 日–3 月 31 日", zh: "进步报告—7、8", words: 6385, secs: 16, t: "绷带拆了以后", d: "手术后的头三个星期：医院、实验室和面包店" },
  { id: "09", kind: "novel", r: [9], when: "4 月 1 日–4 月 18 日", zh: "进步报告—9", words: 6929, secs: 13, t: "揉面机和逗号", d: "揉面机、逗号、墨迹卡：手术后的第一个四月" },
  { id: "10", kind: "novel", r: [10], when: "4 月 21 日–4 月 28 日", zh: "进步报告—10", words: 4546, secs: 6, t: "看清身边的人", d: "面包店、实验室、大学校园，查理换了眼光看人" },
  { id: "11a", kind: "novel", r: [11], when: "5 月 1 日–5 月 10 日", zh: "进步报告—11（前半）", words: 4901, secs: 5, t: "看完电影那晚", d: "从一场电影说起，查理五月初的十天" },
  { id: "11b", kind: "novel", r: [11], when: "5 月 11 日–5 月 25 日", zh: "进步报告—11（后半）", words: 4932, secs: 5, t: "中央公园的音乐会", d: "Gimpy 的事有了了断，和 Alice 去听音乐会" },
  { id: "12", kind: "novel", r: [12], when: "6 月 5 日–6 月 8 日", zh: "进步报告—12", words: 5108, secs: 3, t: "篱笆的另一边", d: "打字机、旧教室、夜里的中央公园：六月初的三天" },
  { id: "13a", kind: "novel", r: [13], when: "6 月 10 日", zh: "进步报告—13（前半）", words: 3386, secs: 5, t: "飞往芝加哥", d: "去芝加哥的飞机上，第一份口述的报告" },
  { id: "13b", kind: "novel", r: [13], when: "6 月 11 日–6 月 13 日", zh: "进步报告—13（后半）", words: 5200, secs: 3, t: "芝加哥的大会", d: "在学术大会上，查理重新打量带他来的人" },
  { id: "14a", kind: "novel", r: [14], when: "6 月 15 日–6 月 19 日", zh: "进步报告—14（一）", words: 3964, secs: 3, t: "回到纽约", d: "查理带着 Algernon 回到纽约，自己安顿下来" },
  { id: "14b", kind: "novel", r: [14], when: "6 月 20 日–6 月 23 日", zh: "进步报告—14（二）", words: 4134, secs: 5, t: "布朗克斯的理发店", d: "去布朗克斯找父亲 Matt，回到公寓又迎来对门的 Fay" },
  { id: "14c", kind: "novel", r: [14], when: "6 月 24 日–7 月 9 日", zh: "进步报告—14（三）", words: 5118, secs: 7, t: "人和人之间的墙", d: "夜里走遍全城，想重新和人连在一起" },
  { id: "15", kind: "novel", r: [15], when: "7 月 12 日", zh: "进步报告—15", words: 1673, secs: 1, t: "最后那扇门", d: "查理带着 Algernon 回到实验室，问起自己的将来" },
  { id: "16a", kind: "novel", r: [16], when: "7 月 14 日–7 月 31 日", zh: "进步报告—16（一）", words: 5261, secs: 6, t: "去看 Warren", d: "去 Warren 看了一天，回来把日子交给实验室" },
  { id: "16b", kind: "novel", r: [16], when: "8 月 11 日–9 月 21 日", zh: "进步报告—16（二）", words: 4602, secs: 8, t: "一场鸡尾酒会", d: "Nemur 太太的酒会，和之后的几条短报告" },
  { id: "16c", kind: "novel", r: [16], when: "9 月 27 日", zh: "进步报告—16（三）", words: 5282, secs: 5, t: "回到老房子", d: "九月底，查理借车回到布鲁克林的老家" },
  { id: "17a", kind: "novel", r: [17], when: "10 月 3 日–10 月 14 日", zh: "进步报告—17（前半）", words: 4569, secs: 9, t: "开始往下走", d: "10 月 3–14 日，他记录衰退的头两个星期" },
  { id: "17b", kind: "novel", r: [17], when: "10 月 17 日–11 月 21 日", zh: "进步报告—17（后半）", words: 4629, secs: 15, t: "最后一份报告", d: "文字一样样退回去，最后剩下的是什么" },
  { id: "m1", kind: "memoir", ch: [1, 2, 3], words: 4589, secs: 10, t: "", d: "" },
  { id: "m2", kind: "memoir", ch: [4, 5], words: 7159, secs: 11, t: "", d: "" },
  { id: "m3", kind: "memoir", ch: [6, 7, 8], words: 5907, secs: 13, t: "", d: "" },
  { id: "m4", kind: "memoir", ch: [9, 10], words: 4128, secs: 8, t: "", d: "" },
  { id: "m5", kind: "memoir", ch: [11, 12, 13, 14], words: 6126, secs: 9, t: "", d: "" },
  { id: "m6", kind: "memoir", ch: [15, 16, 17, 18], words: 7663, secs: 16, t: "", d: "" },
  { id: "m7", kind: "memoir", ch: [19, 20, 21, 22, 23, 24], words: 9476, secs: 18, t: "", d: "" },
  { id: "nv", kind: "extra", t: "中篇和长篇", words: 12018, secs: 12, d: "1959 年的中篇和 1966 年的长篇差在哪里" },
];
// 回忆录的五个部分（章号范围）
window.AL_MEMOIR_PARTS = [
  { en: "The Maze of Time", t: "时间的迷宫", ch: [1, 5] },
  { en: "From Ship to Shrink", t: "从船上到诊室", ch: [6, 10] },
  { en: "Mind over Matter", t: "心胜于物", ch: [11, 14] },
  { en: "The Alchemy of Writing", t: "写作的炼金术", ch: [15, 18] },
  { en: "Post-Publication Blues", t: "出版之后", ch: [19, 24] },
];
// 已经写好、验收过的页（主编维护）。"00" 是「开读之前」，写好后也要加进来
window.AL_READY = ["01", "07", "09", "10", "11a", "11b", "12", "13a", "13b", "14a", "14b", "14c", "15", "16a", "16b", "16c", "17a", "17b"];
