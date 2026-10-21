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
  "00": [
    { k: 1, p: [1, 8], t: "几家店试试；刺激法案", en: "As a young corporate strategy consultant,", w: 976, tier: "先读", line: "立起全书的问题：作者说预测人的反应，几乎只有实验靠得住；反事实测不到" },
    { k: 2, p: [9, 16], t: "因为无知，所以要自由", en: "I believe that recognizing this deep uncertainty", w: 865, tier: "有空", line: "挂上 Hayek/Popper 的政治线，预告演化和随机试验两件工具" },
    { k: 3, p: [17, 25], t: "再谦卑一点：没有魔法", en: "But I will argue that we should", w: 867, tier: "先读", line: "推广难，所以要海量实验；商业已做到；只求边际改进" },
    { k: 4, p: [26, 34], t: "全书五句话", en: "The thesis of this book can therefore", w: 289, tier: "先读", line: "五条论点和三部结构，全书的路线图" },
  ],
  "01": [
    { k: 1, p: [1, 28], t: "摆锤与培根的新工具", en: "To make a point to a", w: 2569, tier: "有空", line: "科学方法的起点：重实验、为实用；留下「怎么归纳」的难题" },
    { k: 2, p: [29, 42], t: "休谟的面包和硬币地图", en: "Writing a little more than a", w: 1703, tier: "先读", line: "归纳问题 = 隐藏条件；预告它是社会科学的核心难题" },
  ],
  "02": [
    { k: 1, p: [1, 24], t: "比萨斜塔与可证伪", en: "Science allows us to make predictions", w: 2272, tier: "先读", line: "定义实验、证伪、重复验证、规则的可靠性，全书的方法底座" },
    { k: 2, p: [25, 40], t: "海王星与表观超光速", en: "How do we know that observation", w: 1759, tier: "有空", line: "证伪的难题：推翻的是哪条？Kuhn 范式像退回经院哲学" },
    { k: 3, p: [41, 53], t: "黑猫白猫：范式是凑合", en: "Those who study the scientific process", w: 984, tier: "有空", line: "作者的综合：范式让证伪可行；第 52 段一段回顾第一部哲学线" },
  ],
  "03": [
    { k: 1, p: [1, 27], t: "一百个开关的化工厂", en: "Evolution through natural selection is a", w: 1860, tier: "有空", line: "隐性知识第一次讲清：演化是「有偏」的试错；第三部的根" },
    { k: 2, p: [28, 36], t: "一万座工厂比赛", en: "Evolutionary methods can compete with one", w: 913, tier: "有空", line: "方法之间可以竞争、层层嵌套；明确知识和隐性知识对擂" },
    { k: 3, p: [37, 55], t: "知识树和手机里的相对论", en: "To my knowledge, Francis Bacon never", w: 1855, tier: "有空", line: "科学像在给理论「育种」；接受科学的理由在科学之外；真 = 能用" },
  ],
  "04": [
    { k: 1, p: [1, 7], t: "「你不能那样做！」", en: "Science does not proceed as a", w: 492, tier: "可跳过", line: "科学家的诚实和士气；一则轶事，后文不再用" },
    { k: 2, p: [8, 11], t: "科学界的创业者", en: "Scientists can be, and often must", w: 500, tier: "有空", line: "个人固执、整体开放：科学的「看不见的手」" },
    { k: 3, p: [12, 28], t: "科学、市场与普通法", en: "The parallels between science and markets", w: 1307, tier: "有空", line: "科学和市场同构，为第三部「自由 = 试错」铺路；第 28 段引出第 5 章" },
  ],
  "05": [
    { k: 1, p: [1, 8], t: "恐龙与陨石坑", en: "Stand in a lab when one", w: 734, tier: "有空", line: "没有实验也能证伪；历史科学只是建规则的脚手架" },
    { k: 2, p: [9, 18], t: "天文学凭什么算科学", en: "Astrophysics is a trickier case. It", w: 1085, tier: "先读", line: "首次提出因果密度；三条件社会政策全违反，通往第二部" },
  ],
  "06": [
    { k: 1, p: [1, 18], t: "房贷与巴基斯坦政变", en: "Imagine that you run a bank.", w: 1174, tier: "先读", line: "立起风险 vs 不确定性；概率陈述证伪不了；14 章还要用" },
    { k: 2, p: [19, 30], t: "这枚硬币算哪一类", en: "So, how do we know that", w: 1123, tier: "有空", line: "参照类问题 = 归纳问题的推广；第 8 章讲推广时再用" },
  ],
  "07": [
    { k: 1, p: [1, 29], t: "从坏血病到抽签分组", en: "Anyone who has ever sought treatment", w: 3504, tier: "先读", line: "随机分组为什么能控制「不知道的原因」，全书方法的地基" },
    { k: 2, p: [30, 38], t: "医生的三条反对", en: "Like many innovations, the RFT faced", w: 1151, tier: "有空", line: "「其他条件从不相等」，引出推广难题；对应后面企业里的阻力" },
  ],
  "08": [
    { k: 1, p: [1, 19], t: "加纳免费看病试验", en: "If biology is an environment of", w: 2115, tier: "先读", line: "内部效度 / 外部效度：一次试验做对了，也不一定推得远" },
    { k: 2, p: [20, 39], t: "费希尔对希尔：吸烟之争", en: "A second important limitation of RFTs", w: 1726, tier: "有空", line: "不能做试验时怎么判因果；为何这招难用到社会政策上" },
  ],
  "09": [
    { k: 1, p: [1, 19], t: "总统屋里的三位顾问", en: "Imagine that a hypothetical US president", w: 1600, tier: "有空", line: "第二部分的论点：经济预测更像历史判断；附第二部分路线图" },
    { k: 2, p: [20, 30], t: "孔德和密尔的梦", en: "We have seen that as we", w: 1237, tier: "可跳过", line: "社会科学思想史铺垫；「理论总能找借口」后两节演示得更具体" },
    { k: 3, p: [31, 47], t: "巴特尔斯的六个变量", en: "The first example is a regression", w: 1631, tier: "先读", line: "改一个假设（滞后一年还是两年），回归算出的效应就不见了" },
    { k: 4, p: [48, 75], t: "《魔鬼经济学》的堕胎论", en: "For the second example, consider Freakonomics,", w: 2364, tier: "有空", line: "回归对回归的拉锯；社会科学自然实验常见的三个毛病" },
  ],
  "10": [
    { k: 1, p: [1, 15], t: "亨德森的经验曲线", en: "It is hard to exaggerate the", w: 1537, tier: "有空", line: "商业版的「社会科学之梦」：把战略变成科学，没做成" },
    { k: 2, p: [16, 46], t: "模型永远不是系统", en: "I graduated from college the year", w: 2918, tier: "有空", line: "作者亲历：有物理规律撑着的分析管用，一涉及人的行为就难" },
    { k: 3, p: [47, 72], t: "改名 FastMart", en: "I was once asked a seemingly", w: 3438, tier: "先读", line: "用改名一例演示回归的三个毛病，引出随机试验" },
  ],
  "11": [
    { k: 1, p: [1, 16], t: "信用卡公司的蓝信封", en: "As in medicine, people with business", w: 1839, tier: "有空", line: "商业把随机试验做成日常；作者自己转向试验的经过" },
    { k: 2, p: [17, 34], t: "六种果酱卖得更多？", en: "The job of experimentation in business", w: 2080, tier: "先读", line: "单次试验难推广，要多轮试；方法可靠度的排序" },
    { k: 3, p: [35, 45], t: "选址：老手胜过模型", en: "Just as with therapeutics, one role", w: 1415, tier: "有空", line: "非实验方法的三种用处；给「非显而易见」下定义" },
    { k: 4, p: [46, 58], t: "「你们的设计师不行」", en: "I was once in a meeting", w: 1697, tier: "有空", line: "同一试验结果可支持相反决定；战略像范式框住试验" },
    { k: 5, p: [59, 72], t: "多数新点子都没用", en: "I have observed the results of", w: 1379, tier: "先读", line: "作者的经验：多数新点子没用，有用的效果也小；用好试验的三个条件" },
  ],
  "12": [
    { k: 1, p: [1, 20], t: "LaLonde 与赫克曼之争", en: "Almost as soon as I saw", w: 2256, tier: "有空", line: "社会试验为何沉寂；方法之争归结为推广问题" },
    { k: 2, p: [21, 38], t: "强制逮捕像抛硬币", en: "The development of experimental knowledge in", w: 1835, tier: "先读", line: "犯罪试验的复现结果常常对不上：单次试验靠不住" },
    { k: 3, p: [39, 52], t: "领福利先去工作", en: "What is usually referred to around", w: 1667, tier: "有空", line: "强制工作要求：少见的一致结论（§7 第 106 段有摘要）" },
    { k: 4, p: [53, 68], t: "择校抽签成了试验", en: "Purposeful randomized experimentation was historically less", w: 1735, tier: "有空", line: "择校抽签成了天然的随机试验；作者说效果有限" },
    { k: 5, p: [69, 84], t: "教室里的模拟拍卖", en: "Controlled experiments in economics date at", w: 1777, tier: "有空", line: "经济学实验从实验室走向田野，仍须实地检验" },
    { k: 6, p: [85, 96], t: "佩里竞选的书呆子们", en: "Over the past twenty years laboratory", w: 1003, tier: "有空", line: "拉票试验在竞选里重演商业试验的套路" },
    { k: 7, p: [97, 114], t: "改环境，别改人", en: "Some themes naturally emerge from this", w: 2140, tier: "先读", line: "第二部的结论：三条方法、三条实质；引出第三部" },
  ],
  "13": [
    { k: 1, p: [1, 14], t: "卖淫合不合法，让各地试", en: "The most obvious application to politics", w: 1822, tier: "先读", line: "前两部落地成政治原则；立起「自由当手段」和它的悖论" },
    { k: 2, p: [15, 24], t: "出走权、小行星、五十套标准", en: "As with all political insights, this", w: 922, tier: "有空", line: "地方各行其是的三道边界；第三道引出社会凝聚力" },
    { k: 3, p: [25, 35], t: "X 地要处死八岁孤儿", en: "Suppose that US jurisdiction X, where", w: 1196, tier: "有空", line: "第 27–31 段唯物论绕路可略读；第 35 段定义社会凝聚力，14、15 章要用" },
  ],
  "14": [
    { k: 1, p: [1, 14], t: "APT 误打误撞做成 SaaS", en: "Social cohesion can be undercut by", w: 1224, tier: "有空", line: "用作者自己公司的故事说明前沿创新靠试错" },
    { k: 2, p: [15, 41], t: "理赔主管和晶体管", en: "This tradition appears under numerous overlapping", w: 2413, tier: "有空", line: "大公司擅长例行创新，难以颠覆自己；市场兜底" },
    { k: 3, p: [42, 72], t: "卢德分子和「金十字架」", en: "Consider that I told the story", w: 3055, tier: "先读", line: "创新与凝聚力的根本张力；末段列出第 15 章的三条路" },
  ],
  "15": [
    { k: 1, p: [1, 18], t: "政策豁免加一个「政策 FDA」", en: "There is a bright line between", w: 2024, tier: "先读", line: "全书分析最直接落地的建议：制度化的社会政策随机试验" },
    { k: 2, p: [19, 38], t: "学校松绑，移民当招聘", en: "Human capital", w: 2591, tier: "有空", line: "第二条办法；多是作者的政策主张，部分配了试验方案" },
    { k: 3, p: [39, 61], t: "托克维尔的牧羊人，社保拆两半", en: "Most government spending in an advanced", w: 2426, tier: "有空", line: "第三条办法；第 41 段为福利国家辩护、第 52 段改结构不改水平" },
    { k: 4, p: [62, 64], t: "别丢了灵魂", en: "I developed the proposals in this", w: 326, tier: "先读", line: "全书的结论：把试错装进人道的约束里" },
  ],
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
  { id: "in", ch: 0, secs: [1, 2, 3, 4], need: [], words: 2997, t: "几家店试试看", d: "看不到「要是没做」，所以要实验也要自由" },
  { id: "01", ch: 1, secs: [1, 2], need: ["sim"], words: 4272, t: "归纳和隐藏条件", d: "见过一千次的规律，凭什么下次还成立" },
  { id: "02", ch: 2, secs: [1, 2, 3], need: [], words: 5015, t: "证伪与范式", d: "实验只能推翻，科学凭什么还可靠" },
  { id: "03", ch: 3, secs: [1, 2, 3], need: [], words: 4628, t: "演化不是瞎试", d: "遗传算法、隐性知识，和科学凭什么算「真」" },
  { id: "04", ch: 4, secs: [1, 2, 3], need: [], words: 2299, t: "科学像一个市场", d: "个人固执，整体开放：科学和市场同构吗" },
  { id: "05", ch: 5, secs: [1, 2], need: [], words: 1819, t: "不做实验的科学", d: "天文学不做实验，凭什么也可靠" },
  { id: "06", ch: 6, secs: [1, 2], need: [], words: 2297, t: "风险与不确定", d: "概率靠分类算出，分类选没选对永远不知道" },
  { id: "07", ch: 7, secs: [1, 2], need: ["sim"], words: 4655, t: "随机试验的诞生", d: "抽签分组凭什么能量出疗效" },
  { id: "08", ch: 8, secs: [1, 2], need: ["sim"], words: 3841, t: "一次试验能搬多远", d: "随机试验推不远；做不了试验时靠什么定案" },
  { id: "09", ch: 9, secs: [1, 2, 3, 4], need: [], words: 6832, t: "换个假设，结论就变", d: "回归和自然实验为什么常给不出可靠结论" },
  { id: "10a", ch: 10, secs: [1, 2], need: [], words: 4455, t: "模型永远不是系统", d: "把战略变成科学的梦，和一位咨询顾问的亲历" },
  { id: "10b", ch: 10, secs: [3], need: ["sim"], words: 3438, t: "改名能多卖多少", d: "便利店改名：回归为何答不了，只有试验能" },
  { id: "11a", ch: 11, secs: [1, 2], need: ["sim"], words: 3919, t: "蓝信封和果酱", d: "商业把试验做成日常，而一次试验为何不够" },
  { id: "11b", ch: 11, secs: [3, 4, 5], need: [], words: 4491, t: "设计师不行", d: "试验之外的方法、战略和组织" },
  { id: "12a", ch: 12, secs: [1, 2, 3], need: [], words: 5758, t: "一次试验定不了乾坤", d: "社会试验的方法之争，犯罪一反、福利一正" },
  { id: "12b", ch: 12, secs: [4, 5, 6, 7], need: [], words: 6655, t: "改环境，别改人？", d: "教育、经济、政治的试验，和第二部的总结" },
  { id: "13", ch: 13, secs: [1, 2, 3], need: [], words: 3940, t: "自由是手段", d: "预测不了政策，就让各地试，但有三道边界" },
  { id: "14", ch: 14, secs: [1, 2, 3], need: [], words: 6692, t: "创新的代价谁来付", d: "带来增长的创新，凭什么得到输家的同意" },
  { id: "15a", ch: 15, secs: [1, 2], need: [], words: 4615, t: "豁免、试验和人力资本", d: "让各州去试，联邦管证据；再加人力资本" },
  { id: "15b", ch: 15, secs: [3, 4], need: [], words: 2752, t: "拆开福利国家", d: "为福利国家辩护，再把它按功能拆开" },
];
window.UC_EXTRA = { "00": { t: "开读之前", d: "" } };
window.UC_READY = ["00", "in", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10a", "10b", "11a", "11b", "12a", "12b", "13", "14", "15a", "15b"];
