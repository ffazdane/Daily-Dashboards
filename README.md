# FazDane Daily Market Dashboards

Public archive of FazDane daily market intelligence dashboards.

## Reports

Interactive HTML reports: `reports/FazDane_Daily_Market_Dashboard_YYYY-MM-DD.html` (older links use `reports/YYYY-MM-DD.html`). Historic reports from 2026-11-01 through 2026-11-06 are currently published. Reports are historical artifacts and financial data has not been independently revalidated for public publication.

## Weekly breadth reports

Weekly FazDane market-breadth analyses live in `weekly-breadth/` (`FazDane_Weekly_Breadth_YYYY-MM-DD.html`) and are listed in the **Weekly Breadth** section of the homepage, above Research. They use `../assets/fazdane-logo.svg`, link back to the archive and keep the disclaimer. The Pages workflow copies this folder into the published site; `scripts/daily.py` does not modify that section.

## GitHub Pages setup

Go to **Settings → Pages** of this repository, choose **GitHub Actions** as the build and deployment source. The included `.github/workflows/pages.yml` deploys the repository on pushes to `main` and can be run manually. After enabling Pages, verify the website address shown in GitHub (typically https://ffazdane.github.io/Daily-Dashboards/). Do **not** describe it as live before checking.

## Daily dashboard process

GitHub Actions runs scripts/daily.py at 7 AM America/Chicago, on main pushes and on manual dispatch. The runner reads dated FRED CSV observations, renders the self-contained HTML report, commits it with the archive index, deploys Pages, and checks the public bytes. Find deployed links in the Actions run summary. Missing series are labeled; if every observation is missing or over seven days old the job fails before committing. Finished dates are immutable on retries.

Select GitHub Actions as the Pages source and allow the workflow token to push archives to main. No custom secrets or data API keys are required. ChatGPT runs independently.

## Accuracy / responsibility

Each archive entry remains unchanged as originally generated. Some market data may be incomplete or unverified. This is research content, not investment advice.

## FazDane branding and disclaimer

Use `assets/fazdane-logo.svg` for the public archive homepage and `../assets/fazdane-logo.svg` in dated reports. The logo asset is a compressed rendition of the uploaded FazDane Analytics mark, embedded for self-contained image loading on GitHub Pages. Retain the visible financial/research disclaimer in every dated report and on the homepage. New reports should include the same top brand bar, link back to the archive and disclaimer, while keeping tactical interpretations separate from verified market facts.
