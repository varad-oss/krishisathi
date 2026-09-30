import path from 'node:path';
import { expect, test, type Route } from '@playwright/test';
import { MOCK_API } from '../playwright.config';
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
    // The engine's top action leads the day: humid weather plus a nearby Late Blight cluster make disease the
    // highest risk, ahead of the 41.2 °C heat forecast.
    await expect(today.getByText('Check your crop for disease this week')).toBeVisible();
    await expect(today.getByText(/Because humid, mild weather favours fungal disease and farmers nearby reported/)).toBeVisible();
    await today.getByText('Why this recommendation?').click();
    await expect(today.getByText(/4 farmer photo diagnoses of Late Blight within about 10 km/)).toBeVisible();
    await expect(today.getByText('AI-classified farmer reports').first()).toBeVisible();
    // Data quality: satellite is honestly not connected, soil is a model estimate.
    await expect(today.getByRole('region', { name: 'Data used today' }).getByText('Not connected')).toBeVisible();

    const risks = page.locator('#risks');
    await expect(risks.getByText('Heat stress')).toBeVisible();
    await expect(risks.getByText('Not assessed: no pest monitoring data is connected.')).toBeVisible();
    await risks.getByText('Heat stress').click();
    await expect(risks.getByText(/Highest temperature .*41\.2°C/)).toBeVisible();

    const weather = page.locator('#weather');
    await expect(weather.getByText('Model estimate').first()).toBeVisible();
    await expect(weather.getByText('Forecast').first()).toBeVisible();
    await expect(weather.getByRole('link', { name: 'Open-Meteo' })).toBeVisible();

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
    await expect(page.locator('#risks').getByText('Check your crop for disease this week')).toBeVisible();

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

test.describe('Farm digital twin', () => {
  test('the farm is registered, the farmer reports follow-through, and history shows it', async ({ page }) => {
    await withFarmProfile(page);
    await mockApi(page);
    await page.goto('/farm');

    const today = page.locator('#today');
    await expect(today.getByText('Check your crop for disease this week')).toBeVisible();
    await expect(today.getByText('Did you follow this recommendation?')).toBeVisible();
    await today.getByRole('button', { name: 'Yes', exact: true }).click();
    await expect(today.getByText(/tell us how the crop responded under Farm history/)).toBeVisible();

    const history = page.locator('#history');
    await expect(history.getByRole('heading', { name: 'Farm history' })).toBeVisible();
    await expect(history.getByText('You said: Yes')).toBeVisible();
    await expect(history.getByText('How did the crop respond?')).toBeVisible();
    await expect(history.getByText(/not proof that the advice worked/).first()).toBeVisible();
    // The token is stored on the device so the record survives reloads.
    expect(await page.evaluate(() => JSON.parse(localStorage.getItem('krishi_farm_twin') ?? 'null')?.token)).toBe('e2e-farm-token');
  });

  test('without a server record the farm page still works and says why history is missing', async ({ page }) => {
    await withFarmProfile(page);
    await mockApi(page, { farmCreate: unavailable() });
    await page.goto('/farm');
    await expect(page.locator('#today').getByText('Check your crop for disease this week')).toBeVisible();
    await expect(page.locator('#history').getByText(/starts once your farm is saved on the server/)).toBeVisible();
  });
});

