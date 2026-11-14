# JobReady Workspace Platform

Premium Coworking, Virtual Office, Company Registration, Tax Compliance and Business Services Platform.

## Pages
- Coworking directory (`coworking/index.html`) and 100 individual landing pages (`coworking/<keyword>/index.html`)
- Home (index.html)
- Virtual Office (jobreadyvirtualoffice.html)
- Company Registration (company_registration.html)
- Business Services (business_services.html)
- Tax & Compliance (tax_compliance.html)
- Enterprise (enterprise.html)
- Workspace guides (seo/index.html; 100 topic pages)

## Responsive interface

All 209 HTML pages (six main pages, the error page, two directories and 200 content pages) use the shared header in `tools/site_components.py`. Four primary routes replace the long service list: Coworking, Virtual office, Business services and Guides. The logo is the Home link; Talk to us is the primary action. Existing enquiry forms are used directly where available.

Coworking groups desks, private/team space, meeting rooms, enterprise offices, budget options and local commutes, with a link to the full 100-page directory. Business services groups operational support, company registration and GST/tax compliance. Grouped dropdowns include short descriptions and active-section highlighting. Only one group opens at a time; Escape closes a group before closing the mobile menu. Outside click, keyboard focus changes, route selection and responsive resizing close menus appropriately. Native details/summary controls keep dropdowns usable without JavaScript. The mobile breakpoint is 1100px; compact mobile actions leave room for the brand. New coworking pages include a mobile enquiry bar with space reserved beneath the content.

`assets/site.css` and `assets/site.js` provide navigation, accessible enquiry forms, keyboard focus and reduced-motion behaviour. `assets/pages.css` adapts service-page grids, typography, buttons, footers and contact options. `assets/utilities.css` replaces the external Tailwind runtime with the utility rules used by the existing pages. System fonts and inline SVG icons remove external font/icon dependencies. Existing external photography is optional; decorative hero images hide if loading fails, leaving the gradient background. No live photo availability was verified during mobile testing.

The four service enquiry forms have labels, name/phone/email autocomplete, phone keyboards and native validation. Continuing opens WhatsApp with the entered details for the visitor to review and send; it does not submit to a backend or confirm a booking. With JavaScript disabled, the form falls back to the visitor's email application. Phone and email alternatives are available alongside each form. No form data is saved locally.

## Local development and checks

### Coworking landing-page collection

The Coworking header menu links to six focused workspace destinations and the full `/coworking/` directory. The directory retains its seven categories and all 100 target pages, with accessible search, filters, result counts and progressive loading. All 100 links remain present in the source and work without JavaScript.

The new responsive design uses `assets/coworking.css`, `assets/coworking.js` and an original workspace illustration. Every page includes its own content and metadata, plans, location information, four visible FAQs with matching JSON-LD, related links and a Name / Phone / Team Size enquiry form. Forms open an editable WhatsApp draft; they do not submit a booking or save details locally. Unconfirmed illustrative prices are replaced by quote requests. Locality pages identify the actual Raja Bazar centre.

Page data is maintained in `content/coworking-pages.json`. Rebuild with `python3 tools/generate_coworking.py`; validate with `python3 tools/check_coworking.py`. The generator also refreshes existing shared headers and adds the 101 collection URLs to the sitemap. It is safe to rerun without duplicating sitemap URLs. Existing `/seo/` guides remain available; review overlapping search intent before deploying both collections as indexable pages.

The source and JavaScript syntax checks pass. Browser visual, responsive and interaction checks for the new collection could not be completed because the managed preview relay timed out on port 4173. The older mobile-check description below records the previous collection's testing; it is not a test result for this new layout.

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

## SEO titles and descriptions

All 209 HTML pages use reviewed metadata in `content/seo-metadata.json`. Titles are limited to 60 characters and descriptions to 155 characters, counting decoded text rather than HTML entities. These are editorial maximums, not guarantees of Google's displayed snippet width or wording.

The copy distinguishes service enquiries from informational guides, adds JobReady branding, and describes locality pages as commute comparisons where appropriate. Search snippets, Open Graph and Twitter text match. Existing article and collection descriptions are synchronised; the 404 page retains `noindex`.

Edit the shared JSON, run `python3 tools/generate_coworking.py` to refresh the landing-page manifest, then `python3 tools/enrich_site_metadata.py` to update the complete site and guide-directory previews without rebuilding image assets. Run `python3 tools/check_metadata.py`, `python3 tools/check_coworking.py` and `python3 tools/check_seo.py` to validate the output. The current character-count audit is `seo/metadata-audit.csv`.

All three page-maintenance scripts read the shared metadata source, so regenerating a page preserves the approved copy. Review a new page's metadata entry before adding it to a generator.

## Contact details
Phone: +91 9172712982
Email: hello@jobreadybpo.com


## Clean URL migration

All public content now uses lowercase, hyphenated directory URLs. Main destinations are `/company-registration/`, `/virtual-office/`, `/business-services/`, `/tax-compliance/`, `/managed-offices/`, `/coworking/` and `/guides/`. New compliance service routes omit repeated locality terms, while the metadata and content retain Patna/Bihar intent. Existing coworking URLs are preserved.

`content/url-migrations.json` is the authoritative legacy-to-canonical mapping. The migration physically moves HTML to directory `index.html` files and updates links, schema URLs, metadata keys, the sitemap and service manifests. Legacy `.html` and extensionless aliases redirect directly to the canonical destination. Static assets remain under their existing paths, including `/seo/assets/`.

Host rules are supplied in `vercel.json` (Vercel), `_redirects` (Cloudflare Pages/Netlify), and `.htaccess` (Apache with mod_rewrite/AllowOverride). Deploy the complete repository, including the host configuration. Other hosts require equivalent permanent redirect rules; plain file hosting alone does not implement them. Production redirects must be verified after deployment. No domain or DNS changes are included.

Older content generators automatically run the migration after generation. The primary metadata tool resolves legacy file names; all-page enrichment writes the guide directory at its canonical location. After content generation or manual additions run:

```sh
python3 tools/migrate_urls.py
python3 tools/enrich_site_metadata.py
python3 tools/check_urls.py
python3 tools/check_metadata.py
python3 tools/check_seo.py
python3 tools/check_coworking.py
```

The migration is safe to rerun. `content/url-migration-report.csv` records the old URL, destination and intended 301 status. The sitemap contains 227 canonical indexable URLs; the 404 page remains excluded. The local Python development server serves the directory URLs but does not implement the host redirect rules.
