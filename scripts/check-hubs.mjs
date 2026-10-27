import { readFile, readdir, access } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const dist = resolve(root, 'dist');
const errors = [];
const requireThat = (condition, message) => { if (!condition) errors.push(message); };
const files = [];
async function walk(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const path = resolve(dir, entry.name);
    if (entry.isDirectory()) await walk(path);
    else if (entry.name.endsWith('.html')) files.push(path);
  }
}
await walk(dist);
const pages = new Map();
for (const file of files) {
  const route = '/' + file.slice(dist.length + 1).replace(/index\.html$/, '');
  const html = await readFile(file, 'utf8');
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]);
  pages.set(route, { html, ids, file });
}
const titles = new Set();
for (const [route, { html, ids }] of pages) {
  const title = html.match(/<title>([^<]+)<\/title>/)?.[1];
  requireThat(title && !titles.has(title), `${route}: missing or duplicate title`);
  titles.add(title);
  requireThat((html.match(/<h1\b/g) || []).length === 1, `${route}: expected one H1`);
  requireThat(ids.length === new Set(ids).size, `${route}: duplicate IDs`);
  requireThat(/<html lang="en">/.test(html), `${route}: missing document language`);
  requireThat(/name="description" content="[^"]+"/.test(html), `${route}: missing description`);
  requireThat(/name="robots" content="noindex, nofollow"/.test(html), `${route}: preserve review indexing`);
  requireThat(route.startsWith('/lp/') ? html.includes('aria-controls="landing-accessibility-dialog"') : html.includes('href="/accessibility/"'), `${route}: missing accessibility assistance`);
  requireThat(html.includes('22311 Ventura Blvd #101'), `${route}: wrong suite`);
  requireThat(!/Confirm before publishing|local shutter supplier|review_note|source_file|\/Users\//i.test(html), `${route}: private note exposed`);
  requireThat(!/href="#"/.test(html), `${route}: empty link`);
  for (const m of html.matchAll(/<img\b[^>]*>/g)) requireThat(/\balt="[^"]*"/.test(m[0]), `${route}: image without alt attribute`);
  for (const match of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const raw = match[1].replaceAll('&amp;', '&');
    if (/^(https?:|data:|mailto:|tel:)/.test(raw)) continue;
    const url = new URL(raw, `https://local.test${route}`);
    const targetRoute = url.pathname;
    if (pages.has(targetRoute)) {
      if (url.hash) requireThat(pages.get(targetRoute).ids.includes(decodeURIComponent(url.hash.slice(1))), `${route}: broken anchor ${raw}`);
    } else {
      try { await access(resolve(dist, '.' + targetRoute)); }
      catch { errors.push(`${route}: missing internal destination ${raw}`); }
    }
  }
  for (const match of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) {
    try { JSON.parse(match[1]); } catch { errors.push(`${route}: malformed structured data`); }
  }
}
const hubs = JSON.parse(await readFile(resolve(root, 'content/product-hubs.json'), 'utf8'));
for (const hub of hubs) {
  const html = pages.get(hub.slug)?.html || '';
  const escapedTitle = hub.title_tag.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#x27;');
  requireThat(html.includes(`<title>${escapedTitle}</title>`), `${hub.slug}: wrong title`);
  requireThat((html.match(/<img\b/g) || []).length >= 5, `${hub.slug}: product photography missing`);
  requireThat((html.match(/<details><summary>/g) || []).length === 3, `${hub.slug}: missing FAQs`);
  requireThat(html.includes('href="tel:+18188845464"') && html.includes('href="mailto:john@johncrawford.com'), `${hub.slug}: contact links missing`);
  requireThat(!/\bGallery\b/.test(html), `${hub.slug}: unconfirmed Gallery designation`);
  const introPreview = html.match(/<section class="section hub-introduction hub-intro-consultation"[\s\S]*?<\/section>/)?.[0] || '';
  const formPreview = introPreview.match(/<form\b[\s\S]*?<\/form>/)?.[0] || '';
  requireThat((formPreview.match(/\bdisabled\b/g) || []).length === 4 && !/data-netlify|action=|type="submit"/.test(formPreview), `${hub.slug}: design-only form must not accept submissions before GHL setup`);
  requireThat(/<\/section>\s*<section class="section hub-introduction hub-intro-consultation"/.test(html), `${hub.slug}: consultation section must follow the hero`);
}
requireThat(pages.get('/motorized-shades/')?.html.includes('The PowerView® App is required for programmed operation.'), 'Missing PowerView scheduling disclosure');
const expectedRoutes = ['/', ...hubs.map(hub => hub.slug), '/accessibility/', '/privacy/', '/lp/custom-window-treatments/', '/lp/motorized-shades/'];
requireThat(pages.size === expectedRoutes.length && expectedRoutes.every(route => pages.has(route)), `Expected the eight website routes and two campaign landing pages; found ${[...pages.keys()].join(', ')}`);
const showroomContent = html => html.match(/<section class="section about"[\s\S]*?<\/section>/)?.[0].replaceAll('src="assets/', 'src="/assets/').replace(/<div class="showroom-actions">[\s\S]*?<\/div>/, '');
const homeShowroom = showroomContent(pages.get('/')?.html || '');
for (const route of ['/lp/custom-window-treatments/', '/lp/motorized-shades/']) {
  const html = pages.get(route)?.html || '';
  requireThat(showroomContent(html) === homeShowroom, `${route}: preserve the approved Woodland Hills artwork, story, address and hours`);
  requireThat(html.includes('href="/landings.css?v=conversion-only-1"'), `${route}: scoped landing-page styles missing`);
  const form = html.match(/<form class="landing-form"[\s\S]*?<\/form>/)?.[0] || '';
  requireThat((form.match(/\bdisabled\b/g) || []).length === 4 && !/action=|data-netlify|type="submit"/.test(form), `${route}: do not accept leads before the form destination is confirmed`);
  requireThat(html.includes('The PowerView® App is required for programmed operation.'), `${route}: missing PowerView disclosure`);
  requireThat(!/class="main-navigation"|class="menu-toggle"|class="footer-nav"/.test(html), `${route}: browsing menus are outside the conversion-only brief`);
  requireThat(!/<iframe\b/.test(html), `${route}: embedded maps must not provide an off-page exit`);
  for (const anchor of html.matchAll(/<a\b[^>]*href="([^"]+)"[^>]*>/g)) {
    requireThat(['#main', '#contact', 'tel:+18188845464'].includes(anchor[1]), `${route}: non-conversion link ${anchor[1]}`);
  }
  for (const id of ['landing-privacy-dialog','landing-accessibility-dialog']) {
    requireThat(html.includes(`<dialog class="landing-info-dialog" id="${id}"`), `${route}: missing on-page information dialog ${id}`);
  }
}
if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
console.log(`All ${pages.size} HTML routes passed: headings, metadata, internal links, assets, contact details and public copy separation.`);
