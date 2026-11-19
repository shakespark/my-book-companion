// 照「试试看」的顺序用 playwright 连着点 05 的蜂窝复用模拟器，打印每步的统计栏和说明，并核对数。用法：node tools/sim05.mjs
// 统计栏五格：全城几个小区 / 每个小区分到几对频率 / 全城同时能打几个电话 / 是不复用时的几倍 / 同一份频率的两个小区相距（公里）
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
await p.goto("file://" + new URL("../chapters/05.html", import.meta.url).pathname);
const S = "#sim-05";
const set = (label, v) => p.selectOption(`${S} select[aria-label="${label}"]`, String(v));
const reset = () => p.click(`${S} button:has-text("回到书里的数")`);
const stats = () => p.$$eval(`${S} .stat .v`, (e) => e.map((x) => x.innerText));
const show = async (lab) => console.log(lab, "|", (await stats()).join(" | "), "\n   ", await p.textContent(`${S} .narrate`));
const expect = async (lab, want) => { const v = await stats(); if (JSON.stringify(v) !== JSON.stringify(want)) errs.push(`${lab}：统计栏 ${v.join(" / ")}，应为 ${want.join(" / ")}`); };
const A = "每个小区多大（平方公里）", F = "能用几个频率", N = "几个小区一组";

// 试试看 1：打开时 → 40 个小区、57 对、2,280（底稿 e-sims.py）；小区 1 平方公里 → 57,000，多 25 倍
await show("1a 打开时"); await expect("1a", ["40", "57", "2,280", "5.7", "14.2"]);
await set(A, "1"); await show("1b 1 平方公里"); await expect("1b", ["1,000", "57", "57,000", "142.5", "2.8"]);
// 试试看 2：回到书里的数，4 个一组（底稿：每小区 100、全城 4,000），再 3 个一组
await reset(); await set(N, "4"); await show("2a 4 个一组"); await expect("2a", ["40", "100", "4,000", "10.0", "10.7"]);
await set(N, "3"); await show("2b 3 个一组"); await expect("2b", ["40", "133", "5,320", "13.3", "9.3"]);
await set(N, "1"); await show("2c 1 个一组"); await expect("2c", ["40", "400", "16,000", "40.0", "5.4"]);
await set(N, "12"); await show("2d 12 个一组"); await expect("2d", ["40", "33", "1,320", "3.3", "18.6"]);
// 试试看 3：回到书里的数，频率加倍 → 4,560，约 2 倍
await reset(); await set(F, "1600"); await show("3a 1600 个频率"); await expect("3a", ["40", "114", "4,560", "5.7", "14.2"]);
// 边界
await reset(); await set(A, "0.25"); await set(F, "1600"); await set(N, "1"); await show("x1 最密");
await reset(); await set(A, "50"); await set(F, "400"); await set(N, "12"); await show("x2 最疏");
// 每种分组：图上编号 1 的格子不相邻（相邻格编号必须不同，N=1 除外）
for (const n of ["3", "4", "7", "12"]) {
  await reset(); await set(N, n);
  const bad = await p.$$eval(`${S} svg polygon`, (ps) => {
    const c = ps.map((q) => { const xy = q.getAttribute("points").split(" ").map((t) => t.split(",").map(Number)); return { g: q.getAttribute("class").split(" ")[0], x: xy.reduce((s, v) => s + v[0], 0) / 6, y: xy.reduce((s, v) => s + v[1], 0) / 6 }; });
    let n = 0; for (const a of c) for (const b of c) if (a !== b && Math.hypot(a.x - b.x, a.y - b.y) < 34 && a.g === b.g) n++; return n;
  });
  const groups = await p.$$eval(`${S} svg polygon`, (ps) => new Set(ps.map((q) => q.getAttribute("class").split(" ")[0])).size);
  console.log(`N=${n}：${groups} 组，相邻同组 ${bad} 处`);
  if (bad) errs.push(`N=${n}：相邻小区同组 ${bad} 处`);
  if (groups !== Number(n)) errs.push(`N=${n}：图上有 ${groups} 组`);
}
const body = await p.textContent(S); if (/undefined|NaN/.test(body)) errs.push("页面上出现 undefined / NaN");
console.log(errs.length ? "✗ " + errs.join("; ") : "✓ 没有脚本错误，「试试看」的数都对上");
await b.close();
