#!/usr/bin/env python3
"""Build the 100 self-contained coworking landing pages and searchable directory."""
from pathlib import Path
from html import escape
import json, re, csv
from xml.etree import ElementTree as ET
from site_components import header
from seo_metadata import for_page

ROOT=Path(__file__).resolve().parents[1]
BASE='https://coworking.jobreadybpo.com'
DATA=json.loads((ROOT/'content/coworking-pages.json').read_text())
CATEGORIES=[('offices','Offices & coworking','Find a practical base for your business.'),('desks','Desks & day passes','A desk for the days you need one.'),('virtual-office','Virtual office','Address services with a defined scope.'),('meeting-rooms','Meeting rooms','Bring the right people together.'),('budget','Budget options','Compare the full cost of your workday.'),('locations','Local commutes','Choose with the actual journey in mind.'),('teams','Private & team space','Room for your people and how they work.')]
def esc(s):return escape(str(s),quote=True)
def category(i):return CATEGORIES[0 if i<=15 else 1 if i<=30 else 2 if i<=45 else 3 if i<=60 else 4 if i<=75 else 5 if i<=90 else 6]
def term(s):
    s=s[0].upper()+s[1:]
    for a,b in [('patna','Patna'),('gst','GST'),('apob','APOB'),('APOB','APOB'),('bihar','Bihar'),('bailey road','Bailey Road'),('boring road','Boring Road'),('kankarbagh','Kankarbagh'),('fraser road','Fraser Road'),('patliputra','Patliputra'),('sk puri','SK Puri'),('gandhi maidan','Gandhi Maidan'),('danapur','Danapur'),('patna junction','Patna Junction'),('Patna junction','Patna Junction'),('dakbunglow chauraha','Dakbunglow Chauraha'),('rajendra nagar','Rajendra Nagar'),('ashiana digha road','Ashiana Digha Road'),('wifi','Wi-Fi')]:s=re.sub(re.escape(a),b,s,flags=re.I)
    return s
def rate(d):
    p=d['starting_price']
    return ('From '+p, 'Confirm current availability and full payable charges.') if p in ('₹999/month','₹1,999/month','₹4,999/month') else ('Let’s find your fit', 'Request a quote for your dates and requirements.')
def plans(d):
    i=int(d['number'])
    if 31<=i<=45 or i in (72,88):return [('Address starter','From ₹999/month','Business-address and mail-notification scope; permitted uses to be confirmed.'),('GST-oriented service','From ₹1,999/month','Documentation support subject to your activity and adviser review.'),('Daily visits / workspace','Request a quote','Book physical workspace separately; address membership does not imply desk access.')]
    if 46<=i<=60 or i==89:return [('Hourly meeting','Request a quote','Confirm duration, guest count, layout and required equipment.'),('Full-day booking','Request a quote','Include setup time, breaks and any overtime in the brief.'),('Monthly recurring sessions','Tailored proposal','Agree the number of sessions, timings and cancellation terms.')]
    if i in (6,71,91,92,93,94,95,100):return [('Daily team-space request','Check availability','Tell us dates, headcount and whether enclosure is essential.'),('Monthly office arrangement','Tailored proposal','Confirm the actual space, services and minimum tenure.'),('Additional seats / services','Separately quoted','Discuss growth and guest needs before signing.')]
    return [('Daily desk','Request a quote','Confirm the access window, seat availability and included services.'),('Monthly desk','From ₹4,999/month','Site-listed reference; confirm seat type, attendance and billing terms.'),('Meeting / address add-ons','Separately quoted','Included only when expressly confirmed in the plan.')]

