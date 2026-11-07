# FazDane Daily Market Dashboards

Public archive of FazDane daily market intelligence dashboards.

## Reports

Interactive HTML reports: `reports/YYYY-MM-DD.html`. Historic reports from 2026-11-01 through 2026-11-06 are currently published. Reports are historical artifacts and financial data has not been independently revalidated for public publication.

## GitHub Pages setup

Go to **Settings → Pages** of this repository, choose **GitHub Actions** as the build and deployment source. The included `.github/workflows/pages.yml` deploys the repository on pushes to `main` and can be run manually. After enabling Pages, verify the website address shown in GitHub (typically https://ffazdane.github.io/Daily-Dashboards/). Do **not** describe it as live before checking.

## Daily dashboard process

Your 7AM ChatGPT automation creates downloadable HTML and PNG artifacts in a ChatGPT chat. It does **not** automatically store them in GitHub. A separate authenticated uploader/integration must transfer the daily files into `reports/`; then this site deploys on push. Do not claim automatic publication or daily posting until an uploader has been built and tested.

To add a report, commit `reports/YYYY-MM-DD.html` (and optionally `reports/YYYY-MM-DD.png`) and update `index.html` with the new day. The Pages workflow will publish the resulting commit.

## Accuracy / responsibility

Each archive entry remains unchanged as originally generated. Some market data may be incomplete or unverified. This is research content, not investment advice.
