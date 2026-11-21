---
name: fazdane-weekly-breadth
description: Build the FazDane weekly market-breadth HTML report from Fazal's ThinkorSwim watchlist and his StockCharts breadth chart set (captured through his PC's browser), then publish it. Use for "weekly breadth" or "analyze this week's market breadth".
---

# FazDane Weekly Breadth Report

Produces the weekly FazDane Analytics market-breadth report (one self-contained HTML page) every weekend from the ThinkorSwim watchlist, the 14-chart StockCharts/MacroMicro set and reachable web data, then publishes it to the chat, the Market Breadth Analyzer project and GitHub Pages.

Branding, CSS tokens, header/ticker row, levels grid, tables, summary cards and disclaimer follow the `fazdane-html-brand` skill. Load it before writing HTML.

## 1. Inputs

1. **ThinkorSwim watchlist screenshot** ("01-A-In Play"): $CPC, $CPCE, $CPCI, $DJT, $DXY, /VX front month, VIX, VIX1D, VVIX, VIXY, SKEW, /NQ, /ES, /RTY (current quarterly contracts), /BTC, /ETH. Read values from the image. `/YMU26` is an expired contract frozen at 51,612 / -195: ignore it and remind Fazal to switch to the current /YM contract.
2. **The 14-chart set (section 2)**, captured live every week (section 3). Never estimate a chart reading; if a chart cannot be captured, mark it "not provided this week" and leave its scorecard line unscored.
3. **Reachable web data** (WebFetch, in parallel):
   - https://www.thetrading.tools/market-breadth : % of all US stocks above 50-/200-day, composite breadth percentile (All US / S&P 500 / Nasdaq-100 / Nasdaq-listed), McClellan Oscillator, NH-NL 10-day, equal-weight vs cap-weight.
   - https://www.thetrading.tools/vix-term-structure : VIX/VIX3M ratio, contango/backwardation and day count, current/last inversion episode, post-inversion forward-return table. The newest close there is provisional; prefer the official VIX close.
   - https://www.thetrading.tools/vix-fear-index : VIX percentile, realized volatility, implied minus realized.
   - Weekly recaps: search "stock market week <dates> recap". Good sources: theclosingprint.net post-market & weekly summary (closes, weekly % for indexes, sectors best/worst, yields, gold, oil, BTC), acthreesixty.substack.com weekend roundup (day-by-day tape, Fed odds), alainguillot.com weekly recap, currentlogic.substack.com (sector table, participation), myweeklystock.substack.com.
   - Confirm any sensational single-source claim with a second source or leave it out and say so.
4. **Last week's report** from the project (`reports/FazDane_Weekly_Breadth_<last Friday>.html`, Projects project_read) to carry the 6-week trend table forward.

## 2. The chart set and how to read each one

