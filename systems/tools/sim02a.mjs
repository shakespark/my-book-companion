// 照「试试看」的顺序用 playwright 连着点 02a 的两个模拟器（恒温器、汽车库存），打印每步的统计栏和说明，并核对页面上写的数。用法：node tools/sim02a.mjs
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
await p.goto("file://" + new URL("../chapters/02a.html", import.meta.url).pathname);
const mk = (S) => ({
  set: (label, v) => p.selectOption(`${S} select[aria-label="${label}"]`, String(v)),
  click: (txt) => p.click(`${S} button:has-text("${txt}")`),
  show: async (lab) => console.log(lab, "|", (await p.$$eval(`${S} .stat`, (e) => e.map((x) => x.innerText.replace(/\n/g, " ")))).join(" | "), "\n   ", await p.textContent(`${S} .narrate`)),
  expect: async (lab, want) => { const v = await p.$$eval(`${S} .stat .v`, (e) => e.map((x) => x.innerText)); if (JSON.stringify(v) !== JSON.stringify(want)) errs.push(`${lab}：统计栏 ${v.join(" / ")}，应为 ${want.join(" / ")}`); },
  label: async (i) => p.$$eval(`${S} .stat .l`, (e, i) => e[i].innerText, i),
});
const H = mk("#sim-02a-heat"), C = mk("#sim-02a-cars");
const eqLabel = async (S, i, want, lab) => { const l = await S.label(i); if (!l.includes(want)) errs.push(`${lab}：统计栏「${l}」里应有「${want}」`); };

// 恒温器 试试看 1：书里那一组（设定 18，漏热 0.1，上限 5，室外一直 10℃）→ 第 8 小时 17.3；设定 18.8 → 18.0
await H.show("H1a 书里那一组"); await H.expect("H1a", ["18", "17.3", "0.7", "17.3"]);
await H.set("设定温度（°C）", 18.8); await H.show("H1b 设定 18.8"); await H.expect("H1b", ["18.8", "18.0", "0.8", "18.0"]);
// 试试看 2：一天一夜，漏热 0.1 → 最低 15.9（第 13 小时）；0.3 → 12.3（第 14 小时）
await H.click("回到书里那一组"); await H.set("室外", 1); await H.show("H2a 昼夜 0.1"); await H.expect("H2a", ["18", "17.2", "15.9", "13"]);
await H.set("漏热比例（每小时）", 0.3); await H.show("H2b 昼夜 0.3"); await H.expect("H2b", ["18", "16.1", "12.3", "14"]);
// 试试看 3：0.3 时上限 10 → 12.7；上限 5、漏热 0.15 → 15.0
await H.set("火炉功率上限（°C/小时）", 10); await H.show("H3a 0.3 上限 10"); await H.expect("H3a", ["18", "16.1", "12.7", "13"]);
await H.set("火炉功率上限（°C/小时）", 5); await H.set("漏热比例（每小时）", 0.15); await H.show("H3b 0.15 上限 5"); await H.expect("H3b", ["18", "16.9", "15.0", "13"]);
// 边界：漏风、火炉很小、设定很高
await H.set("漏热比例（每小时）", 0.4); await H.set("火炉功率上限（°C/小时）", 2); await H.set("设定温度（°C）", 25); await H.show("Hx 昼夜 0.4 上限 2 设定 25");
await H.set("室外", 0); await H.show("Hx 恒定 0.4 上限 2 设定 25");

// 库存 试试看 1：书里那一组 5/3/5 → 最低 135（第 96 天），最高 293（第 86 天），摆幅 158，订单为 0 有 3 天（第 85–87 天）
await C.show("C1 书里那一组"); await C.expect("C1", ["135", "293", "158", "3"]);
await eqLabel(C, 0, "第 96 天", "C1"); await eqLabel(C, 1, "第 86 天", "C1");
const n1 = await p.textContent("#sim-02a-cars .narrate"); if (!n1.includes("188（第 32 天）") || !n1.includes("250（第 44 天）")) errs.push("C1：说明里应有 188（第 32 天）和 250（第 44 天）");
// 试试看 2：反应 2 → 最高 423；改回 3、感知 2 → 最高 311
await C.set("反应延迟（天）", 2); await C.show("C2a 反应 2"); await C.expect("C2a", ["121", "423", "302", "27"]);
await C.set("反应延迟（天）", 3); await C.set("感知延迟（天）", 2); await C.show("C2b 感知 2"); await C.expect("C2b", ["132", "311", "179", "5"]);
// 试试看 3：反应 6 → 最低 187、最高 229，稳在 220；去掉三个延迟 → 第 27 天到 220
await C.click("回到书里那一组"); await C.set("反应延迟（天）", 6); await C.show("C3a 反应 6"); await C.expect("C3a", ["187", "229", "2", "0"]);
await C.click("去掉三个延迟"); await C.show("C3b 没有延迟"); await C.expect("C3b", ["200", "220", "0", "0"]);
// 交货 3、8
await C.click("回到书里那一组"); await C.set("交货延迟（天）", 3); await C.show("C4a 交货 3"); await C.expect("C4a", ["192", "228", "2", "0"]);
await C.set("交货延迟（天）", 8); await C.show("C4b 交货 8"); await C.expect("C4b", ["74", "526", "424", "22"]);
await C.set("反应延迟（天）", 1); await C.show("Cx 反应 1 交货 8");
const body = (await p.textContent("#sim-02a-heat")) + (await p.textContent("#sim-02a-cars")); if (/undefined|NaN/.test(body)) errs.push("页面上出现 undefined / NaN");
console.log(errs.length ? "✗ " + errs.join("; ") : "✓ 没有脚本错误，书里那几组和「试试看」的数都对上");
await b.close();
