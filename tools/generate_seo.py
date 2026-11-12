#!/usr/bin/env python3
"""Generate the static, crawlable workspace guide collection. No dependencies."""
import html
import csv
import json
import re
from pathlib import Path
from urllib.parse import quote
from xml.etree.ElementTree import Element, SubElement, tostring, indent
from site_components import header

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://coworking.jobreadybpo.com'
CATEGORIES = ['Patna workspace guides', 'Booking & costs', 'Provider comparisons', 'Work styles & teams', 'Facilities & flexible plans']

# Each family supplies practical editorial context; every topic also has its own
# decision angle and action, maintained in seo-topics.txt.
FAMILIES = {
 'desk': ('Choose a desk that fits your working week',
  'Start with the work you need to complete: focused individual tasks, frequent calls, or collaboration with colleagues. A hot desk usually means choosing an available seat, while a dedicated desk is assigned to you. Neither automatically includes an enclosed room. A private cabin is a separate option when conversations or equipment need a more controlled environment.',
  'Build a realistic attendance pattern before comparing plans. Someone visiting twice a week may value flexible access more than a fixed seat; a daily user may value a consistent setup and storage. Ask how meeting-room time, visitors, printing and late access are handled. The right desk plan should make an ordinary working day easier, with rules you can understand before the first visit.',
  ['Seat assignment and peak-time availability', 'Included working hours and attendance limits', 'Call etiquette, storage and meeting access', 'Upgrade, cancellation and renewal conditions']),
 'virtual': ('Separate an address service from physical workspace',
  'A virtual office is an address-related service rather than a permanent workstation. Depending on the agreement, it may support business correspondence, particular registration uses or mail handling. Those uses must be confirmed individually. Renting an address does not by itself establish that a registration authority will accept it or that a desk is available whenever you visit.',
  'Before comparing packages, write down where you intend to display the address and which documents you need. Website correspondence, invoicing, company registration and GST filings can involve different requirements. Ask who is authorised to provide the address, how official letters reach you and what happens when the agreement ends. Obtain professional advice for statutory filings rather than relying on a marketing description.',
  ['Permitted uses and exact premises address', 'Identity checks, agreement and supporting documents', 'Mail receipt, notification and collection rules', 'Activation, renewal and exit procedures']),
 'compliance': ('Build the document trail before you apply',
  'An address arrangement must be suitable for the actual legal entity, business activity and application. Requirements may differ between company incorporation, GST registration and other filings. Discuss the proposed use with a chartered accountant, company secretary or other qualified adviser. A provider can explain its available documents, but cannot guarantee approval or replace an authority’s assessment.',
  'Check that the name, premises address and authorisation are consistent across the agreement, consent or NOC and supporting records. Ask how the provider handles official correspondence, physical verification requests and document updates. Do not file using an address merely because a package is advertised as registration-ready. Keep a current copy of the agreement and understand renewal obligations throughout the period the address remains on official records.',
  ['Entity name, activity and intended registration use', 'Agreement, authorisation and premises evidence', 'Adviser review and verification access', 'Renewals, notices and address-change obligations']),
 'local': ('Check the real journey, not just the neighbourhood name',
  'Location searches are a starting point for a commute decision. JobReady’s stated premises are at Ashiana More, Raja Bazar, Indrapuri, Patna. This guide does not establish branches in other neighbourhoods or promise a particular travel time. Use the actual map pin and compare it with options physically located in your preferred area before arranging a visit.',
  'Check the route at the hours you will travel, including the final stretch from parking, public transport or a drop-off point. If clients or colleagues will join you, consider their journey as well. Ask about opening hours before travelling and confirm that the required seat or room is available. A slightly longer route may or may not be worthwhile; judge it against a real trial of the working environment.',
  ['Actual premises address and map pin', 'Peak-hour journey and last-mile access', 'Hours that fit your commute and visitor schedule', 'A confirmed tour or desk before travelling']),
 'booking': ('Turn a workspace enquiry into a clear reservation',
  'Start with the dates, number of people and working hours you need. Explain whether you need an open desk, an enclosed office or a meeting room, and mention any client visits or equipment requirements. That information lets an operator check the right inventory instead of sending a generic package. JobReady’s enquiry links open WhatsApp or email; they do not take payment or automatically reserve space.',
  'Request a written quote that names the workspace type, dates, inclusions, taxes and cancellation conditions. Check availability again before paying, particularly for group visits or a specific room. A confirmed booking should explain arrival instructions, accepted identification, access hours and whom to contact if plans change. Keep a copy of the confirmation and use only payment details you have verified with the business.',
  ['Dates, duration, seat count and workspace type', 'Written availability and itemised quotation', 'Cancellation, rescheduling and overtime rules', 'Confirmation, arrival details and contact person']),
 'meeting': ('Plan the meeting before choosing the room',
  'Match the room to the purpose: an interview, a client presentation, a workshop and a hybrid team call place different demands on layout and equipment. Ask for the practical seated capacity and explain whether people need laptops, writing space or a clear view of a screen. Nominal capacity alone does not tell you whether a room will be comfortable for the whole session.',
  'List the equipment you depend on and confirm it is included or separately quoted. Screen connections, audio pickup, internet access, whiteboards and refreshments should not be assumed. Ask about setup time, visitor arrival, accessibility and extension charges. For a time-sensitive meeting, arrange a technical check and identify a fallback if a screen or call connection does not work as expected.',
  ['Attendee count, layout and meeting purpose', 'Display, audio and hybrid-call requirements', 'Setup time, guest access and refreshments', 'Cancellation, overtime and support contact']),
 'private': ('Make privacy and capacity measurable',
  'An enclosed office should be assessed in person against the work it needs to support. Check desk spacing, circulation, daylight, ventilation and the way sound travels to neighbouring areas. A room described as private may provide visual separation without strong acoustic isolation. Confidential work may also require controls on visitors, keys, storage and network access.',
  'Ask for the exact cabin or suite included in the proposal rather than relying on a representative photograph. Identify furniture, equipment and shared facilities in the agreement. Discuss what happens if your team grows or a room becomes unsuitable. Make sure cleaning, maintenance, access and meeting-room arrangements are clear before deciding that a private office offers the control your business needs.',
  ['Actual room, layout and usable seat capacity', 'Door access, acoustics and storage', 'Furniture, equipment and shared facilities', 'Expansion options and maintenance responsibility']),
 'managed': ('Define what the operator will manage',
  'Managed and serviced offices reduce the work of setting up premises when the contract clearly defines who provides what. Start with seats, furniture, connectivity, utilities, cleaning and access. Separate the standard service from optional customisation. A ready office is only ready for your team when the equipment and permissions needed for its real work are in place.',
  'Agree the handover date and test the core facilities before moving business-critical work. Ask for a named contact and escalation route for outages, maintenance and access problems. For custom layouts, document lead times, approval responsibilities and one-time charges. Review the exit and reinstatement obligations as carefully as the move-in plan so the end of the agreement is predictable.',
  ['Service scope and furniture inventory', 'Handover date and acceptance checks', 'Incident response and operational ownership', 'Customisation, notice and exit charges']),
 'budget': ('Compare the total cost of usable workspace',
  'Use the same assumptions for every quote: number of people, expected attendance, workspace type and duration. Separate recurring fees from one-time charges and refundable deposits. Ask whether taxes, meeting use, printing, parking or out-of-hours access are extra. A lower headline fee can be less useful if the essentials of your working routine are charged separately.',
  'Write down your expected monthly spend and the amount due before move-in. Calculate cost per actual working day if you are comparing daily access with a subscription. Review notice periods, automatic renewal and deposit deductions before choosing a shorter or longer commitment. There are no verified live prices on this guide; request a dated, itemised proposal rather than treating illustrative comparisons as an offer.',
  ['Recurring fee, taxes and included services', 'Deposit, setup and optional usage charges', 'Attendance-based cost and minimum billing', 'Renewal, cancellation and refund terms']),
 'comparison': ('Compare providers with the same brief',
  'JobReady is an independent workspace business in Patna. This page is an editorial comparison guide and does not claim affiliation with, authorisation from or booking access to Spaces, Coworker, Regus or WeWork. Product names belong to their respective owners. No live competitor prices, rankings, local inventory or service guarantees are asserted here.',
  'Use official provider information and current operator confirmation when comparing a workspace brand, a marketplace listing and a local office. Record the actual address, workspace type, date, capacity and total quote. A discovery platform may introduce a listing without operating the premises. Identify who contracts with you, who receives payment and who handles cancellations before choosing a booking route.',
  ['Official location or verified operator identity', 'Matching dates, capacity and workspace type', 'Current quote, taxes and contract terms', 'Payment recipient, support and cancellation owner']),
 'audience': ('Design the workday around your actual tasks',
  'A useful shared workspace supports the way you work, whether that involves deep concentration, scheduled calls, client meetings or a changing remote schedule. Start with the tasks that are hardest to complete in your current environment. Check the space during a normal working period and avoid assuming that a quiet tour reflects peak-hour conditions.',
  'Bring a list of practical requirements: device setup, call duration, storage, permitted hours and any employer security rules. Shared facilities can support a professional routine, but their usage policies should fit that routine. A trial visit is a chance to check comfort and connectivity before a recurring commitment. Community benefits are worth considering when there is a current programme that you would actually use.',
  ['Focus time, calls and collaboration pattern', 'Device, network and security requirements', 'Real attendance and working hours', 'Trial experience and membership fit']),
 'team': ('Align seats, people and operating requirements',
  'Team workspace planning starts with peak attendance rather than total headcount alone. Identify who needs a permanent station, who visits occasionally and which people need to sit together. Discuss guest access, shared meeting demand and whether conversations could disturb other members. A written brief helps an operator evaluate the practical fit before offering a seat package.',
  'Business operations may introduce additional requirements for security, voice calls, equipment or non-standard hours. Ask for a technical walkthrough where appropriate and keep sensitive information out of general enquiries. Agree billing ownership, onboarding, escalation and the rules for adding or removing seats. Do not schedule a launch around a generic availability statement; obtain confirmation of the exact space and services your team requires.',
  ['Peak attendance and seating adjacency', 'Equipment, connectivity and permitted activity', 'Billing, access administration and onboarding', 'Growth, reduction and service escalation']),
 'access': ('Verify the whole shift, not only the entry time',
  'Access outside normal office hours needs a deliberate check of entry, exit and the services available throughout the shift. A claim of extended access does not establish that reception, cooling, cleaning or technical support operates at the same times. This guide does not confirm overnight or round-the-clock service at JobReady; request written confirmation for your proposed schedule.',
  'Explain the exact shift, expected attendance and nature of the work. Ask how late arrivals and visitors are handled, who responds to access failures and what power or internet support is available. Consider transport arrangements and emergency contacts as part of the work plan. Trial the agreed access process before depending on it for a client deadline or a recurring overnight operation.',
  ['Exact shift and days of access', 'Entry, exit and visitor permissions', 'Power, cooling, internet and support coverage', 'Emergency contact and incident procedure']),
 'mail': ('Make correspondence handling a defined process',
  'Mail services need more detail than an address on a website. Confirm which items can be accepted, how receipt is recorded and how quickly you are notified. Official letters, courier parcels and registered items may have different handling requirements. Ask who can collect items on your behalf and how identity or authorisation is checked.',
  'If forwarding or scanning is requested, agree permission, dispatch frequency, fees and privacy arrangements in advance. Understand tracking responsibility and what happens when an item is damaged, refused or left uncollected. Keep the contact details used for notifications current. For official correspondence with deadlines, discuss a process that gives you enough time to act; receipt at a business address is not the same as receipt by your decision-maker.',
  ['Accepted mail types and receipt records', 'Notification timing and authorised collection', 'Forwarding, scanning and privacy permissions', 'Fees, retention and uncollected-item policy']),
 'amenity': ('Turn a feature request into a practical test',
  'Facilities should be assessed against the work you need to do rather than a checklist of marketing terms. Describe the outcome you depend on, such as a stable video call, comfortable workstation or uninterrupted shift. Ask whether the relevant feature is available at the actual premises and included in the specific plan. Availability of the feature named in this guide is not confirmed by the guide itself.',
  'Where possible, inspect or test the facility during a normal working period with permission from the operator. Ask about capacity limits, reservations, maintenance and any separate usage fee. For a critical feature, discuss a fallback and the person responsible when it is unavailable. Record the agreed scope in the proposal so a useful conversation becomes an expectation both sides understand.',
  ['Actual availability at the selected premises', 'Included usage, capacity and reservation rules', 'A permitted practical test or inspection', 'Charges, maintenance and fallback arrangements']),
}

