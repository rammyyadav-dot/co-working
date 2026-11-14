#!/usr/bin/env python3
"""Validate generated SEO coverage, metadata, schemas and crawlable links."""
import json
import re
import struct
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree
from seo_metadata import for_page
from migrate_urls import file_for,destination

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://coworking.jobreadybpo.com'

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.meta, self.schemas = [], set(), {}, []
        self.title, self.h1, self.text, self.faq = '', [], [], []
        self.active = None
        self.script = None
        self.faq_active = False
        self.in_header = False
        self.canonical = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'header': self.in_header = True
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate ID {a["id"]}'
            self.ids.add(a['id'])
        for key in ('href','src'):
            if a.get(key): self.links.append(a[key])
        if tag == 'meta':
            key = a.get('name',a.get('property'))
            if key:
                assert key not in self.meta, f'Duplicate metadata: {key}'
                self.meta[key] = a.get('content')
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = a['href']
        if tag in ('title','h1') or (tag == 'summary' and not self.in_header): self.active = tag
        if tag == 'h1': self.h1.append('')
        if tag == 'summary' and not self.in_header: self.faq.append('')
        if tag == 'script': self.script = '' if a.get('type') == 'application/ld+json' else False

    def handle_data(self, data):
        if self.script is not None:
            if self.script is not False: self.script += data
            return
        self.text.append(data)
        if self.active == 'title': self.title += data
        if self.active == 'h1': self.h1[-1] += data
        if self.active == 'summary': self.faq[-1] += data

    def handle_endtag(self, tag):
        if tag == 'header': self.in_header = False
        if tag == self.active: self.active = None
        if tag == 'script':
            if self.script is not None and self.script is not False: self.schemas.append(json.loads(self.script))
            self.script = None

