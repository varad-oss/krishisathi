import { expect, test } from '@playwright/test';
import { mockApi, withFarmProfile } from './mock-api';

// Regression: no page may scroll horizontally on small phones.
for (const width of [320, 360]) {
  test(`no horizontal overflow at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 800 });
    await withFarmProfile(page);
    await mockApi(page);
    for (const path of ['/', '/farm', '/diagnose', '/advisor', '/dashboard', '/about']) {
      await page.goto(path);
      await page.waitForLoadState('networkidle');
      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      expect(scrollWidth, `${path} overflows`).toBeLessThanOrEqual(width);
    }
  });
}
