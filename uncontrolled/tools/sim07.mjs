// 照「试试看」的顺序用 playwright 连着点 07 的模拟器，打印每步的统计栏。用法：node tools/sim07.mjs（别的页照它改一份放 scratchpad）
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.HOME + "/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
await p.goto("file:///home/lee/my_book_companion/uncontrolled/chapters/07.html");
const S = "#sim-07";
const click = (t) => p.click(`${S} button:has-text("${t}")`);
const stats = async (lab) => console.log(lab, (await p.$$eval(`${S} .stat`, (e) => e.map((x) => x.innerText.replace(/\n/g, " ")))).join(" | "));
await click("做一次试验"); await stats("1a 医生 100 eff0 一次:");
await click("再做 20 次"); await stats("1b +20:");
await p.selectOption(`${S} select >> nth=0`, "coin"); await click("做一次试验"); await click("再做 20 次"); await stats("2 抛硬币:");
await p.selectOption(`${S} select >> nth=1`, "20"); await click("再做 20 次"); await stats("3a 每组20:");
await p.selectOption(`${S} select >> nth=1`, "1500"); await click("再做 20 次"); await stats("3b 每组1500:");
await p.selectOption(`${S} select >> nth=1`, "20"); await p.fill(`${S} input[type=range]`, "10"); await p.dispatchEvent(`${S} input[type=range]`, "input"); await click("做一次试验"); await stats("3c eff10 每组20:");
await p.locator(S).screenshot({ path: "/tmp/s07.png" });
await b.close();
