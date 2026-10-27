"""Build campaign pages using the approved homepage's actual sections and styles."""
from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
HOME = (DIST / 'index.html').read_text()
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
      </div><div class="landing-footer-actions">''' + cta() + '''<a class="btn btn-showroom-contact" href="tel:+18188845464">Call Us</a></div></div>
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
    cards = re.findall(r'<article class="review-card"[\s\S]*?</article>', html)
    selected_ids = ['carol', 'perry', 'mary', 'monica'] if motorized else ['mary', 'lily', 'monica', 'carol']
    selected = [next(card for card in cards if f'review-{id}-name' in card) for id in selected_ids]
    html = html.replace(cards[0], '__SELECTED_REVIEWS__')
    for card in cards[1:]:
        html = html.replace(card, '')
    html = html.replace('__SELECTED_REVIEWS__', '\n'.join(selected))
    return re.sub(r'[ \t]+\n', '\n', html)


def products():
    html = section('window-treatments')
    html = re.sub(r'<div class="section-intro">[\s\S]*?</div>', '<div class="section-intro"><h2 id="products-heading">Choose the look you love.</h2></div>', html)
    copy = {
        'blinds': 'Tilt the slats for daylight and everyday privacy.',
        'shades': 'Soften bright light or choose more room darkening.',
        'shutters': 'Adjust light and privacy with a finished, architectural look.',
        'drapery': 'Bring softness, texture and a fabric you love.'
    }
    for name, text in copy.items():
        card = re.search(r'<article class="product" id="' + name + r'"[\s\S]*?</article>', html).group()
        short = re.sub(r'<p>[\s\S]*?</p>', f'<p>{e(text)}</p>', card)
        short = re.sub(r'\s*<a\b[\s\S]*?</a>', '', short)
        html = html.replace(card, short)
    closing = '<div class="landing-product-close"><p>Motorization makes hard-to-reach windows easier to use.</p>' + cta() + '</div>'
    before, after = html.rsplit('</div>', 1)
    return before + closing + '</div>' + after


def motorization():
    return '''<section class="section linen motorization" id="motorization" aria-labelledby="motor-heading">
      <div class="container feature-grid"><div class="feature-image"><img src="/assets/products/powerview-wall-control.png" alt="Round PowerView wall control mounted beside a pale fabric window shade." width="1280" height="853" loading="lazy" decoding="async"></div>
      <div class="feature-copy"><h2 id="motor-heading">Less reaching. More control.</h2>
      <ul class="simple-list"><li>Adjust tall windows with a remote.</li><li>Open or close several shades together.</li><li>Schedule compatible shades in the PowerView® App.</li></ul>
      <p>Roller, screen, honeycomb and woven wood options. We install the shades and set up your controls.</p>
      <p class="landing-disclosure">The PowerView® App is required for programmed operation.</p>''' + cta() + '</div></div></section>'






def contact(motorized):
    heading = 'Get a free quote for motorized shades.' if motorized else 'Get a free quote for your windows.'
    copy = 'Share your details. John or Max will contact you to discuss your windows and the next steps for your quote.'
    return f'''<section class="section linen contact landing-contact" id="contact" aria-labelledby="contact-heading">
      <div class="container landing-contact-grid"><div class="landing-contact-copy"><h2 id="contact-heading">{heading}</h2><p>{copy}</p>
      <div class="contact-actions"><a class="btn btn-showroom-contact" href="tel:+18188845464">Call Us</a><p class="landing-public-phone">(818) 884-5464</p></div>
      </div>
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
    head = head.replace('</head>', '<link rel="stylesheet" href="/landings.css?v=outcomes-1">\n</head>')
    if motorized:
        head = re.sub(r'  <link rel="preload" href="assets/hero-room-poster-[^\n]+\n', '', head)
        head = head.replace(BASE+'/assets/hero-room-poster-desktop.webp', BASE+'/assets/powerview-wall-remote.jpg')
        head = head.replace('A finished shade installation from John Crawford Company project footage', 'Hunter Douglas PowerView wall-mounted remote beside blue window shades')
        head = head.replace('</head>', '<link rel="preload" as="image" href="/assets/powerview-wall-remote.jpg">\n</head>')
    hero = section('top')
    hero = hero.replace('Request a consultation', 'Get Free Quote')
    hero = re.sub(r'<a class="hero-phone" href="tel:[^"]+">[\s\S]*?</a>', '<a class="btn btn-showroom-contact" href="tel:+18188845464">Call Us</a>', hero)
    headline = 'Motorized shades.<span>Control light from your seat.</span>' if motorized else 'The light you want.<span>The privacy you need.</span>'
    promise = 'Adjust one window or a whole room. We install your shades and set up the controls.' if motorized else 'Custom blinds, shades, shutters and drapery, with motorization options. John and Max handle the measuring and installation.'
    hero = re.sub(r'(<h1 id="hero-heading">)[\s\S]*?</h1>', lambda m: m[1] + headline + '</h1>', hero)
    hero = re.sub(r'<p>[\s\S]*?</p>', '<p>' + e(promise) + '</p>', hero, count=1)
    hero = re.sub(r'<p class="hero-location">[\s\S]*?</p>', '<p class="hero-location">Serving Los Angeles from our Woodland Hills showroom.</p>', hero)
    if motorized:
        hero = re.sub(r'<picture>[\s\S]*?</picture>\s*<video[\s\S]*?</video>', '<img src="/assets/powerview-wall-remote.jpg" alt="" width="1440" height="1080" fetchpriority="high">', hero)
    brandbar = re.search(r'<div class="brand-bar"[\s\S]*?(?=<section class="reviews")', HOME).group().strip()
    if motorized:
        brandbar = re.sub(r'<button class="hero-video-toggle"[\s\S]*?</button>', '', brandbar)
    mobile = re.search(r'<div class="mobile-contact"[\s\S]*?</div>', HOME).group()
    mobile = mobile.replace('Call the showroom', 'Call Us').replace('Request a consultation', 'Get Free Quote')
    body = '\n'.join([header(motorized), '<main id="main">', hero, brandbar, reviews(motorized), motorization() if motorized else products(),
                      showroom(), contact(motorized), '</main>', footer(motorized), mobile, information_dialogs()])
    html = '<!doctype html>\n<html lang="en">\n'+absolute_assets(head)+'\n<body class="landing-page'+(' landing-motorized' if motorized else '')+'">\n<a class="skip-link" href="#main">Skip to content</a>\n'+absolute_assets(body)+'\n</body>\n</html>\n'
    path = DIST / route.strip('/') / 'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html)
    print(f'Built {route}')


build()
build(True)