def esc(s): return html.escape(str(s), quote=True)
def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
def para(s): return f'<p>{esc(s)}</p>'

SNIPPETS = {
 'desk': 'Compare desk types, access hours and costs. Use the JobReady checklist before enquiring.',
 'virtual': 'Check address uses, documents, mail handling and renewal terms with JobReady.',
 'compliance': 'Review address documents, permissions and adviser checks before your JobReady enquiry.',
 'local': 'Compare the commute to Raja Bazar, access hours and availability with JobReady.',
 'booking': 'Check dates, seat availability, inclusions and booking terms. Enquire with JobReady.',
 'meeting': 'Plan capacity, equipment, guest access and rental terms. Send JobReady your meeting brief.',
 'private': 'Compare privacy, usable capacity, access and contract terms with the JobReady checklist.',
 'managed': 'Review furniture, service scope, handover and costs. Discuss your brief with JobReady.',
 'budget': 'Compare total costs, inclusions, deposits and exit terms before enquiring with JobReady.',
 'comparison': 'Independent guide to comparing locations, services and current quotes. No brand affiliation.',
 'audience': 'Match desks, hours, connectivity and costs to your workday with the JobReady guide.',
 'team': 'Plan seats, team access, equipment and billing. Discuss workspace needs with JobReady.',
 'access': 'Check shift hours, entry, facilities and support. Confirm availability with JobReady.',
 'mail': 'Review receipt, notification, collection and forwarding terms before enquiring with JobReady.',
 'amenity': 'Check actual facilities, usage limits and fees before choosing a plan with JobReady.',
}

