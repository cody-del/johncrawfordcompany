// What this site's forms send to GoHighLevel; netlify/lib/lead.mjs does the sending.
export const PHONE = '(818) 884-5464';

// Every website lead gets this tag. John Crawford's GHL lead workflow should
// trigger on it; renaming it detaches every new lead from that workflow without
// any error, so change the GHL trigger in the same sitting.
export const LEAD_TAG = 'website-lead';

const ZIP = {
  name: 'postal-code', label: 'ZIP code', max: 5, required: true, contactField: 'postalCode',
  pattern: /^\d{5}$/, error: 'Please enter a 5-digit ZIP code.',
};

// Each form names its fields, with the names the page's inputs use. A field with
// `tags` adds the tag for its value, one with `contactField` sets that contact
// field, and every answer is also written in the contact's note.
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
        options: {shades: 'Shades', blinds: 'Blinds', shutters: 'Shutters', drapery: 'Drapery', 'motorized-shades': 'Motorized shades', 'not-sure': 'Not sure yet'},
      },
      ZIP,
      {
        name: 'appointment-type', label: 'I’d like to schedule', max: 20,
        options: {'in-home': 'Free in-home consultation', showroom: 'Showroom visit'},
        tags: {'in-home': 'in-home-consultation', showroom: 'showroom-appointment'},
      },
      {name: 'message', label: 'Message', max: 3000, required: true},
    ],
  },
  repair: {
    source: 'Website: Repair page',
    pages: {},
    fields: [
      {name: 'problem', label: 'What’s broken', max: 3000, required: true},
      {name: 'purchased-when', label: 'Bought', max: 80},
      {name: 'purchased-from', label: 'Bought from', max: 160},
      ZIP,
    ],
  },
};
