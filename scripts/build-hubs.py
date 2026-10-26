"""Generate static, crawlable product hubs from the approved public copy."""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
PAGES = json.loads((ROOT / 'content/product-hubs.json').read_text())
IMAGES = json.loads((ROOT / 'content/product-images.json').read_text())
BASE = 'https://john-crawford-homepage.codytodd.chatgpt.site'
HOME = (DIST / 'index.html').read_text()
DIRECTIONS = 'https://www.google.com/maps/search/?api=1&query=John+Crawford+Company+22311+Ventura+Blvd+Woodland+Hills'


def e(value):
    return escape(str(value), quote=True)


def tag_id(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')


def paragraphs(section):
    return '\n'.join('<p>' + e(t) + '</p>' for t in section.get('paragraphs', []))


def image(key, hero=False, caption=True):
    im = IMAGES[key]
    attrs = 'fetchpriority="high"' if hero else 'loading="lazy" decoding="async"'
    return (f'<figure class="hub-photo"><img src="{e(im["src"])}" alt="{e(im["alt"])}" '
            f'width="{im["width"]}" height="{im["height"]}" {attrs}>'
            + (f'<figcaption>{e(im["caption"])}</figcaption>' if caption else '') + '</figure>')


def decorative_accent(filename, css_class, width, height):
    return (f'<img class="{css_class}" src="/assets/accents/{filename}" alt="" '
            f'aria-hidden="true" width="{width}" height="{height}" loading="lazy" decoding="async">')


def partials(path):
    header = re.search(r'<header class="site-header">[\s\S]*?</header>', HOME).group()
    footer = re.search(r'<footer class="site-footer"[\s\S]*?</footer>', HOME).group()
    mobile = re.search(r'<div class="mobile-contact"[\s\S]*?</div>', HOME).group()
    out = []
    for text in (header, footer, mobile):
        text = text.replace('src="assets/', 'src="/assets/')
        text = text.replace('href="#top"', 'href="/"')
        for anchor in ['consultation', 'installation', 'repairs', 'upholstery', 'commercial', 'about']:
            text = text.replace(f'href="#{anchor}"', f'href="/#{anchor}"')
        text = text.replace('back to top', 'home')
        text = text.replace(f'href="{path}"', f'href="{path}" aria-current="page"')
        out.append(text)
    return out


def head(page, hero_key=None, accessibility=False):
    title = page['title_tag']
    desc = page['meta_description']
    path = page['slug']
    hub_css_version = 'accent-placement-corrected-1' if hero_key else 'hubs-1'
    if page['name'] == 'Drapery':
        hub_css_version = 'drapery-details-1'
    elif hero_key:
        hub_css_version = 'product-details-1'
    body_class = 'interior-page accent-review-page' if page['name'] == 'Shades' else 'interior-page'
    og = IMAGES[hero_key]['src'] if hero_key else '/assets/showroom-illustration.svg'
    schema = [{
        '@context': 'https://schema.org', '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': BASE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': page['name'], 'item': BASE + path}
        ]
    }, {
        '@context': 'https://schema.org', '@type': 'WebPage' if accessibility else 'CollectionPage',
        '@id': BASE + path + '#page', 'url': BASE + path, 'name': title,
        'description': desc, 'inLanguage': 'en-US',
        'about': {'@type': 'Thing', 'name': page['name']},
        'publisher': {'@type': 'HomeGoodsStore', '@id': 'https://www.johncrawfordcompany.com/#business',
                      'name': 'John Crawford Company', 'telephone': '+1-818-884-5464',
                      'email': 'john@johncrawford.com',
                      'address': {'@type': 'PostalAddress', 'streetAddress': '22311 Ventura Blvd #101',
                                  'addressLocality': 'Woodland Hills', 'addressRegion': 'CA',
                                  'postalCode': '91364', 'addressCountry': 'US'},
                      'openingHoursSpecification': [{'@type':'OpeningHoursSpecification',
                          'dayOfWeek':['Monday','Tuesday','Wednesday','Thursday','Friday'],
                          'opens':'09:00','closes':'17:00'}]}
    }]
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <meta name="robots" content="noindex, nofollow">
  <meta name="theme-color" content="#FFFFFF">
  <link rel="canonical" href="{BASE}{path}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{BASE}{path}">
  <meta property="og:image" content="{BASE}{og}">
  <meta property="og:image:alt" content="{e(IMAGES[hero_key]['alt']) if hero_key else 'Illustration of the John Crawford Company showroom'}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="data:,">
  <link rel="preload" href="/assets/brand-latin-1.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/assets/brand-latin-0.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/assets/fonts.css?v=fonts-2">
  <link rel="stylesheet" href="/styles.css?v=product-cards-1">
  <link rel="stylesheet" href="/hubs.css?v={hub_css_version}">
  <script src="/app.js?v=hubs-1" defer></script>
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('<', chr(92)+'u003c')}</script>
</head>
<body class="{body_class}">
<a class="skip-link" href="#main">Skip to content</a>'''


def brand_line():
    return '''<div class="hub-brands" aria-label="Window treatment brands">
      <img src="/assets/hunter-douglas.svg" alt="Hunter Douglas" width="181" height="27">
      <span aria-hidden="true"></span><span class="alta-name">Alta</span>
    </div>'''


def hero(page, key):
    section = page['sections'][0]
    photo = IMAGES[key]
    return f'''<section class="hub-hero hub-hero--{tag_id(page['name'])}" aria-labelledby="page-heading">
      <figure class="hub-photo hub-hero-photo"><img src="{e(photo['src'])}" alt="{e(photo['alt'])}" width="{photo['width']}" height="{photo['height']}" fetchpriority="high" decoding="async"><figcaption>{e(photo['caption'])}</figcaption></figure>
      <div class="container hub-hero-grid">
        <div class="hub-hero-copy">
          <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><span aria-current="page">{e(page['name'])}</span></nav>
          <h1 id="page-heading">{e(section['title'])}</h1>
          {paragraphs(section)}
          <div class="hub-hero-actions"><a class="btn btn-primary" href="#contact">{e(section['cta'])}</a><a class="hub-phone" href="tel:+18188845464">(818) 884-5464</a></div>
          {brand_line()}
        </div>
      </div>
    </section>'''


def intro(section, page):
    body = paragraphs(section)
    if page['name'] == 'Shades':
        body += '<p>We also carry Alta shades if you\'d like to compare another option for your project.</p>'
    if page['name'] == 'Blinds':
        body += '<p>We carry Hunter Douglas and Alta blinds and can help you compare the choices for your windows.</p>'
    floral = decorative_accent('floral-corner-complete.png', 'hub-accent-floral', 1254, 1254)
    return f'''<section class="section hub-introduction hub-intro-consultation" aria-labelledby="introduction-heading">
      <div class="container hub-intro-grid">
        <div class="hub-prose hub-intro-copy"><h2 id="introduction-heading">{e(section['title'])}</h2>{body}{floral}</div>
        <form class="hub-consultation-form" aria-label="Consultation form preview" aria-describedby="consultation-preview consultation-required consultation-notice">
          <p class="sr-only" id="consultation-preview">This form is a design preview and does not accept submissions.</p>
          <div class="hub-form-fields">
            <div class="hub-form-field"><label for="consultation-name">Full name</label><input id="consultation-name" name="name" type="text" autocomplete="name" maxlength="120" required disabled></div>
            <div class="hub-form-field"><label for="consultation-phone">Phone number</label><input id="consultation-phone" name="phone" type="tel" autocomplete="tel" minlength="7" maxlength="30" required disabled></div>
            <div class="hub-form-field"><label for="consultation-email">Email</label><input id="consultation-email" name="email" type="email" autocomplete="email" maxlength="254" required disabled></div>
            <p class="hub-form-required" id="consultation-required">All fields are required.</p>
            <button class="btn btn-primary" type="button" disabled>Request a consultation</button>
          </div>
          <p class="hub-form-notice" id="consultation-notice">We collect your name, phone number and email to respond to your project inquiry. <a href="/privacy/">Privacy Policy</a>.</p>
        </form>
      </div>
    </section>'''


def catalog(section, keys, mode):
    items = section.get('items', [])
    if not items:
        return ''
    anchors = ''.join(f'<a href="#{tag_id(item["title"])}">{e(item["title"])}</a>' for item in items)
    body = paragraphs(section)
    if mode == 'Shades':
        body = '<p>As a Hunter Douglas dealer, we can help you compare the collections by fabric, construction and control options.</p>'
    if mode == 'Blinds':
        body = '<p>See how the materials look with the slats or vanes open and closed.</p>'
    cards = []
    for i, (item, key) in enumerate(zip(items, keys)):
        title_id = tag_id(item['title'])
        show_caption = mode == 'Shades'
        cards.append(f'''<article class="collection" id="{title_id}" aria-labelledby="{title_id}-heading">
          {image(key, caption=show_caption)}
          <h3 id="{title_id}-heading">{e(item['title'])}</h3><p>{e(item['text'])}</p>
        </article>''')
    if mode == 'Blinds':
        card_html = ('<div class="collection-grid">' + ''.join(cards[:4]) + '</div>'
                     '<h3 class="wide-opening-heading">For wide windows and sliding doors</h3>'
                     '<div class="collection-grid">' + ''.join(cards[4:]) + '</div>')
    else:
        card_html = '<div class="collection-grid">' + ''.join(cards) + '</div>'
    return f'''<section class="section {'linen ' if mode != 'Shutters' else ''}hub-collections" id="collections" aria-labelledby="collections-heading">
      <div class="container">
        <div class="hub-section-heading"><h2 id="collections-heading">{e(section['title'])}</h2>{body}</div>
        <nav class="collection-jump-links" aria-label="Browse collections">{anchors}</nav>
        {card_html}
      </div>
    </section>'''


def quote(section):
    if 'quote' not in section:
        return ''
    q = section['quote']
    return f'''<figure class="hub-customer-quote">
      <span class="review-stars" role="img" aria-label="Five stars"><span aria-hidden="true">★★★★★</span></span>
      <blockquote><p>{e(q['text'])}</p></blockquote><figcaption>{e(q['author'])}</figcaption>
    </figure>'''


def advice(sections, linen=False):
    blocks = []
    for sec in sections:
        sid = tag_id(sec['title'])
        blocks.append(f'<article class="hub-advice" aria-labelledby="{sid}"><h2 id="{sid}">{e(sec["title"])}</h2>{paragraphs(sec)}{quote(sec)}</article>')
    return '<div class="section hub-advice-section' + (' linen' if linen else '') + '"><div class="container hub-advice-grid">' + ''.join(blocks) + '</div></div>'


def detail_panel(sections, photo_key, title, panel_id, topic_titles=None, prefix='hub-detail', modifiers=''):
    photo = IMAGES[photo_key]
    topics = []
    for topic_title, section in zip(topic_titles or [s['title'] for s in sections], sections):
        sid = tag_id(section['title'])
        topics.append(f'<article class="{prefix}-topic" aria-labelledby="{sid}"><h3 id="{sid}">{e(topic_title)}</h3>{paragraphs(section)}{quote(section)}</article>')
    return f'''<section class="section {prefix}-details{modifiers}" id="{panel_id}" aria-labelledby="{panel_id}-heading">
      <div class="container {prefix}-panel">
        <figure class="{prefix}-photo">
          <img src="{e(photo['src'])}" alt="{e(photo['alt'])}" width="{photo['width']}" height="{photo['height']}" loading="lazy" decoding="async">
          <figcaption>{e(photo['caption'])}</figcaption>
        </figure>
        <div class="{prefix}-copy">
          <h2 id="{panel_id}-heading">{e(title)}</h2>
          {''.join(topics)}
        </div>
      </div>
    </section>'''


def drapery_details(sections):
    return detail_panel(sections, 'carole', 'Drapery hardware and layering', 'drapery-details',
                        ['Choosing the rod or track', 'Pairing drapery with shades'], prefix='hub-drapery')


def faq(section, linen=True):
    questions = ''.join(f'<details><summary>{e(q["question"])}</summary><p>{e(q["answer"])}</p></details>' for q in section['faqs'])
    return f'''<section class="section {'linen ' if linen else ''}hub-questions" aria-labelledby="questions-heading">
      <div class="container questions-grid"><div class="questions-intro"><h2 id="questions-heading">{e(section['title'])}</h2>
        <a class="text-link" href="tel:+18188845464">Ask John and Max: (818) 884-5464</a></div>
        <div class="faq-list">{questions}</div>
      </div>
    </section>'''


def contact(section):
    palm = decorative_accent('palm-corner.svg', 'hub-accent-palm', 400, 400)
    return f'''<section class="section hub-contact hub-contact-accent" id="contact" aria-labelledby="contact-heading">
      <div class="container hub-contact-accent-grid">
        <div class="hub-contact-message"><h2 id="contact-heading">{e(section['title'])}</h2>{paragraphs(section)}</div>
        <div class="hub-contact-details">
          <address>22311 Ventura Blvd #101<br>Woodland Hills, CA 91364</address><p class="hub-hours">Monday-Friday, 9 am-5 pm</p>
          <div class="hub-contact-actions"><a class="btn btn-primary" href="tel:+18188845464">Call (818) 884-5464</a>
            <a class="btn btn-showroom-contact" href="{e(DIRECTIONS)}" target="_blank" rel="noopener noreferrer">Get directions<span class="sr-only"> (opens in a new tab)</span></a></div>
          <a class="text-link" href="mailto:john@johncrawford.com?subject=Window%20treatment%20consultation">Email us your project</a>
        </div>
      </div>
      {palm}
    </section>'''


def related(page):
    links = ''.join(f'<a href="{e(p["slug"])}">{e(p["name"])}</a>' for p in PAGES if p['name'] != page['name'])
    return f'<nav class="hub-related" aria-label="More window treatments"><div class="container"><p>More window treatments</p><div>{links}</div></div></nav>'


def powerview(section):
    return f'''<section class="section linen hub-powerview" aria-labelledby="powerview-heading">
      <div class="container hub-powerview-grid"><div class="hub-prose"><h2 id="powerview-heading">{e(section['title'])}</h2>{paragraphs(section)}
        <p class="powerview-disclosure">{e(section['disclosure'])}</p></div>{image('powerview')}</div>
    </section>'''


CONFIG = {
    'Shades': {'hero':'provenance', 'catalog':['designer-roller','duette','silhouette','vignette','provenance','skyline']},
    'Blinds': {'hero':'parkland', 'catalog':['parkland','everwood','custom-metal','aria','custom-vertical','skyline','luminette']},
    'Shutters': {'hero':'palm-beach', 'catalog':['heritance','newstyle','palm-beach']},
    'Drapery': {'hero':'carole', 'catalog':['carole','luminette','provenance']},
    'Motorized Shades': {'hero':'powerview-blue'},
}
IMAGES['powerview-blue'] = {'src':'/assets/powerview-wall-remote.jpg', 'width':1440, 'height':1080,
    'caption':'Hunter Douglas PowerView® Automation wall-mounted control',
    'alt':'A round white wall control beside blue fabric shades and a dark window frame.'}
IMAGES['somfy-situo'] = {'src':'/assets/products/somfy-situo-5-rts.jpg', 'width':768, 'height':768,
    'caption':'Somfy Situo® 5 RTS remote',
    'alt':'A white Somfy handheld remote with up, stop and down buttons and a channel selector.'}

for page in PAGES:
    name, secs = page['name'], page['sections']
    header, footer, mobile = partials(page['slug'])
    body = [hero(page, CONFIG[name]['hero']), intro(secs[1], page)]
    if name == 'Motorized Shades':
        body += [powerview(secs[2]),
                 detail_panel(secs[3:5], 'somfy-situo', 'Motorization and power planning', 'motorization-power', modifiers=' hub-detail--somfy'),
                 detail_panel(secs[5:7], 'powerview', 'Motorized shade installation and support', 'motorization-support', modifiers=' hub-detail--controls hub-detail--reverse'),
                 faq(secs[7], linen=False), contact(secs[8])]
    else:
        catalog_section = secs[2] if name != 'Shutters' else {**secs[1], 'title': 'Hunter Douglas shutter collections', 'paragraphs': []}
        body += [catalog(catalog_section, CONFIG[name]['catalog'], name)]
        # Keep the material advice with the form, followed by the shutter collections.
        if name == 'Shutters':
            body += [detail_panel(secs[2:4], 'newstyle', 'Shutter panels, louvers and light', 'shutter-details', modifiers=' hub-detail--shutters'), advice([secs[4]]), faq(secs[5]), contact(secs[6])]
        elif name == 'Drapery':
            body += [drapery_details(secs[3:5]), advice([secs[5]], linen=True), faq(secs[6], linen=False), contact(secs[7])]
        else:
            details = (detail_panel(secs[3:5], 'designer-screen', 'Shade fabrics, privacy and fit', 'shade-details', modifiers=' hub-detail--shades')
                       if name == 'Shades' else detail_panel(secs[3:5], 'aria', 'Blind fit and installation', 'blind-details', modifiers=' hub-detail--blinds'))
            body += [details, faq(secs[5]), contact(secs[6])]
    html = head(page, CONFIG[name]['hero']) + header + '<main id="main">' + '\n'.join(body) + related(page) + '</main>' + footer + mobile + '</body></html>\n'
    target = DIST / page['slug'].strip('/') / 'index.html'
    target.parent.mkdir(exist_ok=True)
    target.write_text(html)
    print(page['slug'])

accessibility = {'name':'Accessibility', 'slug':'/accessibility/',
    'title_tag':'Accessibility | John Crawford Company',
    'meta_description':'Need help using the John Crawford Company website? Call (818) 884-5464 or email john@johncrawford.com for help with product information or consultation requests.'}
header, footer, mobile = partials(accessibility['slug'])
html = head(accessibility, accessibility=True) + header.replace('href="#contact"','href="/#contact"') + '''<main id="main" class="accessibility-content section"><div class="container hub-readable">
  <h1>Accessibility</h1>
  <p>We want everyone to be able to find product information and get in touch with John Crawford Company. We are working to make this website easier to use.</p>
  <h2>Need help using the website?</h2>
  <p>If you have difficulty reading a page, browsing window treatments or contacting us through the website, call <a href="tel:+18188845464">(818) 884-5464</a> or email <a href="mailto:john@johncrawford.com">john@johncrawford.com</a>.</p>
  <p>Tell us which page or feature caused the problem and how you would like us to contact you. We can also discuss products and consultation requests by phone.</p>
  <p>Showroom hours: Monday-Friday, 9 am-5 pm.</p>
  <p class="statement-date">Statement reviewed October 22, 2026.</p>
