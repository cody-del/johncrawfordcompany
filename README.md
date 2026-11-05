# John Crawford Company website

Static HTML website for John Crawford Company in Woodland Hills, California.

The live site is https://www.johncrawfordcompany.com/, served by the Netlify site `johncrawfordcompany` (also at https://johncrawfordcompany.netlify.app/).

## Pages

- `/`: approved homepage design.
- `/shades/`, `/blinds/`, `/shutters/`, `/drapery/`, `/motorized-shades/`: first five product hubs, built from the approved copy.
- `/about/`, `/contact/`: company story and contact form design.
- `/services/blind-shade-repair/`, `/services/consultation-measuring/`, `/services/window-treatment-installation/`, `/services/commercial-window-treatments/`, `/upholstery/`: service pages based on the call and intake.
- `/accessibility/`, `/privacy/`, `/terms/`: website assistance, privacy information and website terms of service.
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

Run `python3 scripts/build-landings.py` to rebuild the campaign pages with the approved branding. Both use taller responsive video heroes, customer reviews, four product image/name cards directly below the reviews, three concise benefits in a contained linen panel with a subtle magenta accent, the illustrated Woodland Hills appointment section, and an introduction to John beside the quote form as the final main section. The appointment copy offers a showroom appointment or free in-home consultation. The desktop form is on the right: a full-width name field followed by phone/email together; all fields stack on phones. An optional appointment radio group leads with Free in-home consultation, followed by Showroom appointment, with neither selected by default. The showroom appointment notice, instruction and CTA are grouped beneath a fine divider with a small calendar icon. The verified paragraph about John's installation background and his California store opening in 1995 is restored beneath the Woodland Hills heading. Visits remain appointment only; landing pages omit the address and walk-in hours. There are no browsing menus, FAQs or vendor brand rows; the only off-page links are the footer's Accessibility, Privacy Policy and Terms of Service pages, matching the live landing pages. The quote form's privacy notice opens a short same-page summary that links to the full policy. The campaign forms here remain disabled review copies; the live landing pages, whose forms send to GHL, are in `cody-del/johncrawfordlanding`.

`netlify.toml` publishes `dist` and runs `npm run check` before upload. The Netlify project is connected to `main` for continuous deployment. Product images are labeled by collection and are not presented as John Crawford installations.

## Lead forms and GoHighLevel

The product hub, contact and repair forms post to `/api/lead` (`netlify/functions/lead.mjs`, with validation and GHL requests in `netlify/lib/lead.mjs`). The server upserts the contact and saves a complete submission snapshot in the existing **Latest inquiry details** contact field (`contact.latest_inquiry_details`, ID `INk19lHx5XU2HQQhdFNQ`). It then saves a contact note. The **Note Added** workflow uses that note for the shared welcome email and the inquiry-specific internal email. Tags label the request; adding tags or using Contact Created does not replace the saved-note handoff.

Netlify uses `GHL_PRIVATE_TOKEN` and `GHL_LOCATION_ID`. The John Crawford location is `90BPGKl4VhW1sRil5f6b`. Optional repair uploads also require `GHL_REPAIR_PHOTO_FIELD_ID` (the existing private **Repair request photos** field, `OFy6KwIA4iCqESEDU8gQ`) and `forms.write` on the location token. Reuse these fields; do not create separate repair-answer fields.

### Repair form contract — verified November 5, 2026

| Website input name | Required | Destination |
| --- | --- | --- |
| `name` | Yes | Standard first/last name, split from the full name; complete name in inquiry details and note |
| `phone` | Yes | Standard phone normalized to `+1XXXXXXXXXX`; inquiry details and note |
| `email` | Yes | Standard email; inquiry details and note |
| `postal-code` | Yes | Standard five-digit `postalCode`; inquiry details and note |
| `problem` | Yes | Inquiry details and note, labeled `What’s broken` |
| `purchased-when` | No | Inquiry details and note, labeled `Bought` |
| `purchased-from` | No | Inquiry details and note, labeled `Bought from` |
| `photos` | No | Existing private Repair request photos file field |

Repair routing stays `form = repair`, `source = Website: Repair page`, with both `website-lead` and `website-repair-request` tags. First upsert the contact and inquiry details, then finish optional photo processing, then create the contact note. Its first two lines must be exactly:

```text
John Crawford form submission: Website repair request
Source: Website: Repair page
```

The snapshot includes the full name, normalized phone, email, source, every supplied repair answer and selected photo count. The final note repeats those details and adds photo-upload success or failure after processing. Blank optional answers are omitted. The browser converts selected JPG/PNG/WebP images to compact JPEGs before upload; the backend accepts up to five JPG/PNG photos at **650 KiB each**. Preserve this conversion step and do not send WebP directly to the backend. If a photo upload fails after the contact is saved, preserve the inquiry, record the failure in its note and show the email fallback.

