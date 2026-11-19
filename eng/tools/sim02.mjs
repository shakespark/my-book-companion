// 照「试试看」的顺序用 playwright 连着点 02 的推秋千模拟器，打印每步的统计栏和说明，并核对数。用法：node tools/sim02.mjs（别页照它改）
// 统计栏五格：秋千自己一个来回（秒）/ 推的间隔（秒）/ 半分钟推了几下 / 最后 10 秒最大摆角（度）/ 座位最高升起（厘米）
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
await p.goto("file://" + new URL("../chapters/02.html", import.meta.url).pathname);
const S = "#sim-02";
const set = (label, v) => p.selectOption(`${S} select[aria-label="${label}"]`, String(v));
const reset = () => p.click(`${S} button:has-text("回到跟着秋千推")`);
const stats = () => p.$$eval(`${S} .stat .v`, (e) => e.map((x) => x.innerText));
const show = async (lab) => console.log(lab, "|", (await stats()).join(" | "), "\n   ", await p.textContent(`${S} .narrate`));
const expect = async (lab, want) => { const v = await stats(); if (JSON.stringify(v) !== JSON.stringify(want)) errs.push(`${lab}：统计栏 ${v.join(" / ")}，应为 ${want.join(" / ")}`); };

// 试试看 1：打开时（链长 2 米、中、平常、跟着秋千）→ 约 24 度、17 厘米（底稿 b-swing.py：0.83 米弧长）；每 2 秒约 3 度；每 3.5 秒约 4 度
await show("1a 打开时"); await expect("1a", ["2.84", "2.84", "11", "24", "17.1"]);
await set("多久推一下", "2"); await show("1b 每 2 秒"); await expect("1b", ["2.84", "2.00", "15", "3", "0.3"]);
await set("多久推一下", "3.5"); await show("1c 每 3.5 秒"); await expect("1c", ["2.84", "3.50", "9", "4", "0.5"]);
// 试试看 2：每两个来回一下 → 约 13 度，比每 2 秒高
await set("多久推一下", "2T"); await show("2 每两个来回"); await expect("2", ["2.84", "5.67", "6", "13", "5.3"]);
// 试试看 3：跟着秋千 + 阻尼器 → 约 4 度；链长 3 米 → 周期 3.47 秒；按每 2.5 秒推
await reset(); await set("阻力", "0.2"); await show("3a 阻尼器"); await expect("3a", ["2.84", "2.84", "11", "4", "0.5"]);
await reset(); await set("链长（米）", "3"); await show("3b 链长 3 米跟着推"); await expect("3b", ["3.47", "3.47", "9", "18", "14.1"]);
await set("多久推一下", "2.5"); await show("3c 链长 3 米每 2.5 秒"); await expect("3c", ["3.47", "2.50", "12", "3", "0.4"]);
// 固定秒数正好接近周期：说明要跟着结果走，不能说「上不去」
for (const [L, iv] of [["1", "2"], ["3", "3.5"], ["1.5", "2.5"]]) {
  await reset(); await set("链长（米）", L); await set("多久推一下", iv); await show(`y 链长 ${L} 每 ${iv} 秒`);
  const v = await stats(), txt = await p.textContent(`${S} .narrate`);
  if (Number(v[3]) >= 10 && /上不去/.test(txt)) errs.push(`y 链长 ${L} 每 ${iv} 秒：摆角 ${v[3]} 度，说明却写「上不去」`);
  if (Number(v[3]) < 10) errs.push(`y 链长 ${L} 每 ${iv} 秒：摆角只有 ${v[3]} 度，和周期接近应当荡得起来`);
}
// 边界：最猛的组合（链长 1 米、重、阻力很小、跟着推）不出 NaN，并提示模型不准
await reset(); await set("链长（米）", "1"); await set("每下推多猛", "0.5"); await set("阻力", "0.005"); await show("x1 最猛");
if (!/45 度/.test(await p.textContent(`${S} .narrate`))) errs.push("x1：摆角过 45 度时说明里没提示模型不准");
const body = await p.textContent(S); if (/undefined|NaN/.test(body)) errs.push("页面上出现 undefined / NaN");
console.log(errs.length ? "✗ " + errs.join("; ") : "✓ 没有脚本错误，「试试看」的数都对上");
await b.close();