def office_art(kind='offices'):
    # Original editorial illustration, not a photograph or floor plan of the premises.
    color={'virtual-office':'#56745b','meeting-rooms':'#c17c4a','teams':'#536886','desks':'#537a7c'}.get(kind,'#56745b')
    return f'''<svg viewBox="0 0 560 435" role="img" aria-label="Illustration of a light-filled workspace with desks and plants">
<defs><linearGradient id="floor" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fbfbf1"/><stop offset="1" stop-color="#cbd8ca"/></linearGradient><pattern id="glass" width="56" height="72" patternUnits="userSpaceOnUse"><rect width="56" height="72" fill="#eaf1e8"/><path d="M0 0H56V72" fill="none" stroke="#b4c6b5" stroke-width="2"/></pattern></defs>
<ellipse cx="285" cy="380" rx="228" ry="23" fill="#bbcbbc" opacity=".45"/>
<path d="M63 187 278 63 500 192 282 321Z" fill="url(#floor)"/>
<path d="M63 187V91L278 0V63Z" fill="#f9f9ef"/>
<path d="M278 0 500 128V192L278 63Z" fill="#d6e2d3"/>
<path d="M298 26 476 129V174L298 72Z" fill="url(#glass)" stroke="#a9bda8" stroke-width="3"/>
<path d="M357 61V106M416 96V140" stroke="#9aaf98" stroke-width="3"/>
<path d="m94 110 125-53v54l-125 69Z" fill="#dde7d8"/><path d="m110 117 91-41v28l-91 50Z" fill="#becfb9"/>
<path d="m63 187 219 134 218-129v20L282 343 63 207Z" fill="#b8cbb6"/>
<path d="m145 175 107-61 130 75-106 63Z" fill="#d59c6d"/>
<path d="M145 175v13l131 77v-13Z" fill="#b87e52"/><path d="m276 252 106-63v13l-106 63Z" fill="#c58e60"/>
<path d="M159 195v63m105 5v63m102-111v53" stroke="#607363" stroke-width="6"/>
<path d="m205 148 47-27 39 23-47 27Z" fill="#eeeade"/>
<path d="m244 171 47-27v-38l-47 27Z" fill="#203b46"/><path d="m249 163 36-21v-27l-36 21Z" fill="#617f7f"/><path d="m244 171-39-23v-4l39 23Z" fill="#d0c9b9"/>
<path d="m294 197 33-19 27 16-33 19Z" fill="#f5e9d3"/>
<path d="m309 186 21-12v-23l-21 12Z" fill="#193c5d"/><path d="m312 180 15-9v-14l-15 9Z" fill="#859da3"/>
<path d="m202 221-30 17v38l32 18 31-18v-38Z" fill="{color}"/>
<path d="m172 238 32 19 31-19-31-18Z" fill="#8ca18b"/><path d="M204 294v28m0-10-25 14m25-14 23 14" stroke="#586b59" stroke-width="4"/>
<path d="m339 260-30 17v38l32 18 31-18v-38Z" fill="{color}"/>
<path d="m309 277 32 19 31-19-31-18Z" fill="#8ca18b"/><path d="M341 333v29m0-11-25 14m25-14 23 14" stroke="#586b59" stroke-width="4"/>
<path d="m95 187 24-14 25 14-24 14Z" fill="#d29a72"/><path d="m95 187 5 33 20 12 19-12 5-33-24 14Z" fill="#c58b61"/>
<path d="M120 190v-57m0 27q-33-12-29-31 28-1 29 31m0 14q26-16 27-36-28 2-27 36m0-25q18-19 13-36-19 6-13 36" fill="#4e7657" stroke="#4e7657" stroke-width="3"/>
<path d="m439 216 21-12 21 12-21 12Z" fill="#dbb68c"/><path d="m439 216 5 28 16 9 16-9 5-28-21 12Z" fill="#cda275"/>
<path d="M460 215v-62m0 36q-26-9-24-28 25 0 24 28m0 12q25-12 25-32-24 4-25 32m0-28q13-15 9-29-15 7-9 29" fill="#56785a" stroke="#56785a" stroke-width="3"/>
<path d="m115 331 32-19 47 27-33 19Z" fill="#ede6d7"/><path d="m118 331 43 25v8l-43-25Z" fill="#c7baa4"/>
<path d="M120 333v32m40-9v32m30-48v28" stroke="#83927c" stroke-width="3"/>
<circle cx="265" cy="199" r="6" fill="#eee1b9"/><path d="M265 199v-13" stroke="#d4ba84" stroke-width="3"/>
</svg>'''