test.describe('Regenerative plan and crop options', () => {
  test('practices are placed on the crop cycle and adoption is saved to the farm history', async ({ page }) => {
    await withFarmProfile(page);
    await mockApi(page);
    await page.goto('/farm');

    const soil = page.locator('#soil');
    await expect(soil.getByRole('heading', { name: 'This season' })).toBeVisible();
    await expect(soil.getByRole('heading', { name: 'Next season' })).toBeVisible();
    await expect(soil.getByRole('heading', { name: 'Long-term habits' })).toBeVisible();
    await expect(soil.getByText(/Add your sowing date in the farm profile/)).toBeVisible();

    const coverCrop = soil.locator('details', { hasText: 'Grow a cover crop' });
    await coverCrop.locator('summary').click();
    await expect(coverCrop.getByText('After harvest').first()).toBeVisible();
    await expect(coverCrop.getByText('Based on your soil data')).toBeVisible();
    const saved = page.waitForRequest((r) => /\/api\/farms\/[^/]+\/practices$/.test(r.url()) && r.method() === 'POST');
    await coverCrop.getByRole('button', { name: 'Yes', exact: true }).click();
    expect((await saved).postDataJSON()).toEqual({ practice: 'cover_crop', status: 'adopted' });
    await expect(coverCrop.getByText('Saved in your farm history: Yes')).toBeVisible();
  });

  test('crop options compare verified facts, never rank, and say prices are unavailable', async ({ page }) => {
    await withFarmProfile(page);
    await mockApi(page);
    await page.goto('/farm');

    const options = page.locator('#options');
    await expect(options.getByRole('heading', { name: 'Crop options near you' })).toBeVisible();
    await expect(options.getByText(/This is not a ranking/)).toBeVisible();
    const tomato = options.getByRole('row', { name: /Tomato/ });
    await expect(tomato.getByText('Your crop')).toBeVisible();
    await expect(tomato.getByText('400–800 mm')).toBeVisible();
    await expect(tomato.getByText('about 135 days')).toBeVisible();
    await expect(options.getByText(/no verified source for them yet/)).toBeVisible();
    await expect(options.getByRole('link', { name: /FAO Irrigation Water Management/ })).toBeVisible();
  });

  test('crop options failure is explicit and does not hide the rest of the farm page', async ({ page }) => {
    await withFarmProfile(page);
    await mockApi(page, { cropOptions: unavailable() });
    await page.goto('/farm');
    await expect(page.locator('#options').getByText('Crop options could not be loaded.')).toBeVisible();
    await expect(page.locator('#soil').getByRole('heading', { name: 'This season' })).toBeVisible();
  });
});

test.describe('Something is wrong with my crop', () => {
  test('each problem goes to the right existing tool; the advisor starts with an editable question', async ({ page }) => {
    await withFarmProfile(page);
    await mockApi(page);
    await page.goto('/problem');
    await expect(page.getByRole('heading', { name: 'Something is wrong with my crop' })).toBeVisible();
    await expect(page.getByRole('link', { name: /Take a photo/ })).toHaveAttribute('href', '/diagnose');
    await expect(page.getByRole('link', { name: /Weather problem/ })).toHaveAttribute('href', '/farm#weather');
    await expect(page.getByRole('link', { name: /Soil concern/ })).toHaveAttribute('href', '/farm#soil');

    let asked = false;
    page.on('request', (r) => {
      if (/\/api\/advisory$/.test(r.url())) asked = true;
    });
    await page.getByRole('link', { name: /Crop is not growing well/ }).click();
    await expect(page.getByRole('heading', { name: 'Ask the advisor' })).toBeVisible();
    await expect(page.getByRole('textbox')).toHaveValue(/My crop is not growing well/);
    expect(asked).toBe(false); // prefilled, never sent on the farmer's behalf
  });
});

test.describe('Offline', () => {
  test('saved copies are shown only as dated, labelled copies, and answers are queued until reconnecting', async ({ page, context }) => {
    await withFarmProfile(page);
    await mockApi(page);
    await page.goto('/farm');
    await expect(page.locator('#options').getByText('400–800 mm')).toBeVisible(); // loaded and saved online
    // Client-side navigation (top menu on desktop, bottom bar or footer on phones).
    await page.locator('a[href="/about"]:visible').first().click();
    await expect(page).toHaveURL(/\/about/);

    // Mocked routes answer before the network, so drop API calls explicitly while offline.
    const dropped = (route: Route) => route.abort('internetdisconnected');
    await page.route(`${MOCK_API}/**`, dropped);
    await context.setOffline(true);
    await expect(page.getByRole('status').filter({ hasText: 'You are offline' })).toBeVisible();
    await page.locator('a[href="/farm"]:visible').first().click();
    const options = page.locator('#options');
    await expect(options.getByText('400–800 mm')).toBeVisible(); // the saved copy…
    await expect(options.getByText(/You are offline/)).toBeVisible(); // …with why it is not current
    await expect(options.getByText(/Last successfully updated/)).toBeVisible();

    const coverCrop = page.locator('#soil details', { hasText: 'Grow a cover crop' });
    await coverCrop.locator('summary').click();
    await coverCrop.getByRole('button', { name: 'Yes', exact: true }).click();
    await expect(coverCrop.getByText(/will be sent when you are back online/)).toBeVisible();

    const sent = page.waitForRequest((r) => /\/practices$/.test(r.url()) && r.method() === 'POST');
    await page.unroute(`${MOCK_API}/**`, dropped);
    await context.setOffline(false);
    expect((await sent).postDataJSON()).toEqual({ practice: 'cover_crop', status: 'adopted' });
    await expect(page.getByRole('status').filter({ hasText: 'You are offline' })).toHaveCount(0);
  });
});