The hidden `website` field, minimum three-second fill time, same-origin checks and five-request/15-minute visitor limit remain in place. `netlify/lib/site.mjs` defines each form's fields and labels; `app.js` handles validation and photo preparation. Form markup comes from `scripts/build-hubs.py`, `scripts/build-company-pages.py` and `scripts/build-services.py`. `npm run check` includes the mapping, upload and note-order tests; those use a mocked GHL service and do not send live workflow emails.

## Service-page content and reviews

The Consultation & Measuring and Installation pages have a full editorial rewrite covering the free home visit, samples in the room, measuring, product choices, quote planning, installation and compatible controls. The installation copy preserves the explanation of checking width and height at several points and looking at whether the opening is square and level. New project-detail panels and relevant questions make the content easier to scan. Service testimonials use a white card on linen, readable five-star ratings, a Google attribution and the existing customer wording. The consultation page pairs John’s one-window story with an approved customer review.

Repair, Commercial Window Treatments and Upholstery also have expanded editorial content. Repair explains useful symptom/photo information, parts and condition, and repair-versus-replacement decisions. Commercial covers room use, glare, privacy, controls, project planning and the approved Western Bagel and The Izaka-ya by Katsu-ya references. Upholstery covers reasons to keep a piece, samples and specialist assessment, fabric selection, possible shape changes and honest cost comparisons. The repair form sends its answers to GHL and asks visitors to email photos, and the requested upholstery photo placeholder remains.

## Indexing

Every page except the `/lp/` review copies is indexable (`index, follow, max-image-preview:large`) with a canonical URL on https://www.johncrawfordcompany.com, set by `BASE` in `scripts/build-*.py` and by hand in `dist/index.html`. The `/lp/` copies stay `noindex, nofollow`, because the live campaign pages are on go.johncrawfordcompany.com (`cody-del/johncrawfordlanding`). `scripts/build-sitemap.py`, run last by `npm run build:company`, writes `dist/sitemap.xml` from the indexable pages and `dist/robots.txt`; `check-hubs.mjs` fails if the sitemap and the pages disagree. Individual collection and location pages remain separate future work. The five service pages are linked through the shared Services navigation. Consultation & Measuring and Installation have separate URLs and headings. Both emphasize a free in-home consultation with samples brought to the home and measurements taken there; their primary actions lead to the central contact form. The old installation-page #measuring link forwards to the consultation page. The client-requested upholstery photo placeholder remains on the homepage and upholstery preview page.

Private intake records, transcripts, dealer policies, local credentials and QA artifacts are excluded from this repository.

## Domain launch (redirects from the old dealer site)

www.johncrawfordcompany.com used to point at the Hunter Douglas dealer site (`www` CNAME `10044210.hd-website.com`; the domain and DNS are at GoDaddy). On November 5, 2026 the GoDaddy DNS was moved to Netlify. `launch/legacy-redirects.txt` maps every old URL in `launch/old-site-urls.txt` (the 46 sitemap URLs plus Contact Us, Promotions, Accessibility and Contact from its navigation) to the closest page here with a permanent (301) redirect. Old product pages go to their product hub; nothing reuses Hunter Douglas's product text. The map is **live**: `dist/_redirects` is a copy of it. `node scripts/check-redirects.mjs` (part of `npm run check`) requires every old URL to be a page here or covered by a rule, every target to be a page in `dist/`, no redirect chains, lowercase sources, and `dist/_redirects`, once it exists, to be an exact copy of the map.

Launch order, with John's OK (steps 2–4 are done):

1. Before the move: verify a Search Console **Domain** property for johncrawfordcompany.com through a DNS TXT record at GoDaddy (this doesn't affect the current site) and note the old site's top pages.
2. Switch indexing on: replace `noindex, nofollow` with indexable robots tags and point `BASE` (canonical URLs) in `scripts/build-*.py` at `https://www.johncrawfordcompany.com`, then update the checks that require review indexing (`check-site.mjs`, `check-hubs.mjs`). Add `dist/sitemap.xml` (the site has none yet) and a `dist/robots.txt` that points to it.
3. `cp launch/legacy-redirects.txt dist/_redirects`, run `npm run check`, merge.
4. Add www.johncrawfordcompany.com (primary) and the apex to the Netlify site, then change the GoDaddy DNS: `www` CNAME to the Netlify site and the apex to Netlify's load balancer.
5. Spot-check a few old URLs (`curl -sI https://www.johncrawfordcompany.com/hunter-douglas/shades/cellular-shades/duette` should return 301 to `/shades/`), submit the new sitemap in Search Console, and update the website link on the Google Business Profile.
6. For two to four weeks, watch Search Console's Pages report for 404s and add rules for any old URL this list missed.
