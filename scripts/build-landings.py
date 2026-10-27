"""Build campaign pages using the approved homepage's actual sections and styles."""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
HOME = (DIST / 'index.html').read_text()
IMAGES = json.loads((ROOT / 'content/product-images.json').read_text())
BASE = 'https://john-crawford-homepage.codytodd.chatgpt.site'


def e(value):
    return escape(str(value), quote=True)


def section(name):
    return re.search(r'<section class="[^"]*" id="' + name + r'"[\s\S]*?</section>', HOME).group()


def absolute_assets(text):
    text = re.sub(r'((?:src|href|srcset|data-desktop-src|data-mobile-src)=")assets/', r'\1/assets/', text)
    return text.replace('href="styles.css', 'href="/styles.css').replace('src="app.js', 'src="/app.js')


def cta():
    return '<a class="btn btn-primary" href="#contact">Get Free Quote</a>'


def header(motorized):
    return '''<header class="site-header"><div class="header-inner">
      <div class="brand"><img src="/assets/john-crawford-logo.webp" alt="John Crawford Company — Window Treatments" width="1672" height="941" fetchpriority="high"></div>
      <div class="landing-header-actions"><span class="landing-header-number">(818) 884-5464</span><a class="btn btn-showroom-contact landing-call-cta" href="tel:+18188845464">Call Us</a>
      <a class="btn btn-primary header-cta" href="#contact">Get Free Quote</a></div>
      </div></header>'''


def footer(motorized):
    return '''<footer class="site-footer" id="footer">
      <img class="footer-color-rule" src="/assets/brand-color-rule.png" alt="" width="3000" height="12" loading="lazy" aria-hidden="true">
      <div class="container footer-main">
      <div class="footer-business"><div class="footer-brand"><img src="/assets/john-crawford-logo.webp" alt="John Crawford Company — Window Treatments" width="1672" height="941" loading="lazy" decoding="async"></div>
      <p>Custom window treatments in Los Angeles.<br>Personal service from Woodland Hills.</p></div>
      <div class="landing-footer-actions"><h2>Talk about your project</h2>''' + cta() + '''<a class="btn btn-showroom-contact" href="tel:+18188845464">Call Us</a></div>
      <section class="footer-contact" aria-labelledby="footer-contact-heading"><div class="footer-contact-details"><h2 id="footer-contact-heading">Our Woodland Hills showroom</h2>
      <address>22311 Ventura Blvd #101<br>Woodland Hills, CA 91364</address><p class="footer-hours">Monday–Friday, 9am–5pm<br>Saturday–Sunday closed</p>
      <p class="landing-public-phone">(818) 884-5464</p></div></section></div>
      <div class="container footer-bottom"><p>© <span id="year">2026</span> John Crawford Company. All rights reserved.</p><div class="landing-footer-information">
      <button class="landing-info-button" type="button" data-landing-dialog="landing-accessibility-dialog" aria-haspopup="dialog" aria-controls="landing-accessibility-dialog">Accessibility</button>
      <button class="landing-info-button" type="button" data-landing-dialog="landing-privacy-dialog" aria-haspopup="dialog" aria-controls="landing-privacy-dialog">Privacy Policy</button></div></div></footer>'''


def showroom():
    html = section('about')
    html = re.sub(r'<a class="btn btn-primary" href="https://www.google.com/maps/[^<]+[\s\S]*?</a>',
                  '<a class="btn btn-showroom-contact" href="tel:+18188845464">Call Us</a>', html)
    return html.replace('class="btn btn-showroom-contact" href="#contact">Contact Us', 'class="btn btn-primary" href="#contact">Get Free Quote')


def information_dialogs():
    return '''<dialog class="landing-info-dialog" id="landing-privacy-dialog" aria-labelledby="landing-privacy-heading">
      <div class="landing-dialog-heading"><h2 id="landing-privacy-heading">Privacy Policy</h2><form method="dialog"><button class="landing-info-button" type="submit" autofocus>Close</button></form></div>
      <p>The quote form on this review page does not accept submissions. If you call us, we use the information you provide to respond and discuss your project.</p>
      <p>These pages are hosted through Netlify and ChatGPT Sites. Hosting providers may process technical information, such as IP addresses, browser details and request logs, to deliver and secure the pages. Advertising pixels and audience-tracking analytics have not been installed on these pages.</p>
      <p>For questions about information you provide, call John Crawford Company at <a href="tel:+18188845464">(818) 884-5464</a>. You can also write to 22311 Ventura Blvd #101, Woodland Hills, CA 91364.</p></dialog>
      <dialog class="landing-info-dialog" id="landing-accessibility-dialog" aria-labelledby="landing-accessibility-heading">
      <div class="landing-dialog-heading"><h2 id="landing-accessibility-heading">Accessibility assistance</h2><form method="dialog"><button class="landing-info-button" type="submit" autofocus>Close</button></form></div>
      <p>If you have difficulty reading this page or requesting a quote, call <a href="tel:+18188845464">(818) 884-5464</a>. Tell us which feature caused the problem and how you would like us to contact you.</p>
      <p>We can discuss products and quote requests by phone. Showroom hours are Monday–Friday, 9 am–5 pm.</p></dialog>'''


