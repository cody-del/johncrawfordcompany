// Checks the launch redirect map (launch/legacy-redirects.txt) against the old dealer-site URLs
// (launch/old-site-urls.txt) and the pages in dist/. The map stays switched off until the domain moves:
// dist/_redirects may only exist as an exact copy of the map.
import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const dist = resolve(root, 'dist');
const lines = file => readFileSync(resolve(root, file), 'utf8').split('\n').map(line => line.trim()).filter(line => line && !line.startsWith('#'));
const errors = [];
const requireThat = (ok, message) => { if (!ok) errors.push(message); };

const strip = path => (path.length > 1 ? path.replace(/\/$/, '') : path);
const isPage = path => existsSync(resolve(dist, path.replace(/^\//, ''), 'index.html'));

const rules = lines('launch/legacy-redirects.txt').map(line => {
  const [from, to, status, ...rest] = line.split(/\s+/);
  requireThat(from && to && status === '301' && rest.length === 0, `Malformed rule: ${line}`);
  return { from, to };
});

// Netlify matches a rule with or without a trailing slash; "/x/*" matches anything below /x/.
const matches = (rule, path) => {
  const target = strip(path);
  if (rule.from.endsWith('/*')) return target.startsWith(rule.from.slice(0, -1));
  return strip(rule.from) === target;
};
const firstRule = path => rules.find(rule => matches(rule, path));

for (const { from, to } of rules) {
  requireThat(from === from.toLowerCase(), `${from}: Netlify matching is case-sensitive; the old site uses lowercase URLs`);
  requireThat(!isPage(from.replace(/\/\*$/, '')), `${from}: is a page on the new site, so the rule would never apply`);
  requireThat(to === '/' || (to.endsWith('/') && isPage(to)), `${from}: target ${to} is not a page in dist/`);
  requireThat(!firstRule(to), `${from}: target ${to} is itself redirected (chain)`);
}

const oldUrls = lines('launch/old-site-urls.txt');
requireThat(oldUrls.length === new Set(oldUrls).size, 'launch/old-site-urls.txt lists a URL twice');
for (const url of oldUrls) {
  const rule = firstRule(url);
  requireThat(rule || isPage(url) || url === '/', `${url}: old URL has no page or redirect`);
  requireThat(!rule || !isPage(url), `${url}: is both a new page and redirected`);
}

const live = resolve(dist, '_redirects');
if (existsSync(live)) {
  requireThat(readFileSync(live, 'utf8') === readFileSync(resolve(root, 'launch/legacy-redirects.txt'), 'utf8'),
    'dist/_redirects must be an exact copy of launch/legacy-redirects.txt');
}

if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
console.log(`Redirect map: ${rules.length} rules cover all ${oldUrls.length} old dealer-site URLs; ${existsSync(live) ? 'LIVE in dist/_redirects' : 'not live (switched off until launch)'}.`);
