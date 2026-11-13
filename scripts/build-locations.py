"""Build individual service-area pages from verified local business information."""
from pathlib import Path
import importlib.util
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
PAGES = json.loads((ROOT / 'content/location-pages.json').read_text())
IMAGES = json.loads((ROOT / 'content/product-images.json').read_text())
spec = importlib.util.spec_from_file_location('company_pages', ROOT / 'scripts/build-company-pages.py')
company = importlib.util.module_from_spec(spec)
spec.loader.exec_module(company)
BASE, e = company.BASE, company.e


def paragraphs(items):
    return ''.join(f'<p>{e(item)}</p>' for item in items)


def link(item):
    return f'<a class="text-link" href="{e(item["href"])}">{e(item["text"])}</a>' if item else ''


def photo(image, priority=False):
    image = IMAGES[image] if isinstance(image, str) else image
    loading = 'fetchpriority="high"' if priority else 'loading="lazy"'
    return (f'<figure class="location-photo"><img src="{e(image["src"])}" alt="{e(image["alt"])}" '
            f'width="{image["width"]}" height="{image["height"]}" {loading} decoding="async">'
            f'<figcaption>{e(image["caption"])}</figcaption>' + link(image.get('link')) + '</figure>')


def head(page):
    html = company.head(page, 'WebPage')
    html = html.replace('</head>', '<link rel="stylesheet" href="/locations.css?v=locations-20261112">\n</head>')
    hero = page['hero_image']
    html = html.replace(BASE + '/assets/john-crawford-logo.png', BASE + hero['src'])
    html = html.replace('content="John Crawford Company — Window Treatments"', f'content="{e(hero["alt"])}"')

    def schema(match):
        graph = json.loads(match.group(1))
        graph[0]['mainEntity'] = {'@id': BASE + page['slug'] + '#service'}
        graph[0]['isPartOf'] = {'@id': BASE + '/service-areas/#page'}
        graph[1]['itemListElement'] = [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': BASE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Areas We Serve', 'item': BASE + '/service-areas/'},
            {'@type': 'ListItem', 'position': 3, 'name': page['name'], 'item': BASE + page['slug']}
        ]
        graph.append({'@context': 'https://schema.org', '@type': 'Service',
                      '@id': BASE + page['slug'] + '#service', 'url': BASE + page['slug'],
                      'name': page['heading'], 'serviceType': 'Custom window treatments',
                      'description': page['description'], 'provider': {'@id': BASE + '/#business'},
                      'areaServed': {'@type': 'Place', 'name': page['name'] + ', California'}})
        return '<script type="application/ld+json">' + json.dumps(graph, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
    return re.sub(r'<script type="application/ld\+json">([\s\S]*?)</script>', schema, html)


def introduction(section):
    picture = ('<div>' + photo(section['image']) + link(section.get('image_link')) + '</div>') if section.get('image') else ''
    modifier = ' location-introduction--photo' if picture else ''
    return (f'<section class="section location-introduction{modifier}" aria-labelledby="introduction-heading">'
            f'<div class="container location-intro-grid">{picture}<div class="location-prose">'
            f'<h2 id="introduction-heading">{e(section["heading"])}</h2>{paragraphs(section["paragraphs"])}'
            + link(section.get('link')) + '</div></div></section>')


def products(page):
    items = ''.join(f'<li><h3><a href="{e(item["href"])}">{e(item["title"])}</a></h3><p>{e(item["text"])}</p></li>' for item in page['products'])
    return (f'<section class="section location-products linen" aria-labelledby="products-heading"><div class="container">'
            f'<div class="location-section-heading"><h2 id="products-heading">{e(page["products_heading"])}</h2>'
            f'<p>{e(page["products_intro"])}</p></div><ul class="location-product-list">{items}</ul></div></section>')


def feature(section):
    return (f'<section class="section location-feature" aria-labelledby="feature-heading"><div class="container location-feature-grid">'
            f'<div class="location-prose"><h2 id="feature-heading">{e(section["heading"])}</h2>{paragraphs(section["paragraphs"])}'
            + link(section.get('link')) + '</div>' + photo(section['image']) + '</div></section>')


def visit(section):
    steps = ''.join(f'<li><h3>{e(step["title"])}</h3><p>{e(step["text"])}</p>'
                    + link({'href': step['href'], 'text': step['link_text']}) + '</li>' for step in section.get('steps', []))
    return (f'<section class="section location-visit" aria-labelledby="visit-heading"><div class="container">'
            f'<div class="location-visit-grid"><h2 id="visit-heading">{e(section["heading"])}</h2>'
            f'<div class="location-prose">{paragraphs(section["paragraphs"])}' + link(section.get('link'))
            + ('<p class="location-guide">' + link(section['guide']) + '</p>' if section.get('guide') else '')
            + '</div></div>' + ('<ol class="location-steps">' + steps + '</ol>' if steps else '') + '</div></section>')


def questions(page):
    items = ''.join(f'<details><summary>{e(item["question"])}</summary><div><p>{e(item["answer"])}</p>'
                    + link(item.get('link')) + '</div></details>' for item in page['faqs'])
    return (f'<section class="section location-questions linen" aria-labelledby="questions-heading"><div class="container location-questions-grid">'
            f'<h2 id="questions-heading">{e(page["questions_heading"])}</h2><div class="location-faq-list">{items}</div></div></section>')


def body(page):
    return f'''<main id="main">
    <section class="section location-hero" aria-labelledby="page-heading"><div class="container location-hero-grid">
      <div class="location-hero-copy"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/service-areas/">Areas We Serve</a><span aria-hidden="true">/</span><span aria-current="page">{e(page['name'])}</span></nav>
      <h1 id="page-heading">{e(page['heading'])}</h1><p>{e(page['intro'])}</p>
      <div class="location-actions"><a class="btn btn-primary" href="/contact/#appointment-form">{e(page['hero_cta'])}</a>
      <a class="text-link" href="{e(page['hero_secondary_href'])}">{e(page['hero_secondary'])}</a></div></div>{photo(page['hero_image'], True)}
    </div></section>
    {introduction(page['introduction'])}{products(page)}
    {feature(page['feature']) if page.get('feature') else ''}{visit(page['visit'])}{questions(page)}
    <section class="section location-contact" aria-labelledby="contact-heading"><div class="container location-contact-grid">
      <div class="location-prose"><h2 id="contact-heading">{e(page['contact_heading'])}</h2><p>{e(page['contact_text'])}</p>
      <a class="text-link" href="/service-areas/">All areas we serve</a></div>{company.contact_details()}
    </div></section></main>'''


if __name__ == '__main__':
    for page in PAGES:
        header, footer, mobile = company.partials(page)
        target = DIST / page['slug'].strip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(head(page) + header + body(page) + footer + mobile + '</body></html>\n')
        print(page['slug'])
