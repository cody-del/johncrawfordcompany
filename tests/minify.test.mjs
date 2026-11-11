import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readdirSync, readFileSync, rmSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { extname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { minifyAsset, minifySite } from '../scripts/minify-site.mjs';

// Netlify publishes _site/: dist/ with every .css and .js file minified (Semrush "unminified
// JavaScript and CSS files"). The minified files must behave exactly like the readable sources.
const dist = fileURLToPath(new URL('../dist/', import.meta.url));
const files = dir => readdirSync(dir).flatMap(name => {
  const path = join(dir, name);
  return statSync(path).isDirectory() ? files(path) : [path];
});

test('the minified app.js keeps its globals, form endpoints, Turnstile, Lead and GA4 events', async () => {
  const source = readFileSync(join(dist, 'app.js'), 'utf8');
  const app = await minifyAsset(source, '.js');
  assert.ok(app.length < source.length * 0.75, 'app.js should shrink');
  assert.doesNotMatch(app, /\n\s|\/\/ /, 'no indentation or comments left');
  // Top-level names stay as they are: the script is a classic script, so they are page globals.
  for (const name of ['menuToggle', 'navigation', 'TURNSTILE_LIVE_HOSTS', 'TURNSTILE_SITE_KEY', 'LEAD_MIN_FILL_MS', 'LEAD_CALL_US']) {
    assert.match(app, new RegExp(`\\b${name}=`), `${name} must keep its name`);
  }
  for (const text of ['"/api/lead"', '"/api/repair-upload"', '0x4AAAAAAF1MJ5a53NsFXu0h', 'window.onTurnstileLoad=',
    'api.js?render=explicit&onload=onTurnstileLoad', '"Thank you. We received your request', '??=']) {
    assert.ok(app.includes(text), `minified app.js lost ${text}`);
  }
  assert.deepEqual(app.match(/fbq\([^)]*\)/g), ['fbq("track","Lead")']);
  assert.deepEqual(app.match(/gtag\([^)]*\)/g), ['gtag("event","generate_lead")']);
  assert.ok(app.indexOf('fbq("track","Lead")') > app.indexOf('Thank you. We received your request'), 'Lead must still follow the confirmed thank-you');
});

test('every stylesheet minifies smaller and keeps its rules', async () => {
  const sheets = files(dist).filter(path => extname(path) === '.css');
  assert.ok(sheets.length >= 6);
  for (const path of sheets) {
    const source = readFileSync(path, 'utf8');
    const css = await minifyAsset(source, '.css');
    assert.ok(css.length < source.length, `${path} should shrink`);
    assert.doesNotMatch(css, /\n(?!$)|\/\*/, `${path}: no line breaks (but the last) or comments left`);
  }
  const styles = await minifyAsset(readFileSync(join(dist, 'styles.css'), 'utf8'), '.css');
  assert.match(styles, /border-radius:0 18px[;}]/, 'button shape kept (0 18px 0 18px, shortened)');
  const fonts = await minifyAsset(readFileSync(join(dist, 'assets/fonts.css'), 'utf8'), '.css');
  assert.ok(fonts.includes('url(brand-latin-0.woff2)'), 'font URLs stay relative to /assets/');
});

test('_site has exactly the files in dist, and only .css and .js files change', async () => {
  const out = mkdtempSync(join(tmpdir(), 'jc-site-'));
  try {
    const results = await minifySite(dist, out);
    assert.deepEqual(results.map(r => r.file).sort(), files(dist).filter(path => /\.(css|js)$/.test(path)).map(path => relative(dist, path)).sort());
    for (const path of files(dist)) {
      const rel = relative(dist, path);
      const same = readFileSync(path).equals(readFileSync(join(out, rel)));
      assert.equal(same, !/\.(css|js)$/.test(rel), `${rel}: ${same ? 'should be minified' : 'should be copied unchanged'}`);
    }
  } finally {
    rmSync(out, { recursive: true, force: true });
  }
});