def metadata(t):
    title = t['keyword'] + ' | JobReady'
    # Prefer the specific editorial action when it fits without cutting a sentence.
    desc = t['keyword'] + ': ' + t['action']
    if len(desc) > 165:
        desc = t['keyword'] + '. ' + SNIPPETS[t['family']]
    assert len(title) <= 65 and 70 <= len(desc) <= 165, (title, desc)
    return title, desc

def social_image_name(path):
    return 'workspace-guides' if path == '/seo/' else Path(path).stem

def build_social_image(label, category, name):
    """Render original text-based social artwork; never depend on a remote image."""
    from PIL import Image, ImageDraw, ImageFont
    image = Image.new('RGB', (1200,630), '#f6f7f2')
    draw = ImageDraw.Draw(image)
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    font = lambda size: ImageFont.truetype(font_path, size)
    draw.rectangle((0,0,17,630), fill='#142b29')
    draw.rounded_rectangle((960,45,1150,585), radius=25, fill='#d5edaa')
    for y in (95,215,335,455):
        draw.rounded_rectangle((995,y,1115,y+75), radius=10, fill='#142b29')
        draw.rectangle((1040,y-12,1070,y-3), fill='#f15c35')
    draw.text((60,45), 'JOBREADY / WORKSPACE', font=font(27), fill='#142b29')
    draw.text((60,115), category.upper(), font=font(18), fill='#4c6b25')
    for size in range(62,35,-2):
        lines, line = [], ''
        for word in label.split():
            candidate = (line+' '+word).strip()
            if draw.textlength(candidate,font=font(size)) > 845 and line:
                lines.append(line); line=word
            else: line=candidate
        lines.append(line)
        if len(lines) <= 3: break
    for i,line in enumerate(lines):
        draw.text((60,190+i*(size+18)),line,font=font(size),fill='#142b29')
    draw.line((60,505,900,505), fill='#d9dfd4', width=2)
    draw.text((60,535),'Practical guides. Clearer workspace decisions.',font=font(23),fill='#50625e')
    draw.text((60,580),'coworking.jobreadybpo.com',font=font(18),fill='#50625e')
    image.save(ROOT/'seo/assets/social'/f'{name}.png', optimize=True)

