import assert from 'node:assert/strict';
import { root, json, sha, fs, path, parse, all, attr } from './lib.mjs';

const index = await json('textbook/textbook-index.json');
assert.equal(index.schema_version, 1);
assert.equal(index.scope_root, '..');
assert.equal(index.pages.length, 13);
const sourceDocs = new Map();
for (const page of index.pages) {
  const relative = `textbook/${page.path}`;
  const bytes = await fs.readFile(path.join(root, relative));
  assert.equal(sha(bytes), page.sha256, `stale textbook index: ${relative}`);
  assert.equal(sha(await fs.readFile(path.join(root, 'dist', relative))), page.sha256, `deployed textbook differs: ${relative}`);
  const doc = parse(bytes.toString('utf8'));
  sourceDocs.set(page.path, doc);
  const data = all(doc, n => attr(n, 'id') === 'ln-book-data')[0];
  assert(data, 'offline search index missing');
  const records = JSON.parse(data.childNodes.map(n => n.value || '').join('')).entries;
  assert.equal(records.length, index.sections.length, 'offline search does not cover every indexed section');
}
for (const source of index.sources) {
  assert.equal(sha(await fs.readFile(path.join(root, source.path))), source.sha256, `source fingerprint: ${source.path}`);
  assert.equal(sha(await fs.readFile(path.join(root, 'dist', source.path))), source.sha256, `deployed evidence: ${source.path}`);
}
for (const section of index.sections) {
  assert.equal(all(sourceDocs.get(section.path), n => attr(n, 'id') === section.anchor).length, 1, `missing textbook anchor: ${section.path}#${section.anchor}`);
  assert(section.source_ids.every(id => index.sources[id]), 'invalid evidence reference');
}
console.log(`Portable textbook checks passed: ${index.pages.length} pages, ${index.sections.length} sections, ${index.sources.length} source PDFs.`);
