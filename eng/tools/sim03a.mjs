// 照「试试看」的顺序用 playwright 连着点 03a 的卡诺上限模拟器，打印每步的统计栏和说明，并核对数。用法：node tools/sim03a.mjs
// 统计栏四格（勾上「也按摄氏度直接算」时五格）：热端（开尔文）/ 冷端（开尔文）/ 温差（度）/ 卡诺上限（%）/ 直接用摄氏度算（%，错）
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
await p.goto("file://" + new URL("../chapters/03a.html", import.meta.url).pathname);
const S = "#sim-03a";
const set = (label, v) => p.selectOption(`${S} select[aria-label="${label}"]`, String(v));
const reset = () => p.click(`${S} button:has-text("回到 100 °C 对 20 °C")`);
const wrong = () => p.check(`${S} input[type=checkbox]`);
const stats = () => p.$$eval(`${S} .stat .v`, (e) => e.map((x) => x.innerText));
const flow = () => p.$$eval(`${S} .flow .n`, (e) => e.map((x) => x.innerText));
const show = async (lab) => console.log(lab, "|", (await stats()).join(" | "), "|", (await flow()).join(" / "), "\n   ", await p.textContent(`${S} .narrate`));
const expect = async (lab, want) => { const v = await stats(); if (JSON.stringify(v) !== JSON.stringify(want)) errs.push(`${lab}：统计栏 ${v.join(" / ")}，应为 ${want.join(" / ")}`); };

// 页面上写的数：示意图、概念块、先猜里的 21.4% / 约 21%
await show("0 打开时"); await expect("0", ["373", "293", "80", "21.4"]);
if (JSON.stringify(await flow()) !== JSON.stringify(["100.0 焦", "21.4 焦", "78.6 焦"])) errs.push("0：三根条应为 100 / 21.4 / 78.6 焦");
// 试试看 1：冷端 0 °C → 26.8%；改回 20 °C、热端 120 °C → 25.4%（先猜的答案：降冷端略多）
await set("冷端温度", "0"); await show("1a 冷端 0"); await expect("1a", ["373", "273", "100", "26.8"]);
await set("冷端温度", "20"); await set("热端温度", "120"); await show("1b 热端 120"); await expect("1b", ["393", "293", "100", "25.4"]);
// 试试看 2：回到默认、勾上摄氏度直接算 → 80%；冷端 0 °C → 100%
await reset(); await wrong(); await show("2a 摄氏度直接算"); await expect("2a", ["373", "293", "80", "21.4", "80.0"]);
await set("冷端温度", "0"); await show("2b 冷端 0 摄氏度直接算"); await expect("2b", ["373", "273", "100", "26.8", "100.0"]);
if (!/显然不对/.test(await p.textContent(`${S} .narrate`))) errs.push("2b：冷端 0 °C 错算出 100% 时说明里没点破");
// 试试看 3：回到默认（开关也复位），冷端 30 °C，热端 565 → 63.8%，1600 → 83.8%
await reset(); if ((await stats()).length !== 4) errs.push("3：回到默认后开关没复位");
await set("冷端温度", "30"); await set("热端温度", "565"); await show("3a 565 对 30"); await expect("3a", ["838", "303", "535", "63.8"]);
await set("热端温度", "1600"); await show("3b 1600 对 30"); await expect("3b", ["1873", "303", "1570", "83.8"]);
// 边界：没有温差
await reset(); await set("冷端温度", "100"); await wrong(); await show("x1 100 对 100"); await expect("x1", ["373", "373", "0", "0.0", "0.0"]);
if (!/没有温差/.test(await p.textContent(`${S} .narrate`))) errs.push("x1：没有温差时说明不对");
// 底稿 c-sim.py 的其他数：180 对 30 → 33.1%
await reset(); await set("冷端温度", "30"); await set("热端温度", "180"); await show("x2 180 对 30"); await expect("x2", ["453", "303", "150", "33.1"]);
const body = await p.textContent(S); if (/undefined|NaN/.test(body)) errs.push("页面上出现 undefined / NaN");
console.log(errs.length ? "✗ " + errs.join("; ") : "✓ 没有脚本错误，「试试看」的数都对上");
await b.close();