def visual(d=None):
    price,note=rate(d) if d else ('Work, on your terms.','Desks, business addresses & team spaces')
    kind=category(int(d['number']))[0] if d else 'offices'
    return f'<div class="cw-art"><div class="cw-art-head"><span>A little room for your next idea</span><span><i></i> Patna, Bihar</span></div>{office_art(kind)}<span class="cw-visual-note">Workspace illustration</span><div class="cw-art-foot"><div><strong>{esc(price)}</strong><small>{esc(note)}</small></div><a href="#enquire" aria-label="Discuss your workspace">↗</a></div></div>'

def head(title,desc,path,schemas=()):
    title,desc=for_page(path)
    canonical=BASE+path
    return f'''<!doctype html><html lang="en-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="theme-color" content="#15263b"><link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{canonical}"><meta property="og:locale" content="en_IN"><meta property="og:site_name" content="JobReady"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/coworking.css"><script defer src="/assets/site.js"></script><script defer src="/assets/coworking.js"></script>'''+''.join('<script type="application/ld+json">'+json.dumps(s,ensure_ascii=False).replace('<','\\u003c')+'</script>' for s in schemas)+'</head><body class="cw-page">'+header(path)

def footer():return '''<footer class="cw-footer"><div class="cw-wrap cw-footer-inner"><div><a class="site-brand" href="/index.html">JOBREADY<span>.</span></a><p>A working base for what comes next.<br>Ashiana More, Raja Bazar, Indrapuri, Patna, Bihar 800014.</p></div><div class="cw-footer-links"><a href="/coworking/">Explore coworking</a><a href="tel:+919172712982">Call the team ↗</a><a href="mailto:hello@jobreadybpo.com">Email us ↗</a></div></div></footer>'''

def form(d=None):
    title=d['copy'][3] if d else 'Let’s find your next working base.'
    close=d['copy'][13] if d else 'Tell us how you work, and we’ll help you compare the options. Start with a conversation about your dates, team and budget.'
    service=d['primary_keyword'] if d else 'coworking workspace in Patna'
    return f'''<section class="cw-enquiry" id="enquire" aria-labelledby="enquiry-title"><div><span class="cw-label">A clearer next step</span><h2 id="enquiry-title">{esc(title)}</h2><p>{esc(close)}</p><a class="cw-contact" href="tel:+919172712982">Talk to the team · +91 9172712982 ↗</a></div><form class="cw-form" data-enquiry="{esc(service)}" action="mailto:hello@jobreadybpo.com" method="post" enctype="text/plain"><label for="lead-name">Your name</label><input id="lead-name" name="Name" autocomplete="name" required maxlength="100" placeholder="Full name"><label for="lead-phone">Phone / WhatsApp</label><input id="lead-phone" name="Phone" type="tel" inputmode="tel" autocomplete="tel" required pattern="[+0-9 ()\\-]{{7,20}}" title="Enter a phone number using 7–20 digits, spaces, +, - or parentheses." placeholder="+91 98765 43210"><label for="lead-size">Team size</label><select id="lead-size" name="Team size" required><option value="">Choose your team size</option><option>Just me</option><option>2–4 people</option><option>5–10 people</option><option>11–20 people</option><option>More than 20 people</option><option>No physical seats — address only</option></select><label class="cw-consent"><input type="checkbox" name="Contact permission" value="Agreed" required><span>I agree to be contacted about this enquiry by phone or WhatsApp.</span></label><button class="cw-btn" type="submit">Continue on WhatsApp <span aria-hidden="true">↗</span></button><p class="cw-form-help">Review your message in WhatsApp and send it to start the conversation. This does not reserve space or take payment.</p><details><summary>How your enquiry is handled</summary><p>This page does not save your details. Continuing passes them to WhatsApp as a draft message. The team receives them when you send the message.</p></details><noscript><p class="cw-form-help">With JavaScript off, this form opens your email app. You can also call the team.</p></noscript></form></section>'''

