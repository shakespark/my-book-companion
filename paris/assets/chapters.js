// 全书目录。n: 篇号（按原书顺序，1–23）；part: 第几部分（原书分 4 部分）；journal: 是不是「圣诞日记」（每部分一篇，由许多短条组成）；
// words: 英文原文词数；secs: 分节地图的节数（原书的分隔，加上本站给没有分隔的篇分的节）；en: 原书篇名；t: 本站译的篇名（不是译本的译法）；
// zh: 读者手上台湾译本的篇名（用户提供后填，没有就空着，页面不显示）；ny: 原载《纽约客》的刊期（作者核实后填，如 "1996-01-15"）；d: 一句话（本站写的，给目录用）。
// PM_PARTS 的 d：这一部分一句话（本站写的，各篇交稿后由主编补）。
window.PM_PARTS = [
  { en: "The Winter Circus", t: "冬季马戏团", d: "" },
  { en: "Distant Errors", t: "远方的错误", d: "" },
  { en: "Lessons from Things", t: "从物件学到的", d: "" },
  { en: "A Machine to Draw the World", t: "描绘世界的机器", d: "" },
];
window.PM_CHAPTERS = [
  { n: 1, part: 1, journal: false, words: 5604, secs: 4, en: "Paris to the Moon", t: "从巴黎到月球", zh: "", ny: "", d: "" },
  { n: 2, part: 1, journal: false, words: 2992, secs: 5, en: "Private Domain", t: "私人领地", zh: "", ny: "", d: "" },
  { n: 3, part: 1, journal: false, words: 2347, secs: 3, en: "The Strike", t: "罢工", zh: "", ny: "", d: "" },
  { n: 4, part: 1, journal: true, words: 7588, secs: 13, en: "The Winter Circus, Christmas Journal 1", t: "冬季马戏团", zh: "", ny: "", d: "" },
  { n: 5, part: 2, journal: false, words: 2628, secs: 4, en: "The Rules of the Sport", t: "运动的规矩", zh: "", ny: "", d: "" },
  { n: 6, part: 2, journal: false, words: 2827, secs: 5, en: "The Chill", t: "寒意", zh: "", ny: "", d: "" },
  { n: 7, part: 2, journal: false, words: 2655, secs: 2, en: "A Tale of Two Cafés", t: "两家咖啡馆的故事", zh: "", ny: "", d: "" },
  { n: 8, part: 2, journal: true, words: 6667, secs: 15, en: "Distant Errors, Christmas Journal 2", t: "远方的错误", zh: "", ny: "", d: "" },
  { n: 9, part: 2, journal: false, words: 5734, secs: 5, en: "Papon’s Paper Trail", t: "Papon 的文书痕迹", zh: "", ny: "", d: "" },
  { n: 10, part: 2, journal: false, words: 796, secs: 1, en: "Trouble at the Tower", t: "铁塔上的麻烦", zh: "", ny: "", d: "" },
  { n: 11, part: 3, journal: false, words: 4784, secs: 7, en: "Couture Shock", t: "时装冲击", zh: "", ny: "", d: "" },
  { n: 12, part: 3, journal: false, words: 7465, secs: 8, en: "The Crisis in French Cooking", t: "法国菜的危机", zh: "", ny: "", d: "" },
  { n: 13, part: 3, journal: false, words: 2605, secs: 5, en: "Barney in Paris", t: "Barney 在巴黎", zh: "", ny: "", d: "" },
  { n: 14, part: 3, journal: true, words: 7745, secs: 9, en: "Lessons from Things, Christmas Journal 3", t: "从物件学到的", zh: "", ny: "", d: "" },
  { n: 15, part: 3, journal: false, words: 5689, secs: 6, en: "The Rookie", t: "新秀", zh: "", ny: "", d: "" },
  { n: 16, part: 4, journal: false, words: 4433, secs: 3, en: "The World Cup, and After", t: "世界杯，以及之后", zh: "", ny: "", d: "" },
  { n: 17, part: 4, journal: false, words: 3963, secs: 5, en: "The Balzar Wars", t: "Balzar 之战", zh: "", ny: "", d: "" },
  { n: 18, part: 4, journal: false, words: 4801, secs: 3, en: "Alice in Paris", t: "Alice 在巴黎", zh: "", ny: "", d: "" },
  { n: 19, part: 4, journal: true, words: 6124, secs: 17, en: "A Machine to Draw the World, Christmas Journal 4", t: "描绘世界的机器", zh: "", ny: "", d: "" },
  { n: 20, part: 4, journal: false, words: 9003, secs: 9, en: "A Handful of Cherries", t: "一把樱桃", zh: "", ny: "", d: "" },
  { n: 21, part: 4, journal: false, words: 5611, secs: 7, en: "Like a king", t: "像个国王", zh: "", ny: "", d: "" },
  { n: 22, part: 4, journal: false, words: 6581, secs: 3, en: "Angels Dining at the Ritz", t: "在丽兹吃饭的天使", zh: "", ny: "", d: "" },
  { n: 23, part: 4, journal: false, words: 2776, secs: 2, en: "One Last Ride", t: "最后一程", zh: "", ny: "", d: "" },
];
// 页 00 是「开读之前」（主编写）。已经写好的页（主编统一维护）
window.PM_READY = [0, 3];
