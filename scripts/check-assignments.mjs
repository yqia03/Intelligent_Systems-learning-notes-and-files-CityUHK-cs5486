import assert from 'node:assert/strict';
import { root, json, read, write, all, attr, text, parse, fs, path, sha } from './lib.mjs';
import { prepareIndex, search } from '../web/search-core.js';
const source = await json('source/assignments/assignments.json');
const site = await json('dist/site-manifest.json');
const index = prepareIndex(await json('dist/search-index.json'));
const documents = [];
for (const a of source) {
  const html = await read(`dist/assignments/${a.id}/index.html`), doc = parse(html);
  documents.push(doc);
  assert(text(doc).includes(`Assignment ${a.number}`));
  assert(all(doc, n => attr(n, 'id') === 'requirements').length === 1);
  assert(all(doc, n => attr(n, 'id') === 'original').length === 1);
  assert.equal(site.assignments.find(r => r.id === a.id).completed, a.completed);
  const brief = `assignments/${a.id}/brief/${a.id}.png`;
  assert.equal(sha(await fs.readFile(path.join(root, brief))), sha(await fs.readFile(path.join(root, 'dist/assignments/files', a.id, 'brief', `${a.id}.png`))), 'brief must be copied unchanged');
  for (const q of [`Assignment ${a.number}`, `assignment${a.number}`, `作业${a.number}`]) {
    const result = search(index, q);
    assert(result.total > 0, `missing assignment search: ${q}`);
    assert(result.results.every(r => r.kind === 'assignment' && r.week === a.id), `assignment filter: ${q}`);
  }
  if (a.completed) {
    for (const file of a.downloads) {
      const target = path.join(root, 'dist/assignments/files', a.id, file.path);
      assert((await fs.stat(target)).isFile(), `missing download ${file.path}`);
      assert(all(doc, n => n.tagName === 'a' && attr(n, 'href') === site.base + `assignments/files/${a.id}/${file.path}`).length > 0);
    }
    for (const id of ['solution', 'results', 'downloads']) assert.equal(all(doc, n => attr(n, 'id') === id).length, 1);
  } else {
    assert(text(doc).includes('尚未完成，暂不发布处理过程'));
    assert.equal(all(doc, n => ['solution', 'results', 'downloads'].includes(attr(n, 'id'))).length, 0);
    assert.equal(all(doc, n => attr(n, 'download') !== undefined).length, 0);
    assert(!/解答报告|迭代表|最终向量|获胜神经元为/.test(html), 'unfinished assignment must not publish answers');
  }
}
const home = parse(await read('dist/index.html'));
assert.equal(all(home, n => attr(n, 'data-assignments-entry') !== undefined).length, 1);
assert.equal(all(parse(await read('dist/assignments/index.html')), n => attr(n, 'class') === 'assignment-card').length, 3);
assert.equal(all(documents[1], n => n.tagName === 'img').length, 4, 'A2 brief and original three figures');
assert(text(documents[0]).includes('IPython HTML 对象占位'));
const report = { passed: true, pages: 4, assignments: 3, publishedSolutions: 2, searchPassages: index.filter(r => r.kind === 'assignment').length };
await write('output/assignments-check.json', report);
console.log(JSON.stringify(report, null, 2));
