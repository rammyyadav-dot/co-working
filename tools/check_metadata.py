#!/usr/bin/env python3
"""Check character limits, uniqueness, rendered tags and generator persistence."""
import json
from pathlib import Path
from check_seo import Page
from seo_metadata import ROOT,COPY,for_page

files=sorted(ROOT.rglob('*.html'))
assert {str(p.relative_to(ROOT)) for p in files}==set(COPY)
titles=set();descriptions=set()
for path in files:
    filename=str(path.relative_to(ROOT));page=Page(path.read_text())
    title,description=for_page(filename)
    assert (page.title,page.meta['description'])==(title,description),filename
    assert 0<len(title)<=60 and 80<=len(description)<=155,filename
    assert title.casefold() not in titles and description.casefold() not in descriptions,filename
    titles.add(title.casefold());descriptions.add(description.casefold())
    assert not any(t in title+description for t in ('…','[INSERT','[VERIFY','___')),filename
    assert description.endswith(('.','!','?')),filename
    if filename=='404.html':
        assert 'noindex' in page.meta['robots'],filename
    else:
        assert page.meta['og:title']==page.meta['twitter:title']==title,filename
        assert page.meta['og:description']==page.meta['twitter:description']==description,filename
        assert 'noindex' not in page.meta['robots'],filename
        assert page.meta['og:url']==page.canonical,filename
        assert page.meta['og:image']==page.meta['twitter:image'],filename
        assert page.meta['og:image:alt']==page.meta['twitter:image:alt']==title,filename
        from urllib.parse import urlsplit
        assert (ROOT/urlsplit(page.meta['og:image']).path.lstrip('/')).is_file(),filename
    assert 'keywords' not in page.meta,filename
    def schemas(node):
        if isinstance(node,dict):
            types=node.get('@type',[])
            if isinstance(types,str):types=[types]
            if set(types)&{'Article','WebPage','CollectionPage'}:assert node['description']==description,filename
            for value in node.values():schemas(value)
        elif isinstance(node,list):
            for value in node:schemas(value)
    schemas(page.schemas)
print(f'PASS: {len(files)} unique title/description pairs; titles ≤60, descriptions ≤155; social and document schema descriptions match.')
print('PASS: complete sentences, no truncation placeholders, 404 remains noindex, and every HTML page is covered by the shared metadata source.')
print('Maximum characters:',max(map(len,titles)),'title /',max(map(len,descriptions)),'description')
