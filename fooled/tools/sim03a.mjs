// 照「试试看」的顺序用 playwright 连着点 03a 的模拟器（平行的历史），打印每步的统计栏和说明。用法：node tools/sim03a.mjs
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
await p.goto("file://" + new URL("../chapters/03a.html", import.meta.url).pathname);
const S = "#sim-03a";
const btn = (t) => p.click(`${S} .presets button:has-text("${t}")`);
const set = (label, v) => p.selectOption(`${S} select[aria-label="${label}"]`, String(v));
const again = () => p.click(`${S} button:has-text("换一批运气")`);
const show = async (lab) => console.log(lab, "|", (await p.$$eval(`${S} .stat`, (e) => e.map((x) => x.innerText.replace(/\n/g, " ")))).join(" | "), "\n   ", await p.textContent(`${S} .narrate`));
await btn("6 孔，玩 1 次"); await show("1a 6孔1次");
await set("策略", "dentist"); await show("1b 牙医");
await btn("25 岁玩到 50 岁"); await show("2a 6孔25次");
for (let i = 0; i < 6; i++) { await again(); await show(`2b 换一批运气 ${i + 1}`); }
await btn("500 孔，玩 30 次"); await show("3a 500孔30次");
await set("玩几次", 1000); await show("3b 500孔1000次");
await set("玩几次", 3000); await show("3c 500孔3000次");
await btn("1000 孔，玩 3000 次"); await show("3d 1000孔3000次");
await btn("一千人各玩一次"); await show("4a 一千人各玩一次（6孔）");
await btn("一人连玩一百次"); await show("4b 一人连玩一百次（6孔）");
await set("弹巢数", 500); await show("4c 一人连玩一百次（500孔）");
await set("策略", "dentist"); await show("5 牙医一个人");
await set("看法", "crowd"); await set("玩几次", 3000); await show("6 牙医一千人3000次");
await p.click(`${S} button:has-text("重置")`); await show("7 重置");
const body = await p.textContent(S); if (/undefined|NaN|Infinity/.test(body)) errs.push("页面上出现 undefined / NaN / Infinity");
console.log(errs.length ? "✗ " + errs.join("; ") : "✓ 没有脚本错误");
await b.close();
