import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {submitLead, GHL_API, MIN_FILL_MS} from '../netlify/lib/lead.mjs';
import {createLeadHandler, createRateLimiter} from '../netlify/lib/lead-http.mjs';

const expectedSubmission = "John Crawford form submission: Website lead\nSource: Website: Contact page\nName: Ada Lovelace\nPhone: +18185550142\nEmail: ada@example.com\nProduct interest: Shutters\nZIP code: 91364\nI’d like to schedule: Showroom visit\nMessage: Three bedroom windows.\nPrefer mornings.";
const env = {GHL_PRIVATE_TOKEN: 'pit-test', GHL_LOCATION_ID: 'loc-test'};
const person = {name: 'Ada Lovelace', phone: '818-555-0142', email: 'Ada@Example.com', website: '', elapsedMs: MIN_FILL_MS + 500};
const contact = (extra = {}) => ({
  form: 'contact', page: '/contact/', ...person, product: 'shutters', 'postal-code': '91364',
  'appointment-type': 'showroom', message: 'Three bedroom windows.\nPrefer mornings.', ...extra,
});
const repair = (extra = {}) => ({
  form: 'repair', page: '/services/blind-shade-repair/', ...person, problem: 'Cord snapped on a cellular shade.',
  'purchased-when': '', 'purchased-from': 'Costco', 'postal-code': '91367', ...extra,
});

// Records every GHL call and answers the upsert with a contact id.
function ghl({upsert = {status: 200, body: {contact: {id: 'c-1'}}}, note = {status: 201}} = {}) {
  const calls = [];
  const fetcher = async (url, init) => {
    calls.push({url, init, body: JSON.parse(init.body)});
    const answer = url.endsWith('/notes') ? note : upsert;
    if (answer instanceof Error) throw answer;
    return new Response(JSON.stringify(answer.body ?? {}), {status: answer.status});
  };
  return {calls, fetcher};
}

test('a contact-page lead carries its ZIP, appointment tag and a note with every answer', async () => {
  const {calls, fetcher} = ghl();
  const result = await submitLead(contact(), {fetcher, env});
  assert.deepEqual(result, {status: 200, body: {success: true, contactId: 'c-1'}});
  assert.equal(calls[0].url, `${GHL_API}/contacts/upsert`);
  assert.deepEqual(calls[0].body, {
    locationId: 'loc-test', firstName: 'Ada', lastName: 'Lovelace', phone: '+18185550142', email: 'ada@example.com',
    source: 'Website: Contact page', tags: ['website-lead', 'showroom-appointment'], postalCode: '91364',
    customFields: [{id: 'INk19lHx5XU2HQQhdFNQ', fieldValue: expectedSubmission}],
  });
  assert.equal(calls[1].url, `${GHL_API}/contacts/c-1/notes`);
  assert.equal(calls[1].body.body, expectedSubmission);
});

test('a repair lead skips blank optional answers', async () => {
  const {calls, fetcher} = ghl();
  assert.equal((await submitLead(repair(), {fetcher, env})).status, 200);
  assert.equal(calls[0].body.source, 'Website: Repair page');
  assert.deepEqual(calls[0].body.tags, ['website-lead', 'website-repair-request']);
  assert.equal(calls[1].body.body, 'John Crawford form submission: Website repair request\nSource: Website: Repair page\nName: Ada Lovelace\nPhone: +18185550142\nEmail: ada@example.com\nWhat’s broken: Cord snapped on a cellular shade.\nBought from: Costco\nZIP code: 91367\nPhotos selected: 0');
  assert.deepEqual(calls[0].body.customFields, [{id: 'INk19lHx5XU2HQQhdFNQ', fieldValue: calls[1].body.body}]);
});

test('a product-hub lead names its page and always writes the notification note', async () => {
  const {calls, fetcher} = ghl();
  const result = await submitLead({form: 'consultation', page: '/motorized-shades/', ...person}, {fetcher, env});
  assert.equal(result.status, 200);
  assert.equal(calls.length, 2);
  assert.match(calls[1].body.body, /^John Crawford form submission: Website lead\nSource: Website: Motorized Shades page/);
  assert.equal(calls[0].body.source, 'Website: Motorized Shades page');
  assert.deepEqual(calls[0].body.tags, ['website-lead']);
});

