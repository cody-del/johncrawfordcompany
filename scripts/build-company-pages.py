"""Build the company pages, service-area directory and blog."""
from pathlib import Path
from html import escape
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
CONTENT = json.loads((ROOT / 'content/company-pages.json').read_text())
BLOG_POSTS = json.loads((ROOT / 'content/blog-posts.json').read_text())
SERVICE_AREAS = json.loads((ROOT / 'content/service-areas.json').read_text())
HOURS = json.loads((ROOT / 'content/business-hours.json').read_text())
BASE = 'https://www.johncrawfordcompany.com'
DIRECTIONS = 'https://www.google.com/maps/search/?api=1&query=John+Crawford+Company+22311+Ventura+Blvd+Woodland+Hills'


def e(value):
    return escape(str(value), quote=True)


def paragraphs(items):
    return '\n'.join(f'<p>{e(text)}</p>' for text in items)


def update_navigation():
    path = DIST / 'index.html'
    text = path.read_text()
    text = text.replace('<a href="#about">About</a>', '<a href="/about/">About</a>')
    text = text.replace('<a href="#contact">Contact</a>', '<a href="/contact/">Contact</a>')
    service_destinations = {
        'consultation': '/services/consultation-measuring/',
        'installation': '/services/window-treatment-installation/',
        'repairs': '/services/blind-shade-repair/',
        'upholstery': '/upholstery/',
        'commercial': '/services/commercial-window-treatments/'
    }
    for anchor, destination in service_destinations.items():
        text = text.replace(f'href="#{anchor}"', f'href="{destination}"')
    for legacy, destination in {
        '/services/window-treatment-installation/#measuring': service_destinations['consultation'],
        '/services/window-treatment-installation/#installation': service_destinations['installation']
    }.items():
        text = text.replace(f'href="{legacy}"', f'href="{destination}"')
    services = {page['id']: page for page in json.loads((ROOT / 'content/service-pages.json').read_text())}
    links = '\n'.join(
        f'            <a href="{e(services[key]["slug"])}">{e(services[key]["name"])}</a>'
        for key in ['consultation', 'installation', 'repair', 'commercial', 'upholstery']
    )
    dropdown = f'''<details class="nav-dropdown" name="navigation">
          <summary>Services</summary>
          <div class="dropdown-panel">
{links}
          </div>
        </details>'''
    text, count = re.subn(
        r'<details class="nav-dropdown" name="navigation">\s*<summary>Services</summary>[\s\S]*?</details>',
        lambda match: dropdown, text, count=1
    )
    if count != 1:
        raise ValueError('Expected one Services navigation dropdown on the homepage')
    path.write_text(text)


def partials(page):
    home = (DIST / 'index.html').read_text()
    pieces = [re.search(pattern, home).group() for pattern in [
        r'<header class="site-header">[\s\S]*?</header>',
        r'<footer class="site-footer"[\s\S]*?</footer>',
        r'<div class="mobile-contact"[\s\S]*?</div>'
    ]]
    result = []
    for text in pieces:
        text = text.replace('src="assets/', 'src="/assets/')
        text = text.replace('href="#top"', 'href="/"').replace('back to top', 'home')
        for anchor in ['consultation', 'installation', 'repairs', 'upholstery', 'commercial']:
            text = text.replace(f'href="#{anchor}"', f'href="/#{anchor}"')
        text = text.replace('href="#contact"', 'href="/contact/"')
        text = text.replace(f'href="{page["slug"]}"', f'href="{page["slug"]}" aria-current="page"')
        result.append(text)
    return result


