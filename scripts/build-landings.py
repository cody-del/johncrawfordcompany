"""Build focused campaign pages with the approved website's brand assets."""
from pathlib import Path
from html import escape
import json
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
    return '''<section class="section about" id="about" aria-labelledby="about-heading">
      <div class="container about-grid"><div class="about-copy">
      <h2 class="showroom-title" id="about-heading"><img src="/assets/showroom-visit-headline.png" alt="Visit us in Woodland Hills" width="2514" height="840" loading="lazy" decoding="async"></h2>
      <p class="landing-john-story">John got his start installing window treatments before opening his California store in 1995. That experience still shapes the advice we give in our Woodland Hills showroom.</p>
      <p class="landing-appointment-label"><strong>Appointment Only</strong></p>
      <p>Fill the form to schedule a showroom appointment or free in-home consultation.</p><a class="btn btn-primary" href="#contact">Schedule Appointment</a>
      </div><div class="showroom-card"><figure class="showroom-figure">
      <img src="/assets/showroom-illustration.svg?v=trees-2" alt="Illustration of John Crawford Company’s showroom with its red tile roof and palm trees" width="2394" height="1030" loading="lazy" decoding="async">
      </figure></div></div></section>'''


def information_dialogs():
    return '''<dialog class="landing-info-dialog" id="landing-privacy-dialog" aria-labelledby="landing-privacy-heading">
      <div class="landing-dialog-heading"><h2 id="landing-privacy-heading">Privacy Policy</h2><form method="dialog"><button class="landing-info-button" type="submit" autofocus>Close</button></form></div>
      <p>The quote form on this review page does not accept submissions. If you call us, we use the information you provide to respond and discuss your project.</p>
      <p>These pages are hosted through Netlify and ChatGPT Sites. Hosting providers may process technical information, such as IP addresses, browser details and request logs, to deliver and secure the pages. Advertising pixels and audience-tracking analytics have not been installed on these pages.</p>
      <p>For questions about information you provide, call John Crawford Company at <a href="tel:+18188845464">(818) 884-5464</a>.</p></dialog>
      <dialog class="landing-info-dialog" id="landing-accessibility-dialog" aria-labelledby="landing-accessibility-heading">
      <div class="landing-dialog-heading"><h2 id="landing-accessibility-heading">Accessibility assistance</h2><form method="dialog"><button class="landing-info-button" type="submit" autofocus>Close</button></form></div>
      <p>If you have difficulty reading this page or requesting a quote, call <a href="tel:+18188845464">(818) 884-5464</a>. Tell us which feature caused the problem and how you would like us to contact you.</p>
      <p>We can discuss products, quote requests and accessibility assistance by phone. Showroom visits are by appointment only.</p></dialog>'''


def reviews(motorized):
    html = section('reviews')
    html = re.sub(r'<a class="reviews-source"[\s\S]*?</a>', '<span class="reviews-source">Review source: Google Maps</span>', html)
    cards = re.findall(r'<article class="review-card"[\s\S]*?</article>', html)
    selected_ids = ['carol', 'harley', 'mary', 'monica'] if motorized else ['mary', 'lily', 'monica', 'carol']
    selected = [next(card for card in cards if f'review-{id}-name' in card) for id in selected_ids]
    html = html.replace(cards[0], '__SELECTED_REVIEWS__')
    for card in cards[1:]:
        html = html.replace(card, '')
    html = html.replace('__SELECTED_REVIEWS__', '\n'.join(selected))
    return re.sub(r'[ \t]+\n', '\n', html)


def products(motorized):
    if motorized:
        images = json.loads((ROOT / 'content/product-images.json').read_text())
        options = [('designer-roller', 'Roller Shades'), ('designer-screen', 'Solar Shades'),
                   ('duette', 'Cellular Shades'), ('provenance', 'Woven Wood Shades')]
        cards = []
        for key, label in options:
            photo = images[key]
            cards.append(f'''<article class="product"><img src="{e(photo['src'])}" alt="{e(photo['alt'])}" width="{photo['width']}" height="{photo['height']}" loading="lazy" decoding="async"><div class="product-copy"><h3>{e(label)}</h3></div></article>''')
    else:
        cards = re.findall(r'<article class="product"[\s\S]*?</article>', section('window-treatments'))
        cards = [re.sub(r'\s*<(p|a)\b[\s\S]*?</\1>', '', card) for card in cards]
    heading = 'Shade styles' if motorized else 'Window treatment styles'
    return f'''<section class="section landing-products" id="product-options" aria-labelledby="products-heading"><div class="container">
      <h2 class="sr-only" id="products-heading">{heading}</h2><div class="product-grid">''' + '\n'.join(cards) + '</div></div></section>'


def benefits(motorized):
    if motorized:
        heading = 'Easier control. Every day.'
        items = [
            ('Less reaching', 'Adjust tall and hard-to-reach shades with a compatible remote.'),
            ('A whole room, one control', 'Group compatible shades to open or close them together.'),
            ('Ready to use', 'We install your shades, set up the controls and show you how they work.')
        ]
    else:
        heading = 'Made to fit your home.'
        items = [
            ('Light that suits the room', 'Filter bright daylight, add privacy or choose more room darkening.'),
            ('A fit made for your windows', 'We measure your windows and help you choose the right style, fabric and finish.'),
            ('Installation taken care of', 'Our team installs your treatments and shows you how the controls work.')
        ]
    cards = ''.join(f'<article class="landing-benefit"><h3>{e(title)}</h3><p>{e(copy)}</p></article>' for title, copy in items)
    return f'''<section class="section landing-benefits" id="benefits" aria-labelledby="benefits-heading"><div class="container">
      <h2 id="benefits-heading">{e(heading)}</h2><div class="landing-benefits-grid">{cards}</div></div></section>'''