def reviews(motorized):
    html = section('reviews')
    html = re.sub(r'<a class="reviews-source"[\s\S]*?</a>', '<span class="reviews-source">Review source: Google Maps</span>', html)
    if motorized:
        cards = re.findall(r'<article class="review-card"[\s\S]*?</article>', html)
        ordered = sorted(cards, key=lambda card: 0 if 'review-carol-name' in card else 1 if 'review-perry-name' in card else 2)
        for old, new in zip(cards, ordered):
            html = html.replace(old, f'__REVIEW_{cards.index(old)}__')
        for i, new in enumerate(ordered):
            html = html.replace(f'__REVIEW_{i}__', new)
    return html


def product_card(key, title, anchor, copy):
    image = IMAGES[key]
    return f'''<article class="product" id="{anchor}">
      <img src="{image['src']}" alt="{e(image['alt'])}" width="{image['width']}" height="{image['height']}" loading="lazy" decoding="async">
      <div class="product-copy"><h3>{e(title)}</h3><p>{e(copy)}</p>
      <a class="text-link" href="#contact" aria-label="Get Free Quote for {e(title.lower())}">Get Free Quote</a></div>
      <p class="landing-photo-caption">{e(image['caption'])}</p></article>'''


def products(motorized):
    if not motorized:
        html = section('window-treatments')
        for name in ['blinds', 'shades', 'shutters', 'drapery']:
            html = html.replace(f'href="/{name}/">Explore {name}', f'href="#contact" aria-label="Get Free Quote for {name}">Get Free Quote')
        return html
    cards = [
        ('designer-roller', 'Roller shades', 'roller-shades', 'A clean look with fabrics for soft daylight or more room darkening. We’ll compare opacity and compatible motorized controls for your windows.'),
        ('designer-screen', 'Screen shades', 'screen-shades', 'Filter bright daylight and reduce glare while keeping some of the view. We’ll talk through fabric openness and privacy, especially after dark.'),
        ('duette', 'Honeycomb shades', 'honeycomb-shades', 'A cellular design in a choice of fabrics and opacities. Compare the look and light control, then choose from the operating options available for your windows.'),
        ('provenance', 'Woven wood shades', 'woven-wood-shades', 'Bring natural texture to the room. We’ll help you consider the weave, lining and compatible motorization together.')
    ]
    return '''<section class="section linen products" id="window-treatments" aria-labelledby="products-heading">
      <div class="container"><div class="section-intro"><h2 id="products-heading">Start with the shade style you love</h2>
      <p>Choose the look, fabric and light control first. We’ll confirm the motorization available for the collection and size you select.</p></div>
      <div class="product-grid">''' + ''.join(product_card(*card) for card in cards) + '</div></div></section>'


def motorization(motorized):
    if not motorized:
        html = section('motorization')
        html = html.replace('We offer Hunter Douglas PowerView and Somfy motorization, including compatible hub setup. We’ll help you choose the right controls and show you how to use them.',
                            'We offer Hunter Douglas PowerView® Automation, including compatible hub setup. We’ll help you choose the right controls and show you how to use them.')
        html = html.replace('href="/motorized-shades/">Explore motorized shades', 'href="#contact">Get Free Quote')
        html = html.replace('</ul>', '</ul><p class="landing-disclosure">The PowerView® App is required for programmed operation.</p>')
        return html
    return '''<section class="section linen motorization" id="motorization" aria-labelledby="motor-heading">
      <div class="container feature-grid"><div class="feature-image"><img src="/assets/products/powerview-wall-control.png" alt="Round PowerView wall control mounted beside a pale fabric window shade." width="1280" height="853" loading="lazy" decoding="async"></div>
      <div class="feature-copy"><h2 id="motor-heading">Hunter Douglas PowerView® Automation</h2>
      <p>Lower several shades together when the afternoon sun arrives, or adjust a tall window from your seat. PowerView® Automation operates selected Hunter Douglas window treatments with a remote or the PowerView® App.</p>
      <ul class="simple-list"><li>Handheld and wall-mounted controls</li><li>Group compatible shades by room</li><li>Set schedules in the PowerView® App</li></ul>
      <p>John and Max help you choose the controls, confirm any gateway requirements and set up the system at installation.</p>
      <p class="landing-disclosure">The PowerView® App is required for programmed operation.</p>''' + cta() + '</div></div></section>'


