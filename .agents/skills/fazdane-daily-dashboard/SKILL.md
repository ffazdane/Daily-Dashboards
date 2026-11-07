---
name: fazdane-daily-dashboard
description: Generate or maintain the FazDane daily market HTML and PNG in the November 1 weekend or November 2 weekday format.
---

In ffazdane/Daily-Dashboards, select by Chicago publication date. Saturday and Sunday use reports/2026-11-01.html (narrow teal stack, dial, close tiles and horizontal return charts). Monday through Friday use reports/2026-11-02.html (wider blue layout, breadth gauge, KPI cards, numbered sections and paired rotation/MAG7 panels). Keep the last verified close dated separately, including on Mondays and holidays. Retain interactive daily/5D and horizon tabs and render each PNG at its edition width. Use scripts/briefing.py for layout and scripts/daily.py for dated retrieval, rendering and archive insertion. Run from the repository root on Linux with Python 3, curl and Google Chrome.

Keep the brand bar, mobile shell, summary dial, market tape, drawdowns, sector rotation, Magnificent 7 daily and five-session returns, volatility, watchlist, three planning horizons, calendar, headlines, source ledger and full disclaimer. Name the dial's actual metric. Label mechanical rankings and planning prompts. Only populate claims, events and headlines with attributable dated evidence. Show unavailable coverage explicitly. Never roll historical prices, regime scores or headlines into a new edition.

Use the Chicago publication date and retain each series' observation date. Render self-contained HTML and a full-height PNG from the same default view. Preserve archived pairs on reruns. For authorized publication, use the existing Pages workflow and check its byte comparison of the public index, HTML and PNG.
