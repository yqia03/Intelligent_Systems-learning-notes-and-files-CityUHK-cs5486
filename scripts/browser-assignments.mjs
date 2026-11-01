import assert from 'node:assert/strict';
import { chromium, webkit } from 'playwright';
import { root, json, write, args, fs, path } from './lib.mjs';
import { startPreview } from './preview.mjs';
const options = args(), engine = options.engine || 'chromium';
if (!['chromium', 'webkit'].includes(engine)) throw new Error('Use --engine chromium or webkit');
const preview = options.url ? null : await startPreview({ port: 0 });
const base = options.url || preview.url;
const browser = await ({ chromium, webkit }[engine]).launch();
const assignments = await json('source/assignments/assignments.json');
const folder = `output/playwright/assignments-${options.url ? 'online' : 'local'}-${engine}`;
await fs.mkdir(path.join(root, folder), { recursive: true });
const report = { engine, base, scenarios: [], errors: [], resources: [] };
function watch(page) {
  page.on('pageerror', e => report.errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') report.errors.push(m.text()); });
  page.on('response', r => { if (r.url().startsWith(base) && r.status() >= 400) report.resources.push(`${r.status()} ${r.url()}`); });
}
async function visit(page, route, js = true) {
  const response = await page.goto(new URL(route, base).href, { waitUntil: 'networkidle' });
  assert.equal(response.status(), 200);
  if (js) await page.waitForFunction(() => document.querySelector('#site-theme').textContent !== '主题');
  await page.locator('.assignment-figure img').evaluateAll(async images => {
    images.forEach(image => { image.loading = 'eager'; });
    await Promise.all(images.map(image => image.decode()));
  });
}
async function run(name, action) {
  try { await action(); report.scenarios.push(name); console.log('PASS assignments', name); }
  catch (error) { report.errors.push(`${name}: ${error.message}`); console.log('FAIL assignments', name, error.message); }
}
try {
  for (const width of [1440, 834, 390]) for (const theme of ['light', 'dark']) {
    const context = await browser.newContext({ viewport: { width, height: 960 }, reducedMotion: 'reduce' });
    await context.addInitScript(t => localStorage.setItem('cs5486:theme', t), theme);
    const page = await context.newPage(); watch(page);
    await run(`${width} ${theme} index and all assignments`, async () => {
      await visit(page, 'assignments/');
      assert.equal(await page.locator('.assignment-card').count(), 3);
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
      await page.screenshot({ path: path.join(root, folder, `index-${width}-${theme}.png`) });
      for (const a of assignments) {
        await visit(page, `assignments/${a.id}/`);
        assert.equal(await page.locator('h1').count(), 1);
        assert.equal(await page.locator('.site-assignment-entry[aria-current="page"]').count(), 1);
        assert.equal(await page.locator('.assignment-figure img').count(), a.number === 2 ? 4 : 1);
        assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), `${a.id} page overflow`);
        assert.equal(await page.locator('html').getAttribute('data-theme'), theme);
        await page.screenshot({ path: path.join(root, folder, `${a.id}-${width}-${theme}.png`) });
        if (a.completed) {
          await page.locator('#results').scrollIntoViewIfNeeded();
          await page.screenshot({ path: path.join(root, folder, `${a.id}-results-${width}-${theme}.png`) });
        } else {
          assert.equal(await page.locator('[download]').count(), 0);
          assert((await page.locator('#publication-status').textContent()).includes('尚未完成'));
        }
      }
    });
    await context.close();
  }
  const context = await browser.newContext({ viewport: { width: 390, height: 960 }, reducedMotion: 'reduce', acceptDownloads: true });
  const page = await context.newPage(); watch(page);
  await run('home entry, Assignment search labels and direct link', async () => {
    await visit(page, '');
    await page.locator('[data-assignments-entry]').click();
    await page.waitForURL('**/assignments/');
    await page.locator('.assignment-card').nth(1).click();
    await page.waitForURL('**/assignments/assignment-2/');
    await page.locator('#site-search-open').click();
    await page.locator('#site-search-input').fill('assignment2 RMSE');
    await page.locator('#site-search-form').evaluate(form => form.requestSubmit());
    await page.waitForFunction(() => document.querySelector('#site-search-status').textContent.startsWith('找到'));
    assert((await page.locator('.site-result-label').first().textContent()).includes('Assignment 2'));
    assert(!(await page.locator('.site-result-label').first().textContent()).includes('第 assignment'));
    await page.locator('#site-search-results a').first().click();
    await page.waitForLoadState('networkidle');
    assert(new URL(page.url()).pathname.endsWith('/assignments/assignment-2/'));
    assert(new URL(page.url()).hash);
    await page.reload({ waitUntil: 'networkidle' });
    assert.equal(await page.locator('h1').count(), 1);
  });
  await run('published report download resolves', async () => {
    await visit(page, 'assignments/assignment-2/');
    const link = page.locator('[download][href$="assignment-2-report.pdf"]');
    const response = await context.request.get(new URL(await link.getAttribute('href'), base).href);
    assert.equal(response.status(), 200);
    assert((await response.body()).subarray(0, 5).equals(Buffer.from('%PDF-')));
  });
  await context.close();
  const noJS = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 960 } });
  const plain = await noJS.newPage(); watch(plain);
  await run('all assignment pages and original figures work without JavaScript', async () => {
    await visit(plain, 'assignments/', false);
    for (const a of assignments) {
      await visit(plain, `assignments/${a.id}/`, false);
      assert(await plain.locator('#requirements').isVisible());
      assert(await plain.locator('.assignment-brief img').isVisible());
      if (a.completed) assert(await plain.locator('#solution').isVisible());
      else assert(await plain.locator('#publication-status').isVisible());
      assert(await plain.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    }
  });
  await noJS.close();
} finally {
  await browser.close();
  if (preview) await new Promise(resolve => preview.server.close(resolve));
}
report.passed = report.errors.length === 0 && report.resources.length === 0;
await write(`${folder}/report.json`, report);
console.log(JSON.stringify(report, null, 2));
if (!report.passed) process.exitCode = 1;
