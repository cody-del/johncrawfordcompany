import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, readdirSync, statSync} from 'node:fs';
import {join} from 'node:path';
import {submitLead, GHL_API, MIN_FILL_MS} from '../netlify/lib/lead.mjs';
import {createLeadHandler} from '../netlify/lib/lead-http.mjs';

// These tests post without a Turnstile token; keep a build's real TURNSTILE_SECRET_KEY
// (Netlify sets it for production builds) from switching the human check on here.
delete process.env.TURNSTILE_SECRET_KEY;

const root = new URL('..', import.meta.url).pathname;
const read = path => readFileSync(join(root, path), 'utf8');
const page = route => read(`dist${route}index.html`);
const LEGAL = 'John Crawford Company';
const SERVICE_TEXT = `I agree to receive service texts from <strong>${LEGAL}</strong> about consultations, appointments, estimates, installations, repairs, and customer support.`;
const PROMO_TEXT = `I agree to receive promotional texts from <strong>${LEGAL}</strong> about offers and product news.`;
const DISCLOSURE = 'For either option: Message frequency varies. Message and data rates may apply. Reply <strong>STOP</strong> to opt out or <strong>HELP</strong> for help. Consent is not a condition of purchase.';
const FORM_PAGES = ['/shades/', '/blinds/', '/shutters/', '/drapery/', '/motorized-shades/', '/contact/', '/services/blind-shade-repair/'];
const text = html => html.replace(/<[^>]+>/g, '');

function htmlFiles(dir = join(root, 'dist')) {
  return readdirSync(dir).flatMap(name => {
    const path = join(dir, name);
    return statSync(path).isDirectory() ? htmlFiles(path) : name.endsWith('.html') ? [path] : [];
  });
}

test('every lead form is on a known page and carries the SMS consent block', () => {
  const withForms = htmlFiles().filter(file => readFileSync(file, 'utf8').includes('data-lead-form=')).map(file => file.slice(join(root, 'dist').length).replace(/index\.html$/, '')).sort();
  assert.deepEqual(withForms, [...FORM_PAGES].sort());
  for (const route of FORM_PAGES) {
    const forms = [...page(route).matchAll(/<form\b[\s\S]*?<\/form>/g)].map(match => match[0]).filter(form => form.includes('data-lead-form='));
    assert.equal(forms.length, 1, route);
    const form = forms[0];
    const fieldset = form.match(/<fieldset class="sms-consent">[\s\S]*?<\/fieldset>/)?.[0];
    assert.ok(fieldset, `${route}: SMS fieldset missing`);
    assert.match(fieldset, /<legend>SMS updates \(optional\)<\/legend>/);
    const boxes = [...fieldset.matchAll(/<input\b[^>]*>/g)].map(match => match[0]);
    assert.equal(boxes.length, 2, route);
    assert.deepEqual(boxes.map(box => box.match(/name="([^"]+)"/)[1]), ['sms_transactional', 'sms_marketing']);
    for (const box of boxes) {
      assert.match(box, /type="checkbox"/);
      assert.doesNotMatch(box, /\b(checked|required|disabled)\b/, `${route}: SMS boxes must be unchecked and optional`);
      const described = box.match(/aria-describedby="([^"]+)"/)?.[1];
      assert.ok(described && fieldset.includes(`<p class="sms-disclosure" id="${described}">${DISCLOSURE}</p>`), `${route}: disclosure must describe each box`);
    }
    assert.ok(fieldset.includes(`<span>${SERVICE_TEXT}</span>`), `${route}: service wording`);
    assert.ok(fieldset.includes(`<span>${PROMO_TEXT}</span>`), `${route}: promotional wording`);
    assert.ok(fieldset.includes('<a href="/privacy/">Privacy Policy</a> · <a href="/terms/">Terms</a> · <a href="/sms-consent/">SMS details</a>'), `${route}: policy links`);
    // After the contact fields, before the bot trap, Turnstile (inserted before the button) and submit.
    const at = form.indexOf('<fieldset class="sms-consent">');
    assert.ok(at > form.indexOf('name="email"') && at > form.indexOf('name="phone"') && at > form.indexOf('name="name"'), `${route}: SMS block follows the contact fields`);
    assert.ok(at < form.indexOf('type="submit"') && at < form.indexOf('name="website"'), `${route}: SMS block comes before submit`);
    assert.doesNotMatch(form, /All fields are required/, `${route}: the SMS boxes are optional`);
  }
});

