# John Crawford Company website

Static HTML website for John Crawford Company in Woodland Hills, California.

The live site is https://www.johncrawfordcompany.com/, served by the Netlify site `johncrawfordcompany` (also at https://johncrawfordcompany.netlify.app/).

## Pages

- `/`: approved homepage design.
- `/shades/`, `/blinds/`, `/shutters/`, `/drapery/`, `/motorized-shades/`: first five product hubs, built from the approved copy.
- `/about/`, `/contact/`: company story and contact form design.
- `/services/blind-shade-repair/`, `/services/consultation-measuring/`, `/services/window-treatment-installation/`, `/services/commercial-window-treatments/`, `/upholstery/`: service pages based on the call and intake.
- `/accessibility/`, `/privacy/`, `/terms/`: website assistance, privacy information and website terms of service.

The campaign landing pages are not part of this site: they live at https://go.johncrawfordcompany.com/ and `/motorized-shades/` (`cody-del/johncrawfordlanding`). Their old review copies here, `/lp/custom-window-treatments/` and `/lp/motorized-shades/`, were removed on November 6, 2026; `dist/_redirects` sends those addresses (and anything under `/lp/`) to the go. pages with permanent (301) redirects.

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

`netlify.toml` publishes `dist` and runs `npm run check` before upload. The Netlify project is connected to `main` for continuous deployment. Product images are labeled by collection and are not presented as John Crawford installations.

The shared header uses **Request a consultation** as its Contact-page link, without a duplicate Contact navigation item. Its circular **Call now** control reveals the phone number as a tap-to-call link; Escape and clicking outside close it. The homepage hero and mobile consultation action also link to `/contact/`.

## Lead forms and GoHighLevel

The product hub, contact and repair forms post to `/api/lead` (`netlify/functions/lead.mjs`, with validation and GHL requests in `netlify/lib/lead.mjs`). The server upserts the contact and saves a complete submission snapshot in the existing **Latest inquiry details** contact field (`contact.latest_inquiry_details`, ID `INk19lHx5XU2HQQhdFNQ`). It then saves a contact note. The **Note Added** workflow uses that note for the shared welcome email and the inquiry-specific internal email. Tags label the request; adding tags or using Contact Created does not replace the saved-note handoff.

Netlify uses `GHL_PRIVATE_TOKEN` and `GHL_LOCATION_ID`. The John Crawford location is `90BPGKl4VhW1sRil5f6b`. Optional repair uploads also require `GHL_REPAIR_PHOTO_FIELD_ID` (the existing private **Repair request photos** field, `OFy6KwIA4iCqESEDU8gQ`) and `forms.write` on the location token. Reuse the verified fields below; do not create duplicates.

### Contact form mapping — verified November 5, 2026

Name, phone, email and ZIP use the existing standard contact fields. The Contact object was checked before adding the three missing fields below; reuse these IDs for future forms instead of creating equivalents.

| Website input name | GHL field | Field ID |
| --- | --- | --- |
| `product` | Product interest — single dropdown, `contact.product_interest` | `2I2MvrMS6CKqDxaKLzYv` |
| `appointment-type` | Appointment type — radio select, `contact.appointment_type` | `SKg45GOfgzh35A9YFPXF` |
| `message` | Message — multi line, `contact.message` | `FrUjsXAor23MmsUeT3c4` |

Product choices are Shades, Blinds, Shutters, Drapery, Motorized shades and Not sure yet. Appointment choices are Free in-home consultation and Showroom visit. GHL receives these readable labels, not the website's internal option values. Appointment choice is optional: a blank answer omits that custom-field update rather than clearing an earlier preference. All other visible contact-form fields are required.

Every submitted answer also remains in **Latest inquiry details** and the saved submission note. The note begins `John Crawford form submission: Website lead`, followed by `Source: Website: Contact page`, preserving the existing Note Added workflow. No additional environment variables or custom fields for name, phone, email or ZIP are needed.

### Repair form contract — verified November 5, 2026

| Website input name | Required | Destination |
| --- | --- | --- |
| `name` | Yes | Standard first/last name, split from the full name; complete name in inquiry details and note |
| `phone` | Yes | Standard phone normalized to `+1XXXXXXXXXX`; inquiry details and note |
| `email` | Yes | Standard email; inquiry details and note |
| `postal-code` | Yes | Standard five-digit `postalCode`; inquiry details and note |
| `problem` | Yes | What’s broken? — multi line, `contact.whats_broken`, ID `OfVLHC3hwaE9autFcPpz`; inquiry details and note, labeled `What’s broken` |
| `purchased-when` | No | When did you buy the product? — date picker, `contact.when_did_you_buy_the_product`, ID `RuaSSSqBjgysltRF496w`; inquiry details and note, labeled `Bought` |
| `purchased-from` | No | Where did you buy it? — single line, `contact.where_did_you_buy_it`, ID `mPeAbxuP1EXJ5FRkmD7K`; inquiry details and note, labeled `Bought from` |
| `photos` | No | Existing private Repair request photos file field |