test.describe('Landing → Diagnose → Result', () => {
  test('uploads a photo and shows diagnosis, certainty, verified reference and disclaimer', async ({ page }) => {
    await withFarmProfile(page);
    await mockApi(page);
    await page.goto('/');
    // The farmer starts from "something is wrong", not from a module name.
    await page.getByRole('link', { name: 'Something is wrong with my crop' }).first().click();
    await expect(page.getByRole('heading', { name: 'Something is wrong with my crop' })).toBeVisible();
    await page.getByRole('link', { name: /Take a photo/ }).click();
    await expect(page.getByRole('heading', { name: 'Crop disease check' })).toBeVisible();

    await page.getByRole('main').getByTestId('file-input').setInputFiles(leaf);
    await expect(page.getByAltText('Selected photo')).toBeVisible();
    await page.getByRole('button', { name: 'Check photo' }).click();

    await expect(page.getByRole('heading', { name: 'Possible Late blight' })).toBeVisible();
    await expect(page.getByRole('img', { name: 'Certainty: Moderate' })).toBeVisible();
    await expect(page.getByText('What the AI saw')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Verified reference', exact: true })).toBeVisible();
    await expect(page.getByText(/ICAR/).first()).toBeVisible();
    await expect(page.getByText(/Confirm the product, dose/)).toBeVisible();
    await expect(page.getByText(/not a substitute for an agronomist/).first()).toBeVisible();
    await expect(page.getByText('%')).toHaveCount(0); // no fabricated confidence percentage
    // Moderate certainty + high severity: cautious guidance, a differential and an expert referral.
    await expect(page.getByText(/Act with care: this result is not certain/)).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Possible causes' })).toBeVisible();
    await expect(page.getByText('Early blight')).toBeVisible();
    const expert = page.getByRole('region', { name: 'Ask an agricultural expert' });
    await expect(expert.getByText('Your district KVK: KVK Pune (Pune)')).toBeVisible();
    await expect(expert.getByRole('link', { name: 'Share case on WhatsApp' })).toHaveAttribute('href', /AI%20result%2C%20not%20confirmed/);
    await expect(expert.getByText(/The photo is not included/)).toBeVisible();
    // The farm record links the check, so the farmer can later report whether it was right.
    await expect(page.getByText('Did you follow this recommendation?')).toBeVisible();

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
    await expect(page.getByRole('region', { name: 'Ask an agricultural expert' }).getByText(/could not identify the problem with enough certainty/)).toBeVisible();
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

test.describe('Policymaker early warning', () => {
  test('signals show trend, confidence, observations and geography; thin data and missing satellite data are explicit', async ({ page }) => {
    await mockApi(page);
    await page.goto('/dashboard');
    const ew = page.locator('#early-warning');
    await expect(ew.getByRole('heading', { name: 'Early warning' })).toBeVisible();
    await expect(ew.getByText(/Only 12 confident, located reports in the last 14 days/)).toBeVisible();

    const disease = ew.getByRole('region', { name: 'Disease signals' });
    await expect(disease.getByText('Late blight')).toBeVisible();
    await expect(disease.getByText('Rising')).toBeVisible();
    await expect(disease.getByText('6 reports this week, 2 the week before')).toBeVisible();
    await expect(disease.getByText('Confidence: Moderate')).toBeVisible();
    await expect(disease.getByText('Wheat rust')).toBeVisible();
    await expect(disease.getByText('New this week')).toBeVisible();
    await expect(disease.getByText(/1 weaker signals with fewer than 3 reports are not shown/)).toBeVisible();

    await expect(ew.getByRole('region', { name: 'Weather threats' }).getByText('Punjab')).toBeVisible();
    await expect(ew.getByRole('region', { name: 'Crop-health anomalies' }).getByText(/not connected on this server/)).toBeVisible();

    // Every visualization states period, geography, observations, source and limits.
    for (const label of ['Period:', 'Geography:', 'Observations:', 'Source:', 'Limits:']) await expect(ew.getByText(label, { exact: true })).toBeVisible();
    await expect(ew.getByText(/0\.5° grid cells/)).toBeVisible();
    await expect(page.getByText(/Cluster centres rounded to about 11 km/)).toBeVisible();
    await expect(page.getByText(/One reference point per state, not statewide/).first()).toBeVisible();
  });

  test('early-warning failure is explicit and the rest of the dashboard still loads', async ({ page }) => {
    await mockApi(page, { earlyWarning: unavailable() });
    await page.goto('/dashboard');
    await expect(page.locator('#early-warning').getByRole('alert')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Disease clusters' })).toBeVisible();
  });
});