def quote_form(motorized):
    intro = ('John helps you choose motorized shades and controls that fit your rooms and daily routine.' if motorized else
             'John helps you choose blinds, shades, shutters or drapery for your home, with motorization available.')
    service = ('Our team handles measuring, installation and control setup, then shows you how to use your shades.' if motorized else
               'Our team handles measuring and installation, and shows you how to use your new window treatments.')
    return f'''<section class="section linen landing-quote" aria-labelledby="company-summary-heading"><div class="container landing-quote-grid">
      <div class="landing-company-summary"><p class="landing-company-eyebrow">John Crawford Company</p><h2 id="company-summary-heading">Work with John Crawford.</h2><p>{e(intro)}</p><p>{e(service)}</p><a class="btn btn-showroom-contact" href="tel:+18188845464">Call Us</a></div>
      <form class="landing-form" id="contact" aria-labelledby="quote-heading" aria-describedby="form-preview form-required">
      <h2 id="quote-heading">Get your free quote</h2>
      <p class="landing-follow-up">We’ll follow up about your quote or appointment request.</p>
      <p class="landing-preview-note" id="form-preview">Form preview. Please call us until online quotes are available.</p>
      <div class="landing-form-fields">
      <div class="landing-form-field"><label for="lead-name">Full name</label><input id="lead-name" name="name" autocomplete="name" type="text" maxlength="120" required disabled></div>
      <div class="landing-form-field"><label for="lead-phone">Phone number</label><input id="lead-phone" name="phone" autocomplete="tel" type="tel" maxlength="30" required disabled></div>
      <div class="landing-form-field"><label for="lead-email">Email</label><input id="lead-email" name="email" autocomplete="email" type="email" maxlength="254" required disabled></div>
      </div><p class="landing-required" id="form-required">Contact fields are required.</p>
      <label class="landing-appointment-choice" for="lead-showroom"><input id="lead-showroom" name="showroom-appointment" type="checkbox" value="requested" disabled><span>I’d like a showroom appointment.</span></label>
      <button class="btn btn-primary" type="button" disabled>Get Free Quote</button>
      <p class="landing-privacy">Your details are used to respond to your inquiry. <button class="landing-info-button" type="button" data-landing-dialog="landing-privacy-dialog" aria-haspopup="dialog" aria-controls="landing-privacy-dialog">Privacy Policy</button>.</p></form></div></section>'''


def hero(motorized):
    service = 'Motorized Shades' if motorized else 'Custom Window Treatments'
    headline = f'<span class="landing-hero-title">{service}</span> <span class="landing-hero-location">in Los Angeles &amp; Surrounding Areas</span>'
    promise = ('Open a room to daylight with a touch. We handle measuring, installation and control setup.' if motorized else
               'Get help choosing blinds, shades, shutters or drapery, including motorization. We handle measuring and installation.')
    media = re.search(r'<div class="hero-media"[\s\S]*</div>\s*</section>', section('top')).group()
    media = media.rsplit('</section>', 1)[0]
    video_control = re.search(r'<button class="hero-video-toggle"[\s\S]*?</button>', HOME).group()
    return f'''<section class="hero landing-hero" id="top" aria-labelledby="hero-heading">
      <div class="container landing-hero-inner"><div class="hero-content">
      <h1 id="hero-heading">{headline}</h1>
      <p class="landing-promise">{e(promise)}</p>
      <div class="hero-actions">{cta()}<a class="btn btn-showroom-contact" href="tel:+18188845464">Call Us</a></div>
      </div></div>{media}{video_control}</section>'''


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
    # Campaign pages route showroom visits through appointments, without an address or walk-in hours.
    head = re.sub(r'\s*<script type="application/ld\+json">[\s\S]*?</script>', '', head)
    head = head.replace('</head>', '<link rel="stylesheet" href="/landings.css?v=benefit-panel-centered-1">\n</head>')
    mobile = re.search(r'<div class="mobile-contact"[\s\S]*?</div>', HOME).group()
    mobile = mobile.replace('Call the showroom', 'Call Us').replace('Request a consultation', 'Get Free Quote')
    body = '\n'.join([header(motorized), '<main id="main">', hero(motorized), reviews(motorized), products(motorized),
                      benefits(motorized), showroom(), quote_form(motorized), '</main>', footer(motorized), mobile, information_dialogs()])
    html = '<!doctype html>\n<html lang="en">\n'+absolute_assets(head)+'\n<body class="landing-page'+(' landing-motorized' if motorized else '')+'">\n<a class="skip-link" href="#main">Skip to content</a>\n'+absolute_assets(body)+'\n</body>\n</html>\n'
    path = DIST / route.strip('/') / 'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html)
    print(f'Built {route}')


build()
build(True)
