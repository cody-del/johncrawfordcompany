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

Run `python3 scripts/build-landings.py` to rebuild the campaign pages using the approved branding. Each has five focused sections: hero, selected reviews, the approved quote form, four product image/name cards, and the illustrated appointment-only Woodland Hills section. General cards show blinds, shades, shutters and drapery; the motorized page shows four shade styles. Cards have no descriptions or browsing links. The Hunter Douglas/Alta brand row is removed; the general hero retains its video pause control. Desktop service headlines stay on one line, with natural wrapping on narrow phones, and the hero panel uses an 88% linen background. The quote section is unchanged: three contact fields across on desktop, stacked on mobile, plus the optional showroom appointment checkbox. Showroom visits require an appointment; the landing pages omit the address and walk-in hours. Quote and call actions remain focused on the same-page form and telephone, with Schedule Appointment in the showroom section. Privacy and accessibility help open in same-page dialogs. Forms remain inactive previews pending GHL configuration and tested delivery.

`netlify.toml` publishes `dist` and runs `npm run check` before upload. The Netlify project is connected to `main` for continuous deployment. Product images are labeled by collection and are not presented as John Crawford installations.

## Review status

All pages retain `noindex, nofollow` and review canonical URLs. The current production domain has not been migrated. Individual collection, service and location pages remain separate future work. The client-requested upholstery photo placeholder remains on the homepage.

Private intake records, transcripts, dealer policies, local credentials and QA artifacts are excluded from this repository.
