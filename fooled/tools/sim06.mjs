// 照「试试看」的顺序用 playwright 连着点 06 的模拟器，打印每步的统计栏和说明。用法：node tools/sim06.mjs（03a、03b、09a、11b 照它改）
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
await p.goto("file://" + new URL("../chapters/06.html", import.meta.url).pathname);
const S = "#sim-06";
const preset = (t) => p.click(`${S} .presets button:has-text("${t}")`);
const set = (label, v) => p.selectOption(`${S} select[aria-label="${label}"]`, String(v));
const show = async (lab) => console.log(lab, "|", (await p.$$eval(`${S} .stat`, (e) => e.map((x) => x.innerText.replace(/\n/g, " ")))).join(" | "), "\n   ", await p.textContent(`${S} .narrate`));
await preset("表 6.1"); await show("1a 表6.1 1局");
await set("玩多少局", 100); await show("1b 100局");
await p.click(`${S} button:has-text("换一个你")`); await show("1c 换一个你");
for (const n of [700, 1000, 2000]) { await set("玩多少局", n); await show(`2 ${n}局`); }
await set("玩多少局", 1); await preset("做多"); await show("3a 做多 1周");
await preset("做空"); await show("3b 做空 1周");
await set("玩多少局", 4); await show("3c 做空 4周");
await preset("做多"); await show("3d 做多 4周");
await p.click(`${S} button:has-text("重置")`); await set("每局赢的概率", 10); await set("赢一次赚", 50); await set("输一次亏", 1); await show("4 罗杰斯");
const body = await p.textContent(S); if (/undefined|NaN/.test(body)) errs.push("页面上出现 undefined / NaN");
console.log(errs.length ? "✗ " + errs.join("; ") : "✓ 没有脚本错误");
await b.close();
