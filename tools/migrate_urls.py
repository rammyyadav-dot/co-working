#!/usr/bin/env python3
"""Idempotent URL migration. Run after older content generators, before deploy."""
import json,re,posixpath,csv
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit
from html import unescape,escape
ROOT=Path(__file__).resolve().parents[1]
BASE='https://coworking.jobreadybpo.com'
ROUTES=json.loads((ROOT/'content/url-migrations.json').read_text())
def destination(url):
    return ROUTES.get(url,url)
def file_for(url):
    return url.lstrip('/')+('index.html' if url.endswith('/') else '')
def clean_url(value,source='/'):
    value=unescape(value);u=urlsplit(value)
    if u.scheme and u.scheme not in ('http','https'):return value
    if u.netloc and u.netloc!=urlsplit(BASE).netloc:return value
    if not u.path:return value
    path=posixpath.normpath(u.path if u.path.startswith('/') else posixpath.join(posixpath.dirname(source),u.path))
    if u.path.endswith('/') and not path.endswith('/'):path+='/'
    path=ROUTES.get(path,path)
    # Explicit index paths point to their canonical directory.
    if path.endswith('/index.html'):path=path[:-10]
    if path=='/seo':path='/guides/'
    return urlunsplit((u.scheme,u.netloc,path,u.query,u.fragment))
def normalize(text,source):
    # Handle URLs in schema and generator data before normalising relative attributes.
    for old,new in sorted(ROUTES.items(),key=lambda x:-len(x[0])):
        text=re.sub(re.escape(BASE+old)+r'(?=[?#"\x27\s<]|$)',lambda m:BASE+new,text)
    pattern=r'\b(href|src|action)=("|\x27)(.*?)\2'
    return re.sub(pattern,lambda m:m[1]+'='+m[2]+escape(clean_url(m[3],source),quote=True)+m[2],text,flags=re.S)
def main():
    old_sources={}
    for old,new in ROUTES.items():
        if not old.endswith('.html') or old=='/index.html':continue
        src=ROOT/old.lstrip('/');target=ROOT/file_for(new)
        if src.exists():
            text=normalize(src.read_text(),old)
            target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
            src.unlink();old_sources[target]=old
    for p in ROOT.rglob('*.html'):
        source=old_sources.get(p,'/'+str(p.relative_to(ROOT)))
        p.write_text(normalize(p.read_text(),source))
    # Re-key the metadata source and public page manifests.
    p=ROOT/'content/seo-metadata.json';data=json.loads(p.read_text())
    data={file_for(destination('/'+k)):v for k,v in data.items()}
    p.write_text(json.dumps(dict(sorted(data.items())),ensure_ascii=False,indent=2)+'\n')
    p=ROOT/'content/local-services-map.json';data=json.loads(p.read_text())
    for row in data:row['url']=destination(row['url'])
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    # Sitemap contains only the canonical URLs, and never redirect sources.
    from xml.etree import ElementTree as ET
    ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9')
    p=ROOT/'sitemap.xml'
    root=ET.Element('{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')
    tree=ET.ElementTree(root)
    for page in sorted(ROOT.rglob('*.html')):
        if page.name=='404.html':continue
        key='/'+str(page.relative_to(ROOT))
        url=clean_url(BASE+key)
        ET.SubElement(ET.SubElement(root,'{http://www.sitemaps.org/schemas/sitemap/0.9}url'),'{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text=url
    urls=[n.text for n in tree.findall('.//{*}loc')];assert len(urls)==len(set(urls))
    ET.indent(tree);tree.write(p,encoding='utf-8',xml_declaration=True)
    # Human/AI discovery documents and exported URL columns.
    for p in [ROOT/'llms.txt',ROOT/'humans.txt',ROOT/'seo/metadata.csv',ROOT/'seo/metadata-audit.csv']:
        if p.exists():
            text=p.read_text()
            for old,new in sorted(ROUTES.items(),key=lambda x:-len(x[0])):
                text=re.sub(re.escape(BASE+old)+r'(?=[?#"\x27\s<,]|$)',lambda m:BASE+new,text)
            p.write_text(text)
    # Explicit rules work for static Cloudflare Pages/Netlify and Apache hosts.
    rules=dict(ROUTES)
    for old,new in list(ROUTES.items()):
        if old.endswith('.html') and old!='/index.html':rules[old[:-5]]=new
    (ROOT/'_redirects').write_text('# Permanent URL migrations; no wildcard asset redirects.\n'+''.join(f'{a} {b} 301\n' for a,b in rules.items()))
    redirects=[{'source':a,'destination':b,'statusCode':301} for a,b in rules.items()]
    for new in sorted(set(ROUTES.values())):
        if new!='/':redirects.append({'source':new+'index.html','destination':new,'statusCode':301})
    (ROOT/'vercel.json').write_text(json.dumps({'trailingSlash':True,'redirects':redirects},indent=2)+'\n')
    apache=['# Permanent legacy URLs. Requires Apache mod_rewrite and AllowOverride.','RewriteEngine On']
    for old,new in rules.items():
        apache+=['RewriteCond %{THE_REQUEST} "\\s/+'+re.escape(old.lstrip('/'))+'(?:[?\\s])" [NC]','RewriteRule ^'+re.escape(old.lstrip('/'))+'$ '+new+' [R=301,L,NE]']
    (ROOT/'.htaccess').write_text('\n'.join(apache)+'\n')
    with (ROOT/'content/url-migration-report.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Old URL','Canonical URL','Redirect status']);w.writerows((BASE+a,BASE+b,301) for a,b in ROUTES.items())
    print(f'Clean URLs applied: {len(ROUTES)} legacy paths; permanent redirects and sitemap updated.')
if __name__=='__main__':main()
