# John Crawford Company homepage

Static HTML homepage for John Crawford Company in Woodland Hills, California.

The current review site is https://john-crawford-homepage.codytodd.chatgpt.site/.

## Run locally

No dependency installation or build step is required. Use Node.js for checks and Python 3 for the local preview.

```sh
npm run check
npm run preview
```

Open http://127.0.0.1:4317/.

## Files

- `dist/index.html`: homepage content, metadata, and business structured data.
- `dist/styles.css`: responsive layout and branding.
- `dist/app.js`: navigation, review carousel, dialogs, and hero video controls.
- `dist/assets/`: fonts, branding, product photography, illustrations, and silent hero video.
- `scripts/check-site.mjs`: homepage checks.
- `.openai/hosting.json`: existing Sites project and static directory configuration.

Serve `dist/` as the website root when deploying to a static host. `netlify.toml` sets the Netlify publish directory to `dist` and runs the homepage checks before deployment. The Netlify project is connected to this repository's `main` branch for continuous deployment.

## Review status

This is the homepage review version. It intentionally retains `noindex, nofollow` and a temporary canonical URL. Interior pages, a gallery, and final launch configuration remain pending approval. The client-requested upholstery photo placeholder is retained.

Client reference documents, local workflow state, credentials, and QA screenshots are not included in this repository.
