# JobReady workspace guide collection

100 topic-specific HTML drafts cover the supplied keywords in their original order, plus a searchable directory at `/seo/`. All content is server-rendered static HTML. The directory search progressively enhances a fully crawlable list; JavaScript is not required to read any guide.

## Content and design

- Five categories: Patna (25), commercial/booking (25), provider comparisons (15), audiences (15), features and long-tail searches (20).
- Each topic has its own keyword, search description, decision angle, next action, substantive question and answer, canonical URL and enquiry message. Longer guidance is shared by workspace family to maintain consistency.
- Each page includes a decision guide, service context, five-item checklist, three-option comparison, five FAQs, related guides, breadcrumbs and WhatsApp/email/phone enquiries.
- Responsive local CSS, an original conceptual floor-plan illustration, keyboard focus styles, skip link, native FAQ disclosure controls and reduced-motion support. No external fonts, libraries or image requests are required for this collection.
- Article, BreadcrumbList and FAQPage JSON-LD on topic pages; CollectionPage/ItemList on the directory. FAQ markup matches visible questions and answers. Markup does not promise rich-result eligibility.
- Updated root sitemap contains 107 canonical URLs: six existing primary pages, the directory and 100 topic pages. The error page is excluded. Robots points to that sitemap. Existing virtual-office links now use the real filename.

## Editing and regeneration

From `/workspace/co-working`:

```sh
python3 tools/generate_seo.py
python3 tools/check_seo.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory /workspace/co-working
```

In another terminal, run the browser check against that server:

```sh
node tools/check_seo_browser.cjs
```

The static checker uses only Python's standard library. Browser validation uses the environment's existing Playwright package and Chromium at `/usr/bin/chromium`; these are development checks, not production runtime dependencies.

Metadata enrichment includes keyword-first title tags (at most 65 characters for topic pages), complete unique meta descriptions, full Open Graph image metadata and Twitter large-image cards. Every page retains its topic as a visible H1. The directory and each of the 100 topic pages have their own locally generated 1200×630 PNG preview. The absolute preview URLs use the canonical production host and will become publicly fetchable when the changed files are deployed. Social platforms may cache older previews.

The generator uses the environment's existing Pillow package and DejaVu Sans font to render these original social cards. This is a generation-time dependency only; the published site serves ordinary static PNG files. `metadata.csv` lists all 100 keyword/H1, title, description, canonical and preview-image values for editorial review. Edit the `metadata()` function and `SNIPPETS` mapping in the generator to change the metadata rules.

`tools/seo-topics.txt` maintains keyword, content family, decision angle and action in pipe-separated rows. `tools/seo-decisions.txt` provides the matching topic-specific question and answer, in the same order. `tools/generate_seo.py` owns shared editorial sections, markup, links and metadata. `seo/assets/` owns presentation and directory filtering. Regeneration rewrites topic pages, the directory, `keyword-map.json`, the root sitemap and robots file. Edit the source data or generator instead of editing generated HTML directly. Keep exactly 100 aligned rows in both source files.

`keyword-map.json` maps every supplied keyword to its slug, category and editorial content. It is also suitable for importing the plan into a spreadsheet or CMS workflow.

## Editorial scope

These are designed content drafts, saved in the repository; they have not been deployed or submitted to search engines. Pages are technically indexable. Confirm business details before publication, including the canonical deployment host, actual address, service availability, documentation, opening hours and approved contact channels. Enquiries do not reserve inventory or process payments.

The collection intentionally does not invent prices, reviews, additional Patna branches, competitor inventory, amenities or registration guarantees. Locality pages explain the relationship to the stated Raja Bazar location. Competitor pages are independent selection frameworks; current competitor products and rates have not been researched or asserted.

Some supplied phrases overlap substantially, particularly broad coworking terms and online-booking variants. Each receives the requested draft URL, with a different decision angle, but shared topic context remains. Before publishing all URLs, decide which pages warrant standalone indexing based on genuine service distinctions and verified local evidence. Merge overlapping pages and redirect their URLs if they would serve the same search need; update the source and sitemap accordingly. Add approved location photography, documented service specifics and actual comparison data where available. Avoid turning unverified locality guides into branch landing pages.

## Validation

The static checker verifies 100-keyword coverage, unique titles/descriptions/canonical URLs, valid JSON-LD, matching visible FAQ questions, existing internal assets and fragments, sitemap coverage and the directory link from the home page.

The browser checker visits all 100 topic pages at desktop and mobile widths, checks HTTP responses, headings, FAQ disclosure interaction, enquiry links and horizontal overflow. It also exercises all five directory filters, search and empty state, and fails on JavaScript errors, failed requests or unexpected external requests. Screenshots are written to `/tmp/seo-*.png` for local inspection.