topics = []
decisions = (ROOT / 'tools/seo-decisions.txt').read_text().splitlines()
assert len(decisions) == 100
for i, line in enumerate((ROOT / 'tools/seo-topics.txt').read_text().splitlines(), 1):
    keyword, family, angle, action = line.split('|')
    category = 0 if i <= 25 else 1 if i <= 50 else 2 if i <= 65 else 3 if i <= 80 else 4
    question, answer = decisions[i-1].split('|')
    topics.append(dict(id=i, keyword=keyword, family=family, angle=angle, action=action, question=question, answer=answer, category=category, slug=slug(keyword)))
assert len(topics) == 100 and len({t['slug'] for t in topics}) == 100

def head(title, desc, path, schema, hub=False):
    image = f'{BASE}/seo/assets/social/{social_image_name(path)}.png'
    image_alt = title.removesuffix(' | JobReady') + ' — JobReady workspace guide'
    return f'''<!doctype html>
<html lang="en-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<link rel="canonical" href="{BASE}{path}"><link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/seo/assets/guides.css">
<meta property="og:type" content="{'website' if hub else 'article'}"><meta property="og:locale" content="en_IN"><meta property="og:site_name" content="JobReady Workspace Guides"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{BASE}{path}">
<meta property="og:image" content="{image}"><meta property="og:image:secure_url" content="{image}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{esc(image_alt)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{image}"><meta name="twitter:image:alt" content="{esc(image_alt)}">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('<', chr(92)+'u003c')}</script>
<link rel="stylesheet" href="/assets/site.css"><script src="/assets/site.js" defer></script>
{'<script src="/seo/assets/directory.js" defer></script>' if hub else ''}</head><body>
{header('/seo/') }'''

