// 全书目录。n: 篇号（按原书顺序，1–23）；part: 第几部分（原书分 4 部分）；journal: 是不是「圣诞日记」（每部分一篇，由许多短条组成）；
// words: 英文原文词数；secs: 分节地图的节数（原书的分隔，加上本站给没有分隔的篇分的节）；en: 原书篇名；t: 本站译的篇名（不是译本的译法）；
// zh: 读者手上台湾译本（马可孛罗版，李桂蜜译）的篇名，2026-10-19 照用户给的目录填，繁体照译本原样（空着的页面不显示）；ny: 原载《纽约客》的刊期（作者核实后填，如 "1996-01-15"）；d: 一句话（本站写的，给目录用）。
// PM_PARTS 的 zh：译本的部名；d：这一部分一句话（本站写的，各篇交稿后由主编补）。
window.PM_PARTS = [
  { en: "The Winter Circus", t: "冬季马戏团", zh: "冬季馬戲團", d: "1995 年秋冬：刚到巴黎，炸弹、丑闻和大罢工" },
  { en: "Distant Errors", t: "远方的错误", zh: "遠距錯誤", d: "健身房、咖啡馆、寒冬里的经济恐慌和 Papon 审判" },
  { en: "Lessons from Things", t: "从物件学到的", zh: "直觀教學", d: "时装、法国菜、紫色恐龙和睡前故事" },
  { en: "A Machine to Draw the World", t: "描绘世界的机器", zh: "繪世機", d: "世界杯、Balzar 之战、女儿出生和千禧夜" },
];
window.PM_CHAPTERS = [
  { n: 1, part: 1, journal: false, words: 5604, secs: 4, en: "Paris to the Moon", t: "从巴黎到月球", zh: "巴黎到月球", ny: "", d: "全书导言：作者心里的巴黎从哪来，这本书怎么写" },
  { n: 2, part: 1, journal: false, words: 2992, secs: 5, en: "Private Domain", t: "私人领地", zh: "租屋弊案", ny: "1995-11-13", d: "总理的公寓丑闻，照出人人有份的「私产」" },
  { n: 3, part: 1, journal: false, words: 2347, secs: 3, en: "The Strike", t: "罢工", zh: "罷工風潮", ny: "1995-12-18", d: "大罢工有革命的声势，骨子里在护住好日子" },
  { n: 4, part: 1, journal: true, words: 7588, secs: 13, en: "The Winter Circus, Christmas Journal 1", t: "冬季马戏团", zh: "聖誕札記一：冬季馬戲團", ny: "", d: "头一个圣诞的日记：电视罩住世界，插头挡住它" },
  { n: 5, part: 2, journal: false, words: 2628, secs: 4, en: "The Rules of the Sport", t: "运动的规矩", zh: "運動規則", ny: "1996-05-27", d: "巴黎的纽约式健身房，和法国人的「运动」" },
  { n: 6, part: 2, journal: false, words: 2827, secs: 5, en: "The Chill", t: "寒意", zh: "寒氣逼人", ny: "1997-03-17", d: "寒冬里法国把经济恐慌演成一场场戏" },
  { n: 7, part: 2, journal: false, words: 2655, secs: 2, en: "A Tale of Two Cafés", t: "两家咖啡馆的故事", zh: "雙咖的故事", ny: "1996-12-02", d: "两家老咖啡馆，三位朋友，三种巴黎式解释" },
  { n: 8, part: 2, journal: true, words: 6667, secs: 15, en: "Distant Errors, Christmas Journal 2", t: "远方的错误", zh: "聖誕札記二：遠距錯誤", ny: "", d: "错永远在远方？语言、小店和一把椅子" },
  { n: 9, part: 2, journal: false, words: 5734, secs: 5, en: "Papon’s Paper Trail", t: "Papon 的文书痕迹", zh: "人道罪犯", ny: "1998-04-27", d: "签字的高官受审，审的是法国人对国家和文件的信仰" },
  { n: 10, part: 2, journal: false, words: 796, secs: 1, en: "Trouble at the Tower", t: "铁塔上的麻烦", zh: "鐵塔風波", ny: "1997-08-04", d: "铁塔电梯里一场口角，照出买与做的两种人" },
  { n: 11, part: 3, journal: false, words: 4784, secs: 7, en: "Couture Shock", t: "时装冲击", zh: "時裝衝擊", ny: "1996-07-29", d: "看一周高级定制，在一场秀上找到它的用处" },
  { n: 12, part: 3, journal: false, words: 7465, secs: 8, en: "The Crisis in French Cooking", t: "法国菜的危机", zh: "美國美食危機", ny: "1997-04-28", d: "法国菜为何停在原地：一串诊断和一顿重访的晚饭" },
  { n: 13, part: 3, journal: false, words: 2605, secs: 5, en: "Barney in Paris", t: "Barney 在巴黎", zh: "邦尼在巴黎", ny: "1997-04-21", d: "逃到巴黎躲紫色恐龙，孩子还是成了美国人" },
  { n: 14, part: 3, journal: true, words: 7745, secs: 9, en: "Lessons from Things, Christmas Journal 3", t: "从物件学到的", zh: "聖誕札記三：直觀教學", ny: "", d: "一年的日记，从厨房到方糖，问怎样的东西才算成了" },
  { n: 15, part: 3, journal: false, words: 5689, secs: 6, en: "The Rookie", t: "新秀", zh: "菜鳥的故事", ny: "1999-10-04", d: "给没见过棒球的儿子编了两年的睡前故事" },
  { n: 16, part: 4, journal: false, words: 4433, secs: 3, en: "The World Cup, and After", t: "世界杯，以及之后", zh: "世界盃足球賽", ny: "1998-07-13 和 07-27", d: "美国人看世界杯：零比零是人生，夺冠夜巴黎乱成一团" },
  { n: 17, part: 4, journal: false, words: 3963, secs: 5, en: "The Balzar Wars", t: "Balzar 之战", zh: "餐廳之戰", ny: "1998-08-03", d: "老饭馆被连锁收购，常客起来保卫，作者审问自己" },
  { n: 18, part: 4, journal: false, words: 4801, secs: 3, en: "Alice in Paris", t: "Alice 在巴黎", zh: "愛麗絲漫遊巴黎", ny: "1998-10-26", d: "Alice Waters 来巴黎，作者为她炖砸了一只羊腿" },
  { n: 19, part: 4, journal: true, words: 6124, secs: 17, en: "A Machine to Draw the World, Christmas Journal 4", t: "描绘世界的机器", zh: "聖誕札記四：直觀教學", ny: "", d: "差点离开巴黎的一年，作者改用描图的眼光看这座城" },
  { n: 20, part: 4, journal: false, words: 9003, secs: 9, en: "A Handful of Cherries", t: "一把樱桃", zh: "區區小數", ny: "", d: "为一家老啤酒馆打一场注定要输的仗" },
  { n: 21, part: 4, journal: false, words: 5611, secs: 7, en: "Like a king", t: "像个国王", zh: "國王的選擇", ny: "2000-01-31", d: "在巴黎生女儿，追问「国王的选择」到底何意" },
  { n: 22, part: 4, journal: false, words: 6581, secs: 3, en: "Angels Dining at the Ritz", t: "在丽兹吃饭的天使", zh: "小小羅曼史", ny: "", d: "五岁儿子在丽兹泳池的初恋，照出父母的婚姻" },
  { n: 23, part: 4, journal: false, words: 2776, secs: 2, en: "One Last Ride", t: "最后一程", zh: "旋轉木馬的最後一轉", ny: "", d: "千禧夜的铁塔，最后一圈旋转木马" },
];
// 页 00 是「开读之前」（主编写）。已经写好的页（主编统一维护）
window.PM_READY = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23];