def main():
    topics = json.loads((ROOT/'seo/keyword-map.json').read_text())
    assert len(topics) == 100
    paths = [ROOT/'guides/index.html']+[ROOT/'guides'/t['slug']/'index.html' for t in topics]
    pages = {path:Page(path.read_text()) for path in paths}
    titles, descriptions, canonicals, words = set(), set(), set(), []
    for path, p in pages.items():
        assert len(p.h1) == 1, path
        assert p.title and len(p.title)<=60 and p.title not in titles, path
        desc = p.meta.get('description','')
        assert 70 <= len(desc) <= 155 and desc not in descriptions, (path,len(desc))
        assert p.canonical and p.canonical not in canonicals, path
        assert p.meta['og:url'] == p.canonical, path
        assert p.meta['og:title'] == p.meta['twitter:title'] == p.title, path
        assert p.meta['og:description'] == p.meta['twitter:description'] == desc, path
        assert p.meta['og:type'] == ('website' if path == ROOT/'guides/index.html' else 'article'), path
        assert p.meta['og:locale'] == 'en_IN', path
        assert p.meta['og:site_name'], path
        assert p.meta['twitter:card'] == 'summary_large_image', path
        assert p.meta['og:image'] == p.meta['og:image:secure_url'] == p.meta['twitter:image'], path
        assert p.meta['og:image:alt'] == p.meta['twitter:image:alt'] and p.meta['og:image:alt'], path
        assert p.meta['og:image:width'] == '1200' and p.meta['og:image:height'] == '630', path
        assert p.meta['og:image:type'] == 'image/png', path
        image_url = p.meta['og:image']
        assert image_url.startswith(BASE+'/seo/assets/social/'), path
        image = ROOT/urlsplit(image_url).path.lstrip('/')
        data = image.read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24]) == (1200,630), image
        assert p.meta['robots'] == 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1', path
        assert p.schemas, path
        titles.add(p.title); descriptions.add(desc); canonicals.add(p.canonical)
        words.append(len(re.findall(r'\b\w+\b',' '.join(p.text))))
        for link in p.links:
            u = urlsplit(link)
            if u.scheme or u.netloc: continue
            target = (ROOT/u.path.lstrip('/')) if u.path.startswith('/') else path.parent/u.path
            if not u.path: target = path
            if target.is_dir(): target = target/'index.html'
            assert target.is_file(), (path,link)
            if u.fragment:
                parsed = pages.get(target) or Page(target.read_text())
                assert unquote(u.fragment) in parsed.ids, (path,link)
    for t in topics:
        p = pages[ROOT/'guides'/t['slug']/'index.html']
        assert p.h1 == [t['keyword']]
        assert (p.title,p.meta['description'])==for_page('/seo/'+t['slug']+'.html')
        assert '…' not in p.meta['description'] and p.meta['description'].endswith('.'), p.meta['description']
        assert p.canonical == BASE+'/guides/'+t['slug']+'/'
        graph = p.schemas[0]['@graph']
        faq = next(x for x in graph if x['@type']=='FAQPage')
        assert [x['name'] for x in faq['mainEntity']] == p.faq
        assert p.title in pages[ROOT/'guides/index.html'].text, t['slug']
        assert p.meta['description'] in pages[ROOT/'guides/index.html'].text, t['slug']
        assert t['question'] in p.faq and len(p.faq) == 5
    sitemap = ElementTree.parse(ROOT/'sitemap.xml')
    urls = [x.text for x in sitemap.findall('.//{*}loc')]
    collection = json.loads((ROOT/'coworking/manifest.json').read_text()) if (ROOT/'coworking/manifest.json').exists() else []
    from seo_metadata import COPY
    assert len(urls) == len(set(urls)) == len(COPY)-1  # 404 remains outside the sitemap.
    assert canonicals <= set(urls)
    for url in urls:
        assert url.startswith(BASE+'/')
        target = ROOT/urlsplit(url).path.lstrip('/')
        assert target.exists(), url
    assert BASE+'/sitemap.xml' in (ROOT/'robots.txt').read_text()
    assert 'href="/guides/"' in (ROOT/'index.html').read_text()
    primary_titles, primary_descriptions = set(), set()
    for filename in ['index.html','jobreadyvirtualoffice.html','company_registration.html','business_services.html','tax_compliance.html','enterprise.html']:
        path = ROOT/file_for(destination('/'+filename))
        page = Page(path.read_text())
        assert len(page.h1) == 1 and len(page.title) <= 60, filename
        assert page.meta['robots'] == 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1', filename
        description = page.meta['description']
        assert 120 <= len(description) <= 155 and description.endswith('.'), filename
        assert page.title not in primary_titles and description not in primary_descriptions, filename
        primary_titles.add(page.title); primary_descriptions.add(description)
        assert page.canonical == BASE+destination('/'+filename), filename
        assert page.meta['og:url'] == page.canonical and page.canonical in urls
        assert page.meta['og:title'] == page.meta['twitter:title'] == page.title
        assert page.meta['og:description'] == page.meta['twitter:description'] == description
        image=ROOT/urlsplit(page.meta['og:image']).path.lstrip('/')
        assert image.is_file() and struct.unpack('>II',image.read_bytes()[16:24])==(1200,630)
        for link in page.links:
            u=urlsplit(link)
            if u.scheme or u.netloc: continue
            target=ROOT/u.path.lstrip('/') if u.path.startswith('/') else path.parent/u.path
            if not u.path: target=path
            if target.is_dir(): target=target/'index.html'
            assert target.is_file(), (filename,link)
            if u.fragment:
                assert unquote(u.fragment) in Page(target.read_text()).ids, (filename,link)
    print(f'PASS: 100 keyword guides + directory; unique metadata; 500 matching FAQ records; all internal assets, links and fragments; {len(urls)} sitemap URLs.')
    print('PASS: complete Open Graph and Twitter cards on 101 pages; matching titles/descriptions; 1200×630 PNG assets; complete sentences; titles ≤60 and descriptions ≤155 characters.')
    print('PASS: six primary pages with concise unique metadata, canonical host alignment, social cards, one H1 and working internal destinations.')
    print(f'Topic page visible word range: {min(words[:-1])}–{max(words[1:])} (including navigation and related content).')

if __name__ == '__main__': main()