def services(motorized):
    cards = [
        ('consultation', 'Consultation & measuring', 'Tell us about the rooms, the light and privacy you need, and your budget. We’ll help compare suitable products and take the measurements for your quote.'),
        ('installation', 'Professional installation', 'Our team installs your window treatments and checks the fit and operation. You have help from product selection through the final adjustments.'),
        ('controls', 'Controls & setup' if motorized else 'Help with the details',
         'Choose from the controls available for your shades. We set up the system and show you how to operate it before we finish.' if motorized else 'Fabric, lining, hardware and controls all affect how the treatment works. We help you consider those choices together.'),
        ('support', 'Power & compatibility' if motorized else 'Personal service from John & Max',
         'We’ll review battery, rechargeable or wired options for your selected product. Tell us about any smart-home system so we can check the equipment needed.' if motorized else 'Talk with the people helping you plan and install your window treatments. John and Max can also help with questions after installation.')
    ]
    heading = 'Motorized shade installation and setup' if motorized else 'From your first ideas to the final fit'
    return f'''<section class="section services" id="services" aria-labelledby="services-heading">
      <picture class="services-backdrop"><img src="/assets/services-coastal-screen-shades.webp" alt="" width="1800" height="900" loading="lazy" decoding="async"></picture>
      <div class="container"><div class="section-intro"><h2 id="services-heading">{heading}</h2>
      <p>One team to help you choose, measure and install your window treatments.</p></div><div class="service-grid">''' + ''.join(
        f'<article id="{anchor}"><h3>{e(title)}</h3><p>{e(copy)}</p></article>' for anchor, title, copy in cards
    ) + '</div><div class="landing-section-action">' + cta() + '</div></div></section>'




def contact(motorized):
    heading = 'Get a free quote for motorized shades.' if motorized else 'Get a free quote for your windows.'
    copy = 'Tell us which windows you’d like to operate more easily. We’ll help you consider the shade style, controls and installation.' if motorized else 'Tell us about your rooms and what you’d like to change. We’ll help you compare blinds, shades, shutters, drapery and motorization.'
    return f'''<section class="section linen contact landing-contact" id="contact" aria-labelledby="contact-heading">
      <div class="container landing-contact-grid"><div class="landing-contact-copy"><h2 id="contact-heading">{heading}</h2><p>{copy}</p>
      <div class="contact-actions"><a class="btn btn-showroom-contact" href="tel:+18188845464">Call Us</a><p class="landing-public-phone">(818) 884-5464</p></div>
      <div class="landing-contact-location"><address>22311 Ventura Blvd #101, Woodland Hills, CA 91364</address><p>Monday–Friday, 9 am–5 pm</p></div></div>
      <form class="landing-form" aria-label="Free quote form preview" aria-describedby="form-preview form-required">
      <h3>Get your free quote</h3><p class="landing-preview-note" id="form-preview">This form is a design preview. Please call us about your project.</p>
      <div class="landing-form-fields">
      <div class="landing-form-field"><label for="lead-name">Full name</label><input id="lead-name" name="name" autocomplete="name" type="text" maxlength="120" required disabled></div>
      <div class="landing-form-field"><label for="lead-phone">Phone number</label><input id="lead-phone" name="phone" autocomplete="tel" type="tel" maxlength="30" required disabled></div>
      <div class="landing-form-field"><label for="lead-email">Email</label><input id="lead-email" name="email" autocomplete="email" type="email" maxlength="254" required disabled></div>
      </div><p class="landing-required" id="form-required">All fields are required.</p><button class="btn btn-primary" type="button" disabled>Get Free Quote</button>
      <p class="landing-privacy">We use your contact details to respond to your project inquiry. <button class="landing-info-button" type="button" data-landing-dialog="landing-privacy-dialog" aria-haspopup="dialog" aria-controls="landing-privacy-dialog">Privacy Policy</button>.</p></form></div></section>'''


