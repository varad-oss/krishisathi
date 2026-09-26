import path from 'node:path';
import { expect, test } from '@playwright/test';
import { fixtureData, mockApi, unavailable, withFarmProfile } from './mock-api';

const leaf = path.join(__dirname, 'fixtures', 'leaf.jpg');
const notImage = path.join(__dirname, 'fixtures', 'not-an-image.txt');

test.describe('Landing → farm dashboard → advisory', () => {
  test('first visit sets up the farm, shows today, weather, alerts and soil, then asks the advisor', async ({ page }) => {
    await mockApi(page);
    await page.goto('/');
    await expect(page.getByRole('heading', { level: 1 })).toContainText('agricultural intelligence');
    await page.getByRole('link', { name: 'Open farmer dashboard' }).first().click();

    await expect(page.getByRole('heading', { name: 'Set up your farm' })).toBeVisible();
    await page.getByLabel('Choose a nearby district').selectOption('pune');
    await page.getByLabel('Main crop').selectOption('Tomato');
    await page.getByRole('button', { name: 'Save' }).click();

    const today = page.locator('#today');
    await expect(today.getByText('Pune, Maharashtra')).toBeVisible();
    // The highest-severity item leads the day: a nearby high-severity disease cluster (warning)
    // outranks the 41.2 °C heat forecast (watch).
    await expect(today.getByText('Late Blight reported nearby')).toBeVisible();
    await expect(today.getByText('Warning')).toBeVisible();
    await expect(page.locator('#alerts').getByText(/High heat/)).toBeVisible();

    const weather = page.locator('#weather');
    await expect(weather.getByText('Model estimate').first()).toBeVisible();
    await expect(weather.getByText('Forecast').first()).toBeVisible();
    await expect(weather.getByRole('link', { name: 'Open-Meteo' })).toBeVisible();

    const alerts = page.locator('#alerts');
    await expect(alerts.getByText('Late Blight reported nearby')).toBeVisible();
    await alerts.getByText('Late Blight reported nearby').click();
    await expect(alerts.getByText(/not lab-confirmed/)).toBeVisible();

    const soil = page.locator('#soil');
    await expect(soil.getByText('Organic carbon', { exact: true })).toBeVisible();
    await expect(soil.getByText(/not a test of your field/)).toBeVisible();
    await expect(soil.getByText('Build soil organic matter')).toBeVisible();

    // Satellite is not configured: honest unavailable state, no numbers.
    await expect(page.locator('#crop').getByText(/not connected on this server/)).toBeVisible();

    await page.getByRole('link', { name: 'Ask a question' }).click();
    await expect(page).toHaveURL(/\/advisor/);
    await page.getByRole('button', { name: 'Should I irrigate this week?' }).click();
    await expect(page.getByText('hold irrigation today')).toBeVisible();
    await expect(page.getByText('Weather · used')).toBeVisible();
    await expect(page.getByText(/AI-generated advice/)).toBeVisible();
  });

  test('a failing weather service degrades only the weather panels and can be retried', async ({ page }) => {
    await withFarmProfile(page);
    await mockApi(page, { conditions: { ...unavailable('Weather data is temporarily unavailable.'), times: 1 } });
    await page.goto('/farm');

    const weather = page.locator('#weather');
    await expect(weather.getByRole('alert')).toContainText('temporarily unavailable');
    // Unrelated panels still render real data.
    await expect(page.locator('#soil').getByText('Organic carbon', { exact: true })).toBeVisible();
    await expect(page.locator('#alerts').getByText('Late Blight reported nearby')).toBeVisible();

    await weather.getByRole('button', { name: 'Try again' }).click();
    await expect(weather.getByText('7-day forecast')).toBeVisible();
    await expect(weather.getByRole('alert')).toHaveCount(0);
  });

  test('advisor shows an explicit, retryable error instead of an answer when AI fails', async ({ page }) => {
    await withFarmProfile(page);
    await mockApi(page, { advisory: { ...unavailable('Advisory model is temporarily unavailable.'), times: 1 } });
    await page.goto('/advisor');
    await page.getByLabel('Type your question…').fill('Is it a good time to sow?');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByRole('main').getByRole('alert')).toContainText('No answer could be generated');
    await page.getByRole('button', { name: 'Try again' }).click();
    await expect(page.getByText('hold irrigation today')).toBeVisible();
  });
});

