#!/usr/bin/env python3
"""Check all 100 built landing pages and the complete navigation graph."""
import json,re
from pathlib import Path
from urllib.parse import urlsplit, unquote
from check_seo import Page
ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'coworking/manifest.json').read_text())
assert len(rows)==100
assert len({x['title'] for x in rows})==100
assert len({x['description'] for x in rows})==100
assert len({x['path'] for x in rows})==100
cache={}
def parse(path):
    if path not in cache:cache[path]=Page(path.read_text())
    return cache[path]
hub=parse(ROOT/'coworking/index.html')
answers=[]
for row in rows:
    path=ROOT/row['file'];text=path.read_text();p=parse(path)
    assert len(p.h1)==1,path
    assert p.title==row['title'] and len(p.title)<=60,path
    assert p.meta['description']==row['description'] and len(row['description'])<=155,path
    assert p.canonical=='https://coworking.jobreadybpo.com'+row['path'],path
    assert p.meta['og:title']==p.meta['twitter:title']==p.title,path
    assert row['path'] in hub.links,path
    assert not re.search(r'\[VERIFY|\[INSERT|___',text),path
    assert 'data-enquiry=' in text and 'name="Team size" required' in text,path
    assert 'autocomplete="name" required' in text and 'autocomplete="tel" required' in text,path
    faq=next(x for x in p.schemas if x['@type']=='FAQPage')
    assert len(faq['mainEntity'])==4,path
    for qa in faq['mainEntity']:
        assert qa['name'] in p.faq,path
        assert qa['acceptedAnswer']['text'] in p.text,path
        answers.append(qa['acceptedAnswer']['text'])
    assert {'plans','location','faqs','enquire','main'}<=p.ids,path
assert len(set(answers))==400
for path in list(ROOT.rglob('*.html')):
    p=parse(path)
    assert '/coworking/' in p.links,path
    for link in p.links:
        u=urlsplit(link)
        if u.scheme or u.netloc:continue
        target=ROOT/u.path.lstrip('/') if u.path.startswith('/') else path.parent/u.path
        if not u.path:target=path
        if target.is_dir():target=target/'index.html'
        assert target.is_file(),(path,link)
        if u.fragment:assert unquote(u.fragment) in parse(target).ids,(path,link)
print('PASS: 100 individual landing pages + directory; unique metadata; 400 unique visible answers matching FAQ schema.')
print('PASS: all HTML pages reach Coworking; all internal destinations, assets and fragments exist.')
print('PASS: required lead fields, name/tel autocomplete, truthful enquiry flow, single H1, title/meta limits and no raw placeholders.')
