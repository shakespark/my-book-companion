// 照「试试看」的顺序用 playwright 连着点 04a 的高压送电模拟器，打印每步的统计栏和说明，并核对数。用法：node tools/sim04a.mjs
// 统计栏四格：线上电流（安）/ 路上烧掉 / 烧掉的比例（%）/ 到用户手里（%）
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
await p.goto("file://" + new URL("../chapters/04a.html", import.meta.url).pathname);
const S = "#sim-04a";
const set = (label, v) => p.selectOption(`${S} select[aria-label="${label}"]`, String(v));
const reset = () => p.click(`${S} button:has-text("回到 132 千伏")`);
const stats = () => p.$$eval(`${S} .stat .v`, (e) => e.map((x) => x.innerText));
const narr = () => p.textContent(`${S} .narrate`);
const show = async (lab) => console.log(lab, "|", (await stats()).join(" | "), "\n   ", await narr());
const expect = async (lab, want) => { const v = await stats(); if (JSON.stringify(v) !== JSON.stringify(want)) errs.push(`${lab}：统计栏 ${v.join(" / ")}，应为 ${want.join(" / ")}`); };
const has = async (lab, re) => { if (!re.test(await narr())) errs.push(`${lab}：说明里没有 ${re}`); };

// 试试看 1：打开时 132 kV、10 MW、5 Ω → 76 A、28.7 kW、0.29%；400 kV → 25 A、3.1 kW，约九分之一（底稿 d-sim.py）
await show("1a 打开时"); await expect("1a", ["76", "28.7 千瓦", "0.29", "99.71"]);
await set("输电电压", "400000"); await show("1b 400 kV"); await expect("1b", ["25", "3.1 千瓦", "0.031", "99.97"]); await has("1b", /约九分之一/);
// 试试看 2：接着 11 kV → 909 A、4.13 MW、41%；240 V → 送不过去
await set("输电电压", "11000"); await show("2a 11 kV"); await expect("2a", ["909", "4.13 兆瓦", "41", "58.7"]); await has("2a", /144 倍/);
await set("输电电压", "240"); await show("2b 240 V"); await expect("2b", ["41,667", "8,681 兆瓦", "送不过去", "0"]); await has("2b", /送不过去/);
// 试试看 3：回到 132 kV → 33 kV（4.6%）→ 电阻 10 Ω（9.2%）→ 50 MW（46%）
await reset(); await set("输电电压", "33000"); await show("3a 33 kV"); await expect("3a", ["303", "459 千瓦", "4.6", "95.4"]);
await set("线路电阻", "10"); await show("3b 10 Ω"); await expect("3b", ["303", "918 千瓦", "9.2", "90.8"]);
await set("要送多少电", "50"); await show("3c 50 MW"); await expect("3c", ["1,515", "23 兆瓦", "46", "54.1"]);
await set("输电电压", "132000"); await show("3d 50 MW 10 Ω 132 kV"); await expect("3d", ["379", "1.43 兆瓦", "2.9", "97.1"]);
await set("输电电压", "400000"); await show("3e 50 MW 10 Ω 400 kV"); await expect("3e", ["125", "156 千瓦", "0.31", "99.69"]);
// 页面上写出的数：概念块和示意图的 909 / 76 安、4130 / 28.7 千瓦，检查题 3 的 459 千瓦
await reset(); await set("输电电压", "275000"); await show("y 275 kV"); await expect("y", ["36", "6.6 千瓦", "0.066", "99.93"]);
// 边界：最猛的组合（100 MW、20 Ω、240 V）和最轻的（1 MW、1 Ω、400 kV）不出 NaN
await set("要送多少电", "100"); await set("线路电阻", "20"); await set("输电电压", "240"); await show("x1 最猛");
await set("要送多少电", "1"); await set("线路电阻", "1"); await set("输电电压", "400000"); await show("x2 最轻");
const body = await p.textContent(S); if (/undefined|NaN|Infinity/.test(body)) errs.push("页面上出现 undefined / NaN / Infinity");
console.log(errs.length ? "✗ " + errs.join("; ") : "✓ 没有脚本错误，「试试看」的数都对上");
await b.close();