def mobile():return '<div class="cw-mobile-cta"><span><strong>Your next workspace</strong>Raja Bazar, Patna</span><a href="#enquire" class="cw-btn">Enquire now ↗</a></div>'
def schema_breadcrumb(path,title):return {'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE+'/'},{'@type':'ListItem','position':2,'name':'Coworking','item':BASE+'/coworking/'},{'@type':'ListItem','position':3,'name':title,'item':BASE+path}]}

manifest=[]
for d in DATA:
    i=int(d['number']);row=d['copy'];_,hub,audience,benefit,hero,b1,b2,b3,gst,parking,wifi,terms,cta,closing=row
    if i==68:
        hero='Working within ₹500 for the day? Ask for the current desk rate at Raja Bazar and check the final payable amount against the hours you need.'
    cat,label,catdesc=category(i);path=d['proposed_path'];title,desc=for_page(path);keyword=term(d['primary_keyword']);price,_=rate(d)
    # Keep questions human-readable while preserving the authored, page-specific answers.
    questions=['Can this arrangement support my GST address needs?','What should I know about parking?','How can I check Wi-Fi speed and internet access?','What if my plans or team size change?']
    answers=[gst,parking,wifi,terms]
    # Remove author-facing references; the visitor gets a direct practical instruction.
    answers=[a.replace('No reserved bay has been verified for these drafts; confirm','Please confirm').replace('none is verified in the supplied material','confirm actual performance directly').replace('no tested speed has been supplied for these drafts','ask the team for current test results') for a in answers]
    faq={'@context':'https://schema.org','@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in zip(questions,answers)]}
    schemas=[schema_breadcrumb(path,keyword),faq,{'@context':'https://schema.org','@type':'Service','name':keyword,'serviceType':label,'areaServed':{'@type':'City','name':'Patna'},'provider':{'@type':'Organization','name':'JobReady','url':BASE},'url':BASE+path}]
    islocal=76<=i<=90
    h1=(f'Comparing {esc(d["primary_keyword"])}?' if islocal and i!=76 else esc(keyword)+'.')
    features=''.join(f'<article class="cw-feature"><span class="cw-number">0{j}</span><h3>{h}</h3><p>{esc(b)}</p></article>' for j,(h,b) in enumerate(zip(['A location that works','A plan around your day','Clarity before commitment'],[b1,b2,b3]),1))
    table=''.join('<tr>'+''.join(f'<td>{esc(c)}</td>' for c in p)+'</tr>' for p in plans(d))
    faqhtml=''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q,a in zip(questions,answers))
    locality=hub.split(' / ')[0]
    localcopy=f'Coming from {locality}? Compare the complete journey to Raja Bazar at the hours you expect to travel. The neighbourhood you search for may differ from the centre’s actual location.' if locality not in ('Raja Bazar','Bailey Road','Bailey Road / Ashiana More') else 'Use Ashiana More as your approach landmark, then confirm the exact building entrance before your first visit. Plan around your normal working hours.'
    related=[x for x in DATA if x['number']!=d['number'] and category(int(x['number']))[0]==cat][:3]
    relatedhtml=''.join(f'<a href="{x["proposed_path"]}">{esc(term(x["primary_keyword"]))}<span>Explore this option ↗</span></a>' for x in related)
    audiencecopy=audience[0].lower()+audience[1:]
    text=head(title,desc,path,schemas)+f'''<main id="main"><div class="cw-wrap"><nav class="cw-breadcrumb" aria-label="Breadcrumb"><a href="/index.html">Home</a><span aria-hidden="true">/</span><a href="/coworking/">Coworking</a><span aria-hidden="true">/</span><a href="/coworking/#{cat}">{esc(label)}</a></nav>
<section class="cw-hero"><div><span class="cw-label">{esc(label)} · Patna, Bihar</span><h1>{h1}<span class="cw-benefit">{esc(benefit)}</span></h1><p class="cw-intro">{esc(hero)}</p><div class="cw-actions"><a class="cw-btn" href="#enquire">{esc(cta)} <span aria-hidden="true">↗</span></a><a class="cw-btn cw-btn-light" href="#plans">Compare plans ↓</a></div><p class="cw-under-cta">Made for {esc(audiencecopy)}.</p></div>{visual(d)}</section>
<div class="cw-trust" aria-label="At a glance"><span><b aria-hidden="true">✓</b> Actual Raja Bazar location</span><span><b aria-hidden="true">✓</b> Clear scope before you commit</span><span><b aria-hidden="true">✓</b> Direct conversation with the team</span></div>
<section class="cw-section" id="why"><div class="cw-section-head"><div><span class="cw-label">Designed around your work</span><h2>Why choose our workspace in Patna?</h2></div><p>The right fit starts with your routine. Compare the location, access and services against what an ordinary working day needs.</p></div><div class="cw-feature-grid">{features}</div></section>
<section class="cw-section" id="plans"><div class="cw-section-head"><div><span class="cw-label">Your space. Your pace.</span><h2>Plans with a clearer picture.</h2></div><p>Compare the commitment as well as the price. Ask for a written quote covering access, inclusions and the full payable amount.</p></div><div class="cw-table" role="region" aria-label="Workspace plans and pricing comparison" tabindex="0"><table><thead><tr><th scope="col">Workspace plan</th><th scope="col">Price / basis</th><th scope="col">What to confirm</th></tr></thead><tbody>{table}</tbody></table></div><p class="cw-price-note">Listed starting prices are references from the existing website, not a booking confirmation. Confirm current rates, applicable taxes, deposits, minimum tenure and optional services with the team.</p></section>
<section class="cw-section" id="location"><div class="cw-location"><div><span class="cw-label">Rooted in Patna</span><h2>A real address.<br>A journey worth checking.</h2><address class="cw-address">Ashiana More, Raja Bazar, Indrapuri<br>Patna, Bihar 800014</address><p>{esc(localcopy)}</p><div class="cw-location-notes"><p><strong>Arriving by rail?</strong> Allow for the onward journey from Patna Junction. Ask for the exact map pin before travelling.</p><p><strong>Banking or a coffee break?</strong> Ask the team for current nearby bank and café recommendations around the actual centre.</p></div></div><div class="cw-place-card"><span class="cw-label">Your Patna working base</span><div class="cw-place-mark">Ashiana More.<br>Raja Bazar.<span>PATNA / BIHAR / 800014</span></div><a href="https://www.google.com/maps/search/?api=1&amp;query=Ashiana+More+Raja+Bazar+Indrapuri+Patna+800014" target="_blank" rel="noopener noreferrer">Explore the area on Maps ↗</a></div></div></section>
<section class="cw-section cw-faq-layout" id="faqs"><div><span class="cw-label">Good questions first</span><h2>A little clarity<br>goes a long way.</h2><p>Permissions, parking, connection quality and flexibility: check the details that shape your working day.</p></div><div class="cw-faq">{faqhtml}</div></section>
{form(d)}<section class="cw-related"><span class="cw-label">Keep exploring</span><h2>Another way to make it work.</h2><div class="cw-related-grid">{relatedhtml}</div></section></div></main>{footer()}{mobile()}</body></html>'''
    out=ROOT/path.lstrip('/')/'index.html';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text)
    manifest.append({'number':i,'keyword':d['primary_keyword'],'category':cat,'path':path,'file':str(out.relative_to(ROOT)),'title':title,'description':desc,'price_display':price})

