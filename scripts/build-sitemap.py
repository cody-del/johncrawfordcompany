"""Write dist/sitemap.xml and dist/robots.txt from the indexable pages in dist/.

A page is listed when its robots tag allows indexing, so the /lp/ review copies
(noindex; the live campaign pages are on go.johncrawfordcompany.com) stay out.
build-company-pages.py runs this last; scripts/check-hubs.mjs checks the result.
"""
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
BASE = 'https://www.johncrawfordcompany.com'


def indexable_routes():
    routes = []
    for page in DIST.rglob('index.html'):
        html = page.read_text()
        if 'name="robots" content="index, follow' not in html:
            continue
        relative = page.parent.relative_to(DIST).as_posix()
        routes.append('/' if relative == '.' else f'/{relative}/')
    # Homepage first, then the rest alphabetically, so the file only changes when pages do.
    return sorted(routes, key=lambda route: (route != '/', route))


if __name__ == '__main__':
    urls = ''.join(f'  <url><loc>{escape(BASE + route)}</loc></url>\n' for route in indexable_routes())
    (DIST / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n')
    (DIST / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n')
    print('sitemap.xml + robots.txt')
