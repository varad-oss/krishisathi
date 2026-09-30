import { expect, test } from '@playwright/test';
import { mockApi, withFarmProfile } from './mock-api';

// Regression: no page may scroll horizontally on small phones, in English or in a long native script.
for (const [width, lang] of [[320, 'en'], [360, 'en'], [320, 'ta']] as const) {
  test(`no horizontal overflow at ${width}px (${lang})`, async ({ page }) => {
    await page.setViewportSize({ width, height: 800 });
    if (lang !== 'en') await page.addInitScript((l) => localStorage.setItem('krishi_language', l), lang);
    await withFarmProfile(page);
    await mockApi(page);
    for (const path of ['/', '/problem', '/farm', '/diagnose', '/advisor', '/dashboard', '/about']) {
      await page.goto(path);
      await page.waitForLoadState('networkidle');
      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      expect(scrollWidth, `${path} overflows`).toBeLessThanOrEqual(width);
    }
  });
}
