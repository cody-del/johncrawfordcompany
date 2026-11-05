// Leads go straight to John Crawford Company's GoHighLevel location: the contact
// is upserted, then anything the visitor wrote beyond their contact details is
// added as a note. The way Beautiful Blinds & Shades' landing page sends its own
// (cody-del/beautifullanding, netlify/lib/consultation.mjs). The token and
// location come from this site's Netlify environment variables. Repair photo
// uploads are specific to the main website.
import {FORMS, LEAD_TAG, PHONE} from './site.mjs';
import {repairUploadsConfigured, validateRepairPhotos, uploadRepairPhotos, REPAIR_PHOTO_FALLBACK} from './repair-photos.mjs';

export const GHL_API = 'https://services.leadconnectorhq.com';
const GHL_VERSION = '2021-07-28';
// John Crawford contact.latest_inquiry_details; remap this ID for another subaccount.
const INQUIRY_DETAILS_FIELD_ID = 'INk19lHx5XU2HQQhdFNQ';

// Submissions sooner than this after the page loads are refused. app.js waits
// it out, so a person is never caught by it.
export const MIN_FILL_MS = 3000;

// The pattern zod's z.string().email() accepts, as on the other landing pages.
export const EMAIL = /^(?!\.)(?!.*\.\.)([A-Z0-9_'+\-.]*)[A-Z0-9_+-]@([A-Z0-9][A-Z0-9-]*\.)+[A-Z]{2,}$/i;

const CONTACT_LIMITS = {name: 120, phone: 30, email: 254};

export async function submitLead(data, {fetcher = fetch, rateLimited = () => false, env = process.env, photos = []} = {}) {
  const fail = (status, error) => ({status, body: {success: false, error}});
  if (!data || typeof data !== 'object' || Array.isArray(data)) return fail(400, 'Please check your contact details.');
  const form = typeof data.form === 'string' && Object.hasOwn(FORMS, data.form) ? FORMS[data.form] : null;
  if (!form) return fail(400, `Unable to submit this request. Please call ${PHONE}.`);
  // Hidden field that people never see; bots fill it in.
  if (data.website) return fail(400, `Unable to submit this request. Please call ${PHONE}.`);
  // Time since the page loaded, measured on the visitor's own clock.
  if (!Number.isSafeInteger(data.elapsedMs) || data.elapsedMs < MIN_FILL_MS) return fail(400, `Unable to submit this request. Please call ${PHONE}.`);
  for (const [field, limit] of Object.entries(CONTACT_LIMITS)) {
    if (typeof data[field] !== 'string' || !data[field].trim() || data[field].trim().length > limit) return fail(400, 'Please complete all contact fields.');
  }
  const digits = data.phone.replace(/\D/g, '');
  if (!/^\d{10}$|^1\d{10}$/.test(digits) || !EMAIL.test(data.email.trim())) return fail(400, 'Please enter a valid phone number and email address.');

  // The form's own fields, checked against site.mjs. Each one either goes on
  // the contact (contactField), becomes a tag (tags), or is written in the note.
  const answers = [];
  for (const field of form.fields) {
    const raw = data[field.name];
    if (raw !== undefined && typeof raw !== 'string') return fail(400, 'Please check your details.');
    const value = (raw ?? '').trim();
    if (!value) {
      if (field.required) return fail(400, `Please complete the ${field.label.toLowerCase()} field.`);
      continue;
    }
    if (value.length > field.max || (field.options && !Object.hasOwn(field.options, value))) return fail(400, 'Please check your details.');
    if (field.pattern && !field.pattern.test(value)) return fail(400, field.error);
    answers.push({field, value});
  }
  const photoError = await validateRepairPhotos(photos);
  if (photoError || (photos.length && data.form !== 'repair')) return fail(400, photoError || 'Photos can only be included with repair requests.');
  if (photos.length && !repairUploadsConfigured(env)) return fail(503, 'Photo uploads are temporarily unavailable. Please email your photos to john@johncrawford.com, or send this form without photos.');
  if (rateLimited()) return fail(429, `Too many requests. Please wait a few minutes or call ${PHONE}.`);

  const token = env.GHL_PRIVATE_TOKEN;
  const locationId = env.GHL_LOCATION_ID;
  if (!token || !locationId) {
    console.error('[lead] GHL_PRIVATE_TOKEN and GHL_LOCATION_ID are not configured');
    return fail(500, `We couldn’t send your request. Please call ${PHONE}.`);
  }
  // Only known pages name themselves in the source; anything else gets the form's own.
  const source = (typeof data.page === 'string' && Object.hasOwn(form.pages, data.page) && form.pages[data.page]) || form.source;
  // The page asks for one full name; GHL keeps first and last names apart.
  const [firstName, ...rest] = data.name.trim().split(/\s+/);
  const contact = {
    locationId,
    firstName,
    ...(rest.length ? {lastName: rest.join(' ')} : {}),
    phone: `+${digits.length === 10 ? '1' : ''}${digits}`,
    email: data.email.trim().toLowerCase(),
    source,
    tags: [LEAD_TAG, ...(form.tags ?? [])],
  };
  const note = [];
  for (const {field, value} of answers) {
    if (field.contactField) contact[field.contactField] = value;
    if (field.tags) contact.tags.push(field.tags[value]);
    note.push(`${field.label}: ${field.options ? field.options[value] : value}`);
  }
  // Save a complete submission snapshot before tag-triggered workflows can run.
  // The note is created for every form, including compact forms with no extra answers.
  const inquiryType = LEAD_TAG === 'google_landing_page'
    ? 'Google Ads lead' : data.form === 'repair' ? 'Website repair request' : 'Website lead';
  if (data.form === 'repair') note.push(`Photos selected: ${photos.length}`);
  const submissionDetails = () => [
    `John Crawford form submission: ${inquiryType}`, `Source: ${source}`,
    `Name: ${data.name.trim()}`, `Phone: ${contact.phone}`, `Email: ${contact.email}`, ...note,
  ].join('\n');
  contact.customFields = [{id: INQUIRY_DETAILS_FIELD_ID, field_value: submissionDetails()}];

  const headers = {Authorization: `Bearer ${token}`, Version: GHL_VERSION, 'Content-Type': 'application/json', Accept: 'application/json'};
  let contactId;
  try {
    const response = await fetcher(`${GHL_API}/contacts/upsert`, {
      method: 'POST', headers,
      // Leave time for the note and optional repair-photo upload.
      body: JSON.stringify(contact), signal: AbortSignal.timeout(6000),
    });
    const result = await response.json();
    contactId = result?.contact?.id || result?.contactId;
    // Only a contact id confirms the lead reached GHL.
    if (!response.ok || typeof contactId !== 'string' || !contactId) {
      console.error(`[lead] GHL did not confirm the lead (HTTP ${response.status})`);
      return fail(502, `We couldn’t confirm your request. Please call ${PHONE} for help.`);
    }
  } catch (error) {
    console.error(`[lead] GHL request failed: ${error.name}`);
    return fail(502, `We couldn’t confirm your request. Please call ${PHONE} before submitting again.`);
  }
  let photoUploadFailed = false;
  if (photos.length) {
    try {
      await uploadRepairPhotos(photos, {contactId, env, fetcher});
      note.push(`Repair photos: ${photos.length} saved to the Repair request photos field.`);
    } catch (error) {
      photoUploadFailed = true;
      console.error(`[lead] GHL repair-photo upload failed: ${error.name}`);
      note.push('Repair photos: upload failed. Please follow up with the customer for their photos.');
    }
  }
  // The contact is in GHL by now, so a failed note is logged but the lead still counts.
  let noteFailed = false;
  try {
    const response = await fetcher(`${GHL_API}/contacts/${encodeURIComponent(contactId)}/notes`, {
      method: 'POST', headers,
      body: JSON.stringify({body: submissionDetails()}), signal: AbortSignal.timeout(3000),
    });
    if (!response.ok) {
      noteFailed = true;
      console.error(`[lead] GHL did not save the note (HTTP ${response.status})`);
    }
  } catch (error) {
    noteFailed = true;
    console.error(`[lead] GHL note request failed: ${error.name}`);
  }
  const warning = noteFailed
    ? data.form === 'repair'
      ? `We received your contact details, but couldn’t save all of your repair information. Please call ${PHONE} or email john@johncrawford.com.`
      : `We received your contact details, but could not save the complete inquiry. Please call ${PHONE} or email john@johncrawford.com.`
    : photoUploadFailed ? REPAIR_PHOTO_FALLBACK : '';
  return {status: 200, body: {success: true, contactId, ...(warning ? {warning} : {})}};
}
