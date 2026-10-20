// 全站目录。页 id 和 tools/lint.py 用同一套（lint 从这里读）。主编维护，作者不改。
// DW_CHAPTERS：原书的 4 篇。en 原书篇名，t 本站叫法，d 这一篇一句话（主编补）。
// DW_SECS：每篇的节。原书没有小标题，只有空行分隔；k 节号（tools/extract.py 按空行切的），t 本站起的节名，
//   en 这一节第一段开头几个词（读者在 Kindle 里搜它），w 英文词数（index.tsv），line 这一节在全书的线上的作用（主编写，页面「读之前」里由 dw.js 显示）。
// DW_STAGES：全书的线分成几段（主编写），ch 是这一段包含的篇。
// DW_PAGES：页。secs 这一页包含的节，need 这一页必写的可省小节（pd：原典一节；lint 查），words 英文词数，
//   t 本站标题（不超过 10 个字，作者交稿后主编填），d 一句话（不超过 24 个字）。
window.DW_CHAPTERS = [
  { n: 1, en: "Prologue", t: "序章", d: "" },
  { n: 2, en: "Darwin Turns the Worm", t: "达尔文篇", d: "" },
  { n: 3, en: "The Death of Freud", t: "弗洛伊德篇", d: "" },
  { n: 4, en: "Epilogue", t: "尾声", d: "" },
];
window.DW_SECS = {
  "01": [
    { k: 1, t: "凯奇的笑话：苦难刚刚好", en: "John Cage tells the story somewhere", w: 1236, line: "立题：两人都认为有些苦难躲不掉，劝我们爱上转瞬即逝的东西" },
    { k: 2, t: "冲突是生命的底色", en: "Because of the Oedipus complex,", w: 593, line: "物种怕灭绝，个人想按自己的方式死：冲突和死亡是两人共同的底色" },
    { k: 3, t: "死亡驱力，不再有救赎", en: "Freud at his most fantastically speculative", w: 1383, line: "死亡故事照亮生命故事；蚯蚓和反传记，是两人各自找到的可赞美之物" },
    { k: 4, t: "失去之谜：自然不站队", en: "Redemption – being saved from something", w: 1481, line: "自然有规律、没有意图；我们最受苦于自己的理想" },
    { k: 5, t: "他们不开药方", en: "It was inevitable that these new", w: 519, line: "两人的道德不写成规矩，藏在他们赞美什么、痛骂什么里" },
    { k: 6, t: "巴西的森林，多洛米蒂的散步", en: "That there is much suffering", w: 2069, line: "达尔文失去信仰仍能对自然惊叹；弗洛伊德说美因短暂而可贵，前提是能哀悼" },
    { k: 7, t: "把幸福放进达尔文的方程", en: "It is, needless to say, possible", w: 495, line: "弗洛伊德给「活下去、繁衍」加上「满足」这道题；下面两篇分头去找线索" },
  ],
  "02": [
    { k: 1, t: "小猎犬号归来，纠缠的河岸", en: "Darwin came back, after five years", w: 1868, line: "自然又丰饶又残酷，达尔文左右为难；只有写蚯蚓时他毫无保留地赞美" },
    { k: 2, t: "1837 年的蚯蚓论文", en: "Darwin finished revising the diary of", w: 2724, line: "看得见的地表是地下故事的结尾；农夫只是笨拙地模仿蚯蚓" },
    { k: 3, t: "最后一本书：慢而无声的侧攻", en: "Darwin, Desmond and Moore suggest, returned", w: 2205, line: "晚年回到蚯蚓：不正面攻击宗教，用一本蚯蚓书给出世俗的来世" },
    { k: 4, t: "锡尔切斯特的断墙", en: "Amid much extensive collaboration with his", w: 307, line: "书里唯一需要说服的人，是一位牧师" },
    { k: 5, t: "在破坏中保存", en: "The Romans are no longer at work:", w: 224, line: "蚯蚓又挖空又保存，这也是达尔文自己工作的样子" },
  ],
  "03": [
    { k: 1, t: "1885 年，烧掉笔记的信", en: "In what Freud referred to as", w: 2322, line: "年轻的弗洛伊德就想让传记作者扑空：人该是个解不开的谜" },
    { k: 2, t: "《超越快乐原则》：自己的死法", en: "If we are to take it", w: 1740, line: "死亡驱力：生命想回到无生命，但要绕路，按自己的方式死" },
    { k: 3, t: "自传和反自传", en: "Freud needed the odd notion of", w: 960, line: "死亡驱力解释人怎样不自觉地拆掉自己的人生故事" },
    { k: 4, t: "茨威格要写传，哈姆雷特的鞭子", en: "I am profoundly happy,", w: 908, line: "「传记的真相不存在，就算有也用不上」" },
    { k: 5, t: "歌德奖演说和达·芬奇的偶然", en: "In his speech on receiving the", w: 1601, line: "传记满足一种需要又贬低偶像；偶然和童年让传记无从下手" },
    { k: 6, t: "越研究越看不透", en: "It is an, insufficiently acknowledged", w: 457, line: "精神分析越往前走，弗洛伊德越不信人能被认识" },
    { k: 7, t: "琼斯和盖伊写的临终", en: "It is perhaps worth wondering, given", w: 3201, line: "两位传记作者把他的死写成言行一致的结局，正是他的理论否认的那种" },
    { k: 8, t: "死亡驱力是一份独立", en: "Freud’s notion of the death instinct,", w: 722, line: "死亡驱力是我们逃开所有人给我们写传的那一部分" },
  ],
  "04": [
    { k: 1, t: "笨句子和线轴游戏", en: "For both Darwin and Freud the", w: 2402, line: "失去成了发明的机会：达尔文写不顺反而想得深，孩子把母亲离开变成游戏" },
    { k: 2, t: "金科玉律：记下反面证据", en: "In both these examples there is", w: 909, line: "我们自己也在制造遗忘；把反面证据留住，人才会变" },
    { k: 3, t: "做个好的失去者", en: "Darwin will record his falsifying evidence,", w: 717, line: "放下对永恒和完美的执着：要蚯蚓，不要传记作者" },
    { k: 4, t: "习惯的动物：毛毛虫和自由联想", en: "Men are called", w: 1528, line: "习惯让人守着过去；自由联想像哀悼一样是放手；学会和自己的死一起活" },
  ],
};
window.DW_STAGES = [
  { t: "立题：爱上会消逝的", ch: [1] },
  { t: "达尔文：赞美蚯蚓", ch: [2] },
  { t: "弗洛伊德：反对传记", ch: [3] },
  { t: "做个好的失去者", ch: [4] },
];
window.DW_PAGES = [
  { id: "01a", ch: 1, secs: [1, 2, 3], need: [], words: 3212, t: "苦难刚刚好", d: "凯奇的玩笑开篇：两人都用死亡读懂生命" },
  { id: "01b", ch: 1, secs: [4, 5, 6, 7], need: ["pd"], words: 4564, t: "美因短暂而可贵", d: "自然不站队；能哀悼，才爱得起会消逝的东西" },
  { id: "02a", ch: 2, secs: [1, 2], need: ["pd"], words: 4592, t: "地面是故事的结尾", d: "自然又丰饶又残酷，达尔文在蚯蚓身上找到可赞美的" },
  { id: "02b", ch: 2, secs: [3, 4, 5], need: ["pd"], words: 2736, t: "慢而无声的侧攻", d: "达尔文的最后一本书：蚯蚓埋葬、消化，碰巧保存了世界" },
  { id: "03a", ch: 3, secs: [1, 2], need: ["pd"], words: 4062, t: "想当斯芬克斯", d: "烧掉笔记的信，和「按自己的方式死」" },
  { id: "03b", ch: 3, secs: [3, 4, 5, 6], need: ["pd"], words: 3926, t: "传记的真相得不到", d: "弗洛伊德为什么不信一个人的一生能被写清楚" },
  { id: "03c", ch: 3, secs: [7, 8], need: [], words: 3923, t: "传记作者写的死", d: "两部传记怎样写弗洛伊德之死，死亡驱力是一份独立" },
  { id: "04a", ch: 4, secs: [1, 2], need: ["pd"], words: 3311, t: "失去成了发明", d: "笨句子、线轴游戏和哀悼：失去怎样变成发明" },
  { id: "04b", ch: 4, secs: [3, 4], need: [], words: 2245, t: "要蚯蚓，不要传记作者", d: "做好的失去者：改掉守着过去的习惯，和死一起活" },
];
// 主编写的两页：00 开读之前；vm 达尔文的蚯蚓书（1881 年那本书本身，公有领域，排在达尔文篇之后）
window.DW_EXTRA = {
  "00": { t: "这本书、这位作者、这条线", d: "Phillips 是谁，全书怎么走，读者手上这本电子书的样子" },
  vm: { t: "达尔文的蚯蚓书", d: "1881 年那本书本身：实验、插图、原文选读", after: "02b" },
};
// 已经写好的页（主编统一维护）
window.DW_READY = ["00", "01a", "01b", "02a", "02b", "vm", "03a", "03b", "03c", "04a", "04b"];
