# John Crawford Company website review

Static HTML website for John Crawford Company in Woodland Hills, California.

The public review site is https://john-crawford-homepage.codytodd.chatgpt.site/.
Netlify serves the same checked files at https://johncrawfordcompany.netlify.app/.

## Pages

- `/`: approved homepage design.
- `/shades/`, `/blinds/`, `/shutters/`, `/drapery/`, `/motorized-shades/`: first five product hubs, built from the approved copy.
- `/about/`, `/contact/`: company story and contact form design.
- `/services/blind-shade-repair/`, `/services/consultation-measuring/`, `/services/window-treatment-installation/`, `/services/commercial-window-treatments/`, `/upholstery/`: service pages based on the call and intake.
- `/accessibility/`, `/privacy/`: website assistance, contact and privacy information.
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

Run `npm run build:company` after changing public website content to regenerate hubs, company pages and services, then `npm run check`. Generated HTML is committed so all important content is available without JavaScript.

Run `python3 scripts/build-landings.py` to rebuild the campaign pages with the approved branding. Both use taller responsive video heroes, customer reviews, four product image/name cards directly below the reviews, three concise benefits in a contained linen panel with a subtle magenta accent, the illustrated Woodland Hills appointment section, and an introduction to John beside the quote form as the final main section. The appointment copy offers a showroom appointment or free in-home consultation. The desktop form is on the right: a full-width name field followed by phone/email together; all fields stack on phones. An optional appointment radio group leads with Free in-home consultation, followed by Showroom appointment, with neither selected by default. The showroom appointment notice, instruction and CTA are grouped beneath a fine divider with a small calendar icon. The verified paragraph about John's installation background and his California store opening in 1995 is restored beneath the Woodland Hills heading. Visits remain appointment only; landing pages omit the address and walk-in hours. There are no browsing menus, FAQs, vendor brand rows or off-page links. Privacy and accessibility help open in same-page dialogs. Forms remain disabled previews pending GHL configuration and tested delivery.

`netlify.toml` publishes `dist` and runs `npm run check` before upload. The Netlify project is connected to `main` for continuous deployment. Product images are labeled by collection and are not presented as John Crawford installations.

## Service-page content and reviews

The Consultation & Measuring and Installation pages have a full editorial rewrite covering the free home visit, samples in the room, measuring, product choices, quote planning, installation and compatible controls. The installation copy preserves the explanation of checking width and height at several points and looking at whether the opening is square and level. New project-detail panels and relevant questions make the content easier to scan. Service testimonials use a white card on linen, readable five-star ratings, a Google attribution and the existing customer wording. The consultation page pairs John’s one-window story with an approved customer review.

Repair, Commercial Window Treatments and Upholstery also have expanded editorial content. Repair explains useful symptom/photo information, parts and condition, and repair-versus-replacement decisions. Commercial covers room use, glare, privacy, controls, project planning and the approved Western Bagel and The Izaka-ya by Katsu-ya references. Upholstery covers reasons to keep a piece, samples and specialist assessment, fabric selection, possible shape changes and honest cost comparisons. The existing repair form remains a disabled preview, and the requested upholstery photo placeholder remains.

## Review status

All pages retain `noindex, nofollow` and review canonical URLs. The current production domain has not been migrated. Individual collection and location pages remain separate future work. The five service pages are linked through the shared Services navigation. Consultation & Measuring and Installation have separate URLs and headings. Both emphasize a free in-home consultation with samples brought to the home and measurements taken there; their primary actions lead to the central contact form. The old installation-page #measuring link forwards to the consultation page. The client-requested upholstery photo placeholder remains on the homepage and upholstery preview page.

Private intake records, transcripts, dealer policies, local credentials and QA artifacts are excluded from this repository.