test('app.js sends both choices as booleans and does not validate the boxes as required fields', () => {
  const app = read('dist/app.js');
  assert.match(app, /input:not\(\[type="radio"\]\):not\(\[type="checkbox"\]\)/);
  assert.match(app, /payload\.smsTransactionalOptIn = form\.querySelector\('input\[name="sms_transactional"\]'\)\?\.checked === true;/);
  assert.match(app, /payload\.smsMarketingOptIn = form\.querySelector\('input\[name="sms_marketing"\]'\)\?\.checked === true;/);
  assert.match(app, /formData\.delete\(name\)/);
  // The multipart path appends every payload value, so the booleans travel as "true"/"false" there too.
  assert.match(app, /Object\.entries\(payload\)\.forEach\(\(\[key, value\]\) => body\.append\(key, String\(value\)\)\)/);
});

test('privacy, terms and the SMS consent page carry the A2P clauses', () => {
  const privacy = text(page('/privacy/'));
  assert.ok(privacy.includes('Mobile Information and SMS'));
  assert.ok(privacy.includes('Mobile information will not be shared with third parties or affiliates for marketing or promotional purposes. Sharing with subcontractors and service providers that support customer service, scheduling, website operations, or message delivery is permitted only as needed to provide those services.'));
  assert.ok(privacy.includes('SMS consent is optional and is not a condition of purchase. If you choose to opt in, message frequency varies and message and data rates may apply. Reply STOP to cancel and HELP for assistance. Transactional and promotional SMS choices are collected separately.'));
  assert.match(privacy, /your SMS consent choices/);
  // Nothing on the page may say phone numbers or form details go to advertising partners.
  assert.doesNotMatch(privacy, /(share|sell|send)[^.]*(phone|mobile)[^.]*(advertis|partner|marketing)/i);

  const terms = text(page('/terms/'));
  assert.ok(terms.includes('SMS Terms'));
  assert.ok(terms.includes('By selecting an SMS opt-in checkbox, you consent only to the message category described beside that checkbox. Transactional messages may cover consultations, appointments, estimates, scheduling, project updates, repairs, and customer service. Promotional messages may cover offers, discounts, product announcements, and seasonal promotions. Message frequency varies; message and data rates may apply. Reply STOP to opt out and HELP for assistance. Consent is not a condition of purchase. Carriers are not liable for delayed or undelivered messages.'));

  const html = page('/sms-consent/');
  assert.match(html, /<title>SMS Consent and Messaging Information \| John Crawford Company<\/title>/);
  assert.ok(html.includes('<meta name="robots" content="index, follow, max-image-preview:large">'));
  assert.ok(html.includes('<link rel="canonical" href="https://www.johncrawfordcompany.com/sms-consent/">'));
  const sms = text(html);
  for (const heading of ['How Website Visitors Opt In', 'Consent Is Specific and Voluntary', 'Mobile Information and Sharing', 'Message Types', 'Contact Us']) {
    assert.ok(html.includes(`<h2>${heading}</h2>`), heading);
  }
  assert.ok(sms.includes('Effective November 25, 2026.'));
  assert.ok(sms.includes('www.johncrawfordcompany.com') && sms.includes('go.johncrawfordcompany.com'));
  assert.ok(sms.includes('John Crawford Company does not sell, rent, lease, or share SMS opt-in data, phone numbers, or consent records with third parties or affiliates for their marketing or promotional purposes. Our customer-relationship platform processes records only on our behalf'));
  assert.ok(sms.includes('Neither checkbox is preselected'));
  assert.ok(sms.includes('22311 Ventura Blvd #101') && sms.includes('(818) 884-5464') && sms.includes('john@johncrawford.com'));
});

test('/sms-consent/ is in the sitemap and every page footer links SMS Terms', () => {
  assert.match(read('dist/sitemap.xml'), /<loc>https:\/\/www\.johncrawfordcompany\.com\/sms-consent\/<\/loc>/);
  for (const file of htmlFiles()) {
    const footer = readFileSync(file, 'utf8').match(/<nav aria-label="Policies">[\s\S]*?<\/nav>/)?.[0] || '';
    assert.match(footer, /href="\/terms\/"(?: aria-current="page")?>Terms of Service<\/a>\s*<a href="\/sms-consent\/"(?: aria-current="page")?>SMS Terms<\/a>/, file);
  }
});

