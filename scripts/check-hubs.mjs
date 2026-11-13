import { readFile, readdir, access } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const dist = resolve(root, 'dist');
const errors = [];
const requireThat = (condition, message) => { if (!condition) errors.push(message); };
// A form app.js sends to /api/lead: enabled, one submit button, the hidden bot trap
// and a status line. netlify/lib/site.mjs lists what each kind sends to GHL.
const isLeadForm = (form, kind) => form.includes(`data-lead-form="${kind}"`)
  && !/\bdisabled\b|action=|data-netlify|does not accept submissions/.test(form.replace(/<input[^>]*type="file"[^>]*>/g, ''))
  && (form.match(/type="submit"/g) || []).length === 1 && form.includes('name="website"') && form.includes('class="lead-form-status"');
const hours = JSON.parse(await readFile(resolve(root, 'content/business-hours.json'), 'utf8'));
function checkHoursSchema(value, route) {
  if (!value || typeof value !== 'object') return 0;
  let count = 0;
  if (Object.hasOwn(value, 'openingHoursSpecification')) {
    const specs = value.openingHoursSpecification;
    requireThat(Array.isArray(specs) && specs.length === 1
      && JSON.stringify(specs[0].dayOfWeek) === JSON.stringify(hours.days)
      && specs[0].opens === hours.opens && specs[0].closes === hours.closes,
      `${route}: structured business hours must match content/business-hours.json`);
    count++;
  }
  return count + Object.values(value).reduce((sum, child) => sum + checkHoursSchema(child, route), 0);
}
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
  const footerHours = html.match(/<p class="footer-hours">[\s\S]*?<\/p>/)?.[0] || '';
  requireThat(footerHours.includes(hours.display) && footerHours.includes(hours.closed_display),
    `${route}: visible footer hours must match content/business-hours.json`);
  requireThat(!/Monday[–—-]Friday|Saturday(?:[–—-]Sunday)? closed/i.test(html),
    `${route}: obsolete weekday-only or Saturday-closed hours`);
  const title = html.match(/<title>([^<]+)<\/title>/)?.[1];
  requireThat(title && !titles.has(title), `${route}: missing or duplicate title`);
  titles.add(title);
  requireThat((html.match(/<h1\b/g) || []).length === 1, `${route}: expected one H1`);
  requireThat(ids.length === new Set(ids).size, `${route}: duplicate IDs`);
  requireThat(/<html lang="en">/.test(html), `${route}: missing document language`);
  requireThat(/name="description" content="[^"]+"/.test(html), `${route}: missing description`);
  requireThat(/name="robots" content="index, follow, max-image-preview:large"/.test(html), `${route}: wrong robots tag`);
  requireThat(html.includes(`<link rel="canonical" href="https://www.johncrawfordcompany.com${route}">`) && !html.includes('chatgpt.site'), `${route}: canonical must be its www.johncrawfordcompany.com URL`);
  for (const policy of ['/accessibility/', '/privacy/', '/terms/']) {
    requireThat(html.includes(`href="${policy}"`), `${route}: footer must link ${policy}`);
  }
  requireThat(html.includes('22311 Ventura Blvd #101'), `${route}: show the verified showroom address`);
  requireThat(!/Confirm before publishing|local shutter supplier|review_note|source_file|\/Users\//i.test(html), `${route}: private note exposed`);
  requireThat(!/\bMax\b/.test(html), `${route}: employee name must stay out of public copy`);
  requireThat(/<strong(?: class="appointment-only")?>Appointment Only<\/strong>/.test(html), `${route}: bold showroom appointment notice missing`);
  requireThat(!/>Get directions</i.test(html), `${route}: replace old showroom directions labels`);
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
  let hoursSchemaCount = 0;
  for (const match of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) {
    try { hoursSchemaCount += checkHoursSchema(JSON.parse(match[1]), route); }
    catch { errors.push(`${route}: malformed structured data`); }
  }
  requireThat(hoursSchemaCount > 0,
    `${route}: respect website business hours and campaign-page omissions`);
}
const contactDescription = pages.get('/contact/')?.html.match(/name="description" content="([^"]*)"/)?.[1] || '';
requireThat(contactDescription.includes(hours.display),
  'Contact metadata must use the confirmed business hours');
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
  requireThat(isLeadForm(formPreview, 'consultation'), `${hub.slug}: consultation form must send leads to GHL through app.js`);
  requireThat(/<\/section>\s*<section class="section hub-introduction hub-intro-consultation"/.test(html), `${hub.slug}: consultation section must follow the hero`);
}
requireThat(pages.get('/motorized-shades/')?.html.includes('The PowerView® App is required for programmed operation.'), 'Missing PowerView scheduling disclosure');
const services = JSON.parse(await readFile(resolve(root, 'content/service-pages.json'), 'utf8'));
const serviceAreas = JSON.parse(await readFile(resolve(root, 'content/service-areas.json'), 'utf8'));
const blogPosts = JSON.parse(await readFile(resolve(root, 'content/blog-posts.json'), 'utf8'));
const locations = JSON.parse(await readFile(resolve(root, 'content/location-pages.json'), 'utf8'));
const expectedRoutes = ['/', ...locations.map(location => location.slug), ...blogPosts.map(post => post.slug), ...hubs.map(hub => hub.slug), ...services.map(service => service.slug), '/accessibility/', '/privacy/', '/terms/', '/about/', '/contact/', '/blog/', serviceAreas.slug];
requireThat(pages.size === expectedRoutes.length && expectedRoutes.every(route => pages.has(route)), `Expected ${expectedRoutes.length} routes; found ${[...pages.keys()].join(', ')}`);
for (const service of services) {
  const html = pages.get(service.slug)?.html || '';
  requireThat(html.includes('/services.css?v=service-editorial-1') && html.includes('"@type": "Service"'), `${service.slug}: service template or structured data missing`);
  requireThat((html.match(/<details><summary>/g) || []).length === service.faqs.length, `${service.slug}: missing service questions`);
  requireThat(html.includes('mailto:john@johncrawford.com') && html.includes('href="/contact/#appointment-form"'), `${service.slug}: preserve the email, telephone and central appointment inquiry journey`);
  if (service.id === 'repair') {
    const form = html.match(/<form class="hub-consultation-form service-repair-form"[\s\S]*?<\/form>/)?.[0] || '';
    requireThat(form.includes('id="repair-inquiry"') && html.includes('href="#repair-inquiry"') && isLeadForm(form, 'repair'), 'Repair form must send leads to GHL through app.js');
    for (const name of ['purchased-when', 'purchased-from', 'problem', 'name', 'phone', 'email', 'postal-code']) requireThat(form.includes(`name="${name}"`), `Repair inquiry field missing: ${name}`);
    requireThat(/type="file"[^>]*multiple[^>]*disabled/.test(form) && form.includes('Upload photos') && form.includes('id="repair-photo-selection"'), 'Repair photo uploads must wait for the GHL upload capability check');
    requireThat(form.includes('href="mailto:john@johncrawford.com?subject=Repair%20photos"'), 'Repair photo email fallback missing');
  } else requireThat(!/<form\b/.test(html), `${service.slug}: keep the central contact inquiry destination`);
}
const consultationHtml = pages.get('/services/consultation-measuring/')?.html || '';
const installationHtml = pages.get('/services/window-treatment-installation/')?.html || '';
requireThat(consultationHtml.includes('<h1 id="page-heading">Free in-home consultation &amp; measuring</h1>') && consultationHtml.includes('id="measuring"'), 'Consultation and measuring need their own service page and heading');
requireThat(installationHtml.includes('<h1 id="page-heading">Window treatment installation in Los Angeles</h1>') && !installationHtml.includes('Installation includes a walkthrough'), 'Installation needs its own heading and outcome-focused copy');
for (const html of [consultationHtml, installationHtml]) {
  const hero = html.match(/<section class="section service-hero"[\s\S]*?<\/section>/)?.[0] || '';
  requireThat(/free in-home consultation/i.test(hero) && /samples[\s\S]*home|home[\s\S]*samples/i.test(hero) && /measurements/i.test(hero), 'Both service heroes must explain the free home visit with samples and measuring');
  requireThat(hero.includes('href="/contact/#appointment-form"'), 'Both service hero actions must lead to the central appointment form');
}
for (const [route, { html }] of pages) {
  requireThat(html.includes('href="/services/consultation-measuring/"') && html.includes('href="/services/window-treatment-installation/"') && !/href="\/services\/window-treatment-installation\/#(?:measuring|installation)"/.test(html), `${route}: Consultation & Measuring and Installation need separate navigation destinations`);
  requireThat(/href="\/about\/"(?: aria-current="page")?>About<\/a>/.test(html), `${route}: About navigation missing`);
  const header = html.match(/<header class="site-header">[\s\S]*?<\/header>/)?.[0] || '';
  const footer = html.match(/<footer class="site-footer"[\s\S]*?<\/footer>/)?.[0] || '';
  const navigation = header.match(/<nav class="main-navigation"[\s\S]*?<\/nav>/)?.[0] || '';
  requireThat(!/>Contact<\/a>/.test(navigation), `${route}: omit the duplicate Contact navigation link`);
  requireThat(/<a class="btn btn-primary header-cta" href="\/contact\/"(?: aria-current="page")?>Request a consultation<\/a>/.test(header), `${route}: the header consultation button must open the Contact page`);
  requireThat(header.includes('class="header-call"') && header.includes('<span class="sr-only">Call now</span>') && header.includes('href="tel:+18188845464"'), `${route}: include the labeled phone disclosure and correct tap-to-call number`);
  requireThat(header.includes('href="/service-areas/"') && footer.includes('href="/service-areas/"'), `${route}: Service Areas must be reachable from the header and footer`);
  for (const [label, destinations] of [['Window Treatments', hubs], ['Services', services]]) {
    const dropdown = [...header.matchAll(/<details\b[^>]*>[\s\S]*?<\/details>/g)].find(match => match[0].includes(`<summary>${label}</summary>`))?.[0] || '';
    const hrefs = [...dropdown.matchAll(/<a\b[^>]*href="([^"]+)"/g)].map(match => match[1]);
    requireThat(hrefs.length === destinations.length && destinations.every(page => hrefs.includes(page.slug)), `${route}: ${label} dropdown must link once to each published page`);
  }
}
for (const [route, type] of [['/about/', 'AboutPage'], ['/contact/', 'ContactPage']]) {
  const html = pages.get(route)?.html || '';
  requireThat(html.includes(`"@type": "${type}"`), `${route}: page schema missing`);
  requireThat(html.includes('href="tel:+18188845464"') && html.includes('href="mailto:john@johncrawford.com'), `${route}: direct contact destinations missing`);
  requireThat(html.includes('/company-pages.css?v=company-pages-7'), `${route}: scoped styles missing`);
}
const contactForm = pages.get('/contact/')?.html.match(/<form class="hub-consultation-form"[\s\S]*?<\/form>/)?.[0] || '';
const areaHtml = pages.get(serviceAreas.slug)?.html || '';
const areaCommunities = serviceAreas.regions.flatMap(region => region.communities);
requireThat(serviceAreas.regions.length === 5 && areaCommunities.length === 27 && new Set(areaCommunities).size === 27, 'The single Service Areas hub must retain all five supplied regions and 27 distinct communities');
requireThat(areaHtml.includes('/service-areas.css?v=service-areas-3') && !/<form\b/.test(areaHtml), 'Service Areas should use its directory layout and central contact journey');
const areaMain = areaHtml.match(/<main\b[\s\S]*?<\/main>/)?.[0] || '';
requireThat(!/\bZIP\b|\b\d{5}\b/i.test(areaMain), 'Keep ZIP codes out of the service-area listings and inquiry copy');
for (const region of serviceAreas.regions) {
  requireThat(areaHtml.includes(`id="${region.id}-heading"`) && areaHtml.includes(region.heading.replaceAll('&', '&amp;')), `Service area region missing: ${region.heading}`);
  for (const place of region.communities) {
    const location = locations.find(location => location.name === place);
    const expected = location ? `<a href="${location.slug}">${place}</a>` : place;
    requireThat(areaHtml.includes(`<li class="area-place">${expected}</li>`), `Service area community or published destination missing: ${place}`);
  }
}
for (const location of locations) {
  const html = pages.get(location.slug)?.html || '';
  const main = html.match(/<main\b[\s\S]*?<\/main>/)?.[0] || '';
  requireThat(!/<form\b/.test(main) && main.includes('href="/contact/#appointment-form"'), `${location.slug}: retain the central appointment form journey`);
  const graph = JSON.parse(html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)?.[1] || '[]');
  const service = graph.find(entity => entity['@type'] === 'Service');
  const page = graph.find(entity => entity['@type'] === 'WebPage');
  requireThat(service?.areaServed?.name === `${location.name}, California`, `${location.slug}: describe the actual service area`);
  requireThat(page?.publisher?.address?.addressLocality === 'Woodland Hills' && page?.publisher?.address?.streetAddress === '22311 Ventura Blvd #101', `${location.slug}: use the real Woodland Hills showroom, not an invented branch`);
  requireThat(main.includes('Appointment Only') && main.includes(hours.display), `${location.slug}: show the verified appointment hours`);
}
requireThat(contactForm.includes('id="appointment-form"'), 'Contact appointment destination missing');
requireThat(isLeadForm(contactForm, 'contact'), 'Contact form must send leads to GHL through app.js');
requireThat(contactForm.includes('autocomplete="postal-code"') && contactForm.includes('<select id="company-product"') && contactForm.includes('<textarea id="company-message"'), 'Contact form must include ZIP code, product interest and message');
const appointmentOptions = contactForm.match(/<fieldset class="company-appointment-options">[\s\S]*?<\/fieldset>/)?.[0] || '';
requireThat((appointmentOptions.match(/name="appointment-type"/g) || []).length === 2 && (appointmentOptions.match(/type="radio">/g) || []).length === 2 && !/\brequired\b|\bchecked\b|type="checkbox"/.test(appointmentOptions), 'Contact appointment choices must be one optional, unchecked radio group');
// sitemap.xml lists exactly the indexable pages (scripts/build-sitemap.py), and robots.txt points to it.
const sitemap = await readFile(resolve(dist, 'sitemap.xml'), 'utf8').catch(() => '');
const listed = [...sitemap.matchAll(/<loc>https:\/\/www\.johncrawfordcompany\.com(\/[^<]*)<\/loc>/g)].map(match => match[1]).sort();
const indexable = [...pages].filter(([, page]) => /name="robots" content="index, follow/.test(page.html)).map(([route]) => route).sort();
requireThat(listed.length > 0 && JSON.stringify(listed) === JSON.stringify(indexable), 'sitemap.xml must list exactly the indexable pages; run python3 scripts/build-sitemap.py');
const robots = await readFile(resolve(dist, 'robots.txt'), 'utf8').catch(() => '');
requireThat(/^Sitemap: https:\/\/www\.johncrawfordcompany\.com\/sitemap\.xml$/m.test(robots) && !/^Disallow: \/\s*$/m.test(robots), 'robots.txt must allow crawling and point to the sitemap');

if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
console.log(`All ${pages.size} HTML routes passed: headings, metadata, internal links, assets, contact details and public copy separation.`);
