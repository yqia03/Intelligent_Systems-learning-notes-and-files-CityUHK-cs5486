import { root, json, sha, fs, path } from './lib.mjs';

// The source is the course textbook beside the repository. The index is the
// inventory and integrity record; PDFs are mapped to already-catalogued copies.
const source = await fs.realpath(path.join(root, '../textbook'));
async function input(relative) {
  const target = path.resolve(source, relative);
  if (!target.startsWith(source + path.sep) || await fs.realpath(target) !== target || !(await fs.stat(target)).isFile()) throw new Error(`Unsafe textbook input: ${relative}`);
  return fs.readFile(target);
}
const index = JSON.parse(await input('textbook-index.json'));
if (index.schema_version !== 1 || index.generated_by !== 'learning-notes' || index.entry !== 'index.html' || !Array.isArray(index.pages) || !Array.isArray(index.sources)) throw new Error('Invalid textbook index');
const catalog = await json('materials/catalog.json');
function materialFor(sourcePath) {
  let matches = catalog.files.filter(f => f.source_relative_path === sourcePath && f.path.toLowerCase().endsWith('.pdf'));
  if (!matches.length) matches = catalog.files.filter(f => path.posix.basename(f.source_relative_path) === path.posix.basename(sourcePath) && f.path.toLowerCase().endsWith('.pdf'));
  if (matches.length !== 1) throw new Error(`Cannot uniquely map textbook source: ${sourcePath}`);
  return matches[0];
}
for (const item of index.sources) {
  const material = materialFor(item.path);
  if (sha(await fs.readFile(path.join(root, material.path))) !== item.sha256) throw new Error(`Source PDF hash mismatch: ${item.path}`);
  item.path = material.path;
}
index.scope_root = '..';
const pageNames = ['index.html', ...Array.from({length: 12}, (_, i) => `chapters/week${String(i + 1).padStart(2, '0')}.html`)];
if (index.pages.length !== pageNames.length || pageNames.some(p => index.pages.filter(x => x.path === p).length !== 1)) throw new Error('Unexpected textbook page inventory');
const encodePath = p => p.split('/').map(encodeURIComponent).join('/');
function rebase(value, current, destination, mapPdf) {
  if (!value || /^(?:#|https?:|mailto:|data:)/i.test(value)) return value;
  if (/^[a-z][a-z0-9+.-]*:/i.test(value) || value.startsWith('/') || value.includes('?')) throw new Error(`Unexpected URL: ${value}`);
  const [urlPath, fragment] = value.split('#');
  if (value.split('#').length > 2) throw new Error(`Unexpected URL fragment: ${value}`);
  const decoded = decodeURIComponent(urlPath);
  let target;
  if (mapPdf && /\.pdf$/i.test(decoded)) {
    const sourcePath = path.posix.normalize(path.posix.join('textbook', path.posix.dirname(current), decoded));
    if (sourcePath.startsWith('../') || sourcePath.startsWith('textbook/')) throw new Error(`Unexpected PDF path: ${value}`);
    target = materialFor(sourcePath).path;
  } else {
    target = path.posix.normalize(path.posix.join('textbook', path.posix.dirname(current), decoded));
    if (!target.startsWith('textbook/')) throw new Error(`Unexpected textbook URL: ${value}`);
  }
  const result = encodePath(path.posix.relative(path.posix.dirname(destination), target));
  return result + (fragment === undefined ? '' : '#' + fragment);
}
function transform(html, current, destination, mapPdf) {
  const marker = /<script id="ln-book-data" type="application\/json">([\s\S]*?)<\/script>/;
  const matches = [...html.matchAll(new RegExp(marker.source, 'g'))];
  if (matches.length !== 1) throw new Error(`Missing book data: ${current}`);
  html = html.replace(marker, (_, body) => {
    const data = JSON.parse(body);
    if (!Array.isArray(data.entries)) throw new Error(`Invalid book data: ${current}`);
    for (const entry of data.entries) entry.href = rebase(entry.href, current, destination, mapPdf);
    return `<script id="ln-book-data" type="application/json">${JSON.stringify(data).replace(/</g, '\\u003c')}</script>`;
  });
  html = html.replace(/\b(href|src)="([^"]*)"/g, (_, attr, url) => `${attr}="${rebase(url, current, destination, mapPdf)}"`);
  if (/\/Users\/|file:\/\/|\/private\//.test(html)) throw new Error(`Local path leaked: ${current}`);
  return html;
}
await fs.mkdir(path.join(root, 'textbook/chapters'), {recursive: true});
await fs.mkdir(path.join(root, 'textbook/assets'), {recursive: true});
for (const name of await fs.readdir(path.join(source, 'assets'))) {
  if (!/^[a-f0-9]{64}\.png$/.test(name)) throw new Error(`Unexpected asset: ${name}`);
  const bytes = await input(`assets/${name}`);
  if (sha(bytes) !== name.slice(0, 64)) throw new Error(`Asset hash mismatch: ${name}`);
  await fs.writeFile(path.join(root, 'textbook/assets', name), bytes);
}
for (const page of index.pages) {
  const bytes = await input(page.path);
  if (sha(bytes) !== page.sha256) throw new Error(`Page hash mismatch: ${page.path}`);
  const portable = transform(bytes.toString('utf8'), page.path, `textbook/${page.path}`, true);
  await fs.writeFile(path.join(root, 'textbook', page.path), portable);
  page.sha256 = sha(portable);
  const match = /^chapters\/week(\d\d)\.html$/.exec(page.path);
  if (match) {
    const target = `materials/study-notes/CS5486-Week${match[1]}-学习教材.html`;
    const entries = catalog.files.filter(f => f.path === target);
    if (entries.length !== 1) throw new Error(`Missing catalog record: ${target}`);
    const compatibility = transform(bytes.toString('utf8'), page.path, target, true);
    await fs.writeFile(path.join(root, target), compatibility);
    Object.assign(entries[0], { source_relative_path: `textbook/${page.path}`, bytes: Buffer.byteLength(compatibility), sha256: sha(compatibility), source_sha256: sha(bytes), sanitized: true, modified: true, purpose: 'Latest textbook chapter; companion images and navigation are in textbook/.' });
  }
}
await fs.writeFile(path.join(root, 'textbook/textbook-index.json'), JSON.stringify(index, null, 2) + '\n');
await fs.writeFile(path.join(root, 'materials/catalog.json'), JSON.stringify(catalog, null, 2) + '\n');
console.log(`Synchronized ${index.pages.length} pages, ${index.sources.length} source PDFs, and 12 compatibility copies.`);
