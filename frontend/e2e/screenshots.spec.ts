import path from 'node:path';
import { test } from '@playwright/test';
import { mockApi, withFarmProfile } from './mock-api';

// Visual QA helper, not a regression test: SCREENSHOTS=1 npx playwright test screenshots --project=desktop
test.skip(!process.env.SCREENSHOTS, 'set SCREENSHOTS=1 to capture');

const WIDTHS = (process.env.SCREENSHOT_WIDTHS ?? '320,360,390,412,768,1280').split(',').map(Number);
const LANG = process.env.SCREENSHOT_LANG ?? 'en';
const out = (name: string, w: number) => path.join('test-results', 'screens', `${LANG}-${name}-${w}.png`);

for (const width of WIDTHS) {
  test(`pages at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.addInitScript((l) => localStorage.setItem('krishi_language', l), LANG);
    await withFarmProfile(page);
    await mockApi(page);
    const shoot = async (name: string) => {
      await page.waitForTimeout(600);
      await page.screenshot({ path: out(name, width), fullPage: true });
      await page.screenshot({ path: out(`${name}-viewport`, width) });
    };

    await page.goto('/');
    await shoot('landing');
    await page.goto('/farm');
    await page.locator('#soil').getByText(/./).first().waitFor();
    await page.locator('#alerts details').first().click();
    await page.locator('#soil details').first().click();
    await shoot('farm');
    await page.goto('/diagnose');
    await shoot('diagnose');
    await page.getByRole('main').getByTestId('file-input').setInputFiles(path.join(__dirname, 'fixtures', 'leaf.jpg'));
    await page.locator('button.bg-leaf-600').last().click();
    await page.locator('#result-title').waitFor();
    await shoot('diagnose-result');
    await page.goto('/advisor');
    await page.locator('form textarea').fill('Should I irrigate?');
    await page.locator('form button[type=submit]').click();
    await page.locator('.prose').first().waitFor();
    await shoot('advisor');
    await page.goto('/dashboard');
    await page.waitForTimeout(800);
    await shoot('dashboard');
    await page.goto('/about');
    await shoot('about');
  });
}
