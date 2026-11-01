import { root, json, sha, fs, path } from './lib.mjs';

export async function buildTextbook() {
  const index = await json('textbook/textbook-index.json');
  if (index.generated_by !== 'learning-notes' || index.scope_root !== '..' || index.pages.length !== 13) throw new Error('Unexpected portable textbook index');
  async function copy(relative) {
    const source = path.resolve(root, relative);
    if (!source.startsWith(root + path.sep) || await fs.realpath(source) !== source) throw new Error(`Unsafe textbook resource: ${relative}`);
    const target = path.join(root, 'dist', relative);
    await fs.mkdir(path.dirname(target), { recursive: true });
    await fs.copyFile(source, target);
  }
  for (const page of index.pages) {
    const relative = `textbook/${page.path}`;
    if (sha(await fs.readFile(path.join(root, relative))) !== page.sha256) throw new Error(`Textbook page changed: ${relative}`);
    await copy(relative);
  }
  for (const source of index.sources) {
    if (!source.path.startsWith('materials/') || !source.path.endsWith('.pdf')) throw new Error('Unexpected textbook evidence path');
    if (sha(await fs.readFile(path.join(root, source.path))) !== source.sha256) throw new Error(`Textbook evidence changed: ${source.path}`);
    await copy(source.path);
  }
  for (const name of await fs.readdir(path.join(root, 'textbook/assets'))) {
    if (!/^[a-f0-9]{64}\.png$/.test(name)) throw new Error(`Unexpected textbook asset: ${name}`);
    if (sha(await fs.readFile(path.join(root, 'textbook/assets', name))) !== name.slice(0, 64)) throw new Error(`Textbook image changed: ${name}`);
    await copy(`textbook/assets/${name}`);
  }
  await copy('textbook/textbook-index.json');
}