def footer():
    return '''<footer><div class="wrap"><div><a class="brand" href="/">JOBREADY<span> / workspace</span></a><p>Workspace decisions, made clearer. Coworking, business addresses and team workspace enquiries in Patna.</p><p>Stated location: Ashiana More, Raja Bazar, Indrapuri, Patna, Bihar 800014. Confirm the map pin before visiting.</p></div><div class="contact-line"><a href="tel:+919172712982">+91 9172712982</a><br><a href="mailto:hello@jobreadybpo.com">hello@jobreadybpo.com</a><br><a href="/seo/">All 100 workspace guides</a><br><a href="/business_services.html">Business services</a></div></div></footer></body></html>'''

def visual(t):
    label = {'virtual':'A business address, thoughtfully considered','compliance':'Get the details in order','comparison':'Different options. A clearer decision.','meeting':'Make room for a better meeting'}.get(t['family'], 'Space for your next chapter')
    return f'''<div class="visual"><div class="visual-top"><span>THE WORKSPACE EDIT</span><span>GUIDE {t['id']:03d}</span></div>
<svg viewBox="0 0 420 300" role="img" aria-label="Conceptual workspace floor plan, not a representation of the premises"><rect x="38" y="30" width="344" height="237" rx="6" fill="#f6f7f2" stroke="#142b29" stroke-width="3"/><path d="M38 169h190V30M228 169h154M228 212v55M38 211h55" stroke="#142b29" stroke-width="3" fill="none"/><rect x="66" y="61" width="132" height="70" rx="20" fill="#142b29"/><g fill="#f15c35"><rect x="80" y="45" width="30" height="10" rx="4"/><rect x="152" y="45" width="30" height="10" rx="4"/><rect x="80" y="137" width="30" height="10" rx="4"/><rect x="152" y="137" width="30" height="10" rx="4"/></g><g fill="#d5edaa" stroke="#142b29" stroke-width="2"><rect x="253" y="58" width="45" height="30" rx="3"/><rect x="317" y="58" width="45" height="30" rx="3"/><rect x="253" y="116" width="45" height="30" rx="3"/><rect x="317" y="116" width="45" height="30" rx="3"/></g><path d="M93 211a45 45 0 0 1 45 45M93 211v45" fill="none" stroke="#728665" stroke-width="2"/><circle cx="180" cy="218" r="20" fill="#d5edaa"/><circle cx="325" cy="220" r="28" fill="#142b29"/><path d="M313 220h24m-12-12v24" stroke="#d5edaa" stroke-width="2"/></svg>
<div class="visual-bottom"><span>{esc(label)}</span><span>PATNA, INDIA</span></div><span class="visual-tag">Illustration · explore your options</span></div>'''

def card(t, directory=False):
    title, description = metadata(t)
    data = f' data-guide data-category="{t["category"]}"' if directory else ''
    return f'<a class="card" href="/seo/{t["slug"]}.html"{data}><span class="eyebrow">{esc(CATEGORIES[t["category"]])} / {t["id"]:03d}</span><h3>{esc(title if directory else t["keyword"])}</h3><p>{esc(description if directory else t["angle"])}</p><span class="arrow">Read the guide ↗</span></a>'

def related(t):
    same = [x for x in topics if x['family'] == t['family'] and x != t]
    # Rotate candidates so same-family pages do not all have identical links.
    offset = t['id'] % max(1, len(same))
    same = same[offset:] + same[:offset]
    more = [x for x in topics if x['category'] == t['category'] and x != t and x not in same]
    return (same + more)[:3]