test('the campaign package quotes the form wording exactly', () => {
  const doc = read('docs/a2p-campaign-package.md');
  const plain = value => value.replace(/<\/?strong>/g, '');
  assert.ok(doc.includes(`Checkbox 1 (service): "${plain(SERVICE_TEXT)}"`));
  assert.ok(doc.includes(`Checkbox 2 (promotional): "${plain(PROMO_TEXT)}"`));
  assert.ok(doc.includes(`the form states: "${plain(DISCLOSURE)}"`));
  // And the forms really use that wording, from the one shared source.
  const source = read('scripts/sms_consent.py');
  assert.ok(source.includes(SERVICE_TEXT.replace(LEGAL, '{LEGAL_NAME}')) && source.includes(PROMO_TEXT.replace(LEGAL, '{LEGAL_NAME}')) && source.includes(DISCLOSURE));
  assert.ok(source.includes(`LEGAL_NAME = '${LEGAL}'`));
  for (const url of ['https://www.johncrawfordcompany.com/privacy/', 'https://www.johncrawfordcompany.com/terms/', 'https://www.johncrawfordcompany.com/sms-consent/']) assert.ok(doc.includes(url));
  const samples = [...doc.matchAll(/^\d\. `([^`]+)`$/gm)].map(match => match[1]);
  assert.equal(samples.length, 6);
  for (const sample of samples) assert.ok(sample.startsWith('John Crawford Company:') && sample.endsWith('Reply STOP to opt out or HELP for help.'), sample);
});

// ---- Server: tags and note lines ----

const env = {GHL_PRIVATE_TOKEN: 'pit-test', GHL_LOCATION_ID: 'loc-test', GHL_REPAIR_PHOTO_FIELD_ID: 'repair-files-test'};
const now = () => new Date('2026-11-25T17:30:00.000Z');
const person = {name: 'Ada Lovelace', phone: '818-555-0142', email: 'ada@example.com', website: '', elapsedMs: MIN_FILL_MS + 500};
const hub = extra => ({form: 'consultation', page: '/shutters/', ...person, ...extra});
const repair = extra => ({form: 'repair', page: '/services/blind-shade-repair/', ...person, problem: 'Cord snapped.', 'postal-code': '91364', ...extra});
const png = () => new File([Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a8gAAAABJRU5ErkJggg==', 'base64')], 'photo.png', {type: 'image/png'});

function ghl() {
  const calls = [];
  const fetcher = async (url, init) => {
    calls.push({url, body: init.body instanceof FormData ? null : JSON.parse(init.body)});
    return Response.json(url.endsWith('/upsert') ? {contact: {id: 'c-1'}} : {success: true});
  };
  return {calls, fetcher};
}
const noteOf = calls => calls.find(call => call.url.endsWith('/notes')).body.body;
const smsLines = (service, promo, path) => `Service SMS opt-in: ${service}\nPromotional SMS opt-in: ${promo}\nSMS consent captured 2026-11-25T17:30:00.000Z from ${path}`;

test('each SMS box adds only its own tag and the note records Yes/No with a timestamp', async () => {
  for (const [service, promo, tags] of [
    [true, true, ['sms-transactional-opt-in', 'sms-marketing-opt-in']],
    [true, false, ['sms-transactional-opt-in']],
    [false, true, ['sms-marketing-opt-in']],
    [false, false, []],
  ]) {
    const {calls, fetcher} = ghl();
    assert.equal((await submitLead(hub({smsTransactionalOptIn: service, smsMarketingOptIn: promo}), {fetcher, env, now})).status, 200);
    assert.deepEqual(calls[0].body.tags, ['website-lead', ...tags]);
    const lines = smsLines(service ? 'Yes' : 'No', promo ? 'Yes' : 'No', '/shutters/');
    assert.ok(noteOf(calls).endsWith(lines), noteOf(calls));
    assert.ok(noteOf(calls).startsWith('John Crawford form submission: Website lead\nSource: Website: Shutters page\n'));
    assert.equal(calls[0].body.customFields[0].fieldValue, noteOf(calls), 'the inquiry snapshot carries the same consent lines');
  }
});

test('only a literal true is consent; strings, missing values and junk are recorded as No', async () => {
  for (const value of ['true', 'on', 1, 'yes', null, undefined, {}]) {
    const {calls, fetcher} = ghl();
    assert.equal((await submitLead(hub({smsTransactionalOptIn: value, smsMarketingOptIn: value}), {fetcher, env, now})).status, 200);
    assert.deepEqual(calls[0].body.tags, ['website-lead']);
    assert.ok(noteOf(calls).endsWith(smsLines('No', 'No', '/shutters/')));
  }
  const {calls, fetcher} = ghl();
  await submitLead(hub({page: '<script>', smsTransactionalOptIn: true}), {fetcher, env, now});
  assert.ok(noteOf(calls).endsWith('SMS consent captured 2026-11-25T17:30:00.000Z from unknown page'));
});

test('JSON through the HTTP handler: the booleans reach the tags and note', async () => {
  const {calls, fetcher} = ghl();
  const handler = createLeadHandler((data, options) => submitLead(data, {...options, fetcher, env, now}));
  const response = await handler(new Request('https://www.example.com/api/lead', {
    method: 'POST', headers: {origin: 'https://www.example.com', 'content-type': 'application/json'},
    body: JSON.stringify({...hub({page: '/contact/', form: 'contact', product: 'shades', 'postal-code': '91364', message: 'Hi'}), smsTransactionalOptIn: false, smsMarketingOptIn: true}),
  }));
  assert.equal(response.status, 200);
  assert.deepEqual(calls[0].body.tags, ['website-lead', 'sms-marketing-opt-in']);
  assert.ok(noteOf(calls).endsWith(smsLines('No', 'Yes', '/contact/')));
});

test('multipart repair with photos: text "true"/"false" become the right tags, still added last', async () => {
  for (const [service, promo, tags] of [['true', 'false', ['sms-transactional-opt-in']], ['false', 'true', ['sms-marketing-opt-in']], ['yes', 'on', []]]) {
    const {calls, fetcher} = ghl();
    const handler = createLeadHandler((data, options) => submitLead(data, {...options, fetcher, env, now}));
    const fields = new FormData();
    for (const [name, value] of Object.entries(repair({smsTransactionalOptIn: service, smsMarketingOptIn: promo}))) fields.append(name, String(value));
    fields.append('photos', png());
    const response = await handler(new Request('https://www.example.com/api/lead', {method: 'POST', headers: {origin: 'https://www.example.com'}, body: fields}));
    assert.equal(response.status, 200);
    assert.deepEqual(calls.map(call => new URL(call.url).pathname), ['/contacts/upsert', '/forms/upload-custom-files', '/contacts/c-1/notes', '/contacts/c-1/tags']);
    assert.equal(calls[0].body.tags, undefined, 'no tags before the photos and note are saved');
    assert.equal(calls.at(-1).url, `${GHL_API}/contacts/c-1/tags`);
    assert.deepEqual(calls.at(-1).body, {tags: ['website-lead', 'website-repair-request', ...tags]});
    assert.match(noteOf(calls), new RegExp(smsLines(service === 'true' ? 'Yes' : 'No', promo === 'true' ? 'Yes' : 'No', '/services/blind-shade-repair/') + '\nPhotos selected: 1\n'));
  }
});

test('without photos the SMS tags go on the first save with the lead tags, before the note', async () => {
  const {calls, fetcher} = ghl();
  assert.equal((await submitLead(repair({smsTransactionalOptIn: true, smsMarketingOptIn: true}), {fetcher, env, now})).status, 200);
  assert.deepEqual(calls.map(call => new URL(call.url).pathname), ['/contacts/upsert', '/contacts/c-1/notes']);
  assert.deepEqual(calls[0].body.tags, ['website-lead', 'website-repair-request', 'sms-transactional-opt-in', 'sms-marketing-opt-in']);
});

// Matches the approved Shenandoah package: every sample names the brand and carries STOP and HELP,
// and the privacy page describes only what actually runs (Netlify hosting, GA4 behind Performance cookies).
test('campaign samples name the brand and include STOP and HELP', () => {
  const doc = read('docs/a2p-campaign-package.md');
  const samples = [...doc.matchAll(/^\d\. `(John Crawford Company: [^`]+)`$/gm)].map(m => m[1]);
  assert.equal(samples.length, 6);
  for (const s of samples) assert.match(s, /Reply STOP to opt out or HELP for help\.$/);
});

test('privacy page is accurate about hosting and analytics', () => {
  const privacy = text(page('/privacy/'));
  assert.doesNotMatch(privacy, /ChatGPT Sites|audience-tracking/);
  assert.match(privacy, /If you allow Performance cookies, we use Google Analytics 4/);
  assert.match(privacy, /22311 Ventura Blvd #101, Woodland Hills, CA 91364/);
});
