import test from 'node:test';
import assert from 'node:assert/strict';
import {submitLead, GHL_API, MIN_FILL_MS} from '../netlify/lib/lead.mjs';
import {createLeadHandler} from '../netlify/lib/lead-http.mjs';
import {MAX_REPAIR_PHOTO_BYTES, REPAIR_PHOTO_FALLBACK, validateRepairPhotos, repairUploadsConfigured} from '../netlify/lib/repair-photos.mjs';

const env = {GHL_PRIVATE_TOKEN: 'pit-test', GHL_LOCATION_ID: 'loc-test', GHL_REPAIR_PHOTO_FIELD_ID: 'repair-files-test'};
const data = {
  form: 'repair', page: '/services/blind-shade-repair/', name: 'Repair Test', phone: '8185550142', email: 'repair@example.com',
  website: '', elapsedMs: MIN_FILL_MS + 100, problem: 'Shade will not lift.', 'purchased-when': '2020-06-15', 'purchased-from': 'Original dealer', 'postal-code': '91364',
};
const png = () => new File([Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a8gAAAABJRU5ErkJggg==', 'base64')], 'photo.png', {type: 'image/png'});
function mockGhl({uploadStatus = 200, throwUpload = false} = {}) {
  const calls = [];
  return {calls, fetcher: async (url, init) => {
    calls.push({url, init});
    if (url.includes('/upload-custom-files')) {
      if (throwUpload) throw new TypeError('mock network error');
      return Response.json({contact: {id: 'repair-contact'}}, {status: uploadStatus});
    }
    return Response.json(url.endsWith('/upsert') ? {contact: {id: 'repair-contact'}} : {success: true});
  }};
}

test('repair details, both lead tags and multiple photos reach the same GHL contact', async () => {
  const {calls, fetcher} = mockGhl();
  const result = await submitLead(data, {env, fetcher, photos: [png(), png()]});
  assert.equal(result.body.success, true);
  assert.equal(calls.length, 3);
  const contact = JSON.parse(calls[0].init.body);
  assert.deepEqual(contact.tags, ['website-lead', 'website-repair-request']);
  assert.equal(contact.postalCode, '91364');
  assert.equal(calls[0].url, `${GHL_API}/contacts/upsert`);
  assert.equal(contact.firstName, 'Repair');
  assert.equal(contact.lastName, 'Test');
  assert.equal(contact.phone, '+18185550142');
  assert.equal(contact.email, 'repair@example.com');
  assert.equal(contact.source, 'Website: Repair page');
  const expectedDetails = [
    'John Crawford form submission: Website repair request',
    'Source: Website: Repair page',
    'Name: Repair Test', 'Phone: +18185550142', 'Email: repair@example.com',
    'What’s broken: Shade will not lift.', 'Bought: 2020-06-15', 'Bought from: Original dealer',
    'ZIP code: 91364', 'Photos selected: 2',
  ].join('\n');
  assert.deepEqual(contact.customFields, [
    {id: 'INk19lHx5XU2HQQhdFNQ', fieldValue: expectedDetails},
    {id: 'OfVLHC3hwaE9autFcPpz', fieldValue: 'Shade will not lift.'},
    {id: 'RuaSSSqBjgysltRF496w', fieldValue: '2020-06-15'},
    {id: 'mPeAbxuP1EXJ5FRkmD7K', fieldValue: 'Original dealer'},
  ]);
  assert.equal(new Set(contact.customFields.map(field => field.id)).size, 4);
  const upload = calls[1];
  const url = new URL(upload.url);
  assert.equal(url.origin, GHL_API);
  assert.equal(url.pathname, '/forms/upload-custom-files');
  assert.equal(url.searchParams.get('contactId'), 'repair-contact');
  assert.equal(url.searchParams.get('locationId'), 'loc-test');
  assert.equal(upload.init.headers.Version, 'v3');
  assert.equal(upload.init.headers['Content-Type'], undefined, 'fetch must set the multipart boundary');
  const files = [...upload.init.body.entries()];
  assert.equal(files.length, 2);
  assert.ok(files.every(([key, value]) => key.startsWith('repair-files-test_') && value.size === png().size));
  assert.notEqual(files[0][0], files[1][0]);
  const note = JSON.parse(calls[2].init.body).body;
  assert.equal(calls[2].url, `${GHL_API}/contacts/repair-contact/notes`);
  assert.equal(note, expectedDetails + '\nRepair photos: 2 saved to the Repair request photos field.');
});

test('invalid, oversized, spoofed or excessive photos are refused before any CRM write', async () => {
  const invalid = [
    Array.from({length: 6}, png),
    [new File(['<svg/>'], 'photo.svg', {type: 'image/svg+xml'})],
    [new File([png()], 'unconverted.webp', {type: 'image/webp'})],
    [new File(['not a jpeg'], 'fake.jpg', {type: 'image/jpeg'})],
    [new File([new Uint8Array(MAX_REPAIR_PHOTO_BYTES + 1)], 'big.png', {type: 'image/png'})],
  ];
  for (const photos of invalid) {
    const {calls, fetcher} = mockGhl();
    assert.equal((await submitLead(data, {env, fetcher, photos})).status, 400);
    assert.equal(calls.length, 0);
  }
  assert.ok(await validateRepairPhotos([new File([], 'empty.png', {type: 'image/png'})]));
});

test('configuration is checked without exposing credentials; text-only repair requests still work', async () => {
  const unconfigured = {...env, GHL_REPAIR_PHOTO_FIELD_ID: ''};
  assert.equal(repairUploadsConfigured(unconfigured), false);
  const {calls, fetcher} = mockGhl();
  assert.equal((await submitLead(data, {env: unconfigured, fetcher, photos: [png()]})).status, 503);
  assert.equal(calls.length, 0);
  assert.equal((await submitLead(data, {env: unconfigured, fetcher})).body.success, true);
});

test('a photo-upload error preserves the lead and clearly reports the photo failure', async () => {
  for (const options of [{uploadStatus: 403}, {throwUpload: true}]) {
    const {calls, fetcher} = mockGhl(options);
    const result = await submitLead(data, {env, fetcher, photos: [png()]});
    assert.equal(result.body.success, true);
    assert.equal(result.body.warning, REPAIR_PHOTO_FALLBACK);
    const savedDetails = JSON.parse(calls[0].init.body).customFields[0];
    assert.equal(savedDetails.id, 'INk19lHx5XU2HQQhdFNQ');
    const savedNote = JSON.parse(calls[2].init.body).body;
    assert.equal(savedNote, savedDetails.fieldValue + '\nRepair photos: upload failed. Please follow up with the customer for their photos.');
    assert.ok(savedNote.startsWith('John Crawford form submission: Website repair request\nSource: Website: Repair page\n'));
  }
});

test('the HTTP handler accepts multipart repair data and passes files with all answers', async () => {
  const fields = new FormData();
  for (const [name, value] of Object.entries(data)) fields.append(name, String(value));
  fields.append('photos', png()); fields.append('photos', png());
  let received;
  const handler = createLeadHandler(async (answers, options) => {
    received = {answers, options};
    return {status: 200, body: {success: true}};
  });
  const request = new Request('https://example.com/api/lead', {method: 'POST', headers: {origin: 'https://example.com'}, body: fields});
  assert.equal((await handler(request)).status, 200);
  assert.deepEqual(received.answers, data);
  assert.equal(received.options.photos.length, 2);
});

test('multipart uploads retain origin protection and refuse oversized or non-repair requests', async () => {
  let calls = 0;
  const handler = createLeadHandler(async () => {calls++; return {status: 200, body: {success: true}};});
  const request = (origin, fields) => new Request('https://example.com/api/lead', {method: 'POST', headers: {origin}, body: fields});
  assert.equal((await handler(request('https://other.example', new FormData()))).status, 403);
  const fields = new FormData(); fields.append('form', 'contact'); fields.append('elapsedMs', '4000'); fields.append('photos', png());
  assert.equal((await handler(request('https://example.com', fields))).status, 400);
  // A byte-backed request exercises the streaming limit without Node 24's
  // FormData/Blob producer continuing to enqueue after reader.cancel().
  const oversized = new Request('https://example.com/api/lead', {
    method: 'POST', headers: {origin: 'https://example.com', 'content-type': 'multipart/form-data; boundary=oversized-test'},
    body: new Uint8Array(4 * 1024 * 1024 + 1),
  });
  assert.equal((await handler(oversized)).status, 413);
  assert.equal(calls, 0);
});


test('repair details are never silently lost if GHL refuses the note', async () => {
  const fetcher = async url => Response.json(url.endsWith('/upsert') ? {contact: {id: 'repair-contact'}} : {}, {status: url.endsWith('/notes') ? 503 : 200});
  const result = await submitLead(data, {env, fetcher});
  assert.equal(result.body.success, true);
  assert.match(result.body.warning, /couldn’t save all of your repair information/);
});


test('repair photos use the existing private file field after upsert and finish before the workflow note', async () => {
  const actualEnv = {...env, GHL_REPAIR_PHOTO_FIELD_ID: 'OFy6KwIA4iCqESEDU8gQ'};
  let completeUpload;
  const uploadFinished = new Promise(resolve => { completeUpload = resolve; });
  let markUploadStarted;
  const uploadStarted = new Promise(resolve => { markUploadStarted = resolve; });
  const calls = [];
  const fetcher = async (url, init) => {
    calls.push({url, init});
    if (url.endsWith('/upsert')) return Response.json({contact: {id: 'repair-contact'}});
    if (url.includes('/upload-custom-files')) {
      assert.ok([...init.body.keys()].every(key => key.startsWith('OFy6KwIA4iCqESEDU8gQ_')));
      markUploadStarted();
      await uploadFinished;
    }
    return Response.json({success: true});
  };
  const submission = submitLead(data, {env: actualEnv, fetcher, photos: [png()]});
  await uploadStarted;
  assert.equal(calls.length, 2, 'the Note Added workflow must wait for photo processing');
  completeUpload();
  assert.equal((await submission).body.success, true);
  assert.equal(calls.length, 3);
  assert.ok(calls[2].url.endsWith('/contacts/repair-contact/notes'));
  assert.ok(calls.every(call => !/locations\/.*customFields/.test(call.url)), 'reuse the configured fields; do not create repair custom fields');
});


test('the verified photo contract accepts five photos and exactly 650 KiB per photo', async () => {
  assert.equal(MAX_REPAIR_PHOTO_BYTES, 650 * 1024);
  const bytes = new Uint8Array(650 * 1024);
  bytes.set(new Uint8Array(await png().arrayBuffer()));
  assert.equal(await validateRepairPhotos([new File([bytes], 'limit.png', {type: 'image/png'})]), '');
  const {fetcher, calls} = mockGhl();
  assert.equal((await submitLead(data, {env, fetcher, photos: Array.from({length: 5}, png)})).body.success, true);
  const note = JSON.parse(calls.at(-1).init.body).body;
  assert.match(note, /Photos selected: 5\nRepair photos: 5 saved/);
});
