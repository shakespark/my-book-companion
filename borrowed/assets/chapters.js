// 全站目录。页 id 和 tools/lint.py 用同一套（lint 从这里读）。主编维护，作者不改。
// BT_CHAPTERS：原书的 10 章（10 是尾声）。en 原书章名，t 本站译名，d 这一章一句话（主编补）。
// BT_SECS：每章的节（原书目录页的 50 节，尾声算一节）。k 节号，en 节名（照原书目录页，错字照抄），who 目录页上节名后面的人名，w 英文词数（tools/extract.py 的 index.tsv），
//   line 这一节在全书的线上的作用（主编写，页面「读之前」里由 bt.js 显示）。
// BT_STAGES：全书的线分成几段（主编写），ch 是这一段包含的章。
// BT_PAGES：页。secs 这一页包含的节，words 英文词数，t 本站标题（不超过 10 个字，作者交稿后主编填），d 一句话（不超过 24 个字）。
window.BT_CHAPTERS = [
  { n: 1, en: "Life Is Short, Art Is Long", t: "生命短，技艺长", d: "" },
  { n: 2, en: "The Midpoint of Life", t: "人生的中点", d: "" },
  { n: 3, en: "Limited Time in This World and in the Next", t: "此世和来世的有限时间", d: "" },
  { n: 4, en: "Short and Shortest Times", t: "短时与最短时", d: "" },
  { n: 5, en: "The Economy of Limited Time", t: "有限时间的经济", d: "" },
  { n: 6, en: "The Drama of Time in Short Supply", t: "时间短缺的戏剧", d: "" },
  { n: 7, en: "Finitude, Infinity", t: "有限，无限", d: "" },
  { n: 8, en: "Living with Deadlines", t: "与期限共处", d: "" },
  { n: 9, en: "Short Stories about Short Deadlines", t: "短期限的短故事", d: "" },
  { n: 10, en: "Epilogue on the Sense of Time", t: "尾声：论时间感", d: "" },
];
window.BT_SECS = {
  "01": [
    { k: 1, en: "Medical Aphorisms and the Movement of Time", who: "Hippocrates, Aristotle, Theophrastus", w: 3070, line: "立题：生命短、技艺长之间的落差，两条出路，弃用亚里士多德的时间" },
    { k: 2, en: "Philosophical Remarks on the Brevity of Life", who: "Seneca", w: 1308, line: "时间像钱：塞涅卡说人生不短，是忙碌把它浪费了" },
    { k: 3, en: "Domestic Economy and Time Management", who: "Leon Battista Alberti", w: 1342, line: "近代的时间经济：有了机械钟，一天按钟点安排" },
    { k: 4, en: "Teaching Time Management in London and Paris", who: "Chesterfield, Rilke", w: 919, line: "教人管时间：一封封家书、一位小公务员，都不太成功" },
  ],
  "02": [
    { k: 1, en: "Midway on Life's Journey", who: "Dante, Petrarch, Holderlin", w: 2529, line: "人生的中点：把一生画成一张弓，前后两半不一样" },
    { k: 2, en: "Rejuvenation in Rome-through Rome", who: "Goethe", w: 1609, line: "延长人生那条路：人到中年出走罗马，像重生一回" },
    { k: 3, en: "The Physician's Art of Prolonging Life", who: "Hufeland", w: 1124, line: "延长人生那条路：医生写的长寿术" },
    { k: 4, en: "A Long Life with Faust", who: "Goethe", w: 1979, line: "浮士德返老还童，在人生中点跳出那场赛跑" },
    { k: 5, en: "New Art and Another Life", who: "Vittorio Alfieri, Schiller", w: 1184, line: "两条路之外：把艺术变成不受时间约束的东西" },
    { k: 6, en: "Magic and Style in Life-Time", who: "Balzac", w: 2921, line: "拿愿望换寿命的「浮士德小说」，和给女人多出的十年" },
    { k: 7, en: "Every Day Is a Sonnet", who: "Oscar Wilde", w: 1441, line: "与时间立约的故事再变形；监狱里一天像一年" },
    { k: 8, en: "Untimely Death or Venerable Old Age", who: "Chatterton, Keats, Benn, Thomas Mann", w: 1394, line: "早死的天才和长寿的作家：艺术耗命还是养命" },
    { k: 9, en: "Revocable and Irrevocable Time", who: "Ingeborg Bachmann", w: 1282, line: "时间像暂缓清偿的债：期限这个主题的前奏" },
  ],
  "03": [
    { k: 1, en: "Yet a Little While", who: "Jesus, St. Paul", w: 2154, line: "末日临近，平常的算计都不作数；末日推迟，时间又回来了" },
    { k: 2, en: "In Purgatory, Time Is Precious", who: "Dante", w: 2245, line: "把人的时间带进来世：在炼狱里用时间偿还时间" },
    { k: 3, en: "More Time for a New World", who: "Benjamin Franklin", w: 1994, line: "「时间就是金钱」的经典说法；还债的期限第一次出场" },
    { k: 4, en: "A Purgatory in This World", who: "Max Weber", w: 768, line: "时间经济的宗教来源：加尔文派把炼狱搬到了此世" },
    { k: 5, en: "Revolutionary Historical Times, in Rapid Fire", who: "Heine, Marx", w: 2170, line: "历史在加速：预言出来的思想很快要变成行动" },
  ],
  "04": [
    { k: 1, en: "Two Gods of Time: Chronos and Kairos", who: "Mythology, Classics", w: 1472, line: "质的时间：抓住时机（kairos），对短缺的另一种回应" },
    { k: 2, en: "Stars and Hours", who: "Schiller, Wallenstein; Stefan Zweig", w: 1165, line: "错过时机：历史剧里的命运时刻" },
    { k: 3, en: "Between Austerlitz and Waterloo", who: "Emile Zola", w: 1184, line: "交易所里，短短一段时间就是财富" },
  ],
  "05": [
    { k: 1, en: "Three-Day Friendship: Hospitality", who: "Homer, Knigge", w: 1795, line: "待客三天：前现代的期限，后来被旅行和生意取代" },
    { k: 2, en: "Classicism as Economy of Time", who: "From Plutarch to Andre Gide", w: 1848, line: "缩短技艺那条路：话像钱一样省着说" },
    { k: 3, en: "Living Faster, Talking Less", who: "Jean Paul, Madame de Stael", w: 1151, line: "语言的快慢：法语短而快，德语长而慢" },
  ],
  "06": [
    { k: 1, en: "Epic Is Long, Drama Is Short", who: "Aristotle", w: 629, line: "箴言搬进诗学：史诗长、戏剧短，时间要单一" },
    { k: 2, en: "How Long Is Twenty-Four Hours?", who: "Corneille", w: 1059, line: "规则限定的二十四小时，怎样被巧妙地拉长" },
    { k: 3, en: "Time out of joint", who: "Shakespeare, Hamlet", w: 2110, line: "被暴力缩短的时间，和忧郁者的慢时间" },
    { k: 4, en: "Saladin Learns to Take His Time", who: "Lessing, Nathan the Wise", w: 1340, line: "讲故事赢得时间：用最长的时间对抗权力的短时间" },
    { k: 5, en: "Time and the Oeuvre", who: "Proust", w: 1392, line: "「生命短、作品长」在现代小说里重演" },
  ],
  "07": [
    { k: 1, en: "Curiosity-Thirst for Knowledge-Science", who: "From Aristotle to Leibniz", w: 1619, line: "技艺那一头变成无限：好奇心推动的科学没有终点" },
    { k: 2, en: "A Nothingness of Time in Exchange for Eternity", who: "Pascal, Emily Dickinson", w: 1149, line: "有限的一生对永恒：拿一点时间去赌无限" },
    { k: 3, en: "Too Little Time, Too Much World", who: "Blumenberg", w: 1491, line: "生命时间对世界时间：剪刀的比喻到这里断了" },
    { k: 4, en: "Anthropological Experiences of Shortage", who: "Odo Marquard", w: 851, line: "回到人的短缺：用慢、习惯和人情应对加速" },
  ],
  "08": [
    { k: 1, en: "Clocks, Calendars, Appointment Calendars", who: "Clockmakers, Calendarmakers", w: 1845, line: "期限的工具：钟、历法、记事本" },
    { k: 2, en: "Deadlines in Everyday Life", who: "Tutti, con moto", w: 1951, line: "日常生活里的期限：借、租、分期和贷款" },
    { k: 3, en: "Deadlines in Law, with a Brief Glance at \"Abortion Limits\"", who: "Civil Law, Criminal Law, Labor Law", w: 1977, line: "法律里的期限，和拿期限做政治妥协" },
    { k: 4, en: "but.. for the Present, not Yet\"", who: "Heidegger, Marquard", w: 2027, line: "转折：撇开和技艺的比较，人生是一段以死为终点的期限" },
  ],
  "09": [
    { k: 1, en: "Saved from Death at the Last Minute", who: "Thousand and One Nights; Shakespeare, Merchant of Venice", w: 1696, line: "讲故事推迟死期：期限的压力只有故事说得清" },
    { k: 2, en: "A Ballad about Friendship and Deadlines", who: "Schiller, \"Die Bilrgschaft\"", w: 922, line: "三天的期限和一路的耽搁" },
    { k: 3, en: "A Devil's Pact with Deadlines", who: "Chamisso", w: 896, line: "魔鬼契约里的「一年零一天」怎么算" },
    { k: 4, en: "The Traps and Labors of Deadlines", who: "Flaubert, Maupassant", w: 1117, line: "债务的期限：一个被逼死，一个熬了十年" },
    { k: 5, en: "Deadlines of Honor, Prussian Style", who: "Theodor Fontane", w: 965, line: "荣誉的期限：九个月的倒数和最后通牒" },
    { k: 6, en: "Deadlines for Honor in Imperial Austria", who: "Arthur Schnitzler", w: 1155, line: "荣誉的期限压缩到一夜" },
    { k: 7, en: "A Short Time to Be Humane", who: "Garcia Marquez, Chronicle of a Death Foretold", w: 1646, line: "人人预先知道的死期，全村都在拖" },
    { k: 8, en: "Fifteen Minutes' Delay for Death", who: "Blaise Cendrars", w: 1391, line: "为了拍照把行刑推迟一刻钟" },
    { k: 9, en: "Everyman's Last Reprieve", who: "Hugo von Hofmannsthal", w: 508, line: "富人还债的期限和死神给的最后一小时" },
    { k: 10, en: "A Short Epilogue in the Emergency Room", who: "Tabucchi", w: 701, line: "来不及的对话：期限之间的空隙" },
    { k: 11, en: "A Race around the World", who: "Jules Verne, Around the World in Eighty Days", w: 1147, line: "机器的速度和赌约的期限" },
    { k: 12, en: "Short Time, Comic Style", who: "Camoletti, Boeing-Boeing", w: 754, line: "时刻表上的喜剧：飞机越快，时间越不够" },
    { k: 13, en: "A Twenty-Minute Deadline: Lola Runs", who: "Tom Tywker, Lola Rennt", w: 765, line: "钱和时间一起短缺，二十分钟重来三次" },
  ],
  "10": [
    { k: 1, en: "Epilogue on the Sense of Time", who: "", w: 3500, line: "收尾：时间是身体里的一种感觉，器官旧说是太阳穴，今说是脉搏" },
  ],
};
window.BT_STAGES = [
  { t: "立题", ch: [1] },
  { t: "试各种出路", ch: [2, 3, 4, 5, 6] },
  { t: "技艺变成无限", ch: [7] },
  { t: "换一端：期限", ch: [8, 9] },
  { t: "时间是一种感觉", ch: [10] },
];
window.BT_PAGES = [
  { id: "01a", ch: 1, secs: [1], words: 3070, t: "", d: "" },
  { id: "01b", ch: 1, secs: [2, 3, 4], words: 3569, t: "把时间当钱算", d: "从塞涅卡到里尔克，人们怎样像省钱一样省时间" },
  { id: "02a", ch: 2, secs: [1, 2], words: 4138, t: "人生的中点", d: "按《诗篇》算，人生三十五岁到顶，诗人在弓顶上回看" },
  { id: "02b", ch: 2, secs: [3, 4, 5], words: 4287, t: "长寿术、浮士德与明朗", d: "箴言在歌德身边被拆字、引用、改写成「明朗」" },
  { id: "02c", ch: 2, secs: [6, 7], words: 4362, t: "驴皮、画像和牢房", d: "巴尔扎克和王尔德笔下，拿寿命做交易的浮士德故事" },
  { id: "02d", ch: 2, secs: [8, 9], words: 2676, t: "早死的天才，借来的时间", d: "天才早死与作家长寿，巴赫曼笔下宽限来的时间" },
  { id: "03a", ch: 3, secs: [1, 2], words: 4399, t: "末日与炼狱的账", d: "末日近了不必算账，炼狱里却要以时偿时" },
  { id: "03b", ch: 3, secs: [3, 4, 5], words: 4932, t: "时间算成钱", d: "富兰克林的时间账、此世的炼狱和海涅的雷声" },
  { id: "04", ch: 4, secs: [1, 2, 3], words: 3821, t: "时机，稍纵即逝", d: "克罗诺斯和凯洛斯：从席勒的战场到左拉的交易所" },
  { id: "05", ch: 5, secs: [1, 2, 3], words: 4794, t: "待客三天，说话要省", d: "好客的三天期限和古典主义的「少说」，都是时间经济" },
  { id: "06a", ch: 6, secs: [1, 2, 3], words: 3798, t: "舞台上的二十四小时", d: "三一律、高乃依的正午到正午、哈姆雷特错过的时机" },
  { id: "06b", ch: 6, secs: [4, 5], words: 2732, t: "讲故事和写作品", d: "纳坦用长故事赢得时间，普鲁斯特为写书算余生" },
  { id: "07", ch: 7, secs: [1, 2, 3, 4], words: 5110, t: "技艺变成无限", d: "好奇心、帕斯卡、布鲁门贝格、马夸德：知识无尽，一生太短" },
  { id: "08a", ch: 8, secs: [1, 2], words: 3796, t: "钟、日历和期限", d: "从钟、历、记事本讲到借书贷款：什么是期限" },
  { id: "08b", ch: 8, secs: [3, 4], words: 4004, t: "法律里的期限，人生的期限", d: "从德国法条里的期限，转到以死为终点的人生" },
  { id: "09a", ch: 9, secs: [1, 2, 3, 4], words: 4631, t: "讲故事推迟死期", d: "五个故事里的期限：讲故事、赶路、数日子、还债" },
  { id: "09b", ch: 9, secs: [5, 6, 7, 8], words: 5157, t: "荣誉和镜头定的期限", d: "冯塔纳、施尼茨勒、马尔克斯和桑德拉尔：荣誉与媒体的期限" },
  { id: "09c", ch: 9, secs: [9, 10, 11, 12, 13], words: 3875, t: "从一小时到二十分钟", d: "耶德曼、塔布基、凡尔纳、波音和罗拉：期限的最后一刻" },
  { id: "10", ch: 10, secs: [1], words: 3500, t: "时间是一种感觉", d: "时间睡在太阳穴里，脉搏一快才醒" },
];
// 已经写好的页（主编统一维护）
window.BT_READY = ["00", "01a", "01b", "02a", "02b", "02c", "02d", "03a", "03b", "04", "05", "06a", "06b", "07", "08a", "08b", "09a", "09b", "09c", "10"];