test.describe('Landing → Diagnose → Result', () => {
  test('uploads a photo and shows diagnosis, certainty, verified reference and disclaimer', async ({ page }) => {
    await withFarmProfile(page);
    await mockApi(page);
    await page.goto('/');
    await page.getByRole('link', { name: 'Diagnose a crop' }).first().click();
    await expect(page.getByRole('heading', { name: 'Crop disease check' })).toBeVisible();

    await page.getByRole('main').getByTestId('file-input').setInputFiles(leaf);
    await expect(page.getByAltText('Selected photo')).toBeVisible();
    await page.getByRole('button', { name: 'Check photo' }).click();

    await expect(page.getByRole('heading', { name: 'Possible Late blight' })).toBeVisible();
    await expect(page.getByText('Certainty: Moderate')).toBeVisible();
    await expect(page.getByText('What the AI saw')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Verified reference', exact: true })).toBeVisible();
    await expect(page.getByText(/ICAR/).first()).toBeVisible();
    await expect(page.getByText(/Confirm the product, dose/)).toBeVisible();
    await expect(page.getByText(/not a substitute for an agronomist/).first()).toBeVisible();
    await expect(page.getByText('%')).toHaveCount(0); // no fabricated confidence percentage

    await page.getByRole('button', { name: 'Can this spread to nearby plants?' }).click();
    await expect(page.getByText('hold irrigation today')).toBeVisible();
  });

  test('low-certainty result warns the farmer and shows no chemical options', async ({ page }) => {
    await mockApi(page, { diagnose: { body: fixtureData.diagnosis_uncertain } });
    await page.goto('/diagnose');
    await page.getByRole('main').getByTestId('file-input').setInputFiles(leaf);
    await page.getByRole('button', { name: 'Check photo' }).click();
    await expect(page.getByRole('heading', { name: 'Could not identify the cause' })).toBeVisible();
    await expect(page.getByText(/Do not apply chemicals based on this/)).toBeVisible();
    await expect(page.getByText(/Photo quality is poor/)).toBeVisible();
    await expect(page.getByText('Chemical options (verified reference)')).toHaveCount(0);
  });

  test('rejects unsupported files before upload', async ({ page }) => {
    await mockApi(page);
    await page.goto('/diagnose');
    await page.getByRole('main').getByTestId('file-input').setInputFiles(notImage);
    await expect(page.getByText('Please choose a JPEG, PNG or WebP image.')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Check photo' })).toBeDisabled();
  });

  test('analysis failure never shows a result and can be retried', async ({ page }) => {
    await mockApi(page, { diagnose: { ...unavailable('Diagnostic model is temporarily unavailable.'), times: 1 } });
    await page.goto('/diagnose');
    await page.getByRole('main').getByTestId('file-input').setInputFiles(leaf);
    await page.getByRole('button', { name: 'Check photo' }).click();
    await expect(page.getByRole('main').getByRole('alert')).toContainText('The photo could not be checked');
    await expect(page.getByRole('heading', { name: /Possible/ })).toHaveCount(0);
    await page.getByRole('button', { name: 'Try again' }).click();
    await expect(page.getByRole('heading', { name: 'Possible Late blight' })).toBeVisible();
  });
});

test.describe('Policymaker dashboard', () => {
  test('shows aggregated indicators, clusters, forecast risk and data limitations', async ({ page }) => {
    await mockApi(page);
    await page.goto('/dashboard');
    await expect(page.getByRole('heading', { name: 'Agricultural intelligence' })).toBeVisible();
    await expect(page.getByText('Photo diagnoses (all time)')).toBeVisible();
    await expect(page.getByRole('cell', { name: 'Late Blight' })).toBeVisible();
    await expect(page.getByText('Data limitations')).toBeVisible();
    await expect(page.getByText(/Regional satellite crop-health aggregation is not available/).first()).toBeVisible();
    await expect(page.getByText(/Farmers reached/i)).toHaveCount(0);

    await page.getByLabel('State', { exact: true }).selectOption('KA');
    await expect(page.getByText(/Late blight clusters reported near Pune/)).toBeVisible();

    await page.getByRole('button', { name: 'Generate briefing' }).click();
    await expect(page.getByText('Ask KVK staff to verify the Pune cluster in the field.')).toBeVisible();
    await expect(page.getByText('AI-generated summary')).toBeVisible();
  });

  test('a failing stats service does not blank the rest of the dashboard', async ({ page }) => {
    await mockApi(page, { stats: unavailable() });
    await page.goto('/dashboard');
    await expect(page.getByRole('main').getByRole('alert').first()).toContainText('temporarily unavailable');
    await expect(page.getByRole('cell', { name: 'Late Blight' })).toBeVisible();
  });
});

test.describe('Language', () => {
  test('switching language keeps the current workflow and localizes numbers', async ({ page }) => {
    await withFarmProfile(page);
    await mockApi(page);
    await page.goto('/farm');
    await expect(page.locator('#today').getByText('Pune, Maharashtra')).toBeVisible();

    await page.getByLabel('Language').selectOption('hi');
    await expect(page.locator('html')).toHaveAttribute('lang', 'hi');
    await expect(page).toHaveURL(/\/farm/);
    await expect(page.getByRole('heading', { name: 'मेरा खेत' })).toBeVisible();
    // Devanagari digits for the current temperature (29.4 °C).
    await expect(page.locator('#today')).toContainText('२९.४');

    await page.reload();
    await expect(page.locator('html')).toHaveAttribute('lang', 'hi');
  });
});
