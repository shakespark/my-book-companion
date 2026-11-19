// 照「试试看」的顺序用 playwright 连着点 06b 的瑞士奶酪模拟器，打印每步的统计栏和说明，并核对数。用法：node tools/sim06b.mjs
// 统计栏五格：防线互不相干时的事故概率 / 算上坏日子的事故概率 / 事故里出在坏日子的 / 再加一道第一格降为 / 再加一道第二格降为
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
await p.goto("file://" + new URL("../chapters/06b.html", import.meta.url).pathname);
const S = "#sim-06b";
const set = (label, v) => p.selectOption(`${S} select[aria-label="${label}"]`, String(v));
const reset = () => p.click(`${S} button:has-text("回到打开时的设置")`);
const stats = () => p.$$eval(`${S} .stat .v`, (e) => e.map((x) => x.innerText));
const narr = () => p.textContent(`${S} .narrate`);
const show = async (lab) => console.log(lab, "|", (await stats()).join(" | "), "\n   ", await narr());
const expect = async (lab, want) => { const v = await stats(); if (JSON.stringify(v) !== JSON.stringify(want)) errs.push(`${lab}：统计栏 ${v.join(" / ")}，应为 ${want.join(" / ")}`); };
const has = async (lab, re) => { if (!re.test(await narr())) errs.push(`${lab}：说明里没有 ${re}`); };

// 试试看 1：打开时（3 道、各漏 10%、坏日子 10%、坏日子每道漏 50%）→ 0.1% 和 1.34%（底稿 e-sims.py），高 13 倍，93% 出在坏日子
await show("1 打开时"); await expect("1", ["0.1%", "1.34%", "93%", "1/10", "1/2.1"]); await has("1", /13 倍/);
// 试试看 2：4 道、5 道 → 0.01% / 0.634%，0.001% / 0.313%；5 道差约 300 倍
await set("防线有几道", 4); await show("2a 4 道"); await expect("2a", ["0.01%", "0.634%", "99%", "1/10", "1/2.0"]);
await set("防线有几道", 5); await show("2b 5 道"); await expect("2b", ["0.001%", "0.313%", "99.7%", "1/10", "1/2.0"]); await has("2b", /313 倍/);
// 试试看 3：每道做好一倍（5%）几乎没用；坏日子减半（5%）降到约一半
await reset(); await set("每道平时漏多少", "0.05"); await show("3a 每道漏 5%"); await expect("3a", ["0.0125%", "1.26%", "99%", "1/20", "1/2.0"]);
await set("每道平时漏多少", "0.1"); await set("坏日子占比", "0.05"); await show("3b 坏日子 5%"); await expect("3b", ["0.1%", "0.72%", "87%", "1/10", "1/2.2"]);
// 边界
await reset(); await set("坏日子占比", "0"); await show("x1 没有坏日子"); await expect("x1", ["0.1%", "0.1%", "0%", "1/10", "1/10"]); await has("x1", /连乘/);
await reset(); await set("每道平时漏多少", "0.5"); await set("坏日子里每道漏多少", "0.2"); await show("x2 坏日子不坏"); await has("x2", /算不上坏/);
await reset(); await set("防线有几道", 6); await set("每道平时漏多少", "0.01"); await show("x3 最稳"); await expect("x3", ["1 万亿分之一", "0.156%", "超过 99.9%", "1/100", "1/2.0"]);
await reset(); await set("坏日子占比", "0.01"); await show("x4 坏日子 1%"); await has("x4", /56%|出在坏日子/);
const ticks = await p.$$eval(`${S} svg text`, (e) => e.map((x) => x.textContent));
console.log("   刻度和标签：", ticks.join(" · "));
const body = await p.textContent(S); if (/undefined|NaN|Infinity/.test(body)) errs.push("模拟器里出现 undefined / NaN / Infinity");
console.log(errs.length ? "✗ " + errs.join("; ") : "✓ 没有脚本错误，「试试看」的数都对上");
await b.close();
