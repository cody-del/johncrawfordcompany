import {repairUploadsConfigured} from '../lib/repair-photos.mjs';

export default async function handler(request) {
  if (request.method !== 'GET') return Response.json({error: 'Method not allowed.'}, {status: 405, headers: {Allow: 'GET'}});
  return Response.json({enabled: repairUploadsConfigured()}, {headers: {'Cache-Control': 'no-store'}});
}
export const config = {path: '/api/repair-upload'};
