// 照「试试看」的顺序用 playwright 连着点 09a 的模拟器，打印每步的统计栏和说明。用法：node tools/sim09a.mjs
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
await p.goto("file://" + new URL("../chapters/09a.html", import.meta.url).pathname);
const S = "#sim-09a";
const set = (label, v) => p.selectOption(`${S} select[aria-label="${label}"]`, String(v));
const again = () => p.click(`${S} button:has-text("重新跑一次")`);
const show = async (lab) => console.log(lab, "|", (await p.$$eval(`${S} .stat`, (e) => e.map((x) => x.innerText.replace(/\n/g, " ")))).join(" | "), "\n   ", await p.textContent(`${S} .narrate`));
await show("1a 默认");
await again(); await show("1b 重新跑");
await set("每年赚钱的概率", 45); await show("1c 45%");
await set("每年赚钱的概率", 50); await set("起跑人数", 10); await show("2a N=10");
let hit = 0; for (let i = 0; i < 40; i++) { await again(); const v = await p.textContent(`${S} .stat:nth-child(2) .v`); if (v !== "0") hit++; }
console.log("2b N=10 再跑 40 次，冒出幸存者的次数：", hit);
await set("起跑人数", 100000); await show("2c N=100000");
await set("起跑人数", 10000); await set("每年赚钱的概率", 55); await show("2d 55%");
await p.click(`${S} button:has-text("重置")`); await set("淘汰期后再看几年", 10); await show("3a 再看 10 年");
await set("每年赚钱的概率", 60); await set("淘汰规则", "con2"); await set("淘汰期（年）", 10); await show("3b 60% 连输两年 10 年");
await set("淘汰规则", "cum2"); await show("3c 累计输两年");
await set("每年赚钱的概率", 40); await set("淘汰规则", "one"); await set("起跑人数", 10); await show("4 极端：40% 10 人 10 年");
const body = await p.textContent(S); if (/undefined|NaN|Infinity/.test(body)) errs.push("页面上出现 undefined / NaN / Infinity");
console.log(errs.length ? "✗ " + errs.join("; ") : "✓ 没有脚本错误");
await b.close();
