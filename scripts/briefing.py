from email.utils import parsedate_to_datetime
from html import escape
from xml.etree import ElementTree

import json
import math
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SECTORS = "XLB XLC XLE XLF XLI XLK XLP XLRE XLU XLV XLY".split()
MAG = "NVDA MSFT META AMZN GOOGL AAPL TSLA".split()


def quote(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1mo&interval=1d"
    try:
        data = subprocess.check_output(["curl", "-fsSL", "-A", "Mozilla/5.0", "--max-time", "15", url])
        chart = json.loads(data)["chart"]["result"][0]
        bars = []
        for timestamp, price in zip(chart["timestamp"], chart["indicators"]["quote"][0]["close"]):
            day = datetime.fromtimestamp(timestamp, ZoneInfo("America/New_York")).date()
            if price and math.isfinite(price) and price > 0:
                bars.append((day, price))
        return bars
    except (subprocess.SubprocessError, ValueError, KeyError, TypeError, IndexError):
        return []


def panel(title, body):
    return f'<section class="panel"><div class="sec"><h2>{title}</h2></div>{body}</section>'


def releases(today):
    url = "https://www.federalreserve.gov/feeds/press_all.xml"
    items = []
    try:
        xml = subprocess.check_output(["curl", "-fsSL", "--max-time", "20", url])
        for item in ElementTree.fromstring(xml).findall(".//item"):
            day = parsedate_to_datetime(item.findtext("pubDate")).date()
            link = item.findtext("link", "")
            if 0 <= (today - day).days <= 14 and link.startswith("https://www.federalreserve.gov/"):
                items.append(f'<p><small>{day}</small><br><a href="{escape(link, quote=True)}">{escape(item.findtext("title", ""))}</a></p>')
    except (subprocess.SubprocessError, ElementTree.ParseError, TypeError, ValueError):
        pass
    return "".join(items[:5]) or "<p>Unverified · no recent Federal Reserve releases available.</p>"


def regime(today, momentum, sectors, vix):
    spy = next((row for row in momentum if row[1] == "SPY"), None)
    aligned = [row for row in sectors if spy and row[2] == spy[2]]
    if not spy or len(aligned) != len(SECTORS) or not vix or not 0 <= (today - vix[0]).days <= 7:
        return None, "UNVERIFIED", "Insufficient dated SPY, sector or VIX observations.", "muted"
    change, _, close_day = spy
    rising = sum(row[0] > 0 for row in aligned)
    trend = min(100, max(0, 50 + 10 * change))
    breadth = 100 * rising / len(aligned)
    calm = min(100, max(0, 100 * (35 - vix[1]) / 23))
    score = round((trend + breadth + calm) / 3)
    label, color = ("RISK-OFF · DEFENSIVE", "red") if score < 40 else (
        ("RISK-ON · CONSTRUCTIVE", "green") if score >= 60 else ("MIXED · NEUTRAL", "amber"))
    reading = (f"SPY {change:+.2f}% over five sessions; {rising} of 11 sectors advanced through {close_day}. "
               f"VIX closed at {vix[1]:.2f} on {vix[0]}.")
    return score, label, reading, color


def calendar(today):
    url = "https://www.bls.gov/schedule/news_release/bls.ics"
    try:
        feed = subprocess.check_output(["curl", "-fsSL", "--max-time", "15", url], text=True)
    except (subprocess.SubprocessError, UnicodeError):
        feed = ""
    events = []
    for event in re.split(r"BEGIN:VEVENT", re.sub(r"\n[ \t]", "", feed))[1:]:
        start = re.search(r"^DTSTART[^:]*:(\d{8})", event, re.M)
        title = re.search(r"^SUMMARY:(.+)", event, re.M)
        if start and title:
            day = datetime.strptime(start[1], "%Y%m%d").date()
            if 0 <= (day - today).days <= 14:
                events.append((day, escape(title[1].strip())))
    rows = "".join(f"<p><small>{day}</small> · {title}</p>" for day, title in sorted(set(events))[:6])
    return (rows or "<p>No upcoming BLS release verified in the next 14 days.</p>") + f'<a href="{url}">BLS release calendar</a><p>Earnings dates · unverified</p>'


def render(today, cards, logo, disclaimer, vix=None):
    weekend = today.weekday() >= 5
    edition = "Weekend" if weekend else "Weekday"
    template = "2026-11-01" if weekend else "2026-11-02"
    reference = Path(f"reports/{template}.html").read_text(encoding="utf-8")
    styles = "".join(re.findall(r"<style[^>]*>.*?</style>", reference, re.S))
    symbols = ["SPY", "QQQ", "IWM"] + SECTORS + MAG
    with ThreadPoolExecutor(max_workers=4) as pool:
        prices = {symbol: [bar for bar in bars if bar[0] < today]
                  for symbol, bars in zip(symbols, pool.map(quote, symbols))}
    def moves(group, sessions):
        rows = []
        for symbol in group:
            bars = prices[symbol]
            if len(bars) > sessions and (today - bars[-1][0]).days <= 7:
                day, close = bars[-1]
                change = 100 * (close / bars[-1-sessions][1] - 1)
                rows.append((change, symbol, day))
        return sorted(rows, reverse=True)

    def chart(rows, kind="sector"):
        if not rows:
            return '<p>Unverified · recent closes unavailable.</p>'
        peak = max(abs(value) for value, _, _ in rows) or 1
        result = []
        for value, symbol, day in rows:
            direction = "up" if value >= 0 else "down"
            tone = "positive" if value >= 0 else "negative"
            width = 100 * abs(value) / peak
            bar = f'<div class="track"><div class="fill {direction}" style="width:{width:.1f}%"></div></div>'
            if weekend:
                track = {"sector": "sectorbar", "draw": "drawbar", "mag": "magtrack"}[kind]
                bar = f'<div class="{track}"><i class="{direction}" style="width:{width:.1f}%;background:var(--{"green" if value >= 0 else "red"})"></i></div>'
            if kind == "mag" and not weekend:
                bar = f'<span class="price">${prices[symbol][-1][1]:,.2f}</span>'
            css = {"sector": "sectorrow", "draw": "drawrow", "mag": "magrow"}[kind] if weekend else ("magrow" if kind == "mag" else "rowbar")
            result.append(f'<div class="{css}"><b>{symbol}<small class="obs">{day}</small></b>{bar}<strong class="right {tone}">{value:+.2f}%</strong></div>')
        return "".join(result)

    def tabs(labels, bodies):
        buttons = "".join(f'<button type="button" aria-pressed="{str(index == 0).lower()}" class="{ "active" if index == 0 else "" }" onclick="choose(this,{index})">{label}</button>' for index, label in enumerate(labels))
        panes = "".join(f'<div data-pane {"" if index == 0 else "hidden"}>{body}</div>' for index, body in enumerate(bodies))
        return f'<div><div class="buttons tabs">{buttons}</div>{panes}</div>'

    tape = moves(symbols[:3], 1)
    week = moves(MAG, 5)
    leaders = sorted(moves(SECTORS + MAG + symbols[:3], 5), key=lambda item: abs(item[0]), reverse=True)[:5]
    headline = f"{tape[0][1]} leads tracked ETFs at {tape[0][0]:+.2f}%" if tape else "Latest market observations"
    drawdowns = []
    for _, symbol, day in tape:
        bars = prices[symbol]
        drawdowns.append((100 * (bars[-1][1] / max(price for _, price in bars) - 1), symbol, day))
    tiles = []
    for value, symbol, day in tape:
        tone = "positive" if value >= 0 else "negative"
        tiles.append(f'<div class="{"tile" if weekend else "kpi"}"><span class="ticker">{symbol}</span><strong class="price">${prices[symbol][-1][1]:,.2f}</strong><span class="{tone}">{value:+.2f}%</span><small class="obs">{day}</small></div>')
    tape_html = f'<div class="{"tiles" if weekend else "kpis"}">{"".join(tiles)}</div>' + cards[0]
    rotations = moves(SECTORS, 5)
    score, posture, reading, color = regime(today, moves(["SPY"], 5), rotations, vix)
    displayed = "N/V" if score is None else str(score)
    option_class = "opt" if weekend else "option unverified"
    metrics = ["Total put/call", "SPX put/call", "Equity put/call", "Ticker IV / IV rank", "Dealer gamma / GEX"]
    missing = "".join(f'<div class="{option_class}"><small>{metric}</small><strong>N/V</strong></div>' for metric in metrics)
    options = cards[1] + f'<div class="{"optgrid" if weekend else "options"}">{missing}</div><small>N/V · dated reading unavailable</small>'
    if not weekend:
        tape_html += '<div class="futures"><div class="future">Premarket futures · unverified</div></div>'
    sector = chart(rotations)
    scorecard = tabs(["Last close", "5D"], [chart(moves(MAG, 1), "mag"), chart(week, "mag")])
    watch = []
    for rank, (move, ticker, stamp) in enumerate(leaders, 1):
        bias = "Momentum continuation" if move > 0 else "Downside pressure"
        trigger = "Watch for a higher low; reassess if support breaks." if move > 0 else "Watch for a failed rebound; reassess if resistance is reclaimed."
        watch.append(f'<div class="{"opp" if weekend else "trade"}"><b>{rank:02}</b><div><strong>{ticker}</strong> · {bias}<p>{trigger}</p><small>Five sessions through {stamp}</small></div><strong>{move:+.2f}%</strong></div>')
    horizons = tabs(["1–3 days", "4–10 days", "11–20 days"], [
        f"Model posture · {posture}. Monitor whether the latest SPY move persists.", f"Recheck five-session leadership in {rotations[0][1] if rotations else 'the sector universe'}.", "Review closing drawdowns and Treasury yields before extending the time horizon."])
    sections = [
        ("Market tape", tape_html),
        ("Drawdown vs tracked highs", "<small>Highest close in the one-month window</small>" + chart(drawdowns, "draw")),
        ("Sector rotation", "<small>Five-session ETF price returns</small>" + sector),
        ("Magnificent 7" if weekend else "MAG7 scorecard", scorecard),
        ("Options &amp; volatility", options),
        ("Top 5 trade watchlist", "<small>Conditional setups ranked by absolute five-session return</small>" + ("".join(watch) or "<p>Unverified</p>")),
        ("Next 1–20 trading days", horizons),
        ("Macro &amp; earnings calendar", "".join(cards[2:]) + calendar(today)),
        ("5 market-moving headlines", "<small>Latest dated Federal Reserve releases</small>" + releases(today)),
        ("Source &amp; method ledger", "<p>Market regime model · equal-weight average of three 0–100 components, rounded to the nearest integer. Trend = 50 + 10 × SPY five-session percentage return. Breadth = percent of the 11 sector ETFs advancing over five sessions. Volatility = 100 × (35 − VIX) / 23. Clamp each component to 0–100. Below 40 is defensive, 40–59 neutral, and 60 or higher constructive. These are model readings, not probabilities.</p><p>Dated Yahoo Finance closing prices. Bar lengths are relative to the largest absolute move in each chart. Returns use unadjusted closes. Missing instruments are excluded.</p>" + " · ".join(f'<a href="https://finance.yahoo.com/quote/{symbol}/history/">{symbol}</a>' for symbol in symbols)),
    ]
    last = max((day.isoformat() for _, _, day in tape), default="unverified")
    gauge = f'background:conic-gradient(var(--{color}) {score or 0}%,#26374c 0)'
    if weekend:
        header = f'<header class="brand"><div class="mark">FAZ<b>DANE</b><div class="eyebrow">Weekend market intelligence</div></div><div class="date">{today:%a · %b %d, %Y}<br>Last close {last}</div></header>'
        hero = f'<div class="hero"><div class="dial" style="{gauge}"><div class="inner"><strong>{displayed}</strong><small>REGIME / 100</small></div></div><div><span class="pill">{posture}</span><h1>{headline}</h1><p>Model interpretation · {reading}</p></div></div>'
        body = "".join(panel(title, content) for title, content in sections)
    else:
        header = f'<header class="brand"><div><b>FAZDANE / MARKET</b><small>DAILY INTELLIGENCE · EQUITIES / OPTIONS / MACRO</small></div><div class="date">{today:%a · %b %d, %Y}<br>Chicago edition</div></header>'
        hero = f'<div class="intro"><div><h1>{headline}</h1><p>Last verified ETF close · {last}</p></div><span class="badge">{posture}</span></div><section class="hero"><div class="gauge" style="{gauge}"><div><strong>{displayed}</strong><small>/ 100 REGIME</small></div></div><div><h2>{posture.split(" · ")[-1].title()} posture</h2><p><b>Model interpretation:</b> {reading}</p></div></section>'
        blocks = [f'<div class="panel"><div class="secthead"><h3>{index:02} / {title}</h3></div>{content}</div>' for index, (title, content) in enumerate(sections, 1)]
        body = "".join(f'<section class="section">{block}</section>' for block in blocks[:2])
        body += '<section class="section twocol">' + "".join(blocks[2:4]) + '</section>'
        body += "".join(f'<section class="section">{block}</section>' for block in blocks[4:])
    script = """function choose(button,index){
      const group=button.parentElement;
      Array.from(group.children).forEach((tab,i)=>{
        tab.classList.toggle('active',i===index);
        tab.setAttribute('aria-pressed',String(i===index));
      });
      group.parentElement.querySelectorAll('[data-pane]').forEach((pane,i)=>pane.hidden=i!==index);
    }"""
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="fazdane-layout" content="regime-v3"><title>FazDane {edition} Edition | {today}</title>{styles}<style>.fd-brandbar{{box-sizing:border-box;max-width:900px;margin:0 auto;padding:9px 12px;display:flex;align-items:center;justify-content:space-between;gap:10px;background:#0b1729;border-bottom:1px solid #2b4057;color:#cde3f4;font:11px/1.35 system-ui,-apple-system,Segoe UI,sans-serif}}.fd-brandbar img{{display:block;width:clamp(150px,46vw,245px);height:auto;background:white;padding:2px;border-radius:6px}}.fd-brandbar a{{color:#60ddc6;text-decoration:none;font-weight:700;white-space:nowrap}}.obs{{display:block;font-size:9px;font-weight:400;color:var(--muted)}}.tile .price,.kpi .price{{display:block}}.panel article h2{{font-size:13px}}.buttons,.tabs{{margin:6px 0}}[hidden]{{display:none!important}}a{{color:#83d6eb}}</style></head><body><div class="fd-brandbar"><img alt="FazDane Analytics" src="data:image/svg+xml;base64,{logo}"><a href="../index.html">← Dashboard archive</a></div><main class="shell">{header}{hero}{body}{disclaimer}</main><script>{script}</script></body></html>'''
