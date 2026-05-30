import { test, expect } from "@playwright/test";

test.describe("首页重定向", () => {
  test("根路径重定向到项目管理", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveURL(/\/projects/);
  });
});
