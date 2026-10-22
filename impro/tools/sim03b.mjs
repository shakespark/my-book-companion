// 照「试试看」的顺序用 playwright 连着点 03b 的模拟器，打印每步的统计栏和说明。用法：node tools/sim03b.mjs
// 选项按钮带 data-opt：0 接住再添一点、1 顶回去、2 否认、3 岔开话题。
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(String(e)));
await p.goto("file://" + new URL("../chapters/03b.html", import.meta.url).pathname);
const S = "#sim-03b";
const pick = (k) => p.click(`${S} .picks button[data-opt="${k}"]`);
const reset = () => p.click(`${S} .controls button:has-text("重来")`);
const show = async (lab) => console.log(lab, "|", (await p.$$eval(`${S} .stat`, (e) => e.map((x) => x.innerText.replace(/\n/g, " ")))).join(" | "), "|", await p.textContent(`${S} .narrate`));
const many = async (k, n) => { for (let i = 0; i < n; i++) await pick(k); };

// 试试看 1：一路否认
await many(2, 1); await show("1 否认×1"); await many(2, 1); await show("1 否认×2"); await many(2, 1); await show("1 否认×3");
console.log("  还有选项按钮吗：", await p.$$eval(`${S} .picks button`, (e) => e.length));
// 试试看 2：一路顶回去；再一路岔开
await reset(); await many(1, 5); await show("2a 顶回去×5");
await reset(); await many(3, 3); await show("2b 岔开×3");
// 试试看 3：接住、否认、接住，再一路接住
await reset(); await pick(0); await show("3 接住"); await pick(2); await show("3 否认"); await pick(0); await show("3 接住");
await many(0, 3); await show("3 走完");
// 对照：一路接住
await reset(); await many(0, 5); await show("对照 接住×5");
const txt = await p.textContent(S);
console.log("undefined/NaN：", /undefined|NaN/.test(txt) ? "有" : "无", "| 脚本错误：", errs.length ? errs : "无");
await b.close();