def build_page(t):
    family_title, p1, p2, checklist = FAMILIES[t['family']]
    keyword, angle, action = t['keyword'], t['angle'], t['action']
    path = f'/seo/{t["slug"]}.html'
    title, desc = metadata(t)
    faqs = [
      (f'What should I check when researching {keyword.lower()}?', angle + ' ' + action),
      (t['question'], t['answer']),
      ('How do I get a current quote or check availability?', 'Send JobReady your dates, number of people, required hours and preferred workspace type through WhatsApp or email. Request a written quote with inclusions, taxes and cancellation terms. An enquiry does not reserve space.'),
      ('Where is JobReady located in Patna?', 'The stated location is Ashiana More, Raja Bazar, Indrapuri, Patna, Bihar 800014. Confirm the exact map pin and visiting hours before travelling. Neighbourhood search guides do not establish additional branches.'),
      ('Are the facilities and services mentioned here guaranteed?', 'No. These guides explain what to evaluate. Confirm the particular facility, access hours, documentation or service in a written proposal. Registration approval, instant activation and competitor availability are not guaranteed.'),
    ]
    if t['family'] == 'comparison':
        faqs[3] = ('Can JobReady book a competitor’s workspace for me?', 'This is an independent comparison guide. JobReady does not claim to represent Spaces, Coworker, Regus or WeWork. Use the relevant provider’s official or verified channel to check its locations, prices and bookings.')
    schema = {'@context':'https://schema.org','@graph':[
      {'@type':'Article','@id':BASE+path+'#article','headline':keyword,'description':desc,'mainEntityOfPage':BASE+path,'inLanguage':'en-IN','author':{'@type':'Organization','name':'JobReady Business Outsourcing Company','url':BASE+'/'},'publisher':{'@type':'Organization','name':'JobReady Business Outsourcing Company','url':BASE+'/'}},
      {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE+'/'},{'@type':'ListItem','position':2,'name':'Workspace guides','item':BASE+'/seo/'},{'@type':'ListItem','position':3,'name':keyword,'item':BASE+path}]},
      {'@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in faqs]},
    ]}
    message = quote(f'Hello JobReady, I am enquiring about {keyword}. Please confirm availability, inclusions and a written quote. My dates: __. People: __. Hours: __.')
    special = ''
    if t['family'] == 'comparison':
        special = '<div class="note"><strong>Independent provider guide</strong><p>Brand references help you compare options. No affiliation, live competitor rates or booking authority is claimed.</p></div>'
    elif t['family'] in ('compliance','virtual'):
        special = '<div class="note"><strong>Confirm the permitted use</strong><p>Address services and physical desk access are separate. Ask a qualified adviser about registration requirements; acceptance is determined by the relevant authority.</p></div>'
    elif t['family'] == 'local':
        special = '<div class="note"><strong>Know the actual location</strong><p>JobReady’s stated location is Ashiana More, Raja Bazar, Indrapuri. This page is a commute and selection guide, not confirmation of a branch in the searched neighbourhood.</p></div>'
    else:
        special = '<div class="note"><strong>Availability comes first</strong><p>This is a planning guide. Ask for current availability, confirmed facilities and written terms before booking or travelling.</p></div>'
    faq_html = ''.join(f'<details><summary>{esc(q)}</summary>{para(a)}</details>' for q,a in faqs)
    steps = [action] + checklist
    steps_html = ''.join(f'<li>{esc(x)}</li>' for x in steps)
    if t['family'] == 'comparison':
        rows = [('Workspace brand', 'A specific centre and product, verified through the official provider.', 'Current location, contract, price and booking confirmation.'),('Listing platform', 'A discovery or booking route whose role varies by listing.', 'Actual operator, payment recipient and cancellation responsibility.'),('Independent local operator', 'A direct conversation about a particular local workspace.', 'An onsite visit, service scope and itemised written proposal.')]
    elif t['family'] in ('virtual','compliance','mail'):
        rows = [('Business correspondence', 'A business address or mail service with agreed permissions.', 'Receipt, notification, collection and any forwarding charges.'),('Registration use', 'Documentation suitable for the entity and authority.', 'Adviser review, premises authorisation and verification arrangements.'),('Physical workspace', 'A desk or room when you need somewhere to work.', 'Separate access entitlement, hours and booking terms.')]
    else:
        rows = [('Occasional use', 'A day or hourly arrangement for a specific visit.', 'Minimum duration, included facilities and cancellation terms.'),('Recurring desk', 'A flexible or assigned workstation for repeat attendance.', 'Visit limits, seat assignment, tax and renewal conditions.'),('Private or team space', 'An enclosed room or coordinated group of workstations.', 'Usable capacity, privacy, equipment and service responsibility.')]
    table = ''.join('<tr>'+''.join(f'<td>{esc(c)}</td>' for c in row)+'</tr>' for row in rows)
    return head(title, desc, path, schema) + f'''
<main id="main"><div class="wrap"><nav class="crumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/seo/">Workspace guides</a><span aria-hidden="true">/</span><span>{esc(keyword)}</span></nav>
<div class="hero"><div><span class="eyebrow">{esc(CATEGORIES[t['category']])} · GUIDE {t['id']:03d}</span><h1>{esc(keyword)}</h1><p class="lede">{esc(angle)}</p><div class="actions"><a class="button" href="#enquire">Discuss your requirements ↗</a><a class="button light" href="#checklist">See the checklist ↓</a></div><p class="micro">A practical JobReady guide · Clear questions. Better workspace decisions.</p></div>{visual(t)}</div>
<div class="strip"><div><strong>Choose with context</strong><span>Match the space to your work</span></div><div><strong>Compare the details</strong><span>Hours, inclusions and total cost</span></div><div><strong>Enquire directly</strong><span>Confirm before you commit</span></div></div>
<div class="content"><aside class="toc" aria-label="On this page"><strong>IN THIS GUIDE</strong><a href="#decision">Your starting point</a><a href="#options">Understand the options</a><a href="#checklist">Before you commit</a><a href="#compare">Compare the fit</a><a href="#questions">Common questions</a><a href="#enquire">Make an enquiry ↗</a><p class="micro">Searching locally?<br>Check the actual address and commute before visiting.</p></aside>
<article class="article"><section id="decision"><span class="eyebrow">01 / THE DECISION</span><h2>A clearer brief makes a better choice.</h2>{para(angle)}{para(action)}<h3>{esc(t['question'])}</h3>{para(t['answer'])}{special}</section>
<section id="options"><span class="eyebrow">02 / YOUR OPTIONS</span><h2>{esc(family_title)}</h2>{para(p1)}{para(p2)}</section>
<section id="checklist"><span class="eyebrow">03 / YOUR SHORTLIST</span><h2>What to confirm before you commit</h2><p>Use this checklist in a tour, email or provider conversation. Ask for specific answers that relate to your dates and proposed plan. Where a requirement is essential, have it recorded in the quotation or agreement.</p><ol class="numbered">{steps_html}</ol></section>
<section id="compare"><span class="eyebrow">04 / COMPARE THE FIT</span><h2>Choose the arrangement that solves your need.</h2><p>Compare like for like. These are decision categories, not live packages or confirmed inventory. Ask each provider to explain what is included and what will be quoted separately.</p><div class="table-scroll" role="region" aria-label="Workspace options comparison" tabindex="0"><table><caption class="micro">A practical comparison framework for {esc(keyword.lower())}</caption><thead><tr><th scope="col">Option</th><th scope="col">What to evaluate</th><th scope="col">Ask for clarity on</th></tr></thead><tbody>{table}</tbody></table></div></section>
<section id="questions"><span class="eyebrow">05 / GOOD QUESTIONS</span><h2>Before you make your next move.</h2>{faq_html}</section>
<section class="enquire" id="enquire"><span class="eyebrow" style="color:#d5edaa">LET’S FIND THE RIGHT FIT</span><h2>Tell us what a good workday looks like.</h2><p>Ask JobReady about {esc(keyword.lower())}. Share your dates, headcount, hours and must-have requirements. We’ll start with an enquiry; availability and booking terms need written confirmation.</p><div class="actions"><a class="button" href="https://wa.me/919172712982?text={message}">Enquire on WhatsApp ↗</a><a class="button light" href="mailto:hello@jobreadybpo.com?subject={quote(keyword+' enquiry')}">Email your brief</a></div><p class="micro">Prefer a conversation? <a href="tel:+919172712982">Call +91 9172712982</a>. No payment is collected on this page.</p></section>
</article></div></div><section class="related"><div class="wrap"><div class="related-head"><div><span class="eyebrow">KEEP EXPLORING</span><h2>A few useful next reads.</h2></div><a href="/seo/">Browse all 100 guides ↗</a></div><div class="cards">{''.join(card(x) for x in related(t))}</div></div></section></main>''' + footer()

