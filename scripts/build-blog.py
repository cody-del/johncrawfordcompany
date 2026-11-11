"""Build the approved blog articles as static HTML using the shared site shell."""
from pathlib import Path
import importlib.util
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
POSTS = json.loads((ROOT / 'content/blog-posts.json').read_text())
spec = importlib.util.spec_from_file_location('company_pages', ROOT / 'scripts/build-company-pages.py')
company = importlib.util.module_from_spec(spec)
spec.loader.exec_module(company)
BASE = company.BASE
e = company.e


def paragraphs(block):
    result = []
    for index, text in enumerate(block.get('paragraphs', [])):
        spans = []
        for link in block.get('links', []):
            if link.get('paragraph', 0) != index:
                continue
            if not link['href'].startswith(('/', 'https://', 'tel:')):
                raise ValueError(f'Unsupported article link: {link["href"]}')
            match = re.search(r'(?<!\w)' + re.escape(link['text']) + r'(?!\w)', text)
            if not match:
                raise ValueError(f'Article link text not found: {link["text"]}')
            spans.append((match.start(), match.end(), link))
        html, offset = [], 0
        for start, end, link in sorted(spans, key=lambda span: span[0]):
            if start < offset:
                raise ValueError('Overlapping article links')
            html += [e(text[offset:start]), f'<a href="{e(link["href"])}">{e(text[start:end])}</a>']
            offset = end
        result.append('<p>' + ''.join(html) + e(text[offset:]) + '</p>')
    return ''.join(result)


def table(section):
    data = section['table']
    headings = ''.join(f'<th scope="col">{e(label)}</th>' for label in data['columns'])
    rows = ''.join(
        f'<tr><th scope="row"><a href="{e(row["href"])}">{e(row["product"])}</a></th>'
        + ''.join(f'<td>{e(row[key])}</td>' for key in ['reason', 'light', 'planning']) + '</tr>'
        for row in data['rows']
    )
    return ('<div class="article-comparison" role="region" tabindex="0" aria-label="Product comparison">'
            '<table><caption class="sr-only">Hunter Douglas product comparison for large windows</caption>'
            f'<thead><tr>{headings}</tr></thead><tbody>{rows}</tbody></table></div>')


def section_html(section):
    body = paragraphs(section)
    for subsection in section.get('subsections', []):
        body += f'<h3>{e(subsection["heading"])}</h3>' + paragraphs(subsection)
    if section.get('table'):
        body += table(section)
    if section.get('note'):
        body += f'<p class="article-note">{e(section["note"])}</p>'
    if section.get('cta'):
        cta = section['cta']
        body += f'<div class="article-actions"><a class="btn btn-primary" href="{e(cta["href"])}">{e(cta["text"])}</a></div>'
    return (f'<section class="article-section" id="{e(section["id"])}" aria-labelledby="{e(section["id"])}-heading">'
            f'<h2 id="{e(section["id"])}-heading">{e(section["heading"])}</h2>{body}</section>')


def head(post):
    html = company.head(post, 'WebPage')
    html = html.replace('content="website"', 'content="article"', 1)
    html = html.replace(BASE + '/assets/john-crawford-logo.png', BASE + post['cover']['src'])
    html = html.replace('content="John Crawford Company — Window Treatments"', f'content="{e(post["cover"]["alt"])}"')
    html = html.replace('</head>', '<link rel="stylesheet" href="/blog.css?v=large-windows-20261111">'
                        f'<meta property="article:published_time" content="{e(post["published"])}">\n</head>')

    def schema(match):
        graph = json.loads(match.group(1))
        article_id = BASE + post['slug'] + '#article'
        graph[0]['mainEntity'] = {'@id': article_id}
        graph[0]['isPartOf'] = {'@id': BASE + '/blog/#page'}
        graph[1]['itemListElement'] = [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': BASE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Blog', 'item': BASE + '/blog/'},
            {'@type': 'ListItem', 'position': 3, 'name': post['heading'], 'item': BASE + post['slug']}
        ]
        cover = post['cover']
        graph.append({
            '@context': 'https://schema.org', '@type': 'BlogPosting', '@id': article_id,
            'url': BASE + post['slug'], 'headline': post['heading'], 'description': post['description'],
            'datePublished': post['published'], 'dateModified': post['published'], 'inLanguage': 'en-US',
            'author': {'@type': 'Organization', 'name': post['author'], 'url': BASE + '/about/'},
            'publisher': {'@id': BASE + '/#business'},
            'mainEntityOfPage': {'@id': BASE + post['slug'] + '#page'},
            'isPartOf': {'@id': BASE + '/blog/#page'},
            'image': {'@type': 'ImageObject', 'url': BASE + cover['src'], 'width': cover['width'], 'height': cover['height']}
        })
        return '<script type="application/ld+json">' + json.dumps(graph, ensure_ascii=False).replace('<', '\\u003c') + '</script>'

    return re.sub(r'<script type="application/ld\+json">([\s\S]*?)</script>', schema, html)


def body(post):
    cover = post['cover']
    intro = ''.join(f'<p>{e(text)}</p>' for text in post['intro'])
    sections = ''.join(section_html(section) for section in post['sections'])
    return f'''<main id="main" class="blog-post"><article aria-labelledby="page-heading">
    <header class="article-header"><div class="container article-heading">
      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/blog/">Blog</a></nav>
      <h1 id="page-heading">{e(post['heading'])}</h1>
      <p class="article-meta"><span>By <a href="/about/">{e(post['author'])}</a></span><span aria-hidden="true"> · </span><time datetime="{e(post['published'])}">{e(post['published_display'])}</time></p>
    </div></header>
    <figure class="article-cover"><img src="{e(cover['src'])}" alt="{e(cover['alt'])}" width="{cover['width']}" height="{cover['height']}" fetchpriority="high" decoding="async"><figcaption>{e(cover['caption'])}</figcaption></figure>
    <div class="article-body"><div class="article-lead">{intro}</div>{sections}<p class="article-back"><a href="/blog/">Back to the blog</a></p></div>
    </article></main>'''


if __name__ == '__main__':
    for post in POSTS:
        header, footer, mobile = company.partials(post)
        target = DIST / post['slug'].strip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(head(post) + header + body(post) + footer + mobile + '</body></html>\n')
        print(post['slug'])
