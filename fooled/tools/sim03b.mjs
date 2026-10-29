// 照「试试看」的顺序用 playwright 连着点 03b 的模拟器，打印每步的统计栏和说明。用法：node tools/sim03b.mjs
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
await p.goto("file://" + new URL("../chapters/03b.html", import.meta.url).pathname);
const S = "#sim-03b";
const set = (label, v) => p.selectOption(`${S} select[aria-label="${label}"]`, String(v));
const show = async (lab) => console.log(lab, "|", (await p.$$eval(`${S} .stat`, (e) => e.map((x) => x.innerText.replace(/\n/g, " ")))).join(" | "), "\n   ", await p.textContent(`${S} .narrate`));
const F = { y: "每年", q: "每季", m: "每月", d: "每天", h: "每小时", i: "每分钟", s: "每秒" };
for (const k of ["y", "q", "m"]) { await set("看盘频率", k); await show(`1 ${F[k]}`); }
for (const k of ["d", "h", "i", "s"]) { await set("看盘频率", k); await show(`2 ${F[k]}`); }
for (const k of Object.keys(F)) { await set("看盘频率", k); await show(`3a λ2.5 ${F[k]}`); }
await set("难过的分量", 1);
for (const k of Object.keys(F)) { await set("看盘频率", k); await show(`3b λ1 ${F[k]}`); }
await p.click(`${S} button:has-text("重置")`); await set("年化超额收益", 5); await set("年化波动", 20); await show("4 收益5 波动20 每年");
await p.click(`${S} button:has-text("换 40 次")`); await show("5 换 40 次");
await p.click(`${S} button:has-text("重置")`); await show("6 重置");
const body = await p.textContent(S); if (/undefined|NaN|Infinity/.test(body)) errs.push("页面上出现 undefined / NaN / Infinity");
console.log(errs.length ? "✗ " + errs.join("; ") : "✓ 没有脚本错误");
await b.close();
