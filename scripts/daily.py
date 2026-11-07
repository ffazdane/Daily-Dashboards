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
if report.exists():
    if not snapshot.exists():
        raise SystemExit("Existing report has no PNG; preserving original")
    raise SystemExit(0)

index = Path("index.html")
archive = index.read_text(encoding="utf-8")
disclaimer = re.search(r'<section class="card" aria-labelledby="disclaimer-heading">.*?</section>', archive, re.S).group()
logo = base64.b64encode(Path("assets/fazdane-logo.svg").read_bytes()).decode()
cards = []
verified = 0
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
        status = "Source-verified" if fresh else "Stale observation"
        history = "".join(f"<li>{day} · {observations[day]:,.2f}</li>" for day in stamps[:7])
        body = f"<strong>{observations[stamp]:,.2f} {unit}</strong><p>{status} · {stamp}</p><details><summary>Recent observations</summary><ul>{history}</ul></details>"
    cards.append(f'<article><h2>{label}</h2>{body}<p><a href="{source}">FRED · {symbol}</a></p></article>')
if not verified:
    raise SystemExit("No recent dated observations; retaining previous archive")

report.write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FazDane daily markets · {today}</title>
<style>*{{box-sizing:border-box}}body{{background:#101f30;color:#edf4f7;font:16px/1.45 system-ui;margin:auto;max-width:1080px;padding:28px}}header{{display:flex;justify-content:space-between;align-items:center}}img{{width:190px;background:white;border-radius:8px}}main{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}}article,.card{{padding:16px;background:#203347;border-radius:10px}}h2{{font-size:18px;margin:0 0 8px}}strong{{font-size:1.25em}}a,summary{{color:#76e3d3}}summary{{cursor:pointer}}.card{{font-size:13px}}@media(max-width:600px){{main{{grid-template-columns:1fr}}}}</style>
<header><img alt="FazDane Analytics" src="data:image/svg+xml;base64,{logo}"><a href="../index.html">Daily archive</a></header>
<h1>Market observations · {today}</h1><main>{''.join(cards)}</main><p>Source-verified values match dated FRED records. Options positioning, gamma and tactical signals are unverified and omitted.</p>{disclaimer}</html>''', encoding="utf-8")
subprocess.run(["google-chrome", "--headless", "--no-sandbox", "--disable-dev-shm-usage", "--hide-scrollbars", "--window-size=1100,1100", f"--screenshot={snapshot.resolve()}", report.resolve().as_uri()], check=True)
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
index.write_text(archive.replace(marker, marker + row), encoding="utf-8")
