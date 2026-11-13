#!/usr/bin/env python3
"""Maintain primary-page metadata and local social cards alongside the guides."""
import re
from pathlib import Path
from html import escape
from generate_seo import BASE, build_social_image
from seo_metadata import for_page

ROOT = Path(__file__).resolve().parents[1]
PAGES = {'index.html': ('Coworking Space in Patna', 'homepage'),
 'jobreadyvirtualoffice.html': ('Virtual Office in Patna', 'virtual-office'),
 'company_registration.html': ('Company Registration in Patna', 'company-registration'),
 'business_services.html': ('Business Services in Patna', 'business-services'),
 'tax_compliance.html': ('GST & Tax Compliance in Patna', 'tax-compliance'),
 'enterprise.html': ('Managed Office Space in Patna', 'enterprise')}

def main():
    for filename,(label,card) in PAGES.items():
        title,desc=for_page(filename)
        file = ROOT/filename
        text=file.read_text()
        head,body=text.split('</head>',1)
        head=re.sub(r'<title>.*?</title>',f'<title>{escape(title)}</title>',head,flags=re.S)
        head=re.sub(r'<meta\b[^>]*(?:name="(?:title|description|twitter:[^"]+)"|property="og:[^"]+")[^>]*>\s*','',head)
        head=re.sub(r'<meta\b[^>]*name="robots"[^>]*>\s*', '', head)
        head=re.sub(r'<link\b[^>]*rel="canonical"[^>]*>\s*','',head)
        # Canonical and structured navigation should refer to the same host.
        head=head.replace('https://jobreadybpo.com/',BASE+'/')
        head=head.replace(BASE+'/#enterprise',BASE+'/enterprise.html')
        path='/' if filename=='index.html' else '/'+filename
        canonical=BASE+path
        image=f'{BASE}/seo/assets/social/{card}.png'
        meta={'robots':'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1','description':desc,'twitter:card':'summary_large_image','twitter:title':title,'twitter:description':desc,'twitter:image':image,'twitter:image:alt':label+' — JobReady'}
        og={'type':'website','locale':'en_IN','site_name':'JobReady','title':title,'description':desc,'url':canonical,'image':image,'image:secure_url':image,'image:type':'image/png','image:width':'1200','image:height':'630','image:alt':label+' — JobReady'}
        addition='\n<link rel="canonical" href="'+canonical+'">\n'
        addition+=''.join(f'<meta name="{key}" content="{escape(value,quote=True)}">\n' for key,value in meta.items())
        addition+=''.join(f'<meta property="og:{key}" content="{escape(value,quote=True)}">\n' for key,value in og.items())
        build_social_image(label,'JobReady / Patna workspace & business services',card)
        file.write_text(head+addition+'</head>'+body)
    print('Updated six primary-page metadata sets and 1200×630 social cards.')

if __name__ == '__main__': main()
