import { chromium } from "@playwright/test";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const projectDirectory = resolve(scriptDirectory, "..");
const guidePath = resolve(projectDirectory, "guide", "index.html");
const outputPath = resolve(projectDirectory, "guide", "remm-openclaw-personal-os.pdf");
const browser = await chromium.launch({
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
});
const page = await browser.newPage();
await page.goto(pathToFileURL(guidePath).href, { waitUntil: "networkidle" });
await page.pdf({
  path: outputPath,
  format: "Letter",
  printBackground: true,
  preferCSSPageSize: true,
  tagged: true
});
await browser.close();
console.log(outputPath);
