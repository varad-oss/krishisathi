import { expect, test } from '@playwright/test';
import { fixtureData, mockApi, withFarmProfile } from './mock-api';

test.describe('Read aloud', () => {
  test('Read aloud becomes Stop while playing, and Stop restores it', async ({ page }) => {
    await withFarmProfile(page);
    await mockApi(page, { tts: { delayMs: 400 } });
    await page.goto('/advisor');
    await page.getByRole('button', { name: 'Should I irrigate this week?' }).click();
    await expect(page.getByText('hold irrigation today')).toBeVisible();

    const answer = page.locator('article').last();
    await answer.getByRole('button', { name: 'Read aloud' }).click();
    await expect(answer.getByRole('button', { name: 'Preparing audio…' })).toBeVisible();
    const stop = answer.getByRole('button', { name: 'Stop' });
    await expect(stop).toBeVisible();
    await expect(answer.getByRole('button', { name: 'Read aloud' })).toHaveCount(0);
    await stop.click();
    await expect(answer.getByRole('button', { name: 'Read aloud' })).toBeVisible();
  });

  test('speech failure without a native voice is explained, not replaced by another language', async ({ page }) => {
    await withFarmProfile(page);
    await page.addInitScript(() => Object.defineProperty(window, 'speechSynthesis', { value: undefined }));
    await mockApi(page, { tts: { status: 503, body: { error: { code: 'SERVICE_UNAVAILABLE', message: 'x', request_id: 'r', retryable: true } } } });
    await page.goto('/advisor');
    await page.getByRole('button', { name: 'Should I irrigate this week?' }).click();
    const answer = page.locator('article').last();
    await answer.getByRole('button', { name: 'Read aloud' }).click();
    await expect(answer.getByRole('alert')).toContainText('Audio in English is not available right now');
    await expect(answer.getByRole('button', { name: 'Read aloud' })).toBeVisible();
  });
});

test.describe('Soil and KVK honesty', () => {
  test('soil rate limit shows the real reason and a retry, never values', async ({ page }) => {
    await withFarmProfile(page);
    const regen = { ...fixtureData.regenerative, soil: { status: 'unavailable', reason: 'rate_limited', retryable: true, provenance: fixtureData.regenerative.soil.provenance } };
    await mockApi(page, { regenerative: { body: regen, times: 1 } });
    await page.goto('/farm');
    const soil = page.locator('#soil');
    await expect(soil.getByText(/limits how often it can be asked/)).toBeVisible();
    await expect(soil.getByText('Organic carbon', { exact: true })).toHaveCount(0);
    await soil.getByRole('button', { name: 'Try again' }).click();
    await expect(soil.getByText('Organic carbon', { exact: true })).toBeVisible();
  });

  test('soil point without a prediction explains why', async ({ page }) => {
    await withFarmProfile(page);
    const regen = { ...fixtureData.regenerative, soil: { status: 'no_data', reason: 'no_coverage', provenance: fixtureData.regenerative.soil.provenance } };
    await mockApi(page, { regenerative: { body: regen } });
    await page.goto('/farm');
    await expect(page.locator('#soil').getByText(/happens in towns, on roads and near water/)).toBeVisible();
    await expect(page.locator('#soil').getByRole('button', { name: 'Try again' })).toHaveCount(0);
  });

  test('KVK matched by district shows no distance', async ({ page }) => {
    await withFarmProfile(page);
    await mockApi(page);
    await page.goto('/farm');
    const kvk = page.getByRole('region', { name: 'Krishi Vigyan Kendra (KVK)' });
    await expect(kvk.getByText('KVK Pune')).toBeVisible();
    await expect(kvk.getByText('Serves Pune district')).toBeVisible();
    await expect(kvk.getByText(/km away/)).toHaveCount(0);
  });

  test('KVK outside coverage is stated, with the official portal', async ({ page }) => {
    await withFarmProfile(page);
    await mockApi(page, { kvk: { status: 404, body: { error: { code: 'NOT_FOUND', message: 'none', request_id: 'r', retryable: false } } } });
    await page.goto('/farm');
    const kvk = page.getByRole('region', { name: 'Krishi Vigyan Kendra (KVK)' });
    await expect(kvk.getByText(/could not be determined for this location/)).toBeVisible();
    await expect(kvk.getByRole('link', { name: /official portal/ })).toHaveAttribute('href', 'https://kvk.icar.gov.in/');
  });
});

test.describe('Satellite crop health', () => {
  test('shows NDVI against past seasons, radar through cloud, and history gaps as gaps', async ({ page }) => {
    await withFarmProfile(page);
    const provenance = { ...fixtureData.crop_health.provenance };
    const health = {
      status: 'available', ndvi: 0.41, ndvi_previous: 0.58, change: -0.17, latest_image_date: '2026-09-20', clear_pixel_fraction: 0.82,
      window: { start: '2026-08-31', end: '2026-09-30' }, image_count: 4,
      baseline: { status: 'available', years: [{ year: 2025, ndvi: 0.62, clear_pixel_fraction: 0.9, image_count: 3 }, { year: 2024, ndvi: 0.58, clear_pixel_fraction: 0.7, image_count: 2 }], min: 0.58, max: 0.62, mean: 0.6, position: 'below_range' },
      sar: { status: 'available', orbit_pass: 'ASCENDING', latest_image_date: '2026-09-24', vv_db: -9, vh_db: -19.5, vh_db_previous: -15, vh_change_db: -4.5, water_signal: true },
      provenance,
    };
    const series = ['2026-04-03', '2026-05-03', '2026-06-02', '2026-07-02', '2026-08-01', '2026-08-31'].map((start, i) => ({
      start, end: start, ndvi: [0.3, null, 0.55, 0.6, null, 0.41][i], clear_pixel_fraction: 0.5, image_count: 2,
    }));
    await mockApi(page, { cropHealth: { body: health }, cropHistory: { body: { status: 'available', series } } });
    await page.goto('/farm');
    const crop = page.locator('#crop');
    await expect(crop.getByText('Getting less green')).toBeVisible();
    await expect(crop.getByText(/Less green than the same weeks in past years \(0\.58 to 0\.62\)/)).toBeVisible();
    await expect(crop.getByText(/82% of the area was free of cloud/)).toBeVisible();
    await expect(crop.getByText(/typical of standing water/)).toBeVisible();
    await crop.getByText('View satellite history').click();
    await expect(crop.getByText('Greenness over the last 6 months')).toBeVisible();
    await expect(crop.getByText('no clear image')).toHaveCount(2);
  });
});

test.describe('Connection errors', () => {
  test('a blocked request to a reachable server is a service problem, not "check your internet"', async ({ page }) => {
    await mockApi(page, { stats: { abort: true } });
    await page.goto('/dashboard');
    const alert = page.getByRole('alert').first();
    await expect(alert).toContainText('KrishiSathi services are temporarily unavailable');
    await expect(alert).not.toContainText('Check your connection');
  });

  test('nothing reachable is reported as a connection problem', async ({ page }) => {
    await mockApi(page, { stats: { abort: true }, health: { abort: true } });
    await page.goto('/dashboard');
    await expect(page.getByRole('alert').first()).toContainText('Unable to reach KrishiSathi');
  });
});
