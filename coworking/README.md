# 100 coworking HTML landing pages

Entry point: `/coworking/`. Each target keyword has its own directory with an `index.html`, as listed in `manifest.json`. The Coworking navigation menu on every existing and new HTML page links to the directory and its seven categories.

Serve the entire website root, not only this folder. CSS and JavaScript live in `/assets/`; existing Home and other service-page links are intentionally retained. For local viewing, run `python3 -m http.server 8000` from the website root, then open `http://localhost:8000/coworking/`.

## Included design and behaviour

- Responsive editorial layout with JobReady blue, warm neutral surfaces and an original workspace illustration.
- Category filtering, multiword search, live result counts, empty-state reset and progressive loading of 12 cards at a time.
- All 100 crawlable page links available without JavaScript.
- Unique copy and metadata per landing page, plan comparison table, actual Raja Bazar location, related links and four FAQs with matching JSON-LD.
- Required Name, Phone/WhatsApp and Team Size fields. Form validation runs before an editable WhatsApp draft opens. The visitor must send it; no booking is created.
- Keyboard-accessible navigation and FAQs, skip link, visible focus styling and reduced-motion handling.

## Maintenance

Edit `content/coworking-pages.json` and `tools/generate_coworking.py`, then run:

```sh
python3 tools/generate_coworking.py
python3 tools/check_coworking.py
python3 tools/check_seo.py
node --check assets/coworking.js
node --check assets/site.js
```

All commands above passed for this delivery. They verify source structure, metadata, internal assets/links/fragments and FAQ-to-schema consistency. They do not establish live inventory, approval of registration documents, current pricing or real-device rendering.

Managed browser preview could not be completed: the preview relay timed out opening port 4173. Responsive appearance, browser interactions and external WhatsApp delivery are therefore unverified for this new collection. No enquiry message was sent during development.

The website is not deployed by this delivery. Retained `/seo/` guides overlap with some new search intents; choose the appropriate intent owners before indexing both collections. Unapproved illustrative prices and raw distance placeholders are not displayed as offers in the new interface.
