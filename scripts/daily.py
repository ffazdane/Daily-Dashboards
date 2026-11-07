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
report = Path(f"reports/{today}.html")
snapshot = report.with_suffix(".png")
upgrade = snapshot.exists() and report.exists() and 'content="regime-v3"' not in report.read_text(encoding="utf-8")
if report.exists() and not upgrade:
    if not snapshot.exists():
        raise SystemExit("Existing report has no PNG; preserving original")
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
width = 500 if today.weekday() >= 5 else 960
chrome = ["google-chrome", "--headless", "--no-sandbox", "--disable-dev-shm-usage", "--hide-scrollbars"]
probe = report.with_suffix(".probe.html")
probe.write_text(html.replace("</body>", '<script>document.body.dataset.height = document.documentElement.scrollHeight</script></body>'), encoding="utf-8")
try:
    dom = subprocess.check_output(chrome + [f"--window-size={width},800", "--dump-dom", probe.resolve().as_uri()], text=True)
finally:
    probe.unlink()
height = int(re.search(r'data-height="(\d+)"', dom)[1]) + 10
subprocess.run(chrome + [f"--window-size={width},{height}", f"--screenshot={snapshot.resolve()}", report.resolve().as_uri()], check=True)
if snapshot.read_bytes()[:8] != bytes.fromhex("89504e470d0a1a0a"):
    raise SystemExit("PNG render failed")
row = f'<div class="row"><div class="date">{today}</div><div><a class="link" href="{report.as_posix()}">HTML ↗</a> · <a class="link" href="{snapshot.as_posix()}">PNG ↗</a></div></div>'
marker = '<div id="archive">'
if archive.count(marker) != 1:
    raise SystemExit("Archive template changed")
latest = f'<small>LATEST AVAILABLE DASHBOARD</small><h1>{today}</h1><p class="lead">Dated equity, volatility and Treasury observations.</p><a class="button" href="{report.as_posix()}">Open interactive dashboard</a></section>'
archive, count = re.subn(r'<small>LATEST AVAILABLE DASHBOARD</small>.*?</section>', latest, archive, flags=re.S)
if count != 1:
    raise SystemExit("Latest report section missing")
index.write_text(archive if upgrade else archive.replace(marker, marker + row), encoding="utf-8")
