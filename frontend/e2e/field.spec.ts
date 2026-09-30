import { expect, test, type Page } from '@playwright/test';
import { fixtureData, mockApi, withFarmProfile } from './mock-api';

// Milestone 11: farm → field outline → field-specific satellite evidence → risk confidence → feedback → history →
// interoperability. Map tiles are external and not needed for the test, so they are blocked.
async function blockTiles(page: Page) {
  await page.route(/arcgisonline\.com|tile\.openstreetmap\.org/, (r) => r.abort());
}

async function drawSquare(page: Page) {
  const map = page.getByTestId('plot-map');
  await expect(map).toBeVisible();
  const box = (await map.boundingBox())!;
  const cx = box.x + box.width / 2;
  const cy = box.y + box.height / 2;
  for (const [dx, dy] of [[-60, -50], [60, -50], [60, 50], [-60, 50]]) await page.mouse.click(cx + dx, cy + dy);
}

test.describe('Field intelligence loop', () => {
  test('create farm, draw the field, see field satellite evidence and risk confidence, give feedback, check history and interoperability', async ({ page }) => {
    await blockTiles(page);
    await withFarmProfile(page);
    const saved: unknown[] = [];
    page.on('request', (r) => {
      if (/\/api\/farms\/[^/]+\/plot$/.test(r.url()) && r.method() === 'PUT') saved.push(r.postDataJSON());
    });
    // Before a field is drawn, satellite values describe the circle around the farm point.
    await mockApi(page, { cropHealth: { body: fixtureData.field_crop_health_point } });
    await page.goto('/farm');

    // 1-2. The farm is registered; before a field is drawn, values describe a circle around the location.
    const crop = page.locator('#crop');
    await expect(crop.getByText('Satellite vegetation signal').first()).toBeVisible();
    await expect(crop.getByTestId('satellite-scope')).toContainText('Around your location');
    await expect(crop.getByText('No field drawn.', { exact: false })).toBeVisible();
    await expect(crop.getByText('Used to make satellite observations more specific to your field.', { exact: false })).toBeVisible();

    await crop.getByRole('button', { name: 'Define my field' }).click();
    await expect(crop.getByRole('button', { name: 'Save' })).toBeDisabled();
    await drawSquare(page);
    await expect(crop.getByTestId('plot-area')).toContainText(/About [\d.]+ ha/);
    await crop.getByRole('button', { name: 'Save' }).click();
    await expect(crop.getByTestId('plot-summary')).toContainText('Area: 2.6 ha');
    const body = saved[0] as { geometry: { type: string; coordinates: number[][][] } };
    expect(body.geometry.type).toBe('Polygon');
    expect(body.geometry.coordinates[0]).toHaveLength(5); // four corners, closed ring

    // 3-4. Field-specific satellite evidence, labelled as a monitoring signal with explicit quality.
    await expect(crop.getByTestId('satellite-scope')).toContainText('My field · 2.6 ha');
    await expect(crop.getByTestId('ndvi-value')).toHaveText('0.52');
    await expect(crop.getByText(/field-monitoring indicator, not a diagnosis/)).toBeVisible();
    await crop.getByTestId('satellite-quality').locator('summary').click();
    await expect(crop.getByTestId('satellite-quality')).toContainText('Good');
    await expect(crop.getByText(/Cloud-free pixels: 240 of 256/)).toBeVisible();
    await expect(crop.getByText(/Mapped as cropland: 90% of the area/)).toBeVisible();

    // 5. Risk level and evidence confidence are shown separately, with the reason for the confidence.
    const today = page.locator('#today');
    await expect(today.getByTestId('confidence-chip')).toHaveText('Evidence confidence: Low');
    await expect(today.getByTestId('priority-reason')).toHaveText('Shown first: it is the most serious risk right now.');
    await today.getByText('Why this recommendation?').click();
    await expect(today.getByText('This risk needs several conditions at once; confidence follows the weakest one.')).toBeVisible();
    await expect(page.locator('#risks').getByText(/Risk level says how serious this would be/)).toBeVisible();

    // 6-7. Feedback is recorded and appears in the history.
    await today.getByRole('button', { name: 'Yes', exact: true }).click();
    await expect(today.getByText(/tell us how the crop responded under Farm history/)).toBeVisible();

    // Edit and remove the field; values fall back to the location circle.
    await crop.getByRole('button', { name: 'Edit field' }).click();
    await expect(crop.getByTestId('plot-area')).toBeVisible(); // the saved outline is loaded for editing
    await crop.getByRole('button', { name: 'Cancel' }).click();
    await crop.getByRole('button', { name: 'Remove' }).click();
    await crop.getByRole('button', { name: 'Yes, remove the field' }).click();
    await expect(crop.getByText('No field drawn.', { exact: false })).toBeVisible();
    await expect(crop.getByTestId('satellite-scope')).toContainText('Around your location');

    // 8. Interoperability: India and Brazil through the same contract, unsupported categories explicit.
    await page.goto('/about');
    const br = page.getByTestId('interop-BR');
    await expect(br.getByRole('row', { name: /Observations/ })).toContainText('production_statistic');
    await expect(br.getByRole('row', { name: /Risk signals/ })).toContainText('No real source');
    await expect(page.getByTestId('interop-IN').getByRole('row', { name: /Observations/ })).toContainText('Partners only');
  });

  test('too few clear pixels over the field is shown as not enough data, never a number', async ({ page }) => {
    await blockTiles(page);
    await withFarmProfile(page);
    await mockApi(page, { fieldCropHealth: { body: fixtureData.field_crop_health_insufficient } });
    await page.goto('/farm');
    const crop = page.locator('#crop');
    await expect(crop.getByTestId('satellite-unavailable')).toHaveText(/Too few cloud-free pixels over your field/);
    await expect(crop.getByTestId('ndvi-value')).toHaveCount(0);
  });

  test('evaluation is labelled as self-reported feedback with small groups hidden', async ({ page }) => {
    await mockApi(page);
    await page.goto('/dashboard');
    const panel = page.getByTestId('evaluation-panel');
    await expect(panel.getByRole('heading', { name: 'KrishiSathi self-reported feedback' })).toBeVisible();
    await expect(panel.getByText(/not a success rate, a yield effect or proof/)).toBeVisible();
    await expect(panel.getByTestId('eval-tier-high')).toContainText('‘Diagnosis wrong’ reports: 1 of 8');
    await expect(panel.getByTestId('eval-tier-low')).toContainText('Too few answers to show');
  });
});
