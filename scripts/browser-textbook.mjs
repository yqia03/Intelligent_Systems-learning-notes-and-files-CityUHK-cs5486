import assert from 'node:assert/strict';
import { chromium, webkit } from 'playwright';
import { json, args } from './lib.mjs';
import { startPreview } from './preview.mjs';

const options = args(), engine = options.engine || 'chromium';
if (!['chromium', 'webkit'].includes(engine)) throw new Error('Use --engine chromium or webkit');
const preview = options.url ? null : await startPreview({ port: 0 });
const base = options.url || preview.url;
const index = await json('textbook/textbook-index.json');
const browser = await ({ chromium, webkit }[engine]).launch();
const failures = [], errors = [], resources = [];
async function scenario(name, fn) {
  try { await fn(); console.log('PASS textbook', name); }
  catch (error) { failures.push(`${name}: ${error.message}`); console.error('FAIL textbook', name, error.message); }
}
function watch(page) {
  page.on('pageerror', error => errors.push(`${page.url()}: ${error.message}`));
  page.on('response', response => { if (response.url().startsWith(base) && response.status() >= 400) resources.push(`${response.status()} ${response.url()}`); });
  page.on('requestfailed', request => { if (request.url().startsWith(base) && !/ERR_ABORTED|cancelled|canceled|NS_BINDING_ABORTED/i.test(request.failure()?.errorText || '')) resources.push(`${request.failure()?.errorText} ${request.url()}`); });
}
async function visit(page, route) {
  const response = await page.goto(new URL(route, base).href, { waitUntil: 'networkidle' });
  assert(response && response.status() === 200, `page failed: ${route}`);
  await page.locator('#ln-menu').waitFor({ state: 'visible' });
}
try {
  for (const width of [1440, 390]) {
    const context = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
    const page = await context.newPage(); watch(page);
    for (const entry of index.pages) await scenario(`${entry.path} ${width}px`, async () => {
      await visit(page, `textbook/${entry.path}`);
      assert.equal(await page.locator('#ln-panel').evaluate(el => el.open), false);
      assert.equal(await page.locator('.textbook-body details[open]').count(), 0);
      await page.evaluate(async () => {
        const images = [...document.images];
        images.forEach(image => { image.loading = 'eager'; });
        await Promise.all(images.map(image => image.decode()));
        if (images.some(image => !image.complete || !image.naturalWidth)) throw new Error('Image is missing or has zero width');
      });
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), 'horizontal page overflow');
    });
    await scenario(`directory and keyboard ${width}px`, async () => {
      await visit(page, 'textbook/chapters/week01.html');
      const before = await page.locator('main').boundingBox();
      await page.locator('#ln-menu').focus();
      await page.keyboard.press('Enter');
      assert(await page.locator('#ln-panel').evaluate(el => el.open));
      const after = await page.locator('main').boundingBox();
      assert.equal(before.x, after.x); assert.equal(before.width, after.width);
      await page.locator('#ln-tab-course').click();
      assert.equal(await page.locator('#ln-tab-course').getAttribute('aria-selected'), 'true');
      assert(await page.locator('#ln-course a[href*="week02.html"]').isVisible());
      await page.locator('#ln-tab-chapter').click();
      assert.equal(await page.locator('#ln-tab-chapter').getAttribute('aria-selected'), 'true');
      await page.keyboard.press('Escape');
      assert(!(await page.locator('#ln-panel').evaluate(el => el.open)));
      assert(await page.locator('#ln-menu').evaluate(el => el === document.activeElement));
      await page.locator('#ln-menu').click();
      const anchor = page.locator('#ln-chapter a').first(), href = await anchor.getAttribute('href');
      await anchor.click();
      assert(!(await page.locator('#ln-panel').evaluate(el => el.open)));
      assert.equal(new URL(page.url()).hash, href);
      assert(await page.evaluate(hash => !!document.getElementById(decodeURIComponent(hash.slice(1))), href));
    });
    await context.close();
  }
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage(); watch(page);
  await scenario('offline search and cross-page anchor', async () => {
    await visit(page, 'textbook/index.html');
    await context.setOffline(true);
    await page.locator('#ln-find').click();
    await page.locator('#ln-search').fill('PSO');
    await page.locator('#ln-result-list a').first().waitFor({ state: 'visible' });
    const link = page.locator('#ln-result-list a[href*="week12.html"]').first();
    assert(await link.count(), 'PSO result should link to Week 12');
    const href = await link.getAttribute('href');
    await context.setOffline(false);
    await link.click();
    await page.waitForURL(url => url.pathname.endsWith('/textbook/chapters/week12.html') && !!url.hash);
    assert(await page.evaluate(() => !!document.getElementById(decodeURIComponent(location.hash.slice(1)))), `missing target ${href}`);
  });
  await scenario('rebased PDF source', async () => {
    await visit(page, 'textbook/chapters/week01.html');
    const pdf = page.locator('a[href*=".pdf"]').first();
    const href = await pdf.getAttribute('href'); assert(href, 'PDF citation missing');
    const target = new URL(href, page.url());
    assert(target.href.startsWith(base), `PDF citation escaped site base: ${target}`);
    const response = await context.request.get(target.href);
    assert.equal(response.status(), 200, `PDF citation ${target}`);
    assert((await response.body()).subarray(0, 5).toString() === '%PDF-', 'citation is not a PDF');
  });
  await context.close();
} finally {
  await browser.close();
  if (preview) await new Promise(resolve => preview.server.close(resolve));
}
if (failures.length || errors.length || resources.length) {
  console.error(JSON.stringify({ failures, errors, resources }, null, 2));
  process.exitCode = 1;
} else console.log(`Portable textbook browser checks passed (${engine}).`);