def build(motorized=False):
    slug = 'motorized-shades' if motorized else 'custom-window-treatments'
    route = f'/lp/{slug}/'
    name = 'Motorized & Automated Shades' if motorized else 'Custom Window Treatments'
    title = f'{name} in Los Angeles | John Crawford Company'
    description = ('Compare motorized and automated shades with John Crawford Company. Get help with controls, measuring, installation and setup from Woodland Hills.' if motorized else 'Blinds, shades, shutters, drapery and motorization in Los Angeles. Get personal help with selection, measuring and installation from John Crawford Company.')
    head = HOME[HOME.index('<head>'):HOME.index('</head>')+7]
    head = re.sub(r'<title>[\s\S]*?</title>', f'<title>{e(title)}</title>', head)
    head = re.sub(r'(<meta (?:name="description"|property="og:description") content=")[^"]*', lambda m:m[1]+e(description), head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m:m[1]+e(title), head)
    head = head.replace(f'href="{BASE}/"', f'href="{BASE}{route}"').replace(f'content="{BASE}/"', f'content="{BASE}{route}"')
    head = head.replace('app.js?v=hubs-1', 'app.js?v=landing-conversion-1')
    head = head.replace('</head>', '<link rel="stylesheet" href="/landings.css?v=quote-cta-1">\n</head>')
    if motorized:
        head = re.sub(r'  <link rel="preload" href="assets/hero-room-poster-[^\n]+\n', '', head)
        head = head.replace(BASE+'/assets/hero-room-poster-desktop.webp', BASE+'/assets/powerview-wall-remote.jpg')
        head = head.replace('A finished shade installation from John Crawford Company project footage', 'Hunter Douglas PowerView wall-mounted remote beside blue window shades')
        head = head.replace('</head>', '<link rel="preload" as="image" href="/assets/powerview-wall-remote.jpg">\n</head>')
    hero = section('top')
    hero = hero.replace('Request a consultation', 'Get Free Quote')
    hero = re.sub(r'<a class="hero-phone" href="tel:[^"]+">[\s\S]*?</a>', '<a class="btn btn-showroom-contact" href="tel:+18188845464">Call Us</a>', hero)
    if motorized:
        hero = hero.replace('Custom Window Treatments <span>in Los Angeles, California</span>', 'Motorized Shades <span>in Los Angeles, California</span>')
        hero = hero.replace('Blinds, shades, shutters and drapery, chosen for your rooms and professionally installed.<span class="hero-detail"> Get personal help with the details, from the first fabric sample to the final fit.</span>', 'Adjust one shade or a whole room with compatible remote, wall or app controls.<span class="hero-detail"> John and Max help you choose, measure, install and set up your automated shades.</span>')
        hero = re.sub(r'<picture>[\s\S]*?</picture>\s*<video[\s\S]*?</video>', '<img src="/assets/powerview-wall-remote.jpg" alt="" width="1440" height="1080" fetchpriority="high">', hero)
    else:
        hero = hero.replace('Blinds, shades, shutters and drapery, chosen for your rooms and professionally installed.<span class="hero-detail"> Get personal help with the details, from the first fabric sample to the final fit.</span>', 'Blinds, shades, shutters, drapery and motorization, chosen for your rooms and professionally installed.<span class="hero-detail"> Get personal help from the first fabric sample to the final fit.</span>')
    brandbar = re.search(r'<div class="brand-bar"[\s\S]*?(?=<section class="reviews")', HOME).group().strip()
    if motorized:
        brandbar = re.sub(r'<button class="hero-video-toggle"[\s\S]*?</button>', '', brandbar)
    mobile = re.search(r'<div class="mobile-contact"[\s\S]*?</div>', HOME).group()
    mobile = mobile.replace('Call the showroom', 'Call Us').replace('Request a consultation', 'Get Free Quote')
    body = '\n'.join([header(motorized), '<main id="main">', hero, brandbar, reviews(motorized), products(motorized),
                      showroom(), motorization(motorized), services(motorized), contact(motorized), '</main>', footer(motorized), mobile, information_dialogs()])
    html = '<!doctype html>\n<html lang="en">\n'+absolute_assets(head)+'\n<body class="landing-page'+(' landing-motorized' if motorized else '')+'">\n<a class="skip-link" href="#main">Skip to content</a>\n'+absolute_assets(body)+'\n</body>\n</html>\n'
    path = DIST / route.strip('/') / 'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html)
    print(f'Built {route}')


build()
build(True)
