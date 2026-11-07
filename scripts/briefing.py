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


def render(today, cards, logo, disclaimer):
    reference = Path("reports/2026-11-01.html").read_text(encoding="utf-8")
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

    def table(rows):
        if not rows:
            return '<p class="foot">Unverified · recent closing prices unavailable.</p>'
        return "".join(f'<div class="sectorrow"><b>{symbol}</b><small>{day}</small><strong class="{ "positive" if change >= 0 else "negative" }">{change:+.2f}%</strong></div>' for change, symbol, day in rows)

    tape = moves(symbols[:3], 1)
    week = moves(MAG, 5)
    leaders = sorted(week, key=lambda item: abs(item[0]), reverse=True)[:5]
    headline = f"{tape[0][1]} leads tracked ETFs at {tape[0][0]:+.2f}%" if tape else "Latest market observations"
    drawdowns = []
    for _, symbol, day in tape:
        bars = prices[symbol]
        drawdowns.append((100 * (bars[-1][1] / max(price for _, price in bars) - 1), symbol, day))
    sections = [
        panel("Market tape", table(tape) + cards[0]),
        panel("Drawdown vs tracked highs", "<small>From highest available close in one-month window</small>" + table(drawdowns)),
        panel("Sector rotation", "<small>Five-session ETF price returns</small>" + table(moves(SECTORS, 5))),
        panel("Magnificent 7", "<small>Latest session</small>" + table(moves(MAG, 1)) + "<details><summary>5D returns</summary>" + table(week) + "</details>"),
        panel("Options &amp; volatility", cards[1] + "<p>Put/call, skew, gamma and positioning · unverified</p>"),
        panel("Top 5 trade watchlist", "<small>Largest absolute five-session moves among tracked mega-caps</small>" + table(leaders)),
        panel("Next 1–20 trading days", "<details open><summary>1–3 sessions</summary>Monitor VIX and daily breadth.</details><details><summary>4–10 sessions</summary>Review sector leadership against five-session returns.</details><details><summary>11–20 sessions</summary>Reassess drawdowns and the Treasury curve.</details>"),
        panel("Macro &amp; earnings calendar", "".join(cards[2:]) + "<p>Upcoming releases and earnings dates · unverified</p>"),
        panel("5 market-moving headlines", "<small>Latest Federal Reserve releases · past 14 days</small>" + releases(today)),
        panel("Source &amp; method ledger", '<p>ETF and stock returns use unadjusted Yahoo Finance daily closes before the report date. Dates identify the end of each observation window. Missing instruments are excluded from rankings.</p>' + " · ".join(f'<a href="https://finance.yahoo.com/quote/{symbol}/history/">{symbol}</a>' for symbol in symbols) + "<p>Index and yield tiles link to their dated FRED series. The watchlist ranks historical moves.</p>"),
    ]
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FazDane Daily Market Intelligence | {today}</title>{styles}<style>a,summary{{color:var(--teal)}}summary{{cursor:pointer}}.panel article h2{{font-size:12px}}.dial{{background:#26374c}}.dial strong{{font-size:24px}}</style></head>
<body><div class="fd-brandbar"><img alt="FazDane Analytics" src="data:image/svg+xml;base64,{logo}"><a href="../index.html">← Dashboard archive</a></div><main class="shell"><header class="brand"><div><div class="mark">FAZ<b>DANE</b></div><div class="eyebrow">Daily market intelligence</div></div><div class="date">{today:%a · %b %d, %Y}<br>Chicago edition</div></header>
<div class="hero"><div class="dial"><div class="inner"><strong>{len(tape)}/3</strong><small>ETF CLOSES</small></div></div><div><span class="pill">LAST CLOSE</span><h1>{headline}</h1></div></div>{''.join(sections)}{disclaimer}</main></body></html>'''
