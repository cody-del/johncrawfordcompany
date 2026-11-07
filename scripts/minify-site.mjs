// Copy dist/ to _site/ and minify every .css and .js file in the copy.
//
// dist/ stays the readable, committed source (the checks and tests read it). Netlify publishes
// _site/, so visitors get the minified files at the same addresses, including the ?v= versions
// the pages already use. Everything else (HTML, images, _redirects, robots.txt...) is copied as is.
//
//   node scripts/minify-site.mjs            build _site/ from dist/
//   node scripts/minify-site.mjs src out    build another folder (used by the tests)
import { transform } from 'esbuild';
import { cpSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { extname, join, relative, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Script } from 'node:vm';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');

// Keep the syntax the sources already use (app.js uses ?., ?? and ??=, which is ES2021), so
// minifying never rewrites code into newer syntax than the source, and never lowers it either.
// The CSS target likewise stops esbuild from merging longhands into newer shorthands.
const JS_TARGET = 'es2021';
const CSS_TARGET = ['chrome90', 'edge90', 'firefox90', 'safari14', 'ios14'];

export async function minifyAsset(code, ext) {
  if (ext === '.js') {
    // No `format`: esbuild keeps top-level names, so the classic (non-module) script behaves the same.
    const { code: out } = await transform(code, { loader: 'js', minify: true, target: JS_TARGET, legalComments: 'none', charset: 'utf8' });
    new Script(out); // throws if the minified script doesn't parse
    return out;
  }
  if (ext === '.css') {
    const { code: out } = await transform(code, { loader: 'css', minify: true, target: CSS_TARGET, legalComments: 'none', charset: 'utf8' });
    return out;
  }
  throw new Error(`Not a .css or .js file: ${ext}`);
}

const files = dir => readdirSync(dir).flatMap(name => {
  const path = join(dir, name);
  return statSync(path).isDirectory() ? files(path) : [path];
});

export async function minifySite(src = join(root, 'dist'), out = join(root, '_site')) {
  rmSync(out, { recursive: true, force: true });
  cpSync(src, out, { recursive: true });
  const results = [];
  for (const path of files(out)) {
    const ext = extname(path);
    if (ext !== '.css' && ext !== '.js') continue;
    const before = readFileSync(path, 'utf8');
    const after = await minifyAsset(before, ext);
    writeFileSync(path, after);
    results.push({ file: relative(out, path), before: Buffer.byteLength(before), after: Buffer.byteLength(after) });
  }
  // Every source file must be published, and nothing else may change.
  const srcFiles = files(src).map(path => relative(src, path)).sort();
  const outFiles = files(out).map(path => relative(out, path)).sort();
  if (srcFiles.join('\n') !== outFiles.join('\n')) throw new Error('_site does not contain exactly the files in dist');
  if (!results.length) throw new Error('No .css or .js files found to minify');
  return results;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [src, out] = process.argv.slice(2);
  const results = await minifySite(src && resolve(src), out && resolve(out));
  let before = 0, after = 0;
  for (const r of results) {
    before += r.before; after += r.after;
    console.log(`${r.file}: ${r.before} → ${r.after} bytes`);
  }
  console.log(`Minified ${results.length} files: ${before} → ${after} bytes (${Math.round((1 - after / before) * 100)}% smaller).`);
}
