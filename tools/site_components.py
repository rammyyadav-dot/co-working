"""Shared static markup for the site and generated guides."""
from html import escape

def header(current=''):
    arrow = '<svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="m3 4.5 3 3 3-3" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    def link(url, label, description=''):
        active = ' aria-current="page"' if current == url else ''
        return f'<a href="{url}"{active}><strong>{label}</strong>'+(f'<span>{description}</span>' if description else '')+'</a>'
    workspaces = [
        ('/coworking/#desks', 'Desks & day passes', 'For a day, a week or your regular routine'),
        ('/coworking/#teams', 'Private & team space', 'Find room to focus and work together'),
        ('/coworking/meeting-rooms-in-patna/', 'Meeting rooms', 'Client conversations, interviews and reviews'),
        ('/enterprise.html', 'Enterprise offices', 'Plan a managed base for your team'),
        ('/coworking/#budget', 'Budget options', 'Compare plans around your actual attendance'),
        ('/coworking/#locations', 'Locations & commutes', 'Check the journey to our Raja Bazar centre'),
    ]
    services = [
        ('/business_services.html', 'Business services', 'Support for your day-to-day operations'),
        ('/company_registration.html', 'Company registration', 'Explore incorporation and documentation'),
        ('/tax_compliance.html', 'GST & tax compliance', 'Registration, filing and compliance support'),
    ]
    def group(label,key,items,active=False):
        return f'<details class="site-nav-group site-nav-{key}"'+(' data-current="true"' if active else '')+f'><summary>{label}{arrow}</summary><div class="site-nav-panel" id="site-{key}-panel"><p class="site-nav-eyebrow">'+('Find your working base' if key=='workspaces' else 'Build your business')+'</p><div class="site-nav-panel-links">'+''.join(link(*item) for item in items)+'</div>'+('<a class="site-nav-all" href="/coworking/">Explore all 100 workspace pages <span aria-hidden="true">↗</span></a>' if key=='workspaces' else '')+'</div></details>'
    links=group('Coworking','workspaces',workspaces,current.startswith('/coworking/') or current=='/enterprise.html')
    links+=link('/jobreadyvirtualoffice.html','Virtual office')
    links+=group('Business services','services',services,current in {item[0] for item in services})
    links+=link('/seo/','Guides')
    contacts = {
        '/jobreadyvirtualoffice.html': '/jobreadyvirtualoffice.html#virtual-enquiry',
        '/company_registration.html': '/company_registration.html#lead-form',
        '/business_services.html': '/business_services.html#business-enquiry',
        '/tax_compliance.html': '/tax_compliance.html#contact',
    }
    contact = current+'#enquire' if current.startswith('/coworking/') else contacts.get(current, '/index.html#contact')
    return f'''<a class="site-skip" href="#main">Skip to content</a>
<header class="site-header"><div class="site-header-inner">
<a class="site-brand" href="/index.html" aria-label="JobReady home">JOBREADY<span>.</span></a>
<div class="site-header-actions"><a class="site-call" href="tel:+919172712982" aria-label="Call JobReady at +91 9172712982"><svg width="17" height="17" viewBox="0 0 24 24" aria-hidden="true"><path d="m7 3 3 5-3 3a15 15 0 0 0 6 6l3-3 5 3c0 3-2 5-5 4C8 19 5 16 3 8 2 5 4 3 7 3Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg><span>Call the team</span></a><a class="site-header-cta" href="{contact}">Talk to us <span aria-hidden="true">↗</span></a>
<button class="site-menu-toggle" type="button" aria-expanded="false" aria-controls="site-navigation"><svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg><span>Menu</span></button></div>
<nav class="site-navigation" id="site-navigation" aria-label="Main navigation">{links}<a class="site-nav-contact" href="{contact}"><strong>Talk to us</strong><span>Get help choosing your next step ↗</span></a></nav>
</div><noscript><style>@media(max-width:1099px){{.site-header{{position:relative}}.site-header .site-navigation{{display:flex;flex-direction:column;align-items:stretch}}.site-menu-toggle{{display:none}}}}</style></noscript></header>'''

def enquiry_form(service, options=(), form_id=''):
    key = form_id or 'service-enquiry'
    esc = lambda text: escape(text, quote=True)
    select = ''
    if options:
        select = f'<div class="enquiry-field"><label for="{key}-service">Service</label><select id="{key}-service" name="Service">'+''.join(f'<option>{esc(x)}</option>' for x in options)+'</select></div>'
    return f'''<form class="enquiry-form" id="{key}" data-enquiry="{esc(service)}" action="mailto:hello@jobreadybpo.com" method="post" enctype="text/plain" aria-labelledby="{key}-title">
<span class="enquiry-kicker">LET’S FIND THE RIGHT FIT</span><h2 id="{key}-title">{esc(service)} enquiry</h2>
<p>Tell us what you need. Ask about availability, services and a written quote.</p>
<div class="enquiry-field"><label for="{key}-name">Full name <span>(required)</span></label><input id="{key}-name" name="Name" autocomplete="name" required maxlength="100" placeholder="Your full name"></div>
<div class="enquiry-field"><label for="{key}-phone">Phone number <span>(required)</span></label><input id="{key}-phone" name="Phone" type="tel" inputmode="tel" autocomplete="tel" required pattern="[+0-9 \\(\\)\\-]{{7,20}}" title="Enter a phone number with 7–20 characters using digits, spaces, +, - or parentheses." placeholder="e.g. +91 98765 43210"></div>
<div class="enquiry-field"><label for="{key}-email">Email <span>(optional)</span></label><input id="{key}-email" name="Email" type="email" inputmode="email" autocomplete="email" maxlength="150" placeholder="you@company.com"></div>
{select}<div class="enquiry-field"><label for="{key}-brief">Your requirements <span>(optional)</span></label><textarea id="{key}-brief" name="Requirements" rows="3" maxlength="1200" placeholder="Dates, team size, preferred hours or questions"></textarea></div>
<p class="enquiry-help" id="{key}-help">Opens WhatsApp with your details. Review the message and send it to start your enquiry. No booking or payment is made here.</p>
<button class="enquiry-submit" type="submit" aria-describedby="{key}-help">Continue to WhatsApp <span aria-hidden="true">→</span></button>
<p class="enquiry-alternative">Prefer another way? <a href="tel:+919172712982">Call us</a> or <a href="mailto:hello@jobreadybpo.com">email your brief</a>.</p>
<noscript><p>JavaScript is off. Submitting opens your email app instead; you can also call us directly.</p></noscript></form>'''
