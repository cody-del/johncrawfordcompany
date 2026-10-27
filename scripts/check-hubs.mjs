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
  requireThat(route.startsWith('/lp/') ? !html.includes('22311 Ventura') : html.includes('22311 Ventura Blvd #101'), `${route}: respect landing-page appointment-only addressing or the verified website suite`);
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
const services = JSON.parse(await readFile(resolve(root, 'content/service-pages.json'), 'utf8'));
const expectedRoutes = ['/', ...hubs.map(hub => hub.slug), ...services.map(service => service.slug), '/accessibility/', '/privacy/', '/about/', '/contact/', '/lp/custom-window-treatments/', '/lp/motorized-shades/'];
requireThat(pages.size === expectedRoutes.length && expectedRoutes.every(route => pages.has(route)), `Expected ${expectedRoutes.length} routes including both campaign landing pages; found ${[...pages.keys()].join(', ')}`);
for (const service of services) {
  const html = pages.get(service.slug)?.html || '';
  requireThat(html.includes('/services.css?v=service-editorial-1') && html.includes('"@type": "Service"'), `${service.slug}: service template or structured data missing`);
  requireThat((html.match(/<details><summary>/g) || []).length === service.faqs.length, `${service.slug}: missing service questions`);
  requireThat(html.includes('mailto:john@johncrawford.com') && html.includes('href="/contact/#appointment-form"'), `${service.slug}: preserve the email, telephone and central appointment inquiry journey`);
  if (service.id === 'repair') {
    const form = html.match(/<form class="hub-consultation-form service-repair-form"[\s\S]*?<\/form>/)?.[0] || '';
    requireThat(form.includes('id="repair-inquiry"') && html.includes('href="#repair-inquiry"') && (form.match(/\bdisabled\b/g) || []).length === 8 && !/action=|data-netlify|type="submit"/.test(form), 'Repair form must remain a disabled design preview pending GHL');
    for (const name of ['purchased-when', 'purchased-from', 'problem', 'name', 'phone', 'email', 'photos']) requireThat(form.includes(`name="${name}"`), `Repair inquiry field missing: ${name}`);
    requireThat(/type="file" accept="image\/\*" multiple/.test(form), 'Repair photo control must support multiple images');
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
  if (route.startsWith('/lp/')) continue;
  requireThat(html.includes('href="/services/consultation-measuring/"') && html.includes('href="/services/window-treatment-installation/"') && !/href="\/services\/window-treatment-installation\/#(?:measuring|installation)"/.test(html), `${route}: Consultation & Measuring and Installation need separate navigation destinations`);
  requireThat(/href="\/about\/"(?: aria-current="page")?>About<\/a>/.test(html), `${route}: About navigation missing`);
  requireThat(/href="\/contact\/"(?: aria-current="page")?>Contact<\/a>/.test(html), `${route}: Contact navigation missing`);
  const header = html.match(/<header class="site-header">[\s\S]*?<\/header>/)?.[0] || '';
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
  requireThat(html.includes('/company-pages.css?v=company-pages-6'), `${route}: scoped styles missing`);
}
const contactForm = pages.get('/contact/')?.html.match(/<form class="hub-consultation-form"[\s\S]*?<\/form>/)?.[0] || '';
requireThat(contactForm.includes('id="appointment-form"'), 'Contact appointment destination missing');
requireThat((contactForm.match(/\bdisabled\b/g) || []).length === 9 && !/action=|data-netlify|type="submit"/.test(contactForm), 'Contact form must remain a design preview until GHL is configured');
requireThat(contactForm.includes('autocomplete="postal-code"') && contactForm.includes('<select id="company-product"') && contactForm.includes('<textarea id="company-message"'), 'Contact form must include ZIP code, product interest and message');
const appointmentOptions = contactForm.match(/<fieldset class="company-appointment-options">[\s\S]*?<\/fieldset>/)?.[0] || '';
requireThat((appointmentOptions.match(/name="appointment-type"/g) || []).length === 2 && (appointmentOptions.match(/type="radio" disabled/g) || []).length === 2 && !/\brequired\b|\bchecked\b|type="checkbox"/.test(appointmentOptions), 'Contact appointment choices must be one optional, unchecked design-only radio group');
const showroomArtwork = html => [...(html.match(/<section class="section about"[\s\S]*?<\/section>/)?.[0] || '').matchAll(/<img\b[^>]+src="\/?assets\/([^\"]+)"/g)].map(m => m[1]);
const homeShowroomArtwork = showroomArtwork(pages.get('/')?.html || '');
for (const route of ['/lp/custom-window-treatments/', '/lp/motorized-shades/']) {
  const html = pages.get(route)?.html || '';
  requireThat(JSON.stringify(showroomArtwork(html)) === JSON.stringify(homeShowroomArtwork), `${route}: preserve the approved Woodland Hills artwork`);
  requireThat(!/<address\b|91364|Monday–Friday|openingHoursSpecification|streetAddress/.test(html), `${route}: omit the showroom address and walk-in hours from landing pages`);
  requireThat(html.includes('<strong>Appointment Only</strong>') && html.includes('Fill the form to schedule a showroom appointment or free in-home consultation.'), `${route}: offer a showroom appointment or free in-home consultation through the form`);
  requireThat(/<p class="landing-john-story">[^<]*installing window treatments[^<]*1995\.[^<]*<\/p>/.test(html), `${route}: restore the concise, verified story about John's installation experience and California store`);
  requireThat(!html.includes('Come in to see fabrics and finishes'), `${route}: keep the restored showroom story concise`);
  requireThat(html.includes('href="/landings.css?v=appointment-options-1"'), `${route}: scoped landing-page styles missing`);
  const form = html.match(/<form class="landing-form"[\s\S]*?<\/form>/)?.[0] || '';
  requireThat((form.match(/\bdisabled\b/g) || []).length === 6 && !/action=|data-netlify|type="submit"/.test(form), `${route}: do not accept leads before the form destination is confirmed`);
  const landingAppointmentOptions = form.match(/<fieldset class="landing-appointment-options">[\s\S]*?<\/fieldset>/)?.[0] || '';
  requireThat((landingAppointmentOptions.match(/name="appointment-type"/g) || []).length === 2 && (landingAppointmentOptions.match(/type="radio" disabled/g) || []).length === 2 && !/\brequired\b|\bchecked\b|type="checkbox"/.test(landingAppointmentOptions), `${route}: offer one optional, unchecked appointment radio group`);
  requireThat(landingAppointmentOptions.includes('<legend>I’d like to schedule') && landingAppointmentOptions.includes('Free in-home consultation') && landingAppointmentOptions.includes('Showroom appointment') && landingAppointmentOptions.indexOf('value="in-home"') < landingAppointmentOptions.indexOf('value="showroom"'), `${route}: lead appointment choices with the free in-home consultation`);
  if (/programmed operation|schedule (?:compatible )?shades/i.test(html)) requireThat(html.includes('The PowerView® App is required for programmed operation.'), `${route}: missing PowerView disclosure for programmed shade operation`);
  const openingSection = html.match(/<main[^>]*>\s*(<section\b[\s\S]*?<\/section>)/)?.[1] || '';
  requireThat(!openingSection.includes(form) && /<section class="reviews"[\s\S]*?<\/section>\s*<section class="section landing-products"[\s\S]*?<\/section>\s*<section class="section landing-benefits"[\s\S]*?<\/section>\s*<section class="section about"[\s\S]*?<\/section>\s*<section class="section linen landing-quote"[\s\S]*?<\/section>\s*<\/main>/.test(html) && !!form, `${route}: follow reviews with product images, outcomes, Woodland Hills and the final quote form`);
  requireThat(html.includes('class="container landing-quote-grid"') && /<div class="landing-company-summary">[\s\S]*?<h2 id="company-summary-heading">Work with John Crawford\.<\/h2>[\s\S]*?<\/div>\s*<form class="landing-form"/.test(html), `${route}: place the John introduction beside the right-side form`);
  requireThat((html.match(/<article class="landing-benefit">/g) || []).length === 3, `${route}: include three concise customer outcomes`);
  const expectedService = route.includes('motorized-shades') ? 'Motorized Shades' : 'Custom Window Treatments';
  requireThat(openingSection.includes(`<span class="landing-hero-title">${expectedService}</span> <span class="landing-hero-location">in Los Angeles &amp; Surrounding Areas</span>`), `${route}: identify the service and target area in the hero`);
  requireThat(!/class="brand-bar"|class="brand-names"|class="alta-name"|hunter-douglas-gallery/.test(html), `${route}: omit the Hunter Douglas and Alta brand row`);
  requireThat(openingSection.includes('id="hero-video"') && openingSection.includes('class="hero-video-toggle"'), `${route}: restore the website video with a pause control on both landing pages`);
  const productOptions = html.match(/<section class="section landing-products"[\s\S]*?<\/section>/)?.[0] || '';
  requireThat((productOptions.match(/<article class="product"/g) || []).length === 4 && !/<p\b|<a\b/.test(productOptions), `${route}: show four product images and names without descriptions or browsing links`);
  const reviewSection = html.match(/<section class="reviews"[\s\S]*?<\/section>/)?.[0] || '';
  requireThat(html.includes(reviewSection + '\n' + productOptions) && !!reviewSection && !!productOptions, `${route}: put product cards directly below Google reviews`);
  requireThat((html.match(/<section\b/g) || []).length === 6 && !/id="(?:services|window-treatments|motorization)"/.test(html), `${route}: retain the focused hero, reviews, outcomes, John/form, image cards and illustrated appointment section`);
  requireThat(!/class="main-navigation"|class="menu-toggle"|class="footer-nav"/.test(html), `${route}: browsing menus are outside the conversion-only brief`);
  requireThat(!/<iframe\b/.test(html), `${route}: embedded maps must not provide an off-page exit`);
  requireThat(!/class="[^"]*(?:faq-list|questions-grid)|id="questions"|href="#questions"/.test(html), `${route}: landing-page FAQs must be removed`);
  const conversionContent = html.split('<dialog class="landing-info-dialog"')[0];
  for (const match of conversionContent.matchAll(/<a\b[^>]*href="(#contact|tel:[^"]+)"[^>]*>([\s\S]*?)<\/a>/g)) {
    const label = match[2].replace(/<[^>]*>/g, '').trim();
    const showroomSection = html.match(/<section class="section about"[\s\S]*?<\/section>/)?.[0] || '';
    const isAppointmentAction = match[1] === '#contact' && label === 'Schedule Appointment' && showroomSection.includes(match[0]);
    requireThat(isAppointmentAction || label === (match[1] === '#contact' ? 'Get Free Quote' : 'Call Us'), `${route}: inconsistent conversion action ${label}`);
  }
  requireThat(/<button class="btn btn-primary" type="button" disabled>Get Free Quote<\/button>/.test(html), `${route}: form button must match Get Free Quote actions`);
  for (const anchor of html.matchAll(/<a\b[^>]*href="([^"]+)"[^>]*>/g)) {
    requireThat(['#main', '#contact', 'tel:+18188845464'].includes(anchor[1]), `${route}: non-conversion link ${anchor[1]}`);
  }
  for (const id of ['landing-privacy-dialog','landing-accessibility-dialog']) {
    requireThat(html.includes(`<dialog class="landing-info-dialog" id="${id}"`), `${route}: missing on-page information dialog ${id}`);
  }
}
if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
console.log(`All ${pages.size} HTML routes passed: headings, metadata, internal links, assets, contact details and public copy separation.`);