cards=[]
for d in DATA:
    i=int(d['number']);cat,label,desc=category(i);price,_=rate(d)
    cards.append(f'<a class="cw-card" href="{d["proposed_path"]}" data-workspace data-category="{cat}" data-search="{esc(d["primary_keyword"]+" "+d["target_hub"]+" "+d["audience"])}"><div class="cw-card-top"><span class="cw-tag">{esc(label)}</span><small>{i:03d}</small></div><h3>{esc(term(d["primary_keyword"]))}</h3><p>{esc(d["copy"][3])}. {esc(d["target_hub"])}.</p><div class="cw-card-bottom"><span>{esc(price if price.startswith('From') else 'Discuss your requirements')}</span><span aria-hidden="true">↗</span></div></a>')
filters='<button type="button" class="cw-filter" data-category-filter="all" aria-pressed="true">All options <span>100</span></button>'+''.join(f'<button type="button" class="cw-filter" id="{key}" data-category-filter="{key}" aria-pressed="false">{esc(label)} <span>{sum(category(int(d["number"]))[0]==key for d in DATA)}</span></button>' for key,label,_ in CATEGORIES)
directory=head('Coworking in Patna | Find Your Workspace | JobReady','Explore 100 Patna workspace options: desks, virtual offices, meeting rooms and team space. Compare your needs and enquire with JobReady.','/coworking/')+f'''<main id="main"><div class="cw-wrap"><nav class="cw-breadcrumb" aria-label="Breadcrumb"><a href="/index.html">Home</a><span aria-hidden="true">/</span><span aria-current="page">Coworking</span></nav><section class="cw-hero cw-hub-hero"><div><span class="cw-label">A working base. A fresh perspective.</span><h1>Good work<br>starts with<br><em>the right space.</em></h1><p class="cw-intro">A focused desk. A place to meet. An address for your next chapter. Explore coworking in Patna around the way you actually work.</p><div class="cw-actions"><a class="cw-btn" href="#browse">Find your workspace <span aria-hidden="true">↓</span></a><a class="cw-btn cw-btn-light" href="#enquire">Talk to the team ↗</a></div><span class="cw-hub-count">100 focused options <span aria-hidden="true">/</span> 7 ways to find your fit</span></div>{visual()}</section><div class="cw-trust"><span><b aria-hidden="true">✓</b> Rooted in Raja Bazar, Patna</span><span><b aria-hidden="true">✓</b> Options for every working rhythm</span><span><b aria-hidden="true">✓</b> Enquire directly with JobReady</span></div><section class="cw-browser" id="browse" aria-labelledby="browse-title"><div class="cw-browser-head"><div><span class="cw-label">Room for what’s next</span><h2 id="browse-title">Find your kind of workspace.</h2></div><div class="cw-search"><span aria-hidden="true">⌕</span><label for="workspace-search">Search by service, locality or work style</label><input id="workspace-search" type="search" placeholder="Try “Boring Road” or “day pass”" autocomplete="off"></div></div><div class="cw-filters" aria-label="Filter by workspace category">{filters}</div><p class="cw-results-count" id="results-count" role="status" aria-live="polite">100 options to explore</p><div class="cw-grid">{''.join(cards)}</div><div class="cw-empty" id="workspace-empty" hidden><h3>No matching options just yet.</h3><p>Try a different service, a shorter search, or browse all options.</p><button class="cw-btn cw-btn-light" id="workspace-reset" type="button">Reset filters</button></div><div class="cw-more"><button class="cw-btn cw-btn-light" type="button" id="workspace-more" hidden>Show more options ↓</button></div><div class="cw-hub-note"><strong>One actual location. A choice built around you.</strong><p>JobReady’s stated centre is at Ashiana More, Raja Bazar. Locality pages help compare the commute; they do not establish branches in those neighbourhoods. Confirm availability, pricing and services with the team.</p></div><noscript><p>All 100 pages are listed above. Search and filters require JavaScript; every workspace link works without it.</p></noscript></section>{form()}</div></main>{footer()}{mobile()}</body></html>'''
(ROOT/'coworking/index.html').write_text(directory)
(ROOT/'coworking/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))

# Refresh all existing headers from the shared component, preserving page identity.
for p in list(ROOT.glob('*.html'))+list((ROOT/'seo').glob('*.html')):
    text=p.read_text()
    current='/'+str(p.relative_to(ROOT))
    if p==ROOT/'seo/index.html':current='/seo/'
    pat=r'<a class="site-skip"[^>]*>.*?</a>\s*<header class="site-header">.*?</header>'
    text,count=re.subn(pat,lambda m:header(current),text,count=1,flags=re.S)
    if count:p.write_text(text)

# Preserve existing sitemap entries and add the crawlable collection.
ns='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',ns)
sitemap=ROOT/'sitemap.xml';tree=ET.parse(sitemap);xml=tree.getroot()
present={e.text for e in xml.findall(f'{{{ns}}}url/{{{ns}}}loc')}
for path in ['/coworking/']+[d['proposed_path'] for d in DATA]:
    url=BASE+path
    if url not in present:ET.SubElement(ET.SubElement(xml,f'{{{ns}}}url'),f'{{{ns}}}loc').text=url
ET.indent(tree,space='  ');tree.write(sitemap,encoding='utf-8',xml_declaration=True)
print(f'Generated {len(DATA)} HTML landing pages, directory, metadata manifest; refreshed shared headers and sitemap.')
