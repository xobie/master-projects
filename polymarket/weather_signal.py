#!/usr/bin/env python3
"""
Polymarket Weather Signal — NOAA Only
Pulls daily high temp forecasts for major US cities and outputs trade signals.
Run daily at 7am ET via cron.
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, date
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed

ET = ZoneInfo("America/New_York")

CITIES = [
    ("Albuquerque, NM",     35.0844,  -106.6504),
    ("Anchorage, AK",       61.2181,  -149.9003),
    ("Atlanta, GA",         33.7490,   -84.3880),
    ("Austin, TX",          30.2672,   -97.7431),
    ("Baltimore, MD",       39.2904,   -76.6122),
    ("Boston, MA",          42.3601,   -71.0589),
    ("Charlotte, NC",       35.2271,   -80.8431),
    ("Chicago, IL",         41.8781,   -87.6298),
    ("Cincinnati, OH",      39.1031,   -84.5120),
    ("Cleveland, OH",       41.4993,   -81.6944),
    ("Colorado Springs, CO",38.8339,  -104.8214),
    ("Columbus, OH",        39.9612,   -82.9988),
    ("Dallas, TX",          32.7767,   -96.7970),
    ("Denver, CO",          39.7392,  -104.9903),
    ("Detroit, MI",         42.3314,   -83.0458),
    ("El Paso, TX",         31.7619,  -106.4850),
    ("Fort Worth, TX",      32.7555,   -97.3308),
    ("Fresno, CA",          36.7378,  -119.7871),
    ("Honolulu, HI",        21.3069,  -157.8583),
    ("Houston, TX",         29.7604,   -95.3698),
    ("Indianapolis, IN",    39.7684,   -86.1581),
    ("Jacksonville, FL",    30.3322,   -81.6557),
    ("Kansas City, MO",     39.0997,   -94.5786),
    ("Las Vegas, NV",       36.1699,  -115.1398),
    ("Long Beach, CA",      33.7701,  -118.1937),
    ("Los Angeles, CA",     34.0522,  -118.2437),
    ("Louisville, KY",      38.2527,   -85.7585),
    ("Memphis, TN",         35.1495,   -90.0490),
    ("Mesa, AZ",            33.4152,  -111.8315),
    ("Miami, FL",           25.7617,   -80.1918),
    ("Milwaukee, WI",       43.0389,   -87.9065),
    ("Minneapolis, MN",     44.9778,   -93.2650),
    ("Nashville, TN",       36.1627,   -86.7816),
    ("New Orleans, LA",     29.9511,   -90.0715),
    ("New York, NY",        40.7128,   -74.0060),
    ("Oklahoma City, OK",   35.4676,   -97.5164),
    ("Omaha, NE",           41.2565,   -95.9345),
    ("Philadelphia, PA",    39.9526,   -75.1652),
    ("Phoenix, AZ",         33.4484,  -112.0740),
    ("Pittsburgh, PA",      40.4406,   -79.9959),
    ("Portland, OR",        45.5051,  -122.6750),
    ("Raleigh, NC",         35.7796,   -78.6382),
    ("Sacramento, CA",      38.5816,  -121.4944),
    ("Salt Lake City, UT",  40.7608,  -111.8910),
    ("San Antonio, TX",     29.4241,   -98.4936),
    ("San Diego, CA",       32.7157,  -117.1611),
    ("San Francisco, CA",   37.7749,  -122.4194),
    ("San Jose, CA",        37.3382,  -121.8863),
    ("Seattle, WA",         47.6062,  -122.3321),
    ("St. Louis, MO",       38.6270,   -90.1994),
    ("Tampa, FL",           27.9506,   -82.4572),
    ("Tucson, AZ",          32.2226,  -110.9747),
    ("Virginia Beach, VA",  36.8529,   -75.9780),
    ("Washington, DC",      38.9072,   -77.0369),
]

HEADERS = {"User-Agent": "PolymarketWeatherSignal/1.0 (xobie@users.noreply.github.com)"}

def noaa_fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None

def get_city_forecast(city_tuple):
    city, lat, lon = city_tuple
    # Step 1: points lookup
    data = noaa_fetch(f"https://api.weather.gov/points/{lat:.4f},{lon:.4f}")
    if not data:
        return city, None, None, None, "API error (points)"
    forecast_url = data.get("properties", {}).get("forecast")
    if not forecast_url:
        return city, None, None, None, "No forecast URL"
    # Step 2: forecast
    forecast = noaa_fetch(forecast_url)
    if not forecast:
        return city, None, None, None, "API error (forecast)"
    periods = forecast.get("properties", {}).get("periods", [])
    today = date.today()
    # Find today's daytime high
    for p in periods:
        if p.get("isDaytime") and str(today) in p.get("startTime", ""):
            temp = p.get("temperature")
            unit = p.get("temperatureUnit", "F")
            if unit == "C":
                temp = round(temp * 9/5 + 32)
            return city, temp, p.get("shortForecast", ""), p.get("name", ""), None
    # Fallback: first daytime period
    for p in periods:
        if p.get("isDaytime"):
            temp = p.get("temperature")
            unit = p.get("temperatureUnit", "F")
            if unit == "C":
                temp = round(temp * 9/5 + 32)
            return city, temp, p.get("shortForecast", ""), p.get("name", ""), None
    return city, None, None, None, "No daytime period found"

def confidence(short_forecast):
    if not short_forecast:
        return "⚪", "Unknown"
    f = short_forecast.lower()
    if any(w in f for w in ["sunny", "clear", "mostly sunny", "mostly clear"]):
        return "🟢", "HIGH"
    elif any(w in f for w in ["rain", "shower", "storm", "thunder", "snow", "fog", "blizzard", "freezing"]):
        return "🔴", "LOW"
    else:
        return "🟡", "MED"

def main():
    now = datetime.now(ET)
    today_str = now.strftime("%A %B %d, %Y")

    results = []
    errors = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(get_city_forecast, c): c for c in CITIES}
        for future in as_completed(futures):
            city, temp, short_forecast, period_name, err = future.result()
            if err or temp is None:
                errors.append((city, err or "No data"))
            else:
                emoji, level = confidence(short_forecast)
                results.append((city, temp, emoji, level, short_forecast))

    results.sort(key=lambda x: x[0])

    print(f"# 🌤 Polymarket Weather Signal")
    print(f"**Date:** {today_str}  ")
    print(f"**Generated:** {now.strftime('%I:%M %p ET')}  ")
    print(f"**Source:** NOAA api.weather.gov  ")
    print(f"**Cities:** {len(results)} fetched / {len(errors)} failed")
    print()
    print("---")
    print()
    print("## How to Use")
    print("1. Check Polymarket for daily high temp markets in these cities")
    print("2. Compare the NOAA forecast below against the market's implied line")
    print("3. **🟢 HIGH** = clear conditions, stable forecast = stronger edge")
    print("4. **🔴 LOW** = precip/storm expected = avoid or reduce position size")
    print("5. **🟡 MED** = some variability — use judgement")
    print()
    print("---")
    print()
    print("## 📊 Full City Table")
    print()
    print(f"| City | High | Confidence | Condition |")
    print(f"|------|------|------------|-----------|")
    for city, temp, emoji, level, condition in results:
        print(f"| {city} | {temp}°F | {emoji} {level} | {condition} |")

    print()
    print("---")
    print()

    high_conf = [(c, t, cond) for c, t, e, l, cond in results if e == "🟢"]
    low_conf  = [(c, t, cond) for c, t, e, l, cond in results if e == "🔴"]

    print("## 🟢 Best Edge Today (High Confidence)")
    if high_conf:
        for c, t, cond in high_conf:
            print(f"- **{c}** — {t}°F — {cond}")
    else:
        print("- None today")

    print()
    print("## 🔴 Avoid / Reduce Size (Low Confidence)")
    if low_conf:
        for c, t, cond in low_conf:
            print(f"- **{c}** — {t}°F — {cond}")
    else:
        print("- None today")

    if errors:
        print()
        print("## ⚠️ Failed to Fetch")
        for city, reason in errors:
            print(f"- {city}: {reason}")

    print()
    print("---")
    print(f"*Next signal: tomorrow 7:00 AM ET*")

if __name__ == "__main__":
    main()
