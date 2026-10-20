// 全站目录。页 id 和 tools/lint.py 用同一套（lint 从这里读）。主编维护，作者不改。
// UP_CHAPTERS：原书的 7 章。en 原书章名，t 本站译名，d 这一章一句话（主编补）。
// UP_SECS：每章的节，就是原书的小标题。k 节号（§1 是章首到第一个小标题之间，没有标题；第 1 章的 §0 是序言），en 原书小标题（错字照抄），
//   zh 本站译名，w 英文词数（tools/extract.py 的 index.tsv；不算剪报和文件的转写）。
// UP_STAGES：他一生分几段（主编写），pages 是这一段的页。
// UP_PAGES：页。secs 这一页包含的节，words 英文词数，yrs 年份，age 年纪，where 地点（主编写，页面「读之前」里由 up.js 显示），
//   need 这一页必写的可省小节（econ 经济学 / sowell 和 Sowell 对照 / today 对照今天；views 经济学一节里至少一块看法块；lint 查），
//   t 本站标题（不超过 10 个字，作者交稿后主编填），d 一句话（不超过 24 个字）。
window.UP_CHAPTERS = [
  { n: 1, en: "Starting Out", t: "起步", d: "" },
  { n: 2, en: "Rudderless and Drifting", t: "没了舵，随波漂", d: "" },
  { n: 3, en: "In the Army Now", t: "当兵去了", d: "" },
  { n: 4, en: "Heading West for Opportunity", t: "往西去找机会", d: "" },
  { n: 5, en: "Heading East for Opportunity", t: "往东去找机会", d: "" },
  { n: 6, en: "Teaching and Preaching", t: "教书，也布道", d: "" },
  { n: 7, en: "Afterthoughts", t: "写在后面", d: "" },
];
window.UP_SECS = {
  "01": [
    { k: 0, en: "Preface", zh: "序言", w: 604 },
    { k: 1, en: "（开头）", zh: "开头", w: 1149 },
    { k: 2, en: "Life Back Then", zh: "那时候的日子", w: 1694 },
    { k: 3, en: "Junior High School", zh: "初中", w: 697 },
    { k: 4, en: "First Real Job", zh: "第一份正经工作", w: 862 },
    { k: 5, en: "Always a Job", zh: "总有活干", w: 1079 },
    { k: 6, en: "High School", zh: "高中", w: 2653 },
  ],
  "02": [
    { k: 1, en: "（开头）", zh: "开头", w: 1132 },
    { k: 2, en: "To Los Angeles and College", zh: "去洛杉矶上大学", w: 468 },
    { k: 3, en: "Back to Philly", zh: "回费城", w: 883 },
    { k: 4, en: "Trouble with the Law", zh: "惹上警察", w: 920 },
    { k: 5, en: "Dating My Future Wife", zh: "和未来的妻子约会", w: 1109 },
  ],
  "03": [
    { k: 1, en: "（开头）", zh: "开头", w: 524 },
    { k: 2, en: "Into the Deep South", zh: "进了南方腹地", w: 517 },
    { k: 3, en: "Reporting In", zh: "报到", w: 600 },
    { k: 4, en: "Elevated to Head Clerk", zh: "升了文书长", w: 473 },
    { k: 5, en: "Fighting Segregation While Making Trouble", zh: "一边反隔离，一边惹麻烦", w: 2098 },
    { k: 6, en: "Court-Martialed", zh: "上了军事法庭", w: 811 },
    { k: 7, en: "Ordered to Korea", zh: "调往韩国", w: 1724 },
    { k: 8, en: "Going Home", zh: "回家", w: 422 },
    { k: 9, en: "In the Active Reserve", zh: "转入预备役", w: 632 },
  ],
  "04": [
    { k: 1, en: "（开头）", zh: "开头", w: 1157 },
    { k: 2, en: "In Jail Again", zh: "又进了拘留所", w: 357 },
    { k: 3, en: "Not Becoming an Economist-Almost", zh: "差一点没当成经济学家", w: 370 },
    { k: 4, en: "From a Near-Disaster to Easy Street", zh: "从险些出事到日子好过", w: 934 },
    { k: 5, en: "From Cal State to UCLA", zh: "从州立学院到 UCLA", w: 690 },
    { k: 6, en: "Going For It All", zh: "全力一搏", w: 2987 },
  ],
  "05": [
    { k: 1, en: "（开头）", zh: "开头", w: 1328 },
    { k: 2, en: "Linking Up with Tom Sowell", zh: "结识 Tom Sowell", w: 851 },
    { k: 3, en: "Back to Philadelphia", zh: "回到费城", w: 1200 },
    { k: 4, en: "Controversy at Temple", zh: "在 Temple 大学起了争议", w: 2264 },
    { k: 5, en: "A Year at Hoover", zh: "在胡佛研究所的一年", w: 561 },
    { k: 6, en: "Beginning a Public Life", zh: "开始公共生活", w: 1037 },
    { k: 7, en: "To the \"Old Dominion\" and George Mason", zh: "去弗吉尼亚，到乔治梅森", w: 425 },
  ],
  "06": [
    { k: 1, en: "（开头）", zh: "开头", w: 759 },
    { k: 2, en: "Attacks on Black Conservatives", zh: "黑人保守派挨的攻击", w: 1919 },
    { k: 3, en: "At Work and at Leisure in South Africa", zh: "在南非，工作和休闲", w: 1952 },
    { k: 4, en: "Traveling the World", zh: "走遍世界", w: 285 },
    { k: 5, en: "Dealing with Congress and the White House", zh: "和国会、白宫打交道", w: 861 },
    { k: 6, en: "Consorting with the Reagan Administration", zh: "和里根政府往来", w: 488 },
    { k: 7, en: "Coming on with a Rush", zh: "上 Rush 的节目", w: 448 },
    { k: 8, en: "Becoming a Department Chairman", zh: "当上系主任", w: 1531 },
  ],
  "07": [
    { k: 1, en: "（开头）", zh: "全章", w: 1476 },
  ],
};
window.UP_PAGES = [
  { id: "01a", ch: 1, secs: [0, 1, 2, 3], words: 4144, yrs: "1941–1951", age: "5–15 岁", where: "费城：西费城 → 北费城的公共住房", need: ["econ", "sowell", "today", "views"], t: "一片面包切三份", d: "五岁入学到初中毕业，母亲撑起的北费城" },
  { id: "01b", ch: 1, secs: [4, 5, 6], words: 4594, yrs: "约 1949–1954", age: "13–18 岁", where: "北费城；高中毕业后去洛杉矶看父亲", need: ["econ", "sowell", "today", "views"], t: "帽厂、零工和痛骂", d: "十几岁打工丢了帽厂的活，高中被老师骂醒" },
  { id: "02", ch: 2, secs: [1, 2, 3, 4, 5], words: 4512, yrs: "1954–1959", age: "18–23 岁", where: "费城和洛杉矶之间", need: [], t: "漂着的五年", d: "布店、社区学院、出租车，和一份案底" },
  { id: "03a", ch: 3, secs: [1, 2, 3, 4, 5], words: 4212, yrs: "1959–1960", age: "23–24 岁", where: "南卡 Fort Jackson → 佐治亚 Fort Stewart", need: [], t: "南方军营里的列兵", d: "入伍南下，在佐治亚军营里跟隔离较劲" },
  { id: "03b", ch: 3, secs: [6, 7, 8, 9], words: 3589, yrs: "1960–1965", age: "24–29 岁", where: "Fort Stewart → 韩国 → 费城 → 洛杉矶（预备役）", need: [], t: "军事法庭与韩国", d: "打赢军事法庭却被调去韩国，退役后西行洛杉矶" },
  { id: "04a", ch: 4, secs: [1, 2, 3, 4, 5], words: 3508, yrs: "1962–1967", age: "26–31 岁", where: "洛杉矶：Cal State LA、县缓刑局、UCLA", need: ["econ"], t: "信封里的日子", d: "省着过日子，从一个 D 走进 UCLA 研究生院" },
  { id: "04b", ch: 4, secs: [6], words: 2987, yrs: "1965–1969", age: "29–33 岁", where: "UCLA 经济系", need: ["econ", "sowell", "views"], t: "意图还是效果", d: "UCLA 读博：挂科、Alchian、立场转向" },
  { id: "05a", ch: 5, secs: [1, 2, 3], words: 3379, yrs: "1971–1973", age: "35–37 岁", where: "华盛顿 Urban Institute → 费城 Temple 大学", need: ["econ", "sowell", "views"], t: "贝叶斯派邻居", d: "智库、富人区和 Temple：凭肤色猜人与不当名额" },
  { id: "05b", ch: 5, secs: [4, 5, 6, 7], words: 4287, yrs: "1974–1980", age: "38–44 岁", where: "Temple、斯坦福 Hoover 研究所，到 George Mason", need: ["econ", "sowell", "today", "views"], t: "假分数和最低工资", d: "放水打分上了头版，最低工资报告带他走向公众" },
  { id: "06a", ch: 6, secs: [1, 2, 3], words: 4630, yrs: "1980–1989", age: "44–53 岁", where: "George Mason；南非", need: ["econ", "sowell", "today", "views"], t: "抄来的骂，南非的课", d: "挨骂的黑人保守派，在南非讲歧视的经济学" },
  { id: "06b", ch: 6, secs: [4, 5, 6, 7, 8], words: 3613, yrs: "1978–2010", age: "42–74 岁", where: "国会、白宫、电台和 George Mason 的系主任办公室", need: ["econ", "sowell", "today", "views"], t: "自己拉自己的调", d: "国会作证、拒绝入阁、电台代班、当系主任" },
  { id: "07", ch: 7, secs: [1], words: 1476, yrs: "2010", age: "74 岁", where: "写书时回头看", need: ["econ", "sowell", "today", "views"], t: "七十四岁回头看", d: "差距、榜样和运气：他最后的几点想法" },
];
window.UP_STAGES = [
  { t: "费城长大", yrs: "1936–1954", pages: ["01a", "01b"], d: "母亲一个人带他和妹妹，从西费城搬进北费城的公共住房；从十来岁起一直打工。" },
  { t: "漂着", yrs: "1954–1959", pages: ["02"], d: "高中毕业后不知道要干什么：布匹批发行、洛杉矶的社区学院、出租车，还被警察抓过一次。" },
  { t: "当兵", yrs: "1959–1961", pages: ["03a", "03b"], d: "征兵入伍，在佐治亚的军营里跟种族隔离较劲，上了军事法庭，又被调去韩国。" },
  { t: "洛杉矶读书", yrs: "1962–1971", pages: ["04a", "04b"], d: "带着妻子去洛杉矶，从州立学院读到 UCLA，考过了经济学博士的全部考试。" },
  { t: "往东：华盛顿和费城", yrs: "1971–1980", pages: ["05a", "05b"], d: "Urban Institute、Temple 大学、Hoover 研究所；最低工资的研究让他成了公众人物。" },
  { t: "George Mason 和公共生活", yrs: "1980–2010", pages: ["06a", "06b"], d: "在乔治梅森大学教书三十年，写专栏、去国会作证、上电台，也挨了不少骂。" },
  { t: "回头看", yrs: "2010", pages: ["07"], d: "七十四岁时对种族问题的几点想法。" },
];
// 已经写好的页（主编统一维护）
window.UP_READY = ["00", "01a", "01b", "02", "03a", "03b", "04a", "04b", "05a", "05b", "06a", "06b", "07"];
