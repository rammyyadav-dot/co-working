#!/usr/bin/env python3
"""Verify canonical routes, permanent redirects and crawlable local destinations."""
import json
from pathlib import Path
from urllib.parse import urlsplit,unquote
from xml.etree import ElementTree as ET
from check_seo import Page
from migrate_urls import ROOT,BASE,ROUTES,file_for
pages={p:Page(p.read_text()) for p in ROOT.rglob('*.html')}
rules={a:b for a,b,code in (line.split() for line in (ROOT/'_redirects').read_text().splitlines() if line and not line.startswith('#'))}
v=json.loads((ROOT/'vercel.json').read_text())
vercel={x['source']:x['destination'] for x in v['redirects'] if x['statusCode']==301}
for old,new in ROUTES.items():
 assert old!=new and new not in ROUTES,(old,new)
 assert rules[old]==vercel[old]==new,old
 target=ROOT/file_for(new);assert target.is_file(),(old,new)
 assert pages[target].canonical==BASE+new,(old,new)
for path,page in pages.items():
 if path.name!='404.html':
  canonical=urlsplit(page.canonical).path
  assert canonical.endswith('/') and '.html' not in canonical,path
  assert page.meta['og:url']==page.canonical,path
 for link in page.links:
  u=urlsplit(link)
  if u.netloc or u.scheme:continue
  assert u.path not in ROUTES,(path,link)
  target=(ROOT/u.path.lstrip('/')) if u.path.startswith('/') else path.parent/u.path
  if not u.path:target=path
  if target.is_dir():target=target/'index.html'
  assert target.is_file(),(path,link)
  if u.fragment and target in pages:assert unquote(u.fragment) in pages[target].ids,(path,link)
urls=[n.text for n in ET.parse(ROOT/'sitemap.xml').findall('.//{*}loc')]
assert len(urls)==len(set(urls))==len(pages)-1
assert set(urls)=={p.canonical for file,p in pages.items() if file.name!='404.html'}
print(f'PASS: {len(pages)} pages, {len(ROUTES)} direct permanent URL migrations, all internal assets/anchors and {len(urls)} clean sitemap URLs.')