| # | Chart | Link | Record | Reading rules |
|---|---|---|---|---|
| 1 | $NYSI daily | https://stockcharts.com/sc3/ui/?s=%24NYSI&p=d&b=5&g=0&id=p93366504188 | Value (ratio-adjusted), day change, MA(50), MA(200), RSI | Rising and above its MA = improving; below 0 = bearish regime; a turn up from below -500 is a classic intermediate low. |
| 2 | $NYSI weekly | https://stockcharts.com/sc3/ui/?s=%24NYSI&p=w&b=5&g=0&id=p99428479443 | Value, week change, MA(50), MA(200) | Weekly cross up through its MA = higher-conviction buy. |
| 3 | $VIX daily | https://stockcharts.com/sc3/ui/?s=%24VIX&p=d&b=5&g=0&id=p91860290185 | Close, high, Bollinger bands, RSI | Above 20 elevated; spike outside the upper band then a close back inside = fear climax. |
| 4 | $NYHL daily | https://stockcharts.com/sc3/ui/?s=%24NYHL&p=d&b=5&g=0&id=p77335934174 | Value, Bollinger bands | Negative and below the lower band = capitulation-level new lows. |
| 5 | $BPSPX P&F | https://stockcharts.com/freecharts/pnf/?c=$BPSPX,P&listNum= | Value, change, Status line (Bull/Bear Alert/Confirmed + date), column | Below 30 reversing up = bull alert; above 70 reversing down = bear alert. |
| 6 | $CPCE daily | https://stockcharts.com/sc3/ui/?s=%24CPCE&p=d&b=5&g=0&id=p50581674041 | Close, Bollinger bands | Contrarian: above ~0.90 fear, below ~0.60 complacency. This end-of-day value is official; the ThinkorSwim $CPCE can differ (Nov 20: 0.77 vs 1.02), so score the StockCharts value and note the gap. |
| 7 | $SPX P&F | https://stockcharts.com/freecharts/pnf/?chart=$SPX,PGTADANRBO[PA!B20][D][F1!3!!!2!20]&pref=G | "P&F Pattern" line + date, price objective, support/resistance line | Breakouts = buy, breakdowns = sell; note objective and whether price is above the bullish support line. |
| 8 | $NDX P&F | https://stockcharts.com/freecharts/pnf/?c=%24ndx,PGTADANRBO[PA!B20][D][F1!3!!!2!20] | Same as #7 | Compare with $SPX. |
| 9 | $BPNDX P&F | https://stockcharts.com/freecharts/pnf/?c=$BPNDX,P&listNum= | Same as #5 | Tech participation. |
| 10 | $BPNYA P&F | https://stockcharts.com/freecharts/pnf/?c=$BPNYA,P&listNum= | Same as #5 | Broad participation. |
| 11 | $NYA since 2000 | https://stockcharts.com/sc3/ui/?s=%24NYA&p=d&st=2000-01-03&en=%28today%29&id=p92492720539 | Close, change, Bollinger, RSI, secular trend | Long-term context. |
| 12 | Sector CandleGlance | https://stockcharts.com/freecharts/candleglance.html?[SECT] | Each sector's close, change, position vs 20/50-day SMA | Count sectors above their 50-day; name leaders/laggards. Scroll down past the controls before the screenshot; avoid ad overlays when cropping. |
| 13 | $NDX/$SPX/IWM/$VIX CandleGlance | https://stockcharts.com/freecharts/candleglance.html?$NDX,$SPX,IWM,$VIX\|B\|0 | Close/change and vs 20/50-day | Index trend and VIX direction. |
| 14 | CNN Fear & Greed | https://en.macromicro.me/charts/50108/cnn-fear-and-greed | "Latest Stats" value and prior value (scroll the right panel) | Under 25 extreme fear (contrarian bullish); over 75 extreme greed. |

## 3. Capturing the charts every week

StockCharts and MacroMicro cannot be read from the cloud workspace (robots-disallowed, JavaScript-rendered, client rejected). Capture them in the built-in browser on Fazal's linked PC (read the built-in-browser skill first; load all `Claude_Browser__` tools in one ToolSearch call):

1. For each link: `navigate`, then `computer` screenshot. For P&F charts, `zoom` the header region (about x 0-600, y 150-240) to read the Status/P&F Pattern line exactly; read values from the chart legends, not by eye from bars.
2. stockcharts.com and en.macromicro.me were allowed permanently on Nov 21, 2026. If a site is refused, call `request_access` with scope "site" and retry.
3. Screenshots land on disk at `/tmp/claude-tool-results/<session>/mcp-remote-devices-blob-*.jpg|png` (path printed with each image). Crop each to the chart area with PIL and save as JPEG quality ~82 in a working `img/` folder (about 50-100 KB each).
4. If the browser tools are absent or the desktop app is offline, ask Fazal to open the session in the Claude desktop app on his PC (or attach the 14 screenshots), and say which charts are missing rather than estimating.

## 4. Breadth Scorecard

Score +1 bullish, 0 neutral, -1 bearish from data actually captured:

1. $NYSI daily: rising and above MA (+1) / falling and below (-1)
2. $NYSI weekly: above its MA (+1) / below (-1)
3. $NYHL: positive and improving (+1) / negative and worsening (-1)
4. $BPSPX: X column or Bull Confirmed (+1) / O column or Bear Confirmed (-1)
5. $BPNYA: same
6. $BPNDX: same
7. $SPX P&F: last pattern a buy signal (+1) / sell signal (-1)
8. % above 50-day (thetrading.tools): above 50% (+1) / below 30% (-1)
9. VIX/VIX3M: contango and VIX < 20 (+1) / backwardation (-1; note it is often a contrarian setup)
10. $CPCE + Fear & Greed: extreme fear (+1 contrarian) / extreme greed (-1)

Total: +5 or more Healthy, +1 to +4 Improving, 0 to -3 Weak, -4 or less Washout. Show the table with how many of 10 were scored.

## 5. Report structure

