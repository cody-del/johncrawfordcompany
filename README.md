# John Crawford Company website review

Static HTML website for John Crawford Company in Woodland Hills, California.

The public review site is https://john-crawford-homepage.codytodd.chatgpt.site/.
Netlify serves the same checked files at https://johncrawfordcompany.netlify.app/.

## Pages

- `/`: approved homepage design.
- `/shades/`, `/blinds/`, `/shutters/`, `/drapery/`, `/motorized-shades/`: first five product hubs, built from the approved copy.
- `/accessibility/`: website assistance and verified business contact details.
- `/lp/custom-window-treatments/`: campaign landing page for blinds, shades, shutters, drapery and motorization.
- `/lp/motorized-shades/`: campaign landing page for motorized and automated shade searches.

## Run locally

No frontend dependency installation or framework build is required. Checks use Node.js and Python 3's standard library.

```sh
npm run check
npm run preview
```

Open http://127.0.0.1:4317/.

## Source and publishing

- `dist/`: ready-to-serve HTML, styles, JavaScript and local assets.
- `content/`: approved public product copy and freshly written image alternatives.
- `scripts/build-hubs.py`: regenerates hub HTML from the public copy and homepage navigation/footer.
- `scripts/check-site.mjs`, `scripts/check-hubs.mjs`: metadata, headings, assets, contact and route checks.
- `scripts/check-customer-copy.py`: blocks recognizable internal writer notes and unfinished copy before publication.

Run `python3 scripts/build-hubs.py` after changing public hub content, then `npm run check`. Generated HTML is committed so all important content is available without JavaScript.

Run `python3 scripts/build-landings.py` to rebuild the campaign pages with the approved branding. Both use taller responsive video heroes, customer reviews, four product image/name cards directly below the reviews, three concise benefits, an introduction to John beside the quote form, and the illustrated Woodland Hills appointment section. The desktop form is on the right: a full-width name field followed by phone/email together; all fields stack on phones. The verified paragraph about John's installation background and his California store opening in 1995 is restored beneath the Woodland Hills heading. Visits remain appointment only; landing pages omit the address and walk-in hours. There are no browsing menus, FAQs, vendor brand rows or off-page links. Privacy and accessibility help open in same-page dialogs. Forms remain disabled previews pending GHL configuration and tested delivery.

`netlify.toml` publishes `dist` and runs `npm run check` before upload. The Netlify project is connected to `main` for continuous deployment. Product images are labeled by collection and are not presented as John Crawford installations.

## Review status

All pages retain `noindex, nofollow` and review canonical URLs. The current production domain has not been migrated. Individual collection, service and location pages remain separate future work. The client-requested upholstery photo placeholder remains on the homepage.

Private intake records, transcripts, dealer policies, local credentials and QA artifacts are excluded from this repository.
