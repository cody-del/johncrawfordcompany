import {submitLead} from './lead.mjs';
import {TOKEN_FIELD, verifyHuman} from './turnstile.mjs';
import {PHONE} from './site.mjs';

// At most 5 leads per visitor per 15 minutes. Kept in memory, so it resets when
// the function instance is recycled; it slows a flood rather than stopping it.
export function createRateLimiter({windowMs = 15 * 60 * 1000, max = 5} = {}) {
  const recent = new Map();
  return (key, now = Date.now()) => {
    if (recent.size > 1000) {
      for (const [stale, times] of recent) if (now - times.at(-1) >= windowMs) recent.delete(stale);
    }
    const times = (recent.get(key) ?? []).filter(time => now - time < windowMs);
    const limited = times.length >= max;
    if (!limited) times.push(now);
    recent.set(key, times);
    return limited;
  };
}

export function createLeadHandler(submit = submitLead, rateLimited = createRateLimiter(), isHuman = verifyHuman) {
  return async (request, context) => {
    const send = (status, body, headers = {}) => Response.json(body, {
      status, headers: {'Cache-Control': 'no-store', ...headers},
    });
    if (request.method !== 'POST') return send(405, {error: 'Method not allowed.'}, {Allow: 'POST'});
    if (request.headers.get('origin') !== new URL(request.url).origin) return send(403, {error: 'Invalid origin.'});
    const contentType = request.headers.get('content-type') ?? '';
    const multipart = contentType.startsWith('multipart/form-data;');
    if (!multipart && !contentType.startsWith('application/json')) return send(415, {error: `Please call ${PHONE} to reach us.`});
    // Binary requests must stay below Netlify’s effective 4.5 MB payload limit.
    const limit = multipart ? 4 * 1024 * 1024 : 16384;
    if (Number(request.headers.get('content-length')) > limit) return send(413, {error: 'Request too large.'});
    let data;
    let photos = [];
    try {
      const reader = request.body?.getReader();
      if (!reader) return send(400, {error: 'Invalid request.'});
      const chunks = [];
      let size = 0;
      while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        size += value.byteLength;
        if (size > limit) {
          await reader.cancel();
          return send(413, {error: 'Request too large.'});
        }
        chunks.push(value);
      }
      const body = Buffer.concat(chunks);
      if (multipart) {
        const fields = await new Request(request.url, {method: 'POST', headers: {'Content-Type': contentType}, body}).formData();
        data = {};
        for (const [name, value] of fields) {
          if (name === 'photos' && typeof value !== 'string') {
            photos.push(value);
          } else {
            if (typeof value !== 'string' || Object.hasOwn(data, name)) return send(400, {error: 'Invalid request.'});
            Object.defineProperty(data, name, {value, enumerable: true, writable: true});
          }
        }
        data.elapsedMs = Number(data.elapsedMs);
        if (data.form !== 'repair' || Object.values(data).some(value => typeof value === 'string' && value.length > 4000)) return send(400, {error: 'Invalid repair request.'});
      } else data = JSON.parse(body.toString('utf8'));
    } catch {
      return send(400, {error: 'Invalid request.'});
    }
    const ip = context?.ip ?? request.headers.get('x-nf-client-connection-ip') ?? 'unknown';
    const token = data?.[TOKEN_FIELD];
    if (data && typeof data === 'object') delete data[TOKEN_FIELD];
    if (!(await isHuman(token, ip))) return send(403, {error: `We couldn’t confirm this request came from a person. Please try again, or call ${PHONE}.`});
    const result = await submit(data, {rateLimited: () => rateLimited(ip), photos});
    return send(result.status, result.body);
  };
}