test('missing or invalid answers never reach GHL', async () => {
  const cases = [
    contact({product: ''}), contact({product: 'curtains'}), contact({'postal-code': '9136'}), contact({message: '  '}),
    contact({message: 'x'.repeat(3001)}), contact({'appointment-type': 'later'}), contact({form: 'quote'}),
    repair({problem: ''}), repair({'postal-code': undefined}), repair({'purchased-from': 'x'.repeat(161)}),
    repair({'purchased-when': ['2020']}), repair({website: 'https://spam.example'}), repair({elapsedMs: 10}),
    {form: 'consultation', page: '/shades/', ...person, email: 'ada@'},
  ];
  for (const data of cases) {
    const {calls, fetcher} = ghl();
    const result = await submitLead(data, {fetcher, env});
    assert.equal(result.status, 400, JSON.stringify(data));
    assert.equal(calls.length, 0);
  }
});

test('contact failures are reported and a failed notification note shows a warning', async () => {
  let {fetcher} = ghl({upsert: {status: 401, body: {}}});
  assert.equal((await submitLead(contact(), {fetcher, env})).status, 502);
  ({fetcher} = ghl({note: {status: 400}}));
  const saved = await submitLead(contact(), {fetcher, env});
  assert.equal(saved.status, 200);
  assert.match(saved.body.warning, /could not save the complete inquiry/);
  assert.equal((await submitLead(contact(), {fetcher, env: {GHL_LOCATION_ID: 'x'}})).status, 500);
});

test('the handler refuses other origins and the limiter caps each visitor', async () => {
  const handler = createLeadHandler(async () => ({status: 200, body: {success: true}}));
  const request = origin => new Request('https://www.example.com/api/lead', {method: 'POST', headers: {origin, 'content-type': 'application/json'}, body: '{}'});
  assert.equal((await handler(request('https://other.example'))).status, 403);
  assert.equal((await handler(request('https://www.example.com'))).status, 200);
  const limited = createRateLimiter({max: 2});
  assert.deepEqual([limited('ip', 0), limited('ip', 0), limited('ip', 0)], [false, false, true]);
});

test('every website form is live and matches what site.mjs expects', () => {
  const page = route => readFileSync(new URL(`../dist${route}index.html`, import.meta.url), 'utf8');
  const forms = [
    ...['/shades/', '/blinds/', '/shutters/', '/drapery/', '/motorized-shades/'].map(route => [route, 'consultation', []]),
    ['/contact/', 'contact', ['product', 'postal-code', 'appointment-type', 'message']],
    ['/services/blind-shade-repair/', 'repair', ['problem', 'purchased-when', 'purchased-from', 'postal-code', 'photos']],
  ];
  for (const [route, kind, names] of forms) {
    const form = page(route).match(new RegExp(`<form [^>]*data-lead-form="${kind}"[\\s\\S]*?</form>`))?.[0];
    assert.ok(form, `${route}: no ${kind} form`);
    assert.doesNotMatch(form.replace(/<input[^>]*type="file"[^>]*>/g, ''), /\bdisabled\b/);
    if (kind === 'repair') {
      assert.match(form, /type="file"[^>]*multiple[^>]*disabled/);
      for (const name of ['name', 'phone', 'email', 'postal-code', 'problem']) {
        const input = form.match(new RegExp(`<(?:input|textarea)\\b[^>]*name="${name}"[^>]*>`))?.[0];
        assert.ok(input && /\brequired\b/.test(input), `${route}: ${name} must be required`);
      }
      for (const name of ['purchased-when', 'purchased-from', 'photos']) {
        const input = form.match(new RegExp(`<input\\b[^>]*name="${name}"[^>]*>`))?.[0];
        assert.ok(input && !/\brequired\b/.test(input), `${route}: ${name} must remain optional`);
      }
    }
    for (const name of ['name', 'phone', 'email', 'website', ...names]) assert.match(form, new RegExp(`name="${name}"`), `${route}: ${name}`);
  }
  // The review copies of the campaign pages stay previews; the live ones are in cody-del/johncrawfordlanding.
  for (const route of ['/lp/custom-window-treatments/', '/lp/motorized-shades/']) assert.doesNotMatch(page(route), /data-lead-form/);
  assert.doesNotMatch(page('/privacy/'), /do not accept submissions/);
});
