import { readFile, access } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const html = await readFile(resolve(root, 'dist/index.html'), 'utf8');
const css = await readFile(resolve(root, 'dist/styles.css'), 'utf8');
const errors = [];
const requireThat = (condition, message) => { if (!condition) errors.push(message); };
const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);
requireThat(new Set(ids).size === ids.length, 'Duplicate HTML IDs');
requireThat((html.match(/<h1\b/g) || []).length === 1, 'Expected one H1');
requireThat(/Custom Window Treatments <span>in Los Angeles, California<\/span>/.test(html), 'Missing agreed homepage H1');
requireThat(/name="description" content="[^"]*custom window treatments in Los Angeles/i.test(html), 'Missing main topic in meta description');
requireThat(html.includes('name="robots" content="noindex, nofollow"'), 'Review version must stay noindex');
requireThat(!/href="#"/.test(html), 'Empty placeholder link');
requireThat(!/class="[^"]*(?:eyebrow|kicker)/.test(html), 'Eyebrow text is outside the brief');
requireThat(!/[↗→➜➝]/.test(html), 'Decorative arrows are outside the brief');
requireThat(css.includes('border-radius: 0 18px 0 18px'), 'Button shape does not match supplied reference');
for (const match of html.matchAll(/href="#([^"]+)"/g)) requireThat(ids.includes(match[1]), `Missing anchor: ${match[1]}`);
for (const match of html.matchAll(/(?:src|href)="((?:assets\/)[^"]+|styles\.css(?:\?[^"]*)?|app\.js(?:\?[^"]*)?)"/g)) {
  try { await access(resolve(root, 'dist', match[1].split(/[?#]/)[0])); }
  catch { errors.push(`Missing asset: ${match[1]}`); }
}
for (const match of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) {
  try { const schema = JSON.parse(match[1]); assert.equal(schema.telephone, '+1-818-884-5464'); }
  catch (error) { errors.push(`Invalid business structured data: ${error.message}`); }
}
if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
console.log('Homepage checks passed: metadata, anchors, assets, brand details and review indexing.');
