from briefing import render

import base64
import csv
import math
import re
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

today = datetime.now(ZoneInfo("America/Chicago")).date()
report = Path(f"reports/FazDane_Daily_Market_Dashboard_{today}.html")
if report.exists():
    raise SystemExit(0)

index = Path("index.html")
archive = index.read_text(encoding="utf-8")
disclaimer = re.search(r'<section class="card" aria-labelledby="disclaimer-heading">.*?</section>', archive, re.S).group()
logo = base64.b64encode(Path("assets/fazdane-logo.svg").read_bytes()).decode()
cards = []
verified = 0
vix = None
for symbol, label, unit in [
    ("NASDAQCOM", "Nasdaq Composite", "points"),
    ("VIXCLS", "Cboe volatility index", "points"),
    ("DGS2", "2-year Treasury", "%"),
    ("DGS10", "10-year Treasury", "%"),
]:
    source = f"https://fred.stlouisfed.org/series/{symbol}"
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={symbol}&cosd={today - timedelta(days=21)}&coed={today}"
    result = subprocess.run(["curl", "-fsSL", "--retry", "2", "--max-time", "25", url], capture_output=True, text=True)
    observations = {}
    for row in csv.DictReader(result.stdout.splitlines() if result.returncode == 0 else []):
        try:
            stamp = date.fromisoformat(row["observation_date"])
            value = float(row[symbol])
            if stamp <= today and math.isfinite(value):
                observations[stamp] = value
        except (KeyError, ValueError, TypeError):
            continue
    stamps = sorted(observations, reverse=True)
    body = "<strong>Unavailable</strong><p>Unverified • no dated observation</p>"
    if stamps:
        stamp = stamps[0]
        fresh = (today - stamp).days <= 7
        verified += int(fresh)
        if symbol == 'VIXCLS' and observations[stamp] > 0:
            vix = (stamp, observations[stamp])
        status = "Source-verified" if fresh else "Stale observation"
        history = "".join(f"<li>{day} · {observations[day]:,.2f}</li>" for day in stamps[:7])
        body = f"<strong>{observations[stamp]:,.2f} {unit}</strong><p>{status} · {stamp}</p><details><summary>Recent observations</summary><ul>{history}</ul></details>"
    cards.append(f'<article><h2>{label}</h2>{body}<p><a href="{source}">FRED · {symbol}</a></p></article>')
if not verified:
    raise SystemExit("No recent dated observations; retaining previous archive")

html = render(today, cards, logo, disclaimer, vix)
report.write_text(html, encoding="utf-8")
display_date = f"{today:%A, %B} {today.day}, {today.year}"
row = f'<div class="row"><div><div class="date">{display_date}</div><small>{today}</small></div><div><a class="link" href="{report.as_posix()}">HTML ↗</a></div></div>'
marker = '<div id="archive">'
if archive.count(marker) != 1:
    raise SystemExit("Archive template changed")
latest = f'<small>LATEST AVAILABLE DASHBOARD</small><h1>{display_date}</h1><p class="lead">Dated equity, volatility and Treasury observations.</p><a class="button" href="{report.as_posix()}">Open interactive dashboard</a></section>'
archive, count = re.subn(r'<small>LATEST AVAILABLE DASHBOARD</small>.*?</section>', latest, archive, flags=re.S)
if count != 1:
    raise SystemExit("Latest report section missing")
index.write_text(archive.replace(marker, marker + row), encoding="utf-8")