def head(page, kind):
    business = {
        '@type': 'HomeGoodsStore', '@id': 'https://www.johncrawfordcompany.com/#business',
        'name': 'John Crawford Company', 'telephone': '+1-818-884-5464',
        'email': 'john@johncrawford.com',
        'address': {'@type': 'PostalAddress', 'streetAddress': '22311 Ventura Blvd #101',
                    'addressLocality': 'Woodland Hills', 'addressRegion': 'CA',
                    'postalCode': '91364', 'addressCountry': 'US'},
        'openingHoursSpecification': [{'@type': 'OpeningHoursSpecification',
            'dayOfWeek': HOURS['days'],
            'opens': HOURS['opens'], 'closes': HOURS['closes']}]
    }
    schema = [{
        '@context': 'https://schema.org', '@type': kind,
        '@id': BASE + page['slug'] + '#page', 'url': BASE + page['slug'],
        'name': page['title'], 'description': page['description'],
        'inLanguage': 'en-US', 'about': business, 'publisher': business
    }, {
        '@context': 'https://schema.org', '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': BASE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': page['name'], 'item': BASE + page['slug']}
        ]
    }]
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><script type="text/javascript" charset="UTF-8" src="https://cdn.cookie-script.com/s/bb49fbb8483ced09e550fab9f04307c1.js"></script><script async src="https://ob.esnbranding.com/i/812741747104d2a36e3927a603f46db5.js" class="ct_clicktrue"></script><!-- Meta Pixel: CookieScript runs it only after the visitor allows Targeting cookies. --><script type="text/plain" data-cookiescript="accepted" data-cookiecategory="targeting">!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('dataProcessingOptions',['LDU'],0,0);fbq('init','4317054311941000');fbq('track','PageView');</script><!-- Google Analytics 4 (G-H1RC8T47T3): CookieScript runs it only after the visitor allows Performance cookies, and only on www.johncrawfordcompany.com so previews send nothing. --><script type="text/plain" data-cookiescript="accepted" data-cookiecategory="performance">if(location.hostname==='www.johncrawfordcompany.com'){{window.dataLayer=window.dataLayer||[];window.gtag=function(){{dataLayer.push(arguments);}};gtag('js',new Date());gtag('config','G-H1RC8T47T3');var ga=document.createElement('script');ga.async=true;ga.src='https://www.googletagmanager.com/gtag/js?id=G-H1RC8T47T3';document.head.appendChild(ga);}}</script><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(page['title'])}</title><meta name="description" content="{e(page['description'])}">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="theme-color" content="#FFFFFF">
<link rel="canonical" href="{BASE}{page['slug']}">
<meta property="og:type" content="website"><meta property="og:title" content="{e(page['title'])}">
<meta property="og:description" content="{e(page['description'])}"><meta property="og:url" content="{BASE}{page['slug']}">
<meta property="og:image" content="{BASE}/assets/john-crawford-logo.png"><meta property="og:image:alt" content="John Crawford Company — Window Treatments">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico?v=20261111" type="image/x-icon" sizes="16x16 32x32 48x48">
<link rel="icon" href="/favicon-32x32.png?v=20261111" type="image/png" sizes="32x32">
<link rel="icon" href="/favicon-48x48.png?v=20261111" type="image/png" sizes="48x48">
<link rel="icon" href="/favicon-192x192.png?v=20261111" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=20261111" sizes="180x180">
<link rel="preload" href="/assets/brand-latin-1.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/brand-latin-0.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/fonts.css?v=fonts-2"><link rel="stylesheet" href="/styles.css?v=footer-blog-20261111">
<link rel="stylesheet" href="/hubs.css?v=contact-centered-1"><link rel="stylesheet" href="/company-pages.css?v=company-pages-7">
<script src="/app.js?v=header-contact-20261105" defer></script>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('<', chr(92)+'u003c')}</script>
</head><body class="interior-page company-page company-page--{page.get('css_class', page['name'].lower())}"><noscript><iframe src="https://ob.esnbranding.com/ns/812741747104d2a36e3927a603f46db5.html?ch=" width="0" height="0" style="display:none"></iframe></noscript>
<a class="skip-link" href="#main">Skip to content</a>'''


def breadcrumbs(page):
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><span aria-current="page">{page["name"]}</span></nav>'


def showroom_art(css_class, priority=False):
    loading = 'fetchpriority="high"' if priority else 'loading="lazy"'
    return f'''<figure class="{css_class}"><img src="/assets/showroom-illustration.svg?v=trees-2"
      alt="Illustration of John Crawford Company's Woodland Hills showroom, with a red tile roof and palm trees."
      width="2394" height="1030" {loading} decoding="async"></figure>'''


def contact_details():
    return f'''<div class="hub-contact-details">
      <address>22311 Ventura Blvd #101, Woodland Hills, CA 91364</address>
      <p class="hub-hours appointment-hours"><span>{e(HOURS['display'])}</span><strong class="appointment-only">Appointment Only</strong></p>
      <div class="hub-contact-actions"><a class="btn btn-primary" href="tel:+18188845464">Call (818) 884-5464</a>
      <a class="btn btn-showroom-contact" href="/contact/#appointment-form">Schedule Appointment</a></div>
      <a class="text-link" href="mailto:john@johncrawford.com?subject=Window%20treatment%20consultation">Email us your project</a>
    </div>'''


def consultation_form():
    return '''<form class="hub-consultation-form" id="appointment-form" data-lead-form="contact" aria-labelledby="company-form-heading" aria-describedby="company-form-notice" novalidate>
      <h2 id="company-form-heading">Tell us about your project</h2>
      <div class="hub-form-fields">
      <div class="hub-form-field"><label for="company-name">Full name</label><input id="company-name" name="name" type="text" autocomplete="name" required></div>
      <div class="hub-form-field"><label for="company-phone">Phone number</label><input id="company-phone" name="phone" type="tel" autocomplete="tel" required></div>
      <div class="hub-form-field"><label for="company-email">Email</label><input id="company-email" name="email" type="email" autocomplete="email" required></div>
      <div class="company-form-extra">
        <div class="hub-form-field"><label for="company-product">Product interest</label><select id="company-product" name="product" required><option value="" selected>Select product</option><option value="shades">Shades</option><option value="blinds">Blinds</option><option value="shutters">Shutters</option><option value="drapery">Drapery</option><option value="motorized-shades">Motorized shades</option><option value="not-sure">Not sure yet</option></select></div>
        <div class="hub-form-field"><label for="company-zip">ZIP code</label><input id="company-zip" name="postal-code" type="text" inputmode="numeric" autocomplete="postal-code" pattern="[0-9]{5}" maxlength="5" required></div>
      </div>
      <fieldset class="company-appointment-options">
        <legend>I’d like to schedule<span class="sr-only"> (optional)</span></legend>
        <div class="company-appointment-choices">
          <label for="company-home-consultation"><input id="company-home-consultation" name="appointment-type" value="in-home" type="radio"><span>Free in-home consultation</span></label>
          <label for="company-showroom-appointment"><input id="company-showroom-appointment" name="appointment-type" value="showroom" type="radio"><span>Showroom visit</span></label>
        </div>
      </fieldset>
      <div class="hub-form-field"><label for="company-message">Message</label><textarea id="company-message" name="message" rows="3" maxlength="3000" required></textarea></div>
      <p class="hub-form-required">All fields except appointment choice are required.</p>
      <div class="lead-form-trap" aria-hidden="true"><label>Leave this field empty <input name="website" type="text" tabindex="-1" autocomplete="off"></label></div>
      <button class="btn btn-primary" type="submit">Request a consultation</button>
      </div>
      <p class="lead-form-status" role="status" tabindex="-1"></p>
      <p class="hub-form-notice" id="company-form-notice">We use the information you provide to respond to your project inquiry. <a href="/privacy/">Privacy Policy</a>.</p>
    </form>'''


def about_body(page):
    return f'''<main id="main">
    <section class="section company-hero linen" aria-labelledby="page-heading"><div class="container company-hero-grid">
      <div class="company-hero-copy">{breadcrumbs(page)}<h1 id="page-heading">{e(page['heading'])}</h1><p>{e(page['intro'])}</p>
        <div class="company-actions"><a class="btn btn-primary" href="/contact/">Talk with John</a><a class="text-link" href="/contact/#showroom">Visit the showroom</a></div></div>
      <figure class="company-hero-art company-photo"><img src="/assets/john-crawford-showroom.webp" alt="John Crawford outside his Woodland Hills showroom, pointing to the John Crawford Company sign." width="1024" height="768" fetchpriority="high" decoding="async"></figure>
    </div></section>
    <section class="section company-story" aria-labelledby="story-heading"><div class="container company-story-grid">
      <h2 id="story-heading">{e(page['story_heading'])}</h2><div class="company-prose">{paragraphs(page['story'])}</div>
    </div></section>
    <section class="section company-feature linen" aria-labelledby="approach-heading"><div class="container company-feature-grid">
      <figure class="company-photo"><img src="/assets/products/provenance.jpg" alt="Natural woven shades over tall windows beside a sofa and wood-framed lounge chair." width="1280" height="945" loading="lazy" decoding="async"><figcaption>Hunter Douglas Provenance® Woven Wood Shades</figcaption></figure>
      <div class="company-feature-copy"><h2 id="approach-heading">{e(page['approach_heading'])}</h2>{paragraphs(page['approach'])}<a class="text-link" href="/shades/">Explore window shades</a></div>
    </div></section>
    <section class="section company-single-window" aria-labelledby="single-window-heading"><div class="container company-story-grid">
      <h2 id="single-window-heading">{e(page['single_heading'])}</h2><div class="company-prose">{paragraphs(page['single'])}</div>
    </div></section>
    <section class="section company-visit linen" id="contact" aria-labelledby="visit-heading"><div class="container company-visit-grid">
      <div class="company-feature-copy"><h2 id="visit-heading">{e(page['visit_heading'])}</h2><p>{e(page['visit'])}</p><a class="text-link" href="/contact/">Contact John</a></div>
      {contact_details()}
    </div></section>
    </main>'''


def contact_body(page):
    return f'''<main id="main">
    <section class="section company-contact-hero" id="contact" aria-labelledby="page-heading"><div class="container company-contact-grid">
      <div class="company-hero-copy">{breadcrumbs(page)}<h1 id="page-heading">{e(page['heading'])}</h1><p>{e(page['intro'])}</p>
        <div class="company-contact-channels"><a class="company-phone" href="tel:+18188845464">(818) 884-5464</a><a class="text-link" href="mailto:john@johncrawford.com">john@johncrawford.com</a></div>
      </div>{consultation_form()}
    </div></section>
    <section class="section company-showroom linen" id="showroom" aria-labelledby="showroom-heading"><div class="container company-showroom-grid">
      {showroom_art('company-showroom-art')}
      <div class="company-showroom-info"><h2 id="showroom-heading">{e(page['showroom_heading'])}</h2><p>{e(page['showroom'])}</p>{contact_details()}</div>
    </div><div class="container company-showroom-areas"><p>{e(page['areas'])}</p></div></section>
    <section class="section company-help" aria-labelledby="repair-heading"><div class="container company-help-grid">
      <h2 id="repair-heading">{e(page['repair_heading'])}</h2><div class="company-prose"><p>{e(page['repair'])}</p>
      <a class="text-link" href="mailto:john@johncrawford.com?subject=Window%20treatment%20repair">Email us about a repair</a>
      <nav class="company-product-links" aria-label="Explore window treatments"><a href="/shades/">Shades</a><a href="/blinds/">Blinds</a><a href="/shutters/">Shutters</a><a href="/drapery/">Drapery</a><a href="/motorized-shades/">Motorized shades</a></nav></div>
    </div></section>
    </main>'''


def service_areas_body(page):
    regions = []
    for index, region in enumerate(page['regions']):
        places = ''.join(f'<li class="area-place">{e(place)}</li>' for place in region['communities'])
        modifier = ' area-region--primary' if index == 0 else ''
        regions.append(
            f'<section class="area-region{modifier}" id="{e(region["id"])}" aria-labelledby="{e(region["id"])}-heading">'
            f'<h2 id="{e(region["id"])}-heading">{e(region["heading"])}</h2><ul class="area-places">{places}</ul></section>'
        )
    return f'''<main id="main">
    <section class="section area-hero linen" aria-labelledby="page-heading"><div class="container">
      {breadcrumbs(page)}<h1 id="page-heading">{e(page['heading'])}</h1><p class="area-intro">{e(page['intro'])}</p>
      <div class="area-actions"><a class="btn btn-primary" href="/contact/#appointment-form">Request a consultation</a><a class="text-link" href="tel:+18188845464">Call (818) 884-5464</a></div>
    </div></section>
    <section class="section area-directory" aria-label="Service area communities"><div class="container area-regions">{''.join(regions)}</div></section>
    <section class="section area-contact linen" aria-labelledby="area-contact-heading"><div class="container area-contact-inner">
      <div class="area-contact-copy"><h2 id="area-contact-heading">{e(page['contact_heading'])}</h2><p>{e(page['contact_text'])}</p></div>
      <a class="btn btn-primary" href="/contact/#appointment-form">Request a free in-home visit</a>
    </div></section>
    </main>'''


def blog_body(page):
    cards = []
    for index, post in enumerate(BLOG_POSTS):
        cover = post['cover']
        cards.append(
            f'<article class="blog-card"><a class="blog-card-link" href="{e(post["slug"])}" aria-labelledby="blog-card-{index}-heading">'
            f'<img src="{e(cover["src"])}" alt="" width="{cover["width"]}" height="{cover["height"]}" loading="lazy" decoding="async">'
            f'<div class="blog-card-copy"><time datetime="{e(post["published"])}">{e(post["published_display"])}</time>'
            f'<h2 id="blog-card-{index}-heading">{e(post["heading"])}</h2><p>{e(post["excerpt"])}</p>'
            '<span class="blog-card-read">Read the guide</span></div></a></article>'
        )
    listing = ('<section class="section blog-list" aria-label="Articles"><div class="container">'
               + ''.join(cards) + '</div></section>') if cards else ''
    return f'''<main id="main">
    <section class="section company-hero linen" aria-labelledby="page-heading"><div class="container">
      <div class="company-hero-copy">{breadcrumbs(page)}<h1 id="page-heading">{e(page['heading'])}</h1><p>{e(page['intro'])}</p></div>
    </div></section>
    {listing}
    </main>'''


if __name__ == '__main__':
    update_navigation()
    subprocess.run([sys.executable, str(ROOT / 'scripts/build-hubs.py')], check=True)
    for key, kind, renderer in [('about', 'AboutPage', about_body), ('contact', 'ContactPage', contact_body), ('service_areas', 'CollectionPage', service_areas_body), ('blog', 'Blog', blog_body)]:
        page = SERVICE_AREAS if key == 'service_areas' else CONTENT[key]
        header, footer, mobile = partials(page)
        page_head = head(page, kind)
        if key == 'service_areas':
            page_head = page_head.replace('</head>', '<link rel="stylesheet" href="/service-areas.css?v=service-areas-3">\n</head>')
        if key == 'blog':
            page_head = page_head.replace('</head>', '<link rel="stylesheet" href="/blog.css?v=large-windows-20261111">\n</head>')
        html = page_head + header + renderer(page) + footer + mobile + '</body></html>\n'
        target = DIST / page['slug'].strip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html)
        print(page['slug'])
    subprocess.run([sys.executable, str(ROOT / 'scripts/build-services.py')], check=True)
    subprocess.run([sys.executable, str(ROOT / 'scripts/build-blog.py')], check=True)
    subprocess.run([sys.executable, str(ROOT / 'scripts/build-sitemap.py')], check=True)
