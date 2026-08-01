import { expect, test } from "@playwright/test";

test("guide contains nineteen complete printable pages", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle("Remm's OpenClaw Personal OS");
  await expect(page.locator(".print-page")).toHaveCount(19);
  await expect(page.locator("svg[aria-labelledby='diagram-title diagram-desc']")).toBeVisible();
  await expect(page.locator("#prompt-text")).toContainText("personal-os doctor");
  await expect(page.locator("#first-folder")).toContainText("~/Openclaw/system");
  await expect(page.locator("#first-folder")).toContainText("~/Openclaw/runtime");
  await expect(page.locator("#codex-full-access")).toContainText("Full access");
  await expect(page.locator("#codex-full-access")).toContainText("Prevent sleep while running");
  await expect(page.locator("#prompt-text")).toContainText("START-HERE.md");
});

test("checklist state persists and resets", async ({ page }) => {
  await page.goto("/");
  const first = page.locator("[data-check]").first();
  await first.check();
  await expect(page.locator("#progress")).toContainText("1 of");
  await page.reload();
  await expect(first).toBeChecked();
  await page.locator("#reset-guide").click();
  await expect(first).not.toBeChecked();
  await expect(page.locator("#progress")).toContainText("0 of");
});

test("guide fits a phone viewport without page overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  const overflows = await page.locator(".print-page").evaluateAll((pages) =>
    pages.filter((item) => item.scrollWidth > item.clientWidth + 1).map((item) => item.id)
  );
  expect(overflows).toEqual([]);
});

test("all guide images load", async ({ page }) => {
  await page.goto("/");
  const broken = await page.locator("img").evaluateAll((images) =>
    images.filter((item) => !item.complete || item.naturalWidth === 0).map((item) => item.getAttribute("src"))
  );
  expect(broken).toEqual([]);
});

test("print layout keeps each section within one letter page", async ({ page }) => {
  await page.goto("/");
  await page.emulateMedia({ media: "print" });
  const sizes = await page.locator(".print-page").evaluateAll((pages) =>
    pages.map((item) => ({ id: item.id, client: item.clientHeight, scroll: item.scrollHeight }))
  );
  expect(sizes.filter((item) => item.scroll > item.client + 1)).toEqual([]);
});
