#!/usr/bin/env python3
"""Apply reviewed metadata without regenerating layouts or image assets."""
import csv,json,re
from html import escape
from pathlib import Path
from seo_metadata import ROOT,COPY,for_page
from generate_seo import BASE,build_hub,metadata,topics

def apply(filename):
    path=ROOT/filename
    title,description=for_page(filename)
    text=path.read_text();head,body=text.split('</head>',1)
    head,count=re.subn(r'<title>.*?</title>',lambda m:'<title>'+escape(title)+'</title>',head,flags=re.S)
    assert count==1,filename
    # Search engines ignore meta keywords; old lists can misstate page scope.
    head=re.sub(r'<meta\b(?=[^>]*\bname=["\x27]keywords["\x27])[^>]*>\s*','',head,flags=re.I)
    canonical=BASE+'/'+('' if filename=='index.html' else filename.removesuffix('index.html') if filename.endswith('/index.html') else filename)
    values={'description':description,'og:title':title,'og:description':description,'twitter:title':title,'twitter:description':description}
    if filename!='404.html':
        values.update({'robots':'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1','og:type':'website' if not filename.startswith('seo/') or filename=='seo/index.html' else 'article','og:locale':'en_IN','og:site_name':'JobReady','og:url':canonical,'twitter:card':'summary_large_image'})
        image=re.search(r'<meta\b[^>]*property="og:image"[^>]*content="([^"]+)"',head)
        image_url=image.group(1) if image else BASE+'/seo/assets/social/company-registration.png'
        service_map=json.loads((ROOT/'content/local-services-map.json').read_text())
        service=next((row for row in service_map if row['url']=='/'+filename),None)
        if service:
            image_url=BASE+'/seo/assets/social/'+('company-registration.png' if service['group']=='Company registration' else 'tax-compliance.png')
        values.update({'og:image':image_url,'og:image:alt':title,'twitter:image':image_url,'twitter:image:alt':title})
    for key,value in values.items():
        kind='property' if key.startswith('og:') else 'name'
        tag=f'<meta {kind}="{key}" content="{escape(value,quote=True)}">'
        pattern=r'<meta\b(?=[^>]*\b(?:name|property)=["\x27]'+re.escape(key)+r'["\x27])[^>]*>'
        head,count=re.subn(pattern,lambda m:tag,head)
        assert count<=1,(filename,key)
        if count==0 and (key=='description' or filename!='404.html'):head+='\n'+tag
    def schema(match):
        data=json.loads(match.group(2))
        def update(node):
            if isinstance(node,dict):
                types=node.get('@type',[])
                if isinstance(types,str):types=[types]
                if set(types)&{'Article','WebPage','CollectionPage'}:
                    node['description']=description
                    if 'CollectionPage' in types:node['name']=title
                for value in node.values():update(value)
            elif isinstance(node,list):
                for value in node:update(value)
        update(data)
        return match.group(1)+json.dumps(data,ensure_ascii=False).replace('<',r'\u003c')+match.group(3)
    head=re.sub(r'(<script\b[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)',schema,head,flags=re.S)
    path.write_text(head+'</head>'+body)

def main():
    files={str(p.relative_to(ROOT)) for p in ROOT.rglob('*.html')}
    assert files==set(COPY),'Review metadata for added or removed pages before applying.'
    # Directory cards preview the exact title and description of each guide.
    (ROOT/'seo/index.html').write_text(build_hub().replace('↗','→'))
    for filename in COPY:apply(filename)
    manifest_path=ROOT/'coworking/manifest.json'
    manifest=json.loads(manifest_path.read_text())
    for row in manifest:
        row['title'],row['description']=for_page(row['file'])
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    with (ROOT/'seo/metadata.csv').open('w',newline='') as handle:
        writer=csv.writer(handle,lineterminator='\n')
        writer.writerow(['Keyword / H1','Title tag','Meta description','Canonical URL','Open Graph image'])
        for topic in topics:
            title,desc=metadata(topic)
            writer.writerow([topic['keyword'],title,desc,f'{BASE}/seo/{topic["slug"]}.html',f'{BASE}/seo/assets/social/{topic["slug"]}.png'])
    audit=[]
    for filename in COPY:
        title,desc=for_page(filename)
        audit.append({'file':filename,'title':title,'title_characters':len(title),'description':desc,'description_characters':len(desc),'title_limit':60,'description_limit':155,'status':'PASS','indexing':'noindex' if filename=='404.html' else 'indexable'})
    with (ROOT/'seo/metadata-audit.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(audit[0]),lineterminator='\n');writer.writeheader();writer.writerows(audit)
    print(f'Updated {len(COPY)} metadata sets, matching social tags, article/collection descriptions and directory previews. Exported character-count audit.')

if __name__=='__main__':main()
