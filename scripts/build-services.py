"""Build the four service pages from reviewed public copy and existing assets."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import json
import re
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
PAGES = json.loads((ROOT / 'content/service-pages.json').read_text())
IMAGES = json.loads((ROOT / 'content/product-images.json').read_text())
IMAGES['powerview-blue'] = {
    'src': '/assets/powerview-wall-remote.jpg', 'width': 1440, 'height': 1080,
    'caption': 'Hunter Douglas PowerView® Automation wall-mounted control',
    'alt': 'A round white wall control beside blue fabric shades and a dark window frame.'
}
spec = importlib.util.spec_from_file_location('company_pages', ROOT / 'scripts/build-company-pages.py')
company = importlib.util.module_from_spec(spec)
spec.loader.exec_module(company)
BASE = company.BASE


def e(value):
    return escape(str(value), quote=True)


def paragraphs(items):
    return ''.join(f'<p>{e(item)}</p>' for item in items)


def email_url(page):
    return 'mailto:john@johncrawford.com?subject=' + quote(page['email_subject'])


def link(item, page):
    href = email_url(page) if item.get('email') else item['href']
    return f'<a class="text-link" href="{e(href)}">{e(item["text"])}</a>'


def links(items, page):
    return '<div class="service-links">' + ''.join(link(item, page) for item in items) + '</div>' if items else ''


def photo(key, hero=False):
    if key is None:
        return '<div class="service-photo-placeholder">Photo placeholder</div>'
    im = IMAGES[key]
    attrs = 'fetchpriority="high"' if hero else 'loading="lazy"'
    return (f'<figure class="service-photo"><img src="{e(im["src"])}" alt="{e(im["alt"])}" '
            f'width="{im["width"]}" height="{im["height"]}" {attrs} decoding="async">'
            f'<figcaption>{e(im["caption"])}</figcaption></figure>')


def head(page):
    html = company.head(page, 'WebPage')
    html = html.replace(f'company-page--{page["name"].lower()}', f'service-page service-page--{page["id"]}')
    html = html.replace('</head>', '<link rel="stylesheet" href="/services.css?v=services-1">\n</head>')
    def service_schema(match):
        graph = json.loads(match.group(1))
        service_id = BASE + page['slug'] + '#service'
        graph[0]['mainEntity'] = {'@id': service_id}
        graph.append({'@context': 'https://schema.org', '@type': 'Service', '@id': service_id,
                      'name': page['name'], 'serviceType': page['name'], 'url': BASE + page['slug'],
                      'description': page['description'], 'provider': graph[0]['publisher'],
                      'areaServed': [{'@type': 'City', 'name': 'Los Angeles'},
                                     {'@type': 'Place', 'name': 'Woodland Hills'}]})
        return '<script type="application/ld+json">' + json.dumps(graph, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
    html = re.sub(r'<script type="application/ld\+json">([\s\S]*?)</script>', service_schema, html)
    if page['hero_image']:
        im = IMAGES[page['hero_image']]
        html = html.replace(BASE + '/assets/john-crawford-logo.png', BASE + im['src'])
        html = html.replace('content="John Crawford Company — Window Treatments"', f'content="{e(im["alt"])}"')
    return html


def overview(section, page):
    anchor = f' id="{e(section["id"])}"' if section.get('id') else ''
    topics = ''.join(f'<article><h3>{e(item["title"])}</h3><p>{e(item["text"])}</p></article>' for item in section.get('topics', []))
    return (f'<section class="section service-overview linen"{anchor} aria-labelledby="overview-heading">'
            f'<div class="container"><div class="service-overview-grid"><h2 id="overview-heading">{e(section["heading"])}</h2>'
            f'<div class="service-prose">{paragraphs(section["paragraphs"])}{links(section.get("links"), page)}</div></div>'
            + (f'<div class="service-topic-grid">{topics}</div>' if topics else '') + '</div></section>')


def feature(section, page):
    anchor = f' id="{e(section["id"])}"' if section.get('id') else ''
    checklist = '<ul class="service-checklist">' + ''.join(f'<li>{e(item)}</li>' for item in section.get('checklist', [])) + '</ul>' if section.get('checklist') else ''
    text = (f'<div class="service-feature-copy service-prose"><h2 id="feature-heading">{e(section["heading"])}</h2>'
            + paragraphs(section['paragraphs']) + links(section.get('links'), page))
    if section.get('note'):
        checklist += f'<p>{e(section["note"])}</p>'
    if section.get('link'):
        checklist += links([section['link']], page)
    if section.get('image'):
        if section.get('link'):
            text += links([section['link']], page)
        inner = photo(section['image']) + text + '</div>'
        css_class = 'service-feature-grid'
    else:
        inner = text + '</div><div class="service-photo-guide">' + checklist + '</div>'
        css_class = 'service-feature-grid service-feature-grid--guide'
    return (f'<section class="section service-feature"{anchor} aria-labelledby="feature-heading">'
            f'<div class="container {css_class}">{inner}</div></section>')


def proof(page):
    if page.get('quote'):
        q = page['quote']
        return (f'<section class="service-proof linen" aria-label="Customer review"><div class="container">'
                f'<figure class="service-customer-quote"><blockquote><p>{e(q["text"])}</p></blockquote>'
                f'<figcaption>{e(q["author"])} <span aria-hidden="true">·</span> {e(q["source"])}</figcaption></figure></div></section>')
    if page.get('story'):
        s = page['story']
        return (f'<section class="section service-story linen" aria-labelledby="story-heading"><div class="container service-overview-grid">'
                f'<h2 id="story-heading">{e(s["heading"])}</h2><div class="service-prose">{paragraphs(s["paragraphs"])}</div></div></section>')
    return ''


def body(page):
    hero = (f'<section class="section service-hero" aria-labelledby="page-heading"><div class="container service-hero-grid">'
            f'<div class="service-hero-copy">{company.breadcrumbs(page)}<h1 id="page-heading">{e(page["heading"])}</h1>'
            f'<p>{e(page["intro"])}</p><div class="service-hero-actions"><a class="btn btn-primary" href="{e(email_url(page))}">{e(page["cta"])}</a>'
            f'<a class="text-link" href="tel:+18188845464">(818) 884-5464</a></div></div>{photo(page["hero_image"], True)}</div></section>')
    faq_items = ''.join(f'<details><summary>{e(item["question"])}</summary><p>{e(item["answer"])}</p></details>' for item in page['faqs'])
    faq_background = '' if page.get('quote') or page.get('story') else ' linen'
    faq = (f'<section class="section service-questions{faq_background}" aria-labelledby="questions-heading"><div class="container questions-grid">'
           f'<div class="questions-intro"><h2 id="questions-heading">{e(page["questions_heading"])}</h2><a class="text-link" href="tel:+18188845464">Ask John: (818) 884-5464</a></div>'
           f'<div class="faq-list">{faq_items}</div></div></section>')
    contact_background = ' linen' if not faq_background else ''
    contact_details = company.contact_details().replace('Window%20treatment%20consultation', quote(page['email_subject']))
    contact = (f'<section class="section service-contact{contact_background}" id="contact" aria-labelledby="contact-heading"><div class="container service-contact-grid">'
               f'<div class="service-prose"><h2 id="contact-heading">{e(page["contact_heading"])}</h2><p>{e(page["contact_text"])}</p>'
               f'{links(page["related"], page)}</div>{contact_details}</div></section>')
    return '<main id="main">' + hero + overview(page['overview'], page) + feature(page['feature'], page) + proof(page) + faq + contact + '</main>'


if __name__ == '__main__':
    for page in PAGES:
        header, footer, mobile = company.partials(page)
        html = head(page) + header + body(page) + footer + mobile + '</body></html>\n'
        target = DIST / page['slug'].strip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html)
        print(page['slug'])
