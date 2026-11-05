// What this site's forms send to GoHighLevel; netlify/lib/lead.mjs does the sending.
export const PHONE = '(818) 884-5464';

// Every website lead gets this label; repair requests also get their own tag.
// The saved submission note triggers the Note Added email workflow. Neither
// these tags nor Contact Created replaces that handoff.
export const LEAD_TAG = 'website-lead';

const ZIP = {
  name: 'postal-code', label: 'ZIP code', max: 5, required: true, contactField: 'postalCode',
  pattern: /^\d{5}$/, error: 'Please enter a 5-digit ZIP code.',
};

// Each form names its fields, with the names the page's inputs use. A field with
// `tags` adds the tag for its value, `contactField` sets a standard contact field,
// and `customFieldId` reuses a verified GHL field. Every answer also goes in the note.
export const FORMS = {
  // The short form on each product hub.
  consultation: {
    source: 'Website: Product page',
    pages: {
      '/shades/': 'Website: Shades page',
      '/blinds/': 'Website: Blinds page',
      '/shutters/': 'Website: Shutters page',
      '/drapery/': 'Website: Drapery page',
      '/motorized-shades/': 'Website: Motorized Shades page',
    },
    fields: [],
  },
  contact: {
    source: 'Website: Contact page',
    pages: {},
    fields: [
      {
        name: 'product', label: 'Product interest', max: 20, required: true,
        customFieldId: '2I2MvrMS6CKqDxaKLzYv',
        options: {shades: 'Shades', blinds: 'Blinds', shutters: 'Shutters', drapery: 'Drapery', 'motorized-shades': 'Motorized shades', 'not-sure': 'Not sure yet'},
      },
      ZIP,
      {
        name: 'appointment-type', label: 'I’d like to schedule', max: 20,
        customFieldId: 'SKg45GOfgzh35A9YFPXF',
        options: {'in-home': 'Free in-home consultation', showroom: 'Showroom visit'},
        tags: {'in-home': 'in-home-consultation', showroom: 'showroom-appointment'},
      },
      {name: 'message', label: 'Message', max: 3000, required: true, customFieldId: 'FrUjsXAor23MmsUeT3c4'},
    ],
  },
  repair: {
    source: 'Website: Repair page',
    tags: ['website-repair-request'],
    pages: {},
    fields: [
      {name: 'problem', label: 'What’s broken', max: 3000, required: true, customFieldId: 'OfVLHC3hwaE9autFcPpz'},
      {name: 'purchased-when', label: 'Bought', max: 10, format: 'date', customFieldId: 'RuaSSSqBjgysltRF496w'},
      {name: 'purchased-from', label: 'Bought from', max: 160, customFieldId: 'mPeAbxuP1EXJ5FRkmD7K'},
      ZIP,
    ],
  },
};