def build_hub():
    title = 'Workspace Guides: Coworking & Virtual Offices | JobReady'
    desc = 'Explore 100 practical guides to Patna coworking, virtual offices, booking, workspace costs and provider comparisons. Find the right questions before you commit.'
    schema = {'@context':'https://schema.org','@type':'CollectionPage','name':title,'url':BASE+'/seo/','description':desc,'mainEntity':{'@type':'ItemList','numberOfItems':100,'itemListElement':[{'@type':'ListItem','position':t['id'],'name':t['keyword'],'url':BASE+'/seo/'+t['slug']+'.html'} for t in topics]}}
    filters = '<button type="button" data-filter="all" aria-pressed="true">All guides</button>' + ''.join(f'<button type="button" data-filter="{i}" aria-pressed="false">{esc(c)}</button>' for i,c in enumerate(CATEGORIES))
    return head(title,desc,'/seo/',schema,True)+f'''<main id="main" class="wrap"><div class="directory-hero"><span class="eyebrow">THE JOBREADY WORKSPACE EDIT / 100 GUIDES</span><h1>Find your space.<br>Make your next move.</h1><p class="lede">From a desk for the day to an address for your business. Practical guides to help you ask better questions, compare your options and choose with confidence.</p><a class="button" href="#directory">Explore the collection ↓</a></div><div class="strip"><div><strong>01 / Work locally</strong><span>Patna locations & commutes</span></div><div><strong>02 / Choose clearly</strong><span>Plans, features & comparisons</span></div><div><strong>03 / Move thoughtfully</strong><span>Checklists before commitments</span></div></div><section id="directory" aria-label="Find a workspace guide"><div class="directory-tools"><label class="search-label" for="guide-search">What are you looking for?</label><div class="search"><input id="guide-search" type="search" placeholder="Try GST, Boring Road, meeting rooms…" aria-controls="guides" autocomplete="off"></div><div class="filters" role="group" aria-label="Filter guides by category">{filters}</div><p class="count" id="result-count" role="status" aria-live="polite">100 of 100 guides</p></div><div class="cards directory-grid" id="guides">{''.join(card(t,True) for t in topics)}</div><p class="empty" id="no-results" hidden>No matching guides. Try a broader search or choose “All guides”.</p></section><div class="hub-note"><h2>Useful guidance. Clear expectations.</h2><p>JobReady’s stated location is Ashiana More, Raja Bazar, Indrapuri, Patna. Locality guides help you compare commutes; they do not establish additional branches. Services, amenities, prices and hours must be confirmed directly. Competitor guides are independent editorial comparisons with no claimed affiliation or live competitor inventory.</p><p>For registration-related address use, ask a qualified adviser to review the actual documents. No guide guarantees statutory approval.</p></div></main>'''+footer()

