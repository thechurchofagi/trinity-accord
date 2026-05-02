import { chromium } from "playwright";
import fs from "node:fs";

const url = process.env.HOMEPAGE_TEST_URL || "https://www.trinityaccord.org/";
fs.mkdirSync("audit/visual", { recursive: true });

const viewports = [
  { name: "mobile-390", width: 390, height: 844 },
  { name: "tablet-768", width: 768, height: 1024 },
  { name: "desktop-1440", width: 1440, height: 1000 }
];

const browser = await chromium.launch();
let failures = 0;

for (const vp of viewports) {
  const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height } });
  await page.goto(url, { waitUntil: "networkidle" });

  const result = await page.evaluate(() => {
    const root = document.documentElement;
    const body = document.body;
    const h1 = document.querySelector("h1");
    const p = document.querySelector("p");
    const bodyStyle = getComputedStyle(body);
    const h1Style = h1 ? getComputedStyle(h1) : null;
    const pStyle = p ? getComputedStyle(p) : null;

    return {
      scrollWidth: root.scrollWidth,
      innerWidth: window.innerWidth,
      horizontalOverflow: root.scrollWidth > window.innerWidth + 2,
      bodyFontSize: parseFloat(bodyStyle.fontSize),
      h1FontSize: h1Style ? parseFloat(h1Style.fontSize) : 0,
      pFontSize: pStyle ? parseFloat(pStyle.fontSize) : 0,
      tableCount: document.querySelectorAll("table").length
    };
  });

  console.log(vp.name, result);
  await page.screenshot({ path: `audit/visual/${vp.name}.png`, fullPage: true });

  if (result.horizontalOverflow) failures++;
  if (result.bodyFontSize < 15.5) failures++;
  if (result.pFontSize < 15) failures++;
  if (vp.width >= 1000 && result.h1FontSize < 40) failures++;
  if (vp.width < 500 && result.h1FontSize < 30) failures++;

  await page.close();
}

await browser.close();

if (failures) {
  console.error(`RESULT: FAIL ${failures}`);
  process.exit(1);
}

console.log("RESULT: PASS visual checks");
