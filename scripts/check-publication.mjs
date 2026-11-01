import assert from 'node:assert/strict';
import { root, fs, path, json, sha } from './lib.mjs';

async function files(directory) {
  const entries = await fs.readdir(path.join(root, directory), { withFileTypes: true });
  const groups = await Promise.all(entries.map(entry => {
    const name = `${directory}/${entry.name}`;
    assert(!entry.isSymbolicLink(), `Publication must not contain symlinks: ${name}`);
    return entry.isDirectory() ? files(name) : [name];
  }));
  return groups.flat();
}

const catalog = await json('materials/catalog.json');
const materialFiles = await files('materials');
const catalogPaths = catalog.files.map(entry => entry.path);
assert.equal(new Set(catalogPaths).size, catalogPaths.length, 'Duplicate material catalog entries');
assert.deepEqual(materialFiles.filter(name => name !== 'materials/catalog.json').sort(), [...catalogPaths].sort(), 'Every original material must be catalogued');
for (const entry of catalog.files) {
  assert(entry.path.startsWith('materials/') && !entry.path.split('/').includes('..'), 'Unsafe catalog path');
  const bytes = await fs.readFile(path.join(root, entry.path));
  assert.equal(bytes.length, entry.bytes, `Material size changed: ${entry.path}`);
  assert.equal(sha(bytes), entry.sha256, `Material checksum changed: ${entry.path}`);
}

const assignmentFiles = await files('assignments');
assert.deepEqual(assignmentFiles.filter(name => name.startsWith('assignments/assignment-3/')).sort(), [
  'assignments/assignment-3/brief/assignment-3.png',
], 'Assignment 3 is unfinished: publish only its original brief');
for (const name of [
  'assignments/assignment-1/solution/assignment-1-report.pdf',
  'assignments/assignment-2/solution/assignment-2-report.pdf',
  'assignments/assignment-2/solution/assignment-2-report.md',
  'assignments/assignment-2/code/run_assignment2.m',
  'assignments/assignment-2/data/comparison.csv',
  'assignments/assignment-2/data/training_samples.csv',
  'assignments/assignment-2/data/results.mat',
]) assert(assignmentFiles.includes(name), `Missing publication artifact: ${name}`);

for (const name of [...materialFiles, ...assignmentFiles]) {
  assert(!/(?:^|\/)\.DS_Store$|(?:^|\/)\.env(?:\.|$)|(?:^|\/)\.git\//.test(name), `Private/system file: ${name}`);
  if (!/\.(?:md|txt|json|html|tex|m|csv|py|sh)$/i.test(name)) continue;
  const content = await fs.readFile(path.join(root, name), 'utf8');
  assert(!/\/Users\/[^/\s]+\/|file:\/\/|\/private\/(?:tmp|var)\//i.test(content), `Personal local path in ${name}`);
  assert(!/-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{40,}/.test(content), `Credential pattern in ${name}`);
  if (name.startsWith('assignments/')) assert(!/\*\*(?:EID|Name|Student ID):?\*\*\s*\S/i.test(content), `Identity field in ${name}`);
}
console.log(`Publication checks passed: ${catalog.files.length} catalogued materials, ${assignmentFiles.length} assignment files; Assignment 3 brief only.`);
