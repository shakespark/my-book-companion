// 照「试试看」的顺序用 playwright 连着点 01a 的浴缸模拟器，打印每步的统计栏和说明，并核对书里那一组的数。用法：node tools/sim01a.mjs（01b、02a、02b 照它改）
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
await p.goto("file://" + new URL("../chapters/01a.html", import.meta.url).pathname);
const S = "#sim-01a";
const set = (label, v) => p.selectOption(`${S} select[aria-label="${label}"]`, String(v));
const reset = () => p.click(`${S} button:has-text("回到书里那一组")`);
const stats = () => p.$$eval(`${S} .stat .v`, (e) => e.map((x) => x.innerText));
const show = async (lab) => console.log(lab, "|", (await p.$$eval(`${S} .stat`, (e) => e.map((x) => x.innerText.replace(/\n/g, " ")))).join(" | "), "\n   ", await p.textContent(`${S} .narrate`));
const expect = async (lab, want) => { const v = await stats(); if (JSON.stringify(v) !== JSON.stringify(want)) errs.push(`${lab}：统计栏 ${v.join(" / ")}，应为 ${want.join(" / ")}`); };

// 试试看 1：书里那一组（附录 Bathtub：50 加仑，流出 5，第 5 分钟起流入 5）→ 第 5 分钟 25，之后不动（原书图 7）
await show("1a 书里那一组"); await expect("1a", ["50", "25", "25", "0"]);
await set("第几分钟打开流入", 2); await show("1b 第 2 分钟打开"); await expect("1b", ["50", "40", "40", "0"]);
await set("第几分钟打开流入", 8); await show("1c 第 8 分钟打开"); await expect("1c", ["50", "10", "10", "0"]);
// 试试看 2：一开始就打开；流入 7 流出 5，和流入 5 流出 3，第 10 分钟都是 70
await set("第几分钟打开流入", 0); await set("流入（加仑/分钟）", 7); await show("2a 流入 7 流出 5"); await expect("2a", ["50", "50", "70", "+2"]);
await set("流入（加仑/分钟）", 5); await set("流出（加仑/分钟）", 3); await show("2b 流入 5 流出 3"); await expect("2b", ["50", "50", "70", "+2"]);
// 试试看 3：书里那一组，流入改 10 → 第 5 分钟 25，之后每分钟涨 5，第 10 分钟 50
await reset(); await set("流入（加仑/分钟）", 10); await show("3 流入 10"); await expect("3", ["50", "25", "50", "+5"]);
// 边界：只拔塞子看 20 分钟（第 10 分钟放干）；满了溢出；不打开
await reset(); await set("流入（加仑/分钟）", 0); await set("看多少分钟", 20); await show("x1 只拔塞子 20 分钟"); await expect("x1", ["50", "没打开", "0", "—"]);
await reset(); await set("开始时有多少水（加仑）", 100); await set("第几分钟打开流入", 0); await set("流入（加仑/分钟）", 10); await show("x2 满缸再加"); await expect("x2", ["100", "100", "100", "+5"]);
await reset(); await set("流出（加仑/分钟）", 0); await set("流入（加仑/分钟）", 0); await show("x3 全关"); await expect("x3", ["50", "没打开", "50", "—"]);
const body = await p.textContent(S); if (/undefined|NaN/.test(body)) errs.push("页面上出现 undefined / NaN");
console.log(errs.length ? "✗ " + errs.join("; ") : "✓ 没有脚本错误，书里那一组和「试试看」的数都对上");
await b.close();