def main():
    out = ROOT / 'seo'
    out.mkdir(exist_ok=True)
    (out/'assets/social').mkdir(exist_ok=True)
    for topic in topics:
        build_social_image(topic['keyword'], CATEGORIES[topic['category']], topic['slug'])
        (out / (topic['slug']+'.html')).write_text(build_page(topic).replace('↗','→'))
    build_social_image('Find your space. Make your next move.', '100 practical workspace guides', 'workspace-guides')
    (out / 'index.html').write_text(build_hub().replace('↗','→'))
    (out / 'keyword-map.json').write_text(json.dumps(topics,ensure_ascii=False,indent=2)+'\n')
    with (out/'metadata.csv').open('w',newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['Keyword / H1','Title tag','Meta description','Canonical URL','Open Graph image'])
        for topic in topics:
            title, desc = metadata(topic)
            writer.writerow([topic['keyword'],title,desc,f'{BASE}/seo/{topic["slug"]}.html',f'{BASE}/seo/assets/social/{topic["slug"]}.png'])
    tree = Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    paths = ['/','/jobreadyvirtualoffice.html','/company_registration.html','/business_services.html','/tax_compliance.html','/enterprise.html','/seo/']
    paths += ['/seo/'+t['slug']+'.html' for t in topics]
    for path in paths:
        SubElement(SubElement(tree,'url'),'loc').text=BASE+path
    indent(tree, space='  ')
    (ROOT / 'sitemap.xml').write_bytes(b'<?xml version="1.0" encoding="UTF-8"?>\n'+tostring(tree,encoding='utf-8')+b'\n')
    (ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n')
    print(f'Generated {len(topics)} topic pages, directory, keyword map and {len(paths)} sitemap URLs.')

if __name__ == '__main__': main()
