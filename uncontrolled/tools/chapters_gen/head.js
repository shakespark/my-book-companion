// 全站目录。页 id 和 tools/lint.py 用同一套（lint 从这里读）。主编维护，作者不改。
// UC_CHAPTERS：导言（n: 0）和原书 15 章。part 部，en 原书章名，t 本站叫法，d 这一章一句话（主编补）。
// UC_SECS：每章的节，就是原书的小标题（导言原书没有小标题，节是本站分的）。k 节号，p 段号范围（source/text/NN.txt 的 [k]），t 本站中文节名，
//   en 这一节第一段开头几个词（读者在 Kindle 里搜它），w 英文词数，tier 档（先读 / 有空 / 可跳过），line 这一节在全书的线上的作用（主编写，页面「读之前」里由 uc.js 显示）。
// UC_STAGES：全书的线分成几段（主编写），ch 是这一段包含的章。
// UC_PAGES：页。secs 这一页包含的节，need 这一页必写的可省小节（sim：动手：模拟器；lint 查），words 英文词数，
//   t 本站标题（不超过 10 个字，作者交稿后主编填），d 一句话（不超过 24 个字）。
window.UC_CHAPTERS = [
  { n: 0, part: "", en: "Introduction", t: "导言", d: "" },
  { n: 1, part: "第一部 科学", en: "Induction and the Problem of Induction", t: "归纳和归纳问题", d: "" },
  { n: 2, part: "第一部 科学", en: "Falsification and Paradigms", t: "证伪和范式", d: "" },
  { n: 3, part: "第一部 科学", en: "Implicit and Explicit Knowledge", t: "隐性知识和明确知识", d: "" },
  { n: 4, part: "第一部 科学", en: "Science as a Social Enterprise", t: "科学是一项社会事业", d: "" },
  { n: 5, part: "第一部 科学", en: "Science Without Experiments", t: "没有实验的科学", d: "" },
  { n: 6, part: "第一部 科学", en: "Some Observations Concerning Probability", t: "关于概率的几点看法", d: "" },
  { n: 7, part: "第一部 科学", en: "The Invention and Application of the Randomized Trial", t: "随机试验的发明和应用", d: "" },
  { n: 8, part: "第一部 科学", en: "Limitations of Randomized Trials", t: "随机试验的局限", d: "" },
  { n: 9, part: "第二部 社会科学", en: "Nonexperimental Social Science", t: "不做实验的社会科学", d: "" },
  { n: 10, part: "第二部 社会科学", en: "Business Strategy as Applied Social Science", t: "商业战略：应用的社会科学", d: "" },
  { n: 11, part: "第二部 社会科学", en: "The Experimental Revolution in Business", t: "商业里的试验革命", d: "" },
  { n: 12, part: "第二部 社会科学", en: "Experimental Social Science", t: "做实验的社会科学", d: "" },
  { n: 13, part: "第三部 政治行动", en: "Liberty as Means", t: "自由是手段", d: "" },
  { n: 14, part: "第三部 政治行动", en: "Innovation and Cohesion", t: "创新与凝聚力", d: "" },
  { n: 15, part: "第三部 政治行动", en: "Sustainable Innovation", t: "可持续的创新", d: "" },
];
window.UC_SECS = {
//SECS
};
window.UC_STAGES = [
  { t: "立题：凭什么知道一项措施有没有用", ch: [0] },
  { t: "科学怎样认识因果", ch: [1, 2, 3, 4, 5, 6] },
  { t: "随机试验：发明和局限", ch: [7, 8] },
  { t: "不做实验的社会科学", ch: [9] },
  { t: "商业里的试验", ch: [10, 11] },
  { t: "社会政策里的试验", ch: [12] },
  { t: "政治：自由、凝聚力和试错", ch: [13, 14, 15] },
];
window.UC_PAGES = [
//PAGES
];
window.UC_EXTRA = { "00": { t: "开读之前", d: "" } };
//READY
