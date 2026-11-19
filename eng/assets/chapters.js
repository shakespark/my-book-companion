// 全站目录。tools/gen_chapters.py 生成，别手改节表；每页的 t、d 和 EG_READY 由 tools/accept.py 填（重新生成时保留）。tools/lint.py 从这里读页和节。
// EG_PARTS：全书六段（一章一段：引子和五个时代）。EG_CHAPTERS：n 章号（0 是 Preface），en 原书章名，t 本站章名，part 所在的段。
// EG_SECS：每章的节。原书章内没有小标题，节是本站按段号分的。k 节号（data-sec 写它），lab 显示的节号，
//   p 段号范围（source/text/NN.txt 的 [k]），w 英文词数，en 这一节第一段开头几个词（读者在 Kindle 里搜它），t 本站中文节名，tier 档（先读 / 有空 / 可跳过），line 这一节起什么作用。
// EG_PAGES：页。secs 这一页包含的节，need（sim / sim2：一个 / 两个模拟器，light：轻量页；lint 查），t 本站标题（不超过 10 个字），d 一句话（不超过 24 个字）。
window.EG_PARTS = [
  { n: 1, en: "From idea to reality", zh: "引子：什么是工程" },
  { n: 2, en: "Gravity", zh: "重力" },
  { n: 3, en: "Heat", zh: "热" },
  { n: 4, en: "Electromagnetism", zh: "电磁" },
  { n: 5, en: "Information", zh: "信息" },
  { n: 6, en: "Systems", zh: "系统" },
];
window.EG_CHAPTERS = [
  { n: 0, part: 0, en: "Preface", t: "序" },
  { n: 1, part: 1, en: "From idea to reality", t: "从想法到现实" },
  { n: 2, part: 2, en: "The age of gravity – time for work", t: "重力的时代：做功" },
  { n: 3, part: 3, en: "The age of heat – you can’t get something for nothing", t: "热的时代：天下没有白吃的午餐" },
  { n: 4, part: 4, en: "The age of electromagnetism – the power of attraction", t: "电磁的时代：吸引的力量" },
  { n: 5, part: 5, en: "The age of information – getting smaller", t: "信息的时代：越做越小" },
  { n: 6, part: 6, en: "The age of systems – risky futures", t: "系统的时代：有风险的未来" },
];
window.EG_SECS = {
  "00": [
    {"k": "1", "lab": "§1", "p": "1–4", "w": 548, "t": "工程是什么，有多大", "tier": "有空", "en": "The purpose of this book is", "line": "两条定义、无处不在、分支分了又合"},
    {"k": "2", "lab": "§2", "p": "5–7", "w": 529, "t": "致谢和图片来源", "tier": "可跳过", "en": "Engineering is a big subject and,", "line": "致谢名单和图片授权，不涉内容"},
  ],
  "01": [
    {"k": "1", "lab": "§1", "p": "1–3", "w": 415, "t": "工程师＝有巧思的人", "tier": "先读", "en": "Engineering is, in its most general", "line": "词源、工具塑造人，STEM 需要理清"},
    {"k": "2", "lab": "§2", "p": "4–6", "w": 431, "t": "没有工程的早晨", "tier": "有空", "en": "All through history, people have expressed", "line": "工具与信仰，依赖它却不懂它（Crawford）"},
    {"k": "3", "lab": "§3", "p": "7–9", "w": 650, "t": "工具不是中性的", "tier": "先读", "en": "One only has to think of", "line": "工程带着价值：交通改社会，民主要懂工程"},
    {"k": "4", "lab": "§4", "p": "10–11", "w": 365, "t": "什么算工具", "tier": "有空", "en": "If engineering is about making and using", "line": "工具＝用来做功的东西；预告各章的功"},
    {"k": "5", "lab": "§5", "p": "12–18", "w": 724, "t": "科学、艺术和手艺", "tier": "有空", "en": "It is indisputable that engineering is", "line": "词典定义 STEM；科学的边界；莫里斯"},
    {"k": "6", "lab": "§6", "p": "19–27", "w": 673, "t": "「工程」的六种意思", "tier": "可跳过", "en": "In everyday use, the word ‘engineering’", "line": "日常用法逐条罗列，第 28 段一句收回"},
    {"k": "7", "lab": "§7", "p": "28–31", "w": 505, "t": "四级职称和六大门类", "tier": "有空", "en": "So to recap, we know that", "line": "纵向按职责、横向按行当；一杯水的分工"},
    {"k": "8", "lab": "§8", "p": "32–34", "w": 414, "t": "人工髋关节和起搏器", "tier": "可跳过", "en": "Water is basic to human life", "line": "医学工程两个例子，细节不回到主线"},
    {"k": "9", "lab": "§9", "p": "35–37", "w": 423, "t": "米切姆：目的才是分界", "tier": "先读", "en": "Although these six classifications of the", "line": "内部分法理不清 STEM，意志是关键；先行后知"},
    {"k": "10", "lab": "§10", "p": "38–39", "w": 412, "t": "知与行，五个时代", "tier": "先读", "en": "Confusion about the words ‘engineering’ and", "line": "本书的定义：知 vs 行；全书路线图"},
  ],
  "02": [
    {"k": "1", "lab": "§1", "p": "1–3", "w": 548, "t": "推秋千的时机", "tier": "先读", "en": "What have a child’s swing, a golf club,", "line": "全章引子：顺着固有频率用力；共振也会毁桥"},
    {"k": "2", "lab": "§2", "p": "4–6", "w": 423, "t": "功、能量和功率", "tier": "有空", "en": "So timing is important in the way", "line": "把「干活」换成力×距离；概念块已讲，可略"},
    {"k": "3", "lab": "§3", "p": "7–10", "w": 403, "t": "从神话到日晷", "tier": "可跳过", "en": "It is impossible to know just how", "line": "史前到苏美尔的年表罗列，图 3 时间线已概括"},
    {"k": "4", "lab": "§4", "p": "11–13", "w": 521, "t": "五种古代机械", "tier": "有空", "en": "To help all of this activity, five", "line": "楔杠杆轮滑轮螺旋；首次讲机械效益；安提基特拉"},
    {"k": "5", "lab": "§5", "p": "14–22", "w": 1102, "t": "希腊人：从泰勒斯到欧几里得", "tier": "有空", "en": "The period from 900 BC to 200 BC", "line": "轴心时代；几何成了唯一的理论语言"},
    {"k": "6", "lab": "§6", "p": "23–29", "w": 533, "t": "阿基米德和维特鲁威", "tier": "有空", "en": "One of the first engineers was Archimedes", "line": "第一批工程师；普鲁塔克的鄙夷；经验法则手册"},
    {"k": "7", "lab": "§7", "p": "30–31", "w": 552, "t": "重犁、马镫和伊斯兰", "tier": "有空", "en": "After the fall of the western Roman Empire", "line": "中世纪和伊斯兰黄金时代的发明清单"},
    {"k": "8", "lab": "§8", "p": "32–34", "w": 434, "t": "「工程师」有了名字", "tier": "有空", "en": "Adelard of Bath had translated Euclid", "line": "大教堂工匠、ingeniator、达·芬奇：工程师成形"},
    {"k": "9", "lab": "§9", "p": "35–40", "w": 877, "t": "从速度到牛顿", "tier": "先读", "en": "But still the only theoretical language", "line": "异类量之比→加速度→伽利略、牛顿连起时间和功"},
    {"k": "10", "lab": "§10", "p": "41–45", "w": 542, "t": "三点观察", "tier": "先读", "en": "Three observations are pertinent. Firstly, from", "line": "作者的结论：科学和工程怎样分开、又没分干净"},
  ],
  "03": [
    {"k": "1", "lab": "§1", "p": "1–6", "w": 690, "t": "橡皮筋、桥和应变能", "tier": "有空", "en": "Have you ever stretched an elastic band", "line": "势能、动能、应变能；内功是能力，外功是需求"},
    {"k": "2", "lab": "§2", "p": "7–10", "w": 393, "t": "圣彼得穹顶的铁箍", "tier": "有空", "en": "At the end of the last chapter,", "line": "理论第一次用来救穹顶，反对声里看理论与实践的鸿沟"},
    {"k": "3", "lab": "§3", "p": "11–13", "w": 535, "t": "热机登场：从化工到希罗", "tier": "有空", "en": "Heat is another form of energy.", "line": "热是能量；古人想不通热，希罗拿蒸汽当玩具"},
    {"k": "4", "lab": "§4", "p": "14–16", "w": 966, "t": "从矿井抽水到瓦特", "tier": "先读", "en": "It was another 1,400 years or so", "line": "萨弗里、纽科门、瓦特：一步步改出真能用的蒸汽机"},
    {"k": "5", "lab": "§5", "p": "17–20", "w": 626, "t": "卡诺的理想热机", "tier": "先读", "en": "Despite these clear improvements, the early steam engines", "line": "改进有上限：理想热机的效率取决于冷热两端温差"},
    {"k": "6", "lab": "§6", "p": "21–22", "w": 360, "t": "热是什么：两条定律与熵", "tier": "先读", "en": "Although Carnot had reasoned all this out", "line": "热质说倒台；能量守恒，但可用的那部分只会变少"},
    {"k": "7", "lab": "§7", "p": "23–26", "w": 624, "t": "火车头、内燃机和汽轮机", "tier": "可跳过", "en": "In Chapter 1, we referred to", "line": "四冲程、汽轮机、朗肯循环多是罗列；涡轮的定义下一节开头会再讲"},
    {"k": "8", "lab": "§8", "p": "27–29", "w": 899, "t": "惠特尔的喷气发动机", "tier": "有空", "en": "Frank Whittle was an officer in the", "line": "燃气轮机把四个冲程变成连续流动；涡扇为何更省更静"},
    {"k": "9", "lab": "§9", "p": "30–34", "w": 717, "t": "核电：切尔诺贝利到聚变", "tier": "有空", "en": "Probably the most controversial heat engines", "line": "核电也是热机；事故把「风险」推到台前，留给第 6 章"},
    {"k": "10", "lab": "§10", "p": "35–38", "w": 493, "t": "热机史说明了什么", "tier": "先读", "en": "From Hero of Alexandria’s steam toys", "line": "作者的结论：工程是为目的去做成事，实践带着科学走"},
  ],
  "04": [
    {"k": "1", "lab": "§1", "p": "1–7", "w": 846, "t": "异性相吸：从琥珀到电池", "tier": "有空", "en": "Do opposites attract? There is some evidence", "line": "电荷是什么，加古人到伏打电堆的发现史"},
    {"k": "2", "lab": "§2", "p": "8–11", "w": 498, "t": "法拉第：电生动，动生电", "tier": "先读", "en": "In 1820, Hans Christian Ørsted found", "line": "电流生磁、磁变生电：电能做功，功能发电"},
    {"k": "3", "lab": "§3", "p": "12–14", "w": 458, "t": "发电机越造越好", "tier": "可跳过", "en": "Soon afterwards, in London, Joseph Saxton", "line": "发电机改进的接力名单；只有讲自励的那段值得挑读"},
    {"k": "4", "lab": "§4", "p": "15–17", "w": 658, "t": "交流胜出：变压器的功劳", "tier": "先读", "en": "Up to this time, DC power", "line": "旋转磁场、感应电动机；高压送电损耗小"},
    {"k": "5", "lab": "§5", "p": "18–22", "w": 582, "t": "爱迪生的照明系统", "tier": "有空", "en": "At first, these new alternating currents", "line": "爱迪生、英斯尔、费兰蒂、斯旺：电灯和大电站"},
    {"k": "6", "lab": "§6", "p": "23–25", "w": 473, "t": "国家电网与各路发电", "tier": "有空", "en": "World War I created huge demands", "line": "电网从乱到统一；发电机靠什么转，热电联产"},
    {"k": "7", "lab": "§7", "p": "26–29", "w": 699, "t": "法拉第的场，麦克斯韦的方程", "tier": "先读", "en": "New and innovative ideas for creating", "line": "场的概念、电磁波谱；作者谈理论怎样受检验"},
    {"k": "8", "lab": "§8", "p": "30–31", "w": 415, "t": "从电报到无线电报", "tier": "有空", "en": "Indeed, radiation was about to revolutionize", "line": "酸泡电报到越洋电缆，再到马可尼的无线电报"},
    {"k": "9", "lab": "§9", "p": "32–33", "w": 475, "t": "LC 振荡：电路里的秋千", "tier": "有空", "en": "In 1888, Hertz had produced and", "line": "赫兹的火花隙：电容和线圈来回倒能量；天线"},
    {"k": "10", "lab": "§10", "p": "34–37", "w": 638, "t": "电话和留声机", "tier": "有空", "en": "As Marconi was developing the radio,", "line": "贝尔的电话、话筒原理、爱迪生的留声机和唱片"},
    {"k": "11", "lab": "§11", "p": "38–41", "w": 535, "t": "电子管：会放大的灯泡", "tier": "先读", "en": "Reginald Fessenden (1866–1932) was the first", "line": "二极管单向导电，三极管放大，反馈做出载波"},
    {"k": "12", "lab": "§12", "p": "42–45", "w": 406, "t": "调幅和调频", "tier": "有空", "en": "Radio signals are transmitted via analogue", "line": "载波怎样带上声音；AM 与 FM 的取舍"},
  ],
  "05": [
    {"k": "1", "lab": "§1", "p": "1–4", "w": 610, "t": "从机房到口袋：手机接力", "tier": "先读", "en": "When I was a student in", "line": "全章引子「变小」；手机靠小区复用和切换接力"},
    {"k": "2", "lab": "§2", "p": "5–6", "w": 294, "t": "晶体管和掺杂", "tier": "先读", "en": "The mobile cell phone has only become", "line": "小电压管大电流；掺杂造出自由电子和空穴"},
    {"k": "3", "lab": "§3", "p": "7–9", "w": 789, "t": "拆开一只 npn 晶体管", "tier": "有空", "en": "Transistors are so very important that", "line": "耗尽层怎样让基极电压管住集电极电流（细节）"},
    {"k": "4", "lab": "§4", "p": "10–12", "w": 442, "t": "芯片、穿孔卡和大型机", "tier": "有空", "en": "By the late 1950s, these electronic components", "line": "集成电路和摩尔定律；信息即图样；计算机简史"},
    {"k": "5", "lab": "§5", "p": "13–14", "w": 334, "t": "两种状态和逻辑门", "tier": "先读", "en": "Almost all modern electronics is digital", "line": "数字＝两态；门的功能从晶体管的连接里涌现"},
    {"k": "6", "lab": "§6", "p": "15–18", "w": 610, "t": "触发器怎样数到十五", "tier": "有空", "en": "Flip-flops are made from interconnected logic gates.", "line": "触发器串成二进制计数器，再讲一次涌现"},
    {"k": "7", "lab": "§7", "p": "19–21", "w": 508, "t": "浮点数、ASCII 和比特流", "tier": "可跳过", "en": "Obviously, in a practical counter we need", "line": "程序员熟悉的数和字符表示，加一串应用清单"},
    {"k": "8", "lab": "§8", "p": "22–26", "w": 636, "t": "上云，再变小", "tier": "有空", "en": "By the late 1960s, the average US company", "line": "光纤和云计算；量子、纳米医学；交给系统时代"},
  ],
  "06": [
    {"k": "1", "lab": "§1", "p": "1–5", "w": 683, "t": "「再也不会发生」？", "tier": "有空", "en": "‘We must ensure that this never happens", "line": "全章问题清单；失败是常态，从弯曲金字塔到墨西哥湾"},
    {"k": "2", "lab": "§2", "p": "6–10", "w": 709, "t": "可接受的风险，未知的未知", "tier": "先读", "en": "In Chapter 1, we referred to the disturbing", "line": "风险不能归零只能可接受；知识永远有缺口"},
    {"k": "3", "lab": "§3", "p": "11–13", "w": 530, "t": "安全系数和故障树", "tier": "先读", "en": "How do engineers actually deal with risk?", "line": "「硬」办法：安全系数、纵深防御、事件树和故障树"},
    {"k": "4", "lab": "§4", "p": "14–15", "w": 725, "t": "分层管理，混沌和连锁", "tier": "有空", "en": "But some tools have become so very complex", "line": "太复杂就分层管；初值敏感和连锁失效是新风险"},
    {"k": "5", "lab": "§5", "p": "16–18", "w": 633, "t": "硬系统和软系统", "tier": "有空", "en": "As a result, some engineers have begun", "line": "作者的势差—流—阻抗类比；硬系统都嵌在软系统里"},
    {"k": "6", "lab": "§6", "p": "19–22", "w": 798, "t": "真理、mythos 和 logos", "tier": "有空", "en": "A crucial question at the heart of", "line": "工程要的不是真理而是可靠，最后由注意义务兜底"},
    {"k": "7", "lab": "§7", "p": "23–25", "w": 696, "t": "整子和涌现", "tier": "有空", "en": "No matter how we judge the quality", "line": "Koestler 的 holon；层层涌现；软系统的 why 公式"},
    {"k": "8", "lab": "§8", "p": "26–29", "w": 948, "t": "找隐患：奶酪和气球", "tier": "先读", "en": "How do we deal with risk in", "line": "健康监测和反馈；Reason 的奶酪、Turner 的孵化"},
    {"k": "9", "lab": "§9", "p": "30–31", "w": 547, "t": "多安全才算够安全", "tier": "先读", "en": "The problems we are facing in the", "line": "知行并重的系统哲学；「够安全」就是我们容忍的"},
    {"k": "10", "lab": "§10", "p": "32–35", "w": 508, "t": "气候、筒仓和㶲", "tier": "有空", "en": "Climate change may well be the defining", "line": "气候变化是大考；专业割裂；用㶲看能量的品质"},
  ],
};
window.EG_PAGES = [
  { id: "01", ch: 1, secs: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], need: [], t: "把想法变成现实", d: "工程是做、工具带着价值、按目的分科学和工程" },
  { id: "02", ch: 2, secs: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], need: ["sim"], t: "推秋千到牛顿", d: "共振、功，和速度怎样成了一个量" },
  { id: "03a", ch: 3, secs: ["1", "2", "3", "4", "5", "6"], need: ["sim"], t: "热能做功，有上限", d: "应变能、蒸汽机、卡诺上限和「不能白得」" },
  { id: "03b", ch: 3, secs: ["7", "8", "9", "10"], need: [], t: "从机车到核电", d: "涡轮接替活塞，核电把风险推到台前" },
  { id: "04a", ch: 4, secs: ["1", "2", "3", "4", "5", "6"], need: ["sim"], t: "电能做功，交流胜出", d: "法拉第感应、变压器、高压送电和电网" },
  { id: "04b", ch: 4, secs: ["7", "8", "9", "10", "11", "12"], need: [], t: "从电磁场到无线电", d: "麦克斯韦的波，电报、电话、录音和载波" },
  { id: "05", ch: 5, secs: ["1", "2", "3", "4", "5", "6", "7", "8"], need: ["sim"], t: "晶体管和信息时代", d: "手机、晶体管、0 和 1、从门到计算机" },
  { id: "06a", ch: 6, secs: ["1", "2", "3", "4", "5"], need: ["sim"], t: "风险去不掉，只能压小", d: "安全系数、故障树、分层和硬系统" },
  { id: "06b", ch: 6, secs: ["6", "7", "8", "9", "10"], need: ["sim"], t: "事故在组织里孵化", d: "靠得住、整子、瑞士奶酪和系统思维" },
];
window.EG_EXTRA = { "00": { t: "开读之前", d: "作者、全书地图、最短读法" } };
window.EG_READY = ["00", "01", "02", "03a", "03b", "04a", "04b", "05", "06a", "06b"];
