// 照「试试看」的顺序用 playwright 连着点 06a 的安全系数模拟器，打印每步的统计栏和说明，并核对数。用法：node tools/sim06a.mjs
// 统计栏四格：安全系数 / 可靠指标 β / 失效概率 / 约几根里坏一根
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
await p.goto("file://" + new URL("../chapters/06a.html", import.meta.url).pathname);
const S = "#sim-06a";
const set = (label, v) => p.selectOption(`${S} select[aria-label="${label}"]`, String(v));
const reset = () => p.click(`${S} button:has-text("回到默认")`);
const stats = () => p.$$eval(`${S} .stat .v`, (e) => e.map((x) => x.innerText));
const narr = () => p.textContent(`${S} .narrate`);
const show = async (lab) => console.log(lab, "|", (await stats()).join(" | "), "\n   ", await narr());
const expect = async (lab, want) => { const v = await stats(); if (JSON.stringify(v) !== JSON.stringify(want)) errs.push(`${lab}：统计栏 ${v.join(" / ")}，应为 ${want.join(" / ")}`); };

// 试试看 1：打开时（1.5、10%、20%）→ 约 2.3%、44 根坏一根（底稿 e-sims.py）；荷载分散 10% → 约 0.28%
await show("1a 打开时"); await expect("1a", ["1.5", "2.00", "2.3%", "44"]);
await set("荷载的分散", "0.1"); await show("1b 荷载 10%"); await expect("1b", ["1.5", "2.77", "0.28%", "360"]);
// 试试看 2：荷载回 20%、系数 2 → 约 0.020%；荷载 40% → 约 1.3%，比 1b 的 0.28% 高
await set("荷载的分散", "0.2"); await set("安全系数", "2"); await show("2a 系数 2"); await expect("2a", ["2", "3.54", "0.020%", "4900"]);
await set("荷载的分散", "0.4"); await show("2b 系数 2 荷载 40%"); await expect("2b", ["2", "2.24", "1.3%", "79"]);
if (!/系数大不等于安全/.test(await narr())) errs.push("2b：说明里没点出系数大不等于安全");
// 试试看 3：回到默认、系数 1.1 → 约 33%；强度分散 5% → 约 31%，降得很少
await reset(); await set("安全系数", "1.1"); await show("3a 系数 1.1"); await expect("3a", ["1.1", "0.44", "33%", "3"]);
await set("强度的分散", "0.05"); await show("3b 强度 5%"); await expect("3b", ["1.1", "0.48", "31%", "3.2"]);
if (!/分散大的那一边说了算/.test(await narr())) errs.push("3b：说明里没讲分散大的一边说了算");
// 边界：最安全、最危险
await reset(); await set("安全系数", "3"); await set("强度的分散", "0.05"); await set("荷载的分散", "0.05"); await show("x1 最安全");
await expect("x1", ["3", "12.65", "小于百万分之一", "百万以上"]);
await reset(); await set("安全系数", "1.1"); await set("强度的分散", "0.2"); await set("荷载的分散", "0.4"); await show("x2 最危险");
const body = await p.textContent(S); if (/undefined|NaN|Infinity/.test(body)) errs.push("页面上出现 undefined / NaN / Infinity");
console.log(errs.length ? "✗ " + errs.join("; ") : "✓ 没有脚本错误，「试试看」的数都对上");
await b.close();
