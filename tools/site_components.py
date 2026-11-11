"""Shared static markup for the site and generated guides."""
from html import escape

LINKS = [
    ('/index.html', 'Home'),
    ('/index.html#solutions', 'Coworking'),
    ('/jobreadyvirtualoffice.html', 'Virtual office'),
    ('/company_registration.html', 'Company registration'),
    ('/business_services.html', 'Business services'),
    ('/tax_compliance.html', 'Tax & compliance'),
    ('/index.html#meeting-rooms', 'Meeting rooms'),
    ('/enterprise.html', 'Enterprise'),
    ('/seo/', 'Workspace guides'),
]

def header(current=''):
    links = ''.join(f'<a href="{url}"'+(' aria-current="page"' if current == url else '')+f'>{label}</a>' for url,label in LINKS)
    return f'''<a class="site-skip" href="#main">Skip to content</a>
<header class="site-header"><div class="site-header-inner">
<a class="site-brand" href="/index.html" aria-label="JobReady home">JOBREADY<span>.</span></a>
<div class="site-header-actions"><a class="site-call" href="tel:+919172712982">Call us</a>
<button class="site-menu-toggle" type="button" aria-expanded="false" aria-controls="site-navigation"><svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg><span>Menu</span></button></div>
<nav class="site-navigation" id="site-navigation" aria-label="Main navigation">{links}<a class="site-nav-contact" href="/index.html#contact">Contact & enquiries</a></nav>
</div><noscript><style>@media(max-width:1279px){{.site-header{{position:relative}}.site-header .site-navigation{{display:grid;grid-template-columns:1fr}}.site-menu-toggle{{display:none}}}}</style></noscript></header>'''

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
