---
name: fazdane-daily-dashboard
description: Generate or maintain the FazDane daily market HTML in the November 1 weekend or November 2 weekday format.
---

In ffazdane/Daily-Dashboards, select by Chicago publication date. Saturday and Sunday use reports/2026-11-01.html (narrow teal stack, dial, close tiles and horizontal return charts). Monday through Friday use reports/2026-11-02.html (wider blue layout, regime gauge, KPI cards, numbered sections and paired rotation/MAG7 panels). Keep the last verified close dated separately, including on Mondays and holidays. Retain interactive daily/5D and horizon tabs. Use scripts/briefing.py for layout and scripts/daily.py for dated retrieval, rendering and archive insertion. Run from the repository root on Linux with Python 3 and curl.

Keep the brand bar, mobile shell, summary dial, market tape, drawdowns, sector rotation, Magnificent 7 daily and five-session returns, volatility, watchlist, three planning horizons, calendar, headlines, source ledger and full disclaimer. Always lead with the numeric Market Regime Score on a 0–100 dial, posture, and dated model interpretation. Use regime() in scripts/briefing.py, which equally weights five-session SPY momentum, aligned 11-sector breadth and dated VIX. Print the method and risk thresholds in the ledger. Use N/V when a required input is missing. Reject a daily render that substitutes ETF counts for the regime score. Verify both the weekend REGIME / 100 and weekday / 100 REGIME hero labels when changing templates. Label mechanical rankings and planning prompts. Only populate claims, events and headlines with attributable dated evidence. Show unavailable coverage explicitly. Never roll historical prices, regime scores or headlines into a new edition.

Use the Chicago publication date and retain each series' observation date. Publish only self-contained HTML using reports/FazDane_Daily_Market_Dashboard_YYYY-MM-DD.html. Preserve archived reports on reruns. For authorized publication, use the existing Pages workflow and check its byte comparison of the public index and HTML.

On the archive homepage, use the full English weekday and date for both the latest dashboard heading and the bold archive row label (for example, Saturday, November 7, 2026). Keep the ISO date beneath the row label and in the report filename. Omit the “About the reports” section and retain the financial disclaimer.

Share clean dashboard URLs. When an incoming homepage URL includes `utm_source=chatgpt.com`, remove that parameter from the address bar while preserving other query parameters and the fragment.
