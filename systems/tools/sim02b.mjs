// 照「试试看」的顺序用 playwright 连着点 02b 的油田和渔场模拟器，打印每步的统计栏和说明，并核对书里那几组的数。用法：node tools/sim02b.mjs
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
await p.goto("file://" + new URL("../chapters/02b.html", import.meta.url).pathname);
const S = "#sim-02b";
const set = (label, v) => p.selectOption(`${S} select[aria-label="${label}"]`, String(v));
const reset = () => p.click(`${S} button:has-text("回到书里那一组")`);
const mode = (t) => p.click(`${S} .modes button:has-text("${t}")`);
const stats = () => p.$$eval(`${S} .stat .v`, (e) => e.map((x) => x.innerText));
const show = async (lab) => console.log(lab, "|", (await p.$$eval(`${S} .stat`, (e) => e.map((x) => x.innerText.replace(/\n/g, " ")))).join(" | "), "\n   ", await p.textContent(`${S} .narrate`));
const expect = async (lab, want) => { await show(lab); const v = await stats(); if (JSON.stringify(v) !== JSON.stringify(want)) errs.push(`${lab}：统计栏 ${v.join(" / ")}，应为 ${want.join(" / ")}`); };

// 试试看 1（油田）：书里那一组（图 38）→ 开采第 41 年见顶 28.1，资本第 51 年见顶 60.2；储量 2000、4000（图 39）→ 高峰第 56、72 年
await expect("1a 油田 书里那一组", ["41", "28.1", "60.2", "6.4"]);
await set("油田有多大", 2000); await expect("1b 储量 2000", ["56", "69.9", "108.4", "0.5"]);
await set("油田有多大", 4000); await expect("1c 储量 4000", ["72", "164.2", "214.1", "0"]);
// 试试看 2（油田）：净增 1%、7%（图 40）；越稀缺越贵（图 41），运营成本 1 和 0.1
await reset(); await set("资本每年想净增（%）", 1); await expect("2a 净增 1%", ["81", "8.7", "13.5", "260.4"]);
await set("资本每年想净增（%）", 7); await expect("2b 净增 7%", ["34", "37.7", "81.6", "1.5"]);
await reset(); await set("油价", "rise"); await expect("2c 越稀缺越贵 成本 1", ["41", "28.1", "73.4", "1.4"]);
await set("运营成本（每单位设备每年）", 0.1); await expect("2d 越稀缺越贵 成本 0.1", ["41", "28.1", "113.5", "0"]);
// 试试看 3（渔场）：技术 0 / 1 / 2（图 43–45）；技术 1 寿命 30 → 崩溃
await mode("渔场"); await expect("3a 渔场 技术 0", ["100", "299", "237–241", "稳住", "477"]);
await set("捕捞技术", 1); await expect("3b 技术 1", ["91", "301", "123–224", "来回摆", "417"]);
await set("捕捞技术", 2); await expect("3c 技术 2", ["88", "306", "0–1", "崩溃", "0"]);
await set("捕捞技术", 1); await set("渔船能用多少年", 30); await expect("3d 技术 1 寿命 30", ["68", "305", "0–1", "崩溃", "9"]);
// 边界：渔场回到书里那一组；切回油田时油田的设置还在
await reset(); await expect("x1 渔场 回到书里那一组", ["100", "299", "237–241", "稳住", "477"]);
await set("船队每年想净增（%）", 9); await show("x2 渔场 净增 9%");
await mode("石油"); await show("x3 切回油田（成本 0.1、越稀缺越贵还在）");
await reset(); await expect("x4 油田 回到书里那一组", ["41", "28.1", "60.2", "6.4"]);
const body = await p.textContent(S); if (/undefined|NaN|Infinity/.test(body)) errs.push("页面上出现 undefined / NaN / Infinity");
console.log(errs.length ? "✗ " + errs.join("; ") : "✓ 没有脚本错误，书里那几组和「试试看」的数都对上");
await b.close();
