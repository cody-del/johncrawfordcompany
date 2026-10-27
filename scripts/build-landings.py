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


def cta(text='Request a consultation'):
    return f'<a class="btn btn-primary" href="#contact">{e(text)}</a>'


def header(motorized):
    html = re.search(r'<header class="site-header">[\s\S]*?</header>', HOME).group()
    nav = ('<nav class="main-navigation" id="main-navigation" aria-label="Main navigation">'
           f'<a href="#window-treatments">{"Shade styles" if motorized else "Window Treatments"}</a>'
           '<a href="#reviews">Reviews</a><a href="#about">Visit the Showroom</a>'
           '<a href="#contact">Contact</a></nav>')
    return re.sub(r'<nav class="main-navigation"[\s\S]*?</nav>', nav, html)


def footer(motorized):
    html = re.search(r'<footer class="site-footer"[\s\S]*?</footer>', HOME).group()
    html = re.sub(r'<nav class="footer-social"[\s\S]*?</nav>', '', html)
    if motorized:
        products = [('Roller shades', 'roller-shades'), ('Screen shades', 'screen-shades'),
                    ('Honeycomb shades', 'honeycomb-shades'), ('Woven wood shades', 'woven-wood-shades')]
    else:
        products = [('Blinds', 'blinds'), ('Shades', 'shades'), ('Shutters', 'shutters'),
                    ('Drapery', 'drapery'), ('Motorized shades', 'motorization')]
    links = '<div class="footer-links"><nav class="footer-nav" aria-labelledby="footer-products-heading">'
    links += '<h2 id="footer-products-heading">Window treatments</h2>'
    links += ''.join(f'<a href="#{anchor}">{name}</a>' for name, anchor in products)
    links += '</nav><nav class="footer-nav" aria-labelledby="footer-services-heading">'
    links += '<h2 id="footer-services-heading">Your project</h2>'
    links += '<a href="#services">Measuring &amp; installation</a><a href="#about">Visit the showroom</a>'
    links += '<a href="#questions">Common questions</a><a href="#contact">Request a consultation</a></nav></div>'
    html = re.sub(r'<div class="footer-links">[\s\S]*?</nav>\s*</div>', links, html)
    html = re.sub(r'\s*<a href="https://www.instagram.com/[\s\S]*?</a>', '', html)
    return html


