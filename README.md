# JobReady Workspace Platform

Premium Coworking, Virtual Office, Company Registration, Tax Compliance and Business Services Platform.

## Pages
- Home (index.html)
- Virtual Office (jobreadyvirtualoffice.html)
- Company Registration (company_registration.html)
- Business Services (business_services.html)
- Tax & Compliance (tax_compliance.html)
- Enterprise (enterprise.html)
- Workspace guides (seo/index.html; 100 topic pages)

## Responsive interface

All 108 HTML pages (six main pages, the error page, the guide directory and 100 guides) use the shared header in `tools/site_components.py`. The mobile menu includes all service areas and contact routes; it supports Escape, outside click, link selection and resizing. Without JavaScript, navigation remains visible. The header includes a persistent call link without a bottom overlay obscuring content.

`assets/site.css` and `assets/site.js` provide navigation, accessible enquiry forms, keyboard focus and reduced-motion behaviour. `assets/pages.css` adapts service-page grids, typography, buttons, footers and contact options. `assets/utilities.css` replaces the external Tailwind runtime with the utility rules used by the existing pages. System fonts and inline SVG icons remove external font/icon dependencies. Existing external photography is optional; decorative hero images hide if loading fails, leaving the gradient background. No live photo availability was verified during mobile testing.

The four service enquiry forms have labels, name/phone/email autocomplete, phone keyboards and native validation. Continuing opens WhatsApp with the entered details for the visitor to review and send; it does not submit to a backend or confirm a booking. With JavaScript disabled, the form falls back to the visitor's email application. Phone and email alternatives are available alongside each form. No form data is saved locally.

## Local development and checks

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory /workspace/co-working
```

Run checks from the checkout in another terminal:

```sh
python3 tools/check_seo.py
node tools/check_mobile.cjs
```

The mobile check uses the environment's Playwright and Chromium. It visits all 108 pages at 320, 375, 390, 768, 1024 and 1440px widths, checking overflow and clipped text, menu interaction, guide tables and FAQs. It also checks enquiry validation and message composition through intercepted requests (no messages sent), search/filtering, landscape menu scrolling, reduced motion and navigation without JavaScript. Screenshots are saved under `/tmp/mobile-*.png`. These are Chromium viewport checks, not real-device Safari or Android certification.

Edit the guide generator and shared component source before running `python3 tools/generate_seo.py` to refresh guides. Main service-page HTML is edited directly; when changing the header markup, update it in those seven documents as well as in the shared component. Use `python3 tools/generate_utilities.py` if utility usage changes. See `seo/README.md` for the content and metadata workflow.

Run `python3 tools/enrich_primary_metadata.py` to refresh the six main pages' title tags, descriptions, canonical links, Open Graph/Twitter metadata and local social cards. Those main-page titles and descriptions were shortened during the mobile/SEO review, outdated canonical hosts were aligned, and broken footer anchors were replaced with real destinations. `tools/check_seo.py` checks these pages alongside the guides. The external Seobility report and production site could not be fetched under this environment's network policy, so a new live audit score has not been measured. Backlinks and host-level cache/compression settings are outside the static source validation.

## Contact
Phone: +91 9172712982
Email: hello@jobreadybpo.com
