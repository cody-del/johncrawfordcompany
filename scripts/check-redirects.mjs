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

const WWW = 'https://www.johncrawfordcompany.com';
const allRules = lines('launch/legacy-redirects.txt').map(line => {
  const [from, to, status, ...rest] = line.split(/\s+/);
  // Full-URL rules (apex/http -> www) need Netlify's force flag; path rules are plain 301s.
  const absolute = /^https?:\/\//.test(from || '');
  requireThat(from && to && status === (absolute ? '301!' : '301') && rest.length === 0, `Malformed rule: ${line}`);
  return { from, to, absolute };
});
const hostRules = allRules.filter(rule => rule.absolute);
const rules = allRules.filter(rule => !rule.absolute);

// Every apex/http variant of the domain must reach www in one hop (Netlify alone takes http -> https -> www).
for (const from of ['http://johncrawfordcompany.com/*', 'https://johncrawfordcompany.com/*', 'http://www.johncrawfordcompany.com/*']) {
  const rule = hostRules.find(r => r.from === from);
  requireThat(rule && rule.to === `${WWW}/:splat`, `${from}: needs a one-hop rule to ${WWW}/:splat`);
}
requireThat(hostRules.every(r => r.to === `${WWW}/:splat`), 'Full-URL rules may only send to the https www host');

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
  // The only off-site targets are the campaign pages on go.johncrawfordcompany.com.
  const GO_PAGES = ['https://go.johncrawfordcompany.com/', 'https://go.johncrawfordcompany.com/motorized-shades/'];
  requireThat(to === '/' || to === '/sitemap.xml' && existsSync(resolve(dist, 'sitemap.xml')) || GO_PAGES.includes(to) || (to.endsWith('/') && isPage(to)), `${from}: target ${to} is not a page in dist/ or on go.johncrawfordcompany.com`);
  requireThat(!firstRule(to), `${from}: target ${to} is itself redirected (chain)`);
}

const oldUrls = lines('launch/old-site-urls.txt');
requireThat(oldUrls.length === new Set(oldUrls).size, 'launch/old-site-urls.txt lists a URL twice');
for (const url of oldUrls) {
  const rule = firstRule(url);
  requireThat(rule || isPage(url) || url === '/', `${url}: old URL has no page or redirect`);
  requireThat(!rule || !isPage(url), `${url}: is both a new page and redirected`);
}

// Search Console 404 / soft-404 clean-up (2026-11-09): these old URLs go straight to the page with the same topic.
// Lifestyle articles without an equivalent page stay 404 on purpose; sending them to the homepage would be a soft 404.
const GSC_TARGETS = {
  '/home': '/',
  '/sitemap': '/sitemap.xml',
  '/motorized-window-coverings': '/motorized-shades/',
  '/more-products-services/services/wells-fargo-financing': '/contact/',
  '/hunter-douglas/featured/top-down-bottom-up-shades': '/shades/',
  '/hunter-douglas/featured/door-coverings': '/blinds/',
  '/inspiration-solutions/shape/bay-bow-corner-window-blinds-and-shades': '/shutters/',
  '/inspiration-solutions/shape/arched-window-blinds-and-shades': '/shutters/',
  '/inspiration-solutions/shape/picture-window-blinds-and-shades': '/shades/',
  '/inspiration-solutions/room/bathroom-blinds-and-shades': '/blinds/',
  '/inspiration-solutions/room/bedroom-blinds-and-shades': '/blinds/',
  '/inspiration-solutions/function/child-and-pet-friendly-blinds-and-shades': '/shades/',
  '/inspiration-solutions/design/motorized-skylight-shades': '/motorized-shades/',
  '/inspiration-solutions/design/zebra-shades': '/shades/',
  '/inspiration-solutions/design/cozy-home-energy-efficient-shades': '/shades/',
  '/inspiration-solutions/design/drapery-vs-side-panels': '/drapery/',
  '/inspiration-solutions/design/window-blinds-guide': '/blinds/',
  '/window-treatments/shades/roman-shades/carole-roman': '/shades/',
  '/window-treatments/blinds/vertical-blinds/vertical-solutions': '/blinds/',
  '/window-treatments/blinds/vertical-blinds/somner': '/blinds/',
  '/window-treatments/blinds/fabric-blinds/aria': '/blinds/',
  // Search Console 404s, 2026-11-10.
  '/window-treatments/shades/sheer-shades/luminette': '/shades/',
  '/window-treatments/shades/sheer-shades/pirouette': '/shades/',
  '/content/dealer/en/us/california/john-crawford-company-10044210/home/about.html': '/about/',
  '/content/dealer/en/us/california/john-crawford-company-10044210/home/privacy-policy.html': '/privacy/',
  '/content/dealer/en/us/california/john-crawford-company-10044210/home/sitemap.html': '/sitemap.xml',
  '/content/dealer/en/us/california/john-crawford-company-10044210/home/inspiration-solutions/shape/arched-window-blinds-and-shades.html': '/shutters/',
};
for (const [from, to] of Object.entries(GSC_TARGETS)) {
  const rule = firstRule(from);
  requireThat(rule && rule.to === to, `${from}: should redirect to ${to}, not ${rule ? rule.to : 'nothing'}`);
}
const LEFT_404 = [
  '/inspiration-solutions/design/Creating-a-breakfast-nook', '/inspiration-solutions/design/window-treatments-for-different-needs',
  '/inspiration-solutions/design/designing-an-outdoor-kitchen', '/inspiration-solutions/design/coastal-decor-ideas',
  '/inspiration-solutions/design/leather-furnishings', '/inspiration-solutions/design/decorating-with-green',
  '/inspiration-solutions/design/decorating-with-earth-tones', '/inspiration-solutions/design/glass-tables',
  '/inspiration-solutions/design/three-ideas-eco-friendly-flooring', '/inspiration-solutions/design/adding-curb-appeal',
  '/inspiration-solutions/design/kitchen-lighting-basics', '/inspiration-solutions/design/creating-a-gallery-wall',
  '/inspiration-solutions/design/Outdoor-patio-lighting', '/inspiration-solutions/design/creating-a-kitchen-island',
];
for (const url of LEFT_404) requireThat(!firstRule(url) && !firstRule(url.toLowerCase()) && !isPage(url), `${url}: has no equivalent page and must stay a 404 (no redirect)`);

const live = resolve(dist, '_redirects');
if (existsSync(live)) {
  requireThat(readFileSync(live, 'utf8') === readFileSync(resolve(root, 'launch/legacy-redirects.txt'), 'utf8'),
    'dist/_redirects must be an exact copy of launch/legacy-redirects.txt');
}

if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
console.log(`Redirect map: ${rules.length} path rules + ${hostRules.length} apex/http rules cover all ${oldUrls.length} old dealer-site URLs; ${existsSync(live) ? 'LIVE in dist/_redirects' : 'not live (switched off until launch)'}.`);