def reviews(motorized):
    html = section('reviews')
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
      <a class="text-link" href="#contact">Discuss {e(title.lower())}</a></div>
      <p class="landing-photo-caption">{e(image['caption'])}</p></article>'''


def products(motorized):
    if not motorized:
        html = section('window-treatments')
        for name in ['blinds', 'shades', 'shutters', 'drapery']:
            html = html.replace(f'href="/{name}/">Explore {name}', f'href="#contact">Discuss {name}')
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
        html = html.replace('href="/motorized-shades/">Explore motorized shades', 'href="#contact">Discuss motorized shades')
        html = html.replace('</ul>', '</ul><p class="landing-disclosure">The PowerView® App is required for programmed operation.</p>')
        return html
    return '''<section class="section linen motorization" id="motorization" aria-labelledby="motor-heading">
      <div class="container feature-grid"><div class="feature-image"><img src="/assets/products/powerview-wall-control.png" alt="Round PowerView wall control mounted beside a pale fabric window shade." width="1280" height="853" loading="lazy" decoding="async"></div>
      <div class="feature-copy"><h2 id="motor-heading">Hunter Douglas PowerView® Automation</h2>
      <p>Lower several shades together when the afternoon sun arrives, or adjust a tall window from your seat. PowerView® Automation operates selected Hunter Douglas window treatments with a remote or the PowerView® App.</p>
      <ul class="simple-list"><li>Handheld and wall-mounted controls</li><li>Group compatible shades by room</li><li>Set schedules in the PowerView® App</li></ul>
      <p>John and Max help you choose the controls, confirm any gateway requirements and set up the system at installation.</p>
      <p class="landing-disclosure">The PowerView® App is required for programmed operation.</p>''' + cta('Discuss your motorized shades') + '</div></div></section>'


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


def questions(motorized):
    general = [
        ('How do I choose between blinds, shades, shutters and drapery?', 'Start with how you use the room, the amount of light and privacy you need, and the look you like. We’ll help you compare materials, fabrics and controls with your windows and budget in mind.'),
        ('Can you help with privacy and room darkening?', 'Yes. We can compare fabrics, opacity, linings and layering. Daytime and nighttime privacy can differ, especially with solar and sheer fabrics. The product, fit and light around the edges all affect how dark a room feels.'),
        ('Can I include motorization?', 'Motorization is available with compatible window treatments. Tell us which windows you want to control, and whether you prefer a remote, wall control or app. We’ll confirm the options for the product you choose.'),
        ('What affects the price?', 'Window dimensions, product style, material, fabric, lining, controls and installation requirements affect your quote. Share your priorities and budget so we can help you compare suitable choices.'),
        ('Which areas do you serve?', 'We’re based in Woodland Hills and serve the San Fernando Valley and parts of greater Los Angeles, including Calabasas, Beverly Hills, Malibu and Santa Monica. Contact us with your ZIP code to discuss your project.')
    ]
    motor = [
        ('Can I use a remote instead of an app?', 'Many systems offer a handheld remote or wall control as well as an app. We’ll confirm the options available for your shades. The PowerView® App is required for programmed operation.'),
        ('Can the shades open and close on a schedule?', 'Selected systems support scheduled operation. With Hunter Douglas PowerView® Automation, you set schedules in the PowerView® App. We’ll confirm the controls and any gateway needed for your setup.'),
        ('Will motorized shades work with my smart-home system?', 'Tell us which system you use. We’ll check the shade motor, controls and any gateway or accessories needed to connect them.'),
        ('Can you motorize shades I already have?', 'Sometimes. The product, age, condition and available components determine what’s possible. Send the brand and model if you know them, along with photos, so we can review the options.'),
        ('How are motorized shades powered?', 'Power choices depend on the product and may include replaceable batteries, rechargeable power or a wired connection. We’ll discuss access for charging or battery changes. If electrical work is needed, we can discuss the shade requirements with your electrician.'),
        general[-1]
    ]
    title = 'Questions about motorized shades' if motorized else 'Before you choose your window treatments'
    return f'''<section class="section questions" id="questions" aria-labelledby="questions-heading"><div class="container questions-grid">
      <div class="questions-intro"><h2 id="questions-heading">{title}</h2><p>Talk through your windows with John and Max. Call <a href="tel:+18188845464">(818) 884-5464</a>.</p></div>
      <div class="faq-list">''' + ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q,a in (motor if motorized else general)) + '</div></div></section>'


def contact(motorized):
    heading = 'Let’s talk about your motorized shades.' if motorized else 'Let’s talk about your windows.'
    copy = 'Tell us which windows you’d like to operate more easily. We’ll help you consider the shade style, controls and installation.' if motorized else 'Tell us about your rooms and what you’d like to change. We’ll help you compare blinds, shades, shutters, drapery and motorization.'
    return f'''<section class="section linen contact landing-contact" id="contact" aria-labelledby="contact-heading">
      <div class="container landing-contact-grid"><div class="landing-contact-copy"><h2 id="contact-heading">{heading}</h2><p>{copy}</p>
      <div class="contact-actions"><a class="btn btn-primary" href="tel:+18188845464">Call (818) 884-5464</a><a class="text-link" href="mailto:john@johncrawford.com?subject={'Motorized%20shades' if motorized else 'Window%20treatment'}%20consultation">Email us your project</a></div>
      <div class="landing-contact-location"><address>22311 Ventura Blvd #101, Woodland Hills, CA 91364</address><p>Monday–Friday, 9 am–5 pm</p></div></div>
      <form class="landing-form" aria-label="Consultation form preview" aria-describedby="form-preview form-required">
      <h3>Request a consultation</h3><p class="landing-preview-note" id="form-preview">This form is a design preview. Please call or email us about your project.</p>
      <div class="landing-form-fields">
      <div class="landing-form-field"><label for="lead-name">Full name</label><input id="lead-name" name="name" autocomplete="name" type="text" maxlength="120" required disabled></div>
      <div class="landing-form-field"><label for="lead-phone">Phone number</label><input id="lead-phone" name="phone" autocomplete="tel" type="tel" maxlength="30" required disabled></div>
      <div class="landing-form-field"><label for="lead-email">Email</label><input id="lead-email" name="email" autocomplete="email" type="email" maxlength="254" required disabled></div>
      </div><p class="landing-required" id="form-required">All fields are required.</p><button class="btn btn-primary" type="button" disabled>Request a consultation</button>
      <p class="landing-privacy">We use your contact details to respond to your project inquiry. <a href="/privacy/">Privacy Policy</a>.</p></form></div></section>'''


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
    head = head.replace('</head>', '<link rel="stylesheet" href="/landings.css?v=landing-1">\n</head>')
    if motorized:
        head = re.sub(r'  <link rel="preload" href="assets/hero-room-poster-[^\n]+\n', '', head)
        head = head.replace(BASE+'/assets/hero-room-poster-desktop.webp', BASE+'/assets/powerview-wall-remote.jpg')
        head = head.replace('A finished shade installation from John Crawford Company project footage', 'Hunter Douglas PowerView wall-mounted remote beside blue window shades')
        head = head.replace('</head>', '<link rel="preload" as="image" href="/assets/powerview-wall-remote.jpg">\n</head>')
    hero = section('top')
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
    body = '\n'.join([header(motorized), '<main id="main">', hero, brandbar, reviews(motorized), products(motorized),
                      section('about'), motorization(motorized), services(motorized), questions(motorized), contact(motorized), '</main>', footer(motorized), mobile])
    html = '<!doctype html>\n<html lang="en">\n'+absolute_assets(head)+'\n<body class="landing-page'+(' landing-motorized' if motorized else '')+'">\n<a class="skip-link" href="#main">Skip to content</a>\n'+absolute_assets(body)+'\n</body>\n</html>\n'
    path = DIST / route.strip('/') / 'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html)
    print(f'Built {route}')


build()
build(True)