File: `FazDane_Weekly_Breadth_YYYY-MM-DD.html` (Friday's date). Order:

1. Top bar, FazDane logo on a white badge, H1 with the week's thesis, sub-line, pulsing dateline "<Date> | Weekly Close", ticker row (SPX, Nasdaq, Dow, RUT weekly %, VIX, Fear & Greed, regime badge with scorecard), bottom bar pills.
2. Internals-at-a-glance grid (5 cells).
3. Weekly Summary (2 paragraphs, highlighted numbers).
4. **Chart-by-Chart Breadth Insights** (the core of the report; do not show charts as a bare gallery):
   - Intro line with the tally of bearish / neutral / bullish charts, then a 14-tile signal strip (`.sig-strip` / `.sig-tile.bear|neu|bull`, each tile linking to its card).
   - Four themed groups, each with a heading and a one-line question: **Breadth Momentum** ($NYSI daily, $NYSI weekly, $NYHL), **Participation** ($BPSPX, $BPNYA, $BPNDX), **Price Structure** ($SPX P&F, $NDX P&F, $NYA, index CandleGlance, sector CandleGlance), **Fear & Sentiment** ($VIX, $CPCE, Fear & Greed).
   - One `.ci-card` per chart: the cropped chart image on the left (P&F charts and the sector panel as `.wide` cards with the image on top), and on the right a numbered title with a Bullish/Neutral/Bearish pill, stat chips with the exact readings taken from the chart, a 2-4 sentence insight explaining what the chart says and why it matters, and a "Watch next" line naming the specific level or event that would change the read.
   - Note any data discrepancy inside the relevant card (e.g. ThinkorSwim vs StockCharts put/call).
   - Keep the card data in a small Python list (key, number, title, signal, wide, stats, insight, watch) and render it, so next week only the readings and text change.
5. Breadth Scorecard table + total.
6. Inline SVG charts in brand colors (labels with dark text stroke): 6-week % above 50/200-day lines with /NQ under each date; one chart for the week's story (volatility term structure, implied vs realized, or index/sector bars).
7. 6-week internals trend table (drop the oldest week, add the new one).
8. Breadth Read bullets, Volatility table, Macro & Drivers table, Scenarios table, 6 summary cards, sources line, disclaimer, footer.

Render with Playwright at 900px and 390px: no overlapping labels, no horizontal scroll on mobile, every image loads.

Images: in the standalone file embed them as base64 JPEG; in the GitHub copy reference `img/YYYY-MM-DD/<name>.jpg`.

## 6. Logo

Source: `C:\Users\ffazd\OneDrive\Desktop\Antigravity Projects\Logo\FazDane Logo.png`. Use the white rounded `.logo-badge` already embedded (base64) in earlier reports in /mnt/user-data/outputs; in the GitHub copy use `../assets/fazdane-logo.svg`.

## 7. Publishing

1. Save to `/mnt/user-data/outputs/` and send with SendUserFile (display: render).
2. Project: Projects project_write `reports/FazDane_Weekly_Breadth_YYYY-MM-DD.html` (copy under the working directory first; pass local_path).
3. GitHub Pages, repo `ffazdane/Daily-Dashboards`, branch `main`:
   - `git fetch origin main` and reset to it first; other jobs push to this repo daily.
   - Put the report in `weekly-breadth/` (logo swapped to `../assets/fazdane-logo.svg`, `<a class="back" href="../index.html">← FazDane archive</a>` after `<div class="wrap">`) and the images in `weekly-breadth/img/YYYY-MM-DD/`.
   - In `index.html` insert a row right after `<h2 id="weekly-breadth-heading">Weekly Breadth</h2>` (newest first): `<div class="row"><div><span class="pill">BREADTH</span><div class="date">HEADLINE</div><small>Week ending Month D, YYYY</small></div><div><a class="link" href="weekly-breadth/FILE">HTML ↗</a></div></div>`. Check for an existing row by the weekly file path, not by date (the daily archive also contains each date).
   - Serve the repo locally and confirm every image loads, then commit with the session's attribution lines, rebase, push to main.
   - Wait for the "Daily market dashboard" workflow run for that commit. If `deploy-pages` fails with "Fetching artifact metadata failed" / "No artifacts named pages-…", that is a GitHub-side error: re-run once (`gh run rerun <id> --failed`); if it fails again, tell Fazal the commit is in but the site has not redeployed, and that the next push or the daily job will publish it.

## 8. Reply to Fazal

Short: the thesis, 4-5 bullets (breadth, chart-set signals and scorecard, volatility, macro), the bias with confirmation/failure levels, any missing charts, data discrepancies or unverified claims, publishing status, and a Sources list of the web pages used.
