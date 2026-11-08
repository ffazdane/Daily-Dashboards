---
name: fazdane-daily-dashboard
description: Generate, brand and publish FazDane daily market intelligence as HTML-only GitHub Pages reports, preserving the original weekday/weekend layouts.
---

In ffazdane/Daily-Dashboards, select by Chicago publication date. Saturday and Sunday use reports/2026-11-01.html (narrow teal stack, dial, close tiles and horizontal return charts). Monday through Friday use reports/2026-11-02.html (wider blue layout, regime gauge, KPI cards, numbered sections and paired rotation/MAG7 panels). Keep the last verified close dated separately, including on Mondays and holidays. Retain interactive daily/5D and horizon tabs. Use scripts/briefing.py for layout and scripts/daily.py for dated retrieval, rendering and archive insertion. Run from the repository root on Linux with Python 3 and curl.

Keep the brand bar, mobile shell, summary dial, market tape, drawdowns, sector rotation, Magnificent 7 daily and five-session returns, volatility, watchlist, three planning horizons, calendar, headlines, source ledger and full disclaimer. Always lead with the numeric Market Regime Score on a 0–100 dial, posture, and dated model interpretation. Use regime() in scripts/briefing.py, which equally weights five-session SPY momentum, aligned 11-sector breadth and dated VIX. Print the method and risk thresholds in the ledger. Use N/V when a required input is missing. Reject a daily render that substitutes ETF counts for the regime score. Verify both the weekend REGIME / 100 and weekday / 100 REGIME hero labels when changing templates. Label mechanical rankings and planning prompts. Only populate claims, events and headlines with attributable dated evidence. Show unavailable coverage explicitly. Never roll historical prices, regime scores or headlines into a new edition.

Use the Chicago publication date and retain each series' observation date. Publish only self-contained HTML using reports/FazDane_Daily_Market_Dashboard_YYYY-MM-DD.html. Preserve archived reports on reruns. For authorized publication, use the existing Pages workflow and check its byte comparison of the public index and HTML.

On the archive homepage, use the full English weekday and date for both the latest dashboard heading and the bold archive row label (for example, Saturday, November 7, 2026). Keep the ISO date beneath the row label and in the report filename. Omit the “About the reports” section and retain the financial disclaimer.

Share clean dashboard URLs. When an incoming homepage URL includes `utm_source=chatgpt.com`, remove that parameter from the address bar while preserving other query parameters and the fragment.

## Required FazDane branding
- Every new published HTML report **must display the provided FazDane Analytics logo**. Use `assets/fazdane-logo.svg` on the public homepage and `../assets/fazdane-logo.svg` or a self-contained embedded logo in reports.
- Make the logo legible and responsive on mobile. Keep the dark navy, teal, blue-green visual language and archive-home navigation.
- Preserve a prominent **Financial & Research Disclaimer** on the homepage and every report (educational only; not investment advice; market data can be stale/unverified; options carry significant risk).

## Official-logo enforcement (mandatory on EVERY daily HTML)
- The actual uploaded **FazDane Analytics artwork** is required in the top header of **every** dated report, not merely the word `FAZDANE` styled as text. The canonical source is `assets/fazdane-logo.svg`. Do not replace the official artwork with a newly generated illustration, a lookalike, or a text-only wordmark.
- A locally downloadable HTML briefing must remain self-contained: embed the official logo image as a `data:image/svg+xml;base64,...` URI (or embed the artwork equivalently). GitHub Pages reports may use the same self-contained approach. Referencing `../assets/fazdane-logo.svg` is acceptable only for website-specific reports where the asset is deployed with the page.
- Put the official logo at the **top of the daily dashboard**, before market-regime cards, with useful alt text (`FazDane Analytics logo`), responsive width, preserved aspect ratio and a readable white backing.
- In the report generator (`scripts/briefing.py` / `scripts/daily.py`), do not substitute text-only brand markup when images are missing. Instead, fail with an actionable message when the logo source cannot be embedded.
- The GitHub Pages workflow (`.github/workflows/pages.yml`) must inspect the newest daily HTML and **fail deployment** if a FazDane logo `<img>` element with a valid data URI or deployed asset reference is absent, or if the financial disclaimer is missing. Merely finding the string `FazDane` in a heading or title is **not** a sufficient branding check.
- For manual ChatGPT-created releases, check the actual HTML file before committing, even if an older edition already had a logo. Verify the top header, link to the archive and disclaimer, then confirm GitHub Pages deployment and published-file verification.
- Historical reports can remain archived, but when republishing or revising a specific date ensure its actual logo artwork is present. The latest report must never show text-only branding.

## HTML-only public hosting policy
- The **public GitHub repository and GitHub Pages site publish HTML only**, not dashboard PNG files. Do not commit PNGs under `reports/`, do not add PNG archive links, and do not deploy or verify PNGs on the public website.
- A separate **ChatGPT daily briefing** may still generate and deliver a verified downloadable local PNG snapshot when requested. That PNG must not be copied into GitHub.
- Maintain `.github/workflows/pages.yml` so it only stages `reports/*.html`; do not restore `.github/workflows/report-snapshot.yml`.
- After publication, verify both the public homepage and newest HTML report against repository contents, using the workflow's deployed-file byte comparison. Never report success before verification.
- Preserve the existing GitHub Actions schedule, Weekly Breadth and Research archive sections unless the user explicitly asks to change them.

## Publication checklist
- [ ] Dated market facts, verification status and sources distinguished from tactical interpretations.
- [ ] Score, sector rotation, MAG7, VIX/IV/put-call/gamma (mark N/V where missing), five trade watches, 1–20-session outlook, events, sourced headlines.
- [ ] **Official FazDane Analytics artwork is visibly rendered as a top-header image** (not text-only), with mobile sizing, archive-home link and financial disclaimer in published HTML.
- [ ] Generator and deployment both reject any newest HTML missing the official logo image or disclaimer.
- [ ] Index latest report and archive contain HTML links only; no PNG files or links in GitHub Pages.
- [ ] GitHub Actions succeeds; public homepage and latest HTML byte checks pass.