</div></main>''' + footer.replace('href="#contact"','href="/#contact"') + mobile.replace('href="#contact"','href="/#contact"') + '</body></html>\n'
target=DIST/'accessibility/index.html';target.parent.mkdir(exist_ok=True);target.write_text(html)


def support_page(name, slug, title, description, body):
    page = {'name': name, 'slug': slug, 'title_tag': title, 'meta_description': description}
    header, footer, mobile = partials(slug)
    html = (head(page, accessibility=True) + header.replace('href="#contact"', 'href="/#contact"')
            + '<main id="main" class="section"><div class="container hub-readable">' + body
            + '</div></main>' + footer.replace('href="#contact"', 'href="/#contact"')
            + mobile.replace('href="#contact"', 'href="/#contact"') + '</body></html>\n')
    target = DIST / slug.strip('/') / 'index.html'
    target.parent.mkdir(exist_ok=True)
    target.write_text(html)


support_page('Privacy Policy', '/privacy/', 'Privacy Policy | John Crawford Company',
    'How John Crawford Company handles website consultation requests, contact information, hosting and embedded services.', '''
  <h1>Privacy Policy</h1>
  <p class="statement-date">Effective October 22, 2026.</p>
  <p>This policy describes information collected through the John Crawford Company website and how to contact us about it.</p>
  <h2>Information you provide</h2>
  <p>The consultation form displayed on this preview does not accept submissions. If you email us, we receive the contact information, project details and any photos or attachments you choose to send.</p>
  <h2>How your information is used</h2>
  <p>We use inquiry information to respond, discuss your project and provide the help you request. Our website providers also process information to operate and protect the website.</p>
  <h2>Website providers</h2>
  <p>This website is hosted through Netlify and, for the preview, ChatGPT Sites. Hosting providers may process technical information, such as IP addresses, browser details and request logs, to deliver and secure the website.</p>
  <h2>Embedded services and tracking</h2>
  <p>This website includes a Google Maps embed. Loading that map may allow Google to receive device and visit information and use its own cookies or similar technologies. Social profile links take you to separate services when you open them. Those providers' privacy practices apply to their services. See <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google's Privacy Policy<span class="sr-only"> (opens in a new tab)</span></a>.</p>
  <p>We have not installed advertising pixels or audience-tracking analytics on this website. The website does not change its behavior in response to browser Do Not Track signals. Embedded third-party services may follow their own tracking practices.</p>
  <h2>Your inquiry and privacy requests</h2>
  <p>To ask about access, correction or deletion of information you provided directly to us, email <a href="mailto:john@johncrawford.com">john@johncrawford.com</a> or call <a href="tel:+18188845464">(818) 884-5464</a>. We may need to verify your request and retain records required for an ongoing project or by law.</p>
  <p>You can also write to John Crawford Company, 22311 Ventura Blvd #101, Woodland Hills, CA 91364.</p>
  <h2>Policy updates</h2>
  <p>We will post changes on this page and update the effective date when this policy changes.</p>''')