These three repair-answer fields were added in GHL by the user and verified in the Contact object on November 5, 2026. The website reuses their exact IDs. The optional purchase-date input uses a native date picker and sends a validated `YYYY-MM-DD` value without timezone conversion. Blank optional purchase answers omit those field updates rather than clearing earlier contact values. The form labels match the GHL questions; no new CRM fields are created by the integration.

Repair routing stays `form = repair`, `source = Website: Repair page`, with both `website-lead` and `website-repair-request` tags. First upsert the contact and inquiry details, then finish optional photo processing, then create the contact note. When photos are attached, the upsert leaves the tags off and they are added last (`POST /contacts/{id}/tags`, retried through the upsert if that fails): the tags start the **JC | 01 Form Inquiries** workflow, and its repair alert email shows `{{contact.repair_request_photos}}`, so the photos must already be saved. Without photos, the tags go on in the first upsert as before. Its first two lines must be exactly:

```text
John Crawford form submission: Website repair request
Source: Website: Repair page
```

The snapshot includes the full name, normalized phone, email, source, every supplied repair answer and selected photo count. The final note repeats those details and adds photo-upload success or failure after processing. Blank optional answers are omitted. The browser converts selected JPG/PNG/WebP images to compact JPEGs before upload; the backend accepts up to five JPG/PNG photos at **650 KiB each**. Preserve this conversion step and do not send WebP directly to the backend. If a photo upload fails after the contact is saved, preserve the inquiry, record the failure in its note and show the email fallback.

The hidden `website` field, minimum three-second fill time, same-origin checks and five-request/15-minute visitor limit remain in place. `netlify/lib/site.mjs` defines each form's fields and labels; `app.js` handles validation and photo preparation. Form markup comes from `scripts/build-hubs.py`, `scripts/build-company-pages.py` and `scripts/build-services.py`. `npm run check` includes the mapping, upload and note-order tests; those use a mocked GHL service and do not send live workflow emails.

## Spam protection

Every lead form goes through these checks in `/api/lead` before anything reaches GHL:

- **Cloudflare Turnstile.** `dist/app.js` adds an invisible human check to each form. Visitors only see a checkbox if Cloudflare wants one. `netlify/lib/turnstile.mjs` (identical in `johncrawfordcompany` and `johncrawfordlanding`) checks the token with Cloudflare and refuses the lead with a 403 when the token is missing or refused. If Cloudflare can't be reached, the lead goes through rather than being lost. One widget, made in the gbp@shadestrategy.com Cloudflare account, covers `www.johncrawfordcompany.com`, `johncrawfordcompany.com` and `go.johncrawfordcompany.com`. Its site key, `0x4AAAAAAF1MJ5a53NsFXu0h`, is `TURNSTILE_SITE_KEY` in `dist/app.js` (public, in the page) and its secret is the Netlify variable `TURNSTILE_SECRET_KEY` (Production, Functions, secret). Other hosts, such as deploy previews, use Cloudflare's always-pass test site key; give Deploy Previews the test secret `1x0000000000000000000000000000000AA`, or no secret, which switches the check off. Netlify functions read the secret at deploy time, so redeploy after setting it.
- **Netlify rate limit.** `netlify/functions/lead.mjs` limits each visitor (IP + domain) to 10 requests per 3 minutes. Netlify counts these itself, for every copy of the function and across restarts, and answers with a 429.
- **In the function:** a hidden `website` field, a 3-second minimum after page load, same-origin JSON only, size limits, field checks, and an in-memory limit of 5 leads per visitor per 15 minutes.

## Service-page content and reviews

The Consultation & Measuring and Installation pages have a full editorial rewrite covering the free home visit, samples in the room, measuring, product choices, quote planning, installation and compatible controls. The installation copy preserves the explanation of checking width and height at several points and looking at whether the opening is square and level. New project-detail panels and relevant questions make the content easier to scan. Service testimonials use a white card on linen, readable five-star ratings, a Google attribution and the existing customer wording. The consultation page pairs John’s one-window story with an approved customer review.

Repair, Commercial Window Treatments and Upholstery also have expanded editorial content. Repair explains useful symptom/photo information, parts and condition, and repair-versus-replacement decisions. Commercial covers room use, glare, privacy, controls, project planning and the approved Western Bagel and The Izaka-ya by Katsu-ya references. Upholstery covers reasons to keep a piece, samples and specialist assessment, fabric selection, possible shape changes and honest cost comparisons. The repair form sends its answers to GHL and asks visitors to email photos, and the requested upholstery photo placeholder remains.

## Indexing

Every page is indexable (`index, follow, max-image-preview:large`) with a canonical URL on https://www.johncrawfordcompany.com, set by `BASE` in `scripts/build-*.py` and by hand in `dist/index.html`. `scripts/build-sitemap.py`, run last by `npm run build:company`, writes `dist/sitemap.xml` from the indexable pages and `dist/robots.txt`; `check-hubs.mjs` fails if the sitemap and the pages disagree. Individual collection and location pages remain separate future work. The five service pages are linked through the shared Services navigation. Consultation & Measuring and Installation have separate URLs and headings. Both emphasize a free in-home consultation with samples brought to the home and measurements taken there; their primary actions lead to the central contact form. The old installation-page #measuring link forwards to the consultation page. The client-requested upholstery photo placeholder remains on the homepage and upholstery preview page.

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
