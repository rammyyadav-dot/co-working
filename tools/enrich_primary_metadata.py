#!/usr/bin/env python3
"""Maintain primary-page metadata and local social cards alongside the guides."""
import re
from pathlib import Path
from html import escape
from generate_seo import BASE, build_social_image

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
 'index.html': ('Coworking Space in Patna | Desks & Virtual Office | JobReady',
  'Explore coworking desks, private offices, virtual addresses and meeting room options in Patna. Contact JobReady in Raja Bazar for availability and a quote.',
  'Coworking Space in Patna', 'homepage'),
 'jobreadyvirtualoffice.html': ('Virtual Office in Patna | Business Address | JobReady',
  'Explore virtual office options in Patna with JobReady. Discuss business address use, GST documents, mail handling and meeting access before choosing a plan.',
  'Virtual Office in Patna', 'virtual-office'),
 'company_registration.html': ('Company Registration in Patna | Startup Support | JobReady',
  'Discuss company registration in Patna with JobReady. Get guidance on incorporation documents, business address needs and filing support. Request a quote.',
  'Company Registration in Patna', 'company-registration'),
 'business_services.html': ('Business Services in Patna | Startup Support | JobReady',
  'Explore business services in Patna: mail handling, compliance, bookkeeping, payroll, marketing and IT support. Discuss your requirements with JobReady.',
  'Business Services in Patna', 'business-services'),
 'tax_compliance.html': ('GST & Tax Compliance in Patna | JobReady',
  'Discuss GST registration, return filing, bookkeeping, payroll and tax compliance support in Patna. Share your business requirements and request a quote.',
  'GST & Tax Compliance in Patna', 'tax-compliance'),
 'enterprise.html': ('Managed Office Space in Patna | Enterprise | JobReady',
  'Explore managed office options in Patna for growing teams. Discuss seats, equipment, access hours and service scope with JobReady. Request a proposal.',
  'Managed Office Space in Patna', 'enterprise'),
}

def main():
    for filename,(title,desc,label,card) in PAGES.items():
        assert len(title) <= 65 and 120 <= len(desc) <= 165
        file = ROOT/filename
        text=file.read_text()
        head,body=text.split('</head>',1)
        head=re.sub(r'<title>.*?</title>',f'<title>{escape(title)}</title>',head,flags=re.S)
        head=re.sub(r'<meta\b[^>]*(?:name="(?:title|description|twitter:[^"]+)"|property="og:[^"]+")[^>]*>\s*','',head)
        head=re.sub(r'<link\b[^>]*rel="canonical"[^>]*>\s*','',head)
        # Canonical and structured navigation should refer to the same host.
        head=head.replace('https://jobreadybpo.com/',BASE+'/')
        head=head.replace(BASE+'/#enterprise',BASE+'/enterprise.html')
        path='/' if filename=='index.html' else '/'+filename
        canonical=BASE+path
        image=f'{BASE}/seo/assets/social/{card}.png'
        meta={'description':desc,'twitter:card':'summary_large_image','twitter:title':title,'twitter:description':desc,'twitter:image':image,'twitter:image:alt':label+' — JobReady'}
        og={'type':'website','locale':'en_IN','site_name':'JobReady','title':title,'description':desc,'url':canonical,'image':image,'image:secure_url':image,'image:type':'image/png','image:width':'1200','image:height':'630','image:alt':label+' — JobReady'}
        addition='\n<link rel="canonical" href="'+canonical+'">\n'
        addition+=''.join(f'<meta name="{key}" content="{escape(value,quote=True)}">\n' for key,value in meta.items())
        addition+=''.join(f'<meta property="og:{key}" content="{escape(value,quote=True)}">\n' for key,value in og.items())
        build_social_image(label,'JobReady / Patna workspace & business services',card)
        file.write_text(head+addition+'</head>'+body)
    print('Updated six primary-page metadata sets and 1200×630 social cards.')

if __name__ == '__main__': main()
