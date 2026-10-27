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

Run `python3 scripts/build-landings.py` to rebuild the two campaign pages with the approved website's branding. Both inherit `styles.css`; additions in `landings.css` are scoped to landing pages. Each has three main sections: a short outcome offer with the three-field quote form in the opening section, four selected customer reviews, and the illustrated Woodland Hills trust section. Landing-page copy is written separately from the website; catalog blocks, service explanations and the website's showroom story are omitted. Woodland Hills artwork, address and hours are preserved. There are no browsing menus, FAQs or off-page links. Every conversion action says Call Us or Get Free Quote; privacy and accessibility assistance open in same-page dialogs. Quote forms remain disabled design previews pending actual GHL configuration and tested delivery to John and Max; telephone links are active.

`netlify.toml` publishes `dist` and runs `npm run check` before upload. The Netlify project is connected to `main` for continuous deployment. Product images are labeled by collection and are not presented as John Crawford installations.

## Review status

All pages retain `noindex, nofollow` and review canonical URLs. The current production domain has not been migrated. Individual collection, service and location pages remain separate future work. The client-requested upholstery photo placeholder remains on the homepage.

Private intake records, transcripts, dealer policies, local credentials and QA artifacts are excluded from this repository.
