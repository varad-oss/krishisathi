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

// Every supported language on every page at 360 px (long scripts such as Tamil and Malayalam find wrapping bugs).
for (const lang of ['hi', 'mr', 'ta', 'te', 'bn', 'kn', 'gu', 'pa', 'ml']) {
  test(`all pages fit at 360px in ${lang}`, async ({ page }, info) => {
    test.skip(info.project.name !== 'desktop', 'viewport is set explicitly; one project is enough');
    test.setTimeout(120_000);
    await page.route(/arcgisonline\.com|tile\.openstreetmap\.org/, (r) => r.abort());
    await page.setViewportSize({ width: 360, height: 800 });
    await page.addInitScript((l) => localStorage.setItem('krishi_language', l), lang);
    await withFarmProfile(page);
    await mockApi(page);
    const overflowing: string[] = [];
    for (const path of ['/', '/farm', '/problem', '/diagnose', '/advisor', '/history', '/more', '/dashboard', '/about']) {
      await page.goto(path);
      await page.waitForLoadState('networkidle');
      const width = await page.evaluate(() => document.documentElement.scrollWidth);
      if (width > 360) overflowing.push(`${path} (${width}px)`);
    }
    expect(overflowing, overflowing.join(', ')).toEqual([]);
  });
}
