// 照「试试看」的顺序用 playwright 连着点 01b 的两种回路模拟器，打印每步的统计栏和说明，并核对书里那几组数。用法：node tools/sim01b.mjs
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
await p.goto("file://" + new URL("../chapters/01b.html", import.meta.url).pathname);
const S = "#sim-01b";
const set = (label, v) => p.selectOption(`${S} select[aria-label="${label}"]`, String(v));
const reset = () => p.click(`${S} button:has-text("回到书里那一组")`);
const mode = (m) => p.click(`${S} button[data-mode="${m}"]`);
const stats = () => p.$$eval(`${S} .stat .v`, (e) => e.map((x) => x.innerText));
const show = async (lab) => console.log(lab, "|", (await p.$$eval(`${S} .stat`, (e) => e.map((x) => x.innerText.replace(/\n/g, " ")))).join(" | "), "\n   ", await p.textContent(`${S} .narrate`));
const expect = async (lab, want) => { const v = await stats(); if (JSON.stringify(v) !== JSON.stringify(want)) errs.push(`${lab}：统计栏 ${v.join(" / ")}，应为 ${want.join(" / ")}`); };
const RATE = "凉得快慢（每分钟缩小温差的百分之几）", ROOM = "室温（°C），也就是目标", MIN = "看多久（分钟）", MY = "你的利率（每年百分之几）", YRS = "看多少年";

// 试试看 1：咖啡默认（每分钟 25%、dt 0.25、室温 18、8 分钟）→ 100°C 那杯 28.4，第 1 分钟降 18.7，第 8 分钟降 3.1，温差减半约 2.7 分钟
await show("1a 咖啡默认"); await expect("1a", ["28.4", "18.7", "3.1", "2.7"]);
await set(ROOM, 25); await show("1b 室温 25"); await expect("1b", ["34.5", "17.1", "2.8", "2.7"]);
// 试试看 2：回到书里那一组，改成附录的 10% → 8 分钟 54.5；看 20 分钟 → 28.8；减半 6.8 分钟
await reset(); await set(RATE, 10); await show("2a 10%"); await expect("2a", ["54.5", "7.9", "3.9", "6.8"]);
await set(MIN, 20); await show("2b 10% 看 20 分钟"); const v2 = await stats(); if (v2[0] !== "28.8" || v2[3] !== "6.8") errs.push("2b：" + v2.join(" / "));
// 0°C 那杯 8 分钟约 15.7（从图上那条线读不到统计栏，这里直接算一遍和页面写的数核对）
{ let T = 0; for (let i = 0; i < 32; i++) T += (18 - T) * 0.25 * 0.25; if (Math.round(T * 10) / 10 !== 15.7) errs.push("0°C 那杯 8 分钟应为 15.7，算得 " + T); }
// 试试看 3：存款。默认 7%、12 年 → 225.22，第 11 年到 200，前一年 196.72，70 ÷ 7 = 10
await reset(); await mode("bank"); await show("3a 存款默认 7%"); await expect("3a", ["225.22", "第 11 年", "196.72", "10"]);
// 书上图 1—13 的五个终值
for (const [r, v] of [[2, "126.82"], [4, "160.10"], [6, "201.22"], [8, "251.82"], [10, "313.84"]]) { await set(MY, r); const s = await stats(); console.log(`   ${r}% 第 12 年 ${s[0]}`); if (s[0] !== v) errs.push(`${r}% 第 12 年应为 ${v}，实际 ${s[0]}`); }
await set(MY, 2); await show("3b 2%"); await expect("3b", ["126.82", "12 年内没到", "—", "35"]);
await set(YRS, 40); await show("3c 2% 看 40 年"); await expect("3c", ["220.80", "第 36 年", "199.99", "35"]);
// 边界：1% 看 40 年也到不了；切回咖啡再切回来；60% 最快
await set(MY, 1); await show("x1 1% 40 年"); await expect("x1", ["148.89", "40 年内没到", "—", "70"]);
await mode("coffee"); await set(RATE, 60); await set(MIN, 30); await set(ROOM, 0); await show("x2 咖啡 60% 30 分钟 室温 0");
await mode("bank"); await show("x3 切回存款（保留 1%、40 年）");
const body = await p.textContent(S); if (/undefined|NaN|Infinity/.test(body)) errs.push("页面上出现 undefined / NaN / Infinity");
console.log(errs.length ? "✗ " + errs.join("; ") : "✓ 没有脚本错误，书里那几组和「试试看」的数都对上");
await b.close();
