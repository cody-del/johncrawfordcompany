import {randomUUID} from 'node:crypto';

export const MAX_REPAIR_PHOTOS = 5;
export const MAX_REPAIR_PHOTO_BYTES = 650 * 1024;
export const REPAIR_PHOTO_FALLBACK = 'We received your repair request, but couldn’t save the photos. Please email them to john@johncrawford.com.';

export function repairUploadsConfigured(env = process.env) {
  return Boolean(env.GHL_PRIVATE_TOKEN && env.GHL_LOCATION_ID && env.GHL_REPAIR_PHOTO_FIELD_ID);
}

export async function validateRepairPhotos(photos) {
  if (!Array.isArray(photos) || photos.length > MAX_REPAIR_PHOTOS) return 'Please choose up to five photos.';
  for (const file of photos) {
    if (!file || !['image/jpeg', 'image/png'].includes(file.type) || typeof file.arrayBuffer !== 'function') return 'Please choose JPG or PNG photos.';
    if (!file.size || file.size > MAX_REPAIR_PHOTO_BYTES) return 'A photo is too large. Please choose a smaller photo.';
    const bytes = new Uint8Array(await file.slice(0, 8).arrayBuffer());
    const jpeg = bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff;
    const png = [137, 80, 78, 71, 13, 10, 26, 10].every((byte, i) => bytes[i] === byte);
    if (!((file.type === 'image/jpeg' && jpeg) || (file.type === 'image/png' && png))) return 'We couldn’t read a photo. Please choose JPG or PNG photos.';
  }
  return '';
}

// GHL's contact-file endpoint keeps the photos in the contact's file-upload field.
// https://marketplace.gohighlevel.com/docs/ghl/forms/upload-to-custom-fields/
export async function uploadRepairPhotos(photos, {contactId, env, fetcher = fetch}) {
  const body = new FormData();
  for (const [index, file] of photos.entries()) {
    const extension = file.type === 'image/png' ? 'png' : 'jpg';
    body.append(`${env.GHL_REPAIR_PHOTO_FIELD_ID}_${randomUUID()}`, file, `repair-photo-${index + 1}.${extension}`);
  }
  const url = new URL('https://services.leadconnectorhq.com/forms/upload-custom-files');
  url.searchParams.set('contactId', contactId);
  url.searchParams.set('locationId', env.GHL_LOCATION_ID);
  const response = await fetcher(url.toString(), {
    method: 'POST', headers: {Authorization: `Bearer ${env.GHL_PRIVATE_TOKEN}`, Version: 'v3', Accept: 'application/json'},
    body, signal: AbortSignal.timeout(15000),
  });
  if (!response.ok) throw new Error(`GHL photo upload returned HTTP ${response.status}`);
}
