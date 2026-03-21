#!/usr/bin/env python3
"""
One-time script: pre-cache NOAA grid forecast URLs for all cities.
Run once. Saves to noaa_grid_cache.json.
Daily signal script uses cached URLs — much faster.
"""

import json, time, urllib.request, urllib.error

CITIES = [
    ("New York, NY",         40.7128, -74.0060),
    ("Los Angeles, CA",      34.0522, -118.2437),
    ("Chicago, IL",          41.8781, -87.6298),
    ("Houston, TX",          29.7604, -95.3698),
    ("Phoenix, AZ",          33.4484, -112.0740),
    ("Philadelphia, PA",     39.9526, -75.1652),
    ("San Antonio, TX",      29.4241, -98.4936),
    ("San Diego, CA",        32.7157, -117.1611),
    ("Dallas, TX",           32.7767, -96.7970),
    ("San Jose, CA",         37.3382, -121.8863),
    ("Austin, TX",           30.2672, -97.7431),
    ("Jacksonville, FL",     30.3322, -81.6557),
    ("Fort Worth, TX",       32.7555, -97.3308),
    ("Columbus, OH",         39.9612, -82.9988),
    ("Charlotte, NC",        35.2271, -80.8431),
    ("Indianapolis, IN",     39.7684, -86.1581),
    ("San Francisco, CA",    37.7749, -122.4194),
    ("Seattle, WA",          47.6062, -122.3321),
    ("Denver, CO",           39.7392, -104.9903),
    ("Nashville, TN",        36.1627, -86.7816),
    ("Oklahoma City, OK",    35.4676, -97.5164),
    ("El Paso, TX",          31.7619, -106.4850),
    ("Washington, DC",       38.9072, -77.0369),
    ("Las Vegas, NV",        36.1699, -115.1398),
    ("Louisville, KY",       38.2527, -85.7585),
    ("Memphis, TN",          35.1495, -90.0490),
    ("Portland, OR",         45.5051, -122.6750),
    ("Baltimore, MD",        39.2904, -76.6122),
    ("Milwaukee, WI",        43.0389, -87.9065),
    ("Albuquerque, NM",      35.0844, -106.6504),
    ("Tucson, AZ",           32.2226, -110.9747),
    ("Fresno, CA",           36.7378, -119.7871),
    ("Sacramento, CA",       38.5816, -121.4944),
    ("Kansas City, MO",      39.0997, -94.5786),
    ("Atlanta, GA",          33.7490, -84.3880),
    ("Omaha, NE",            41.2565, -95.9345),
    ("Colorado Springs, CO", 38.8339, -104.8214),
    ("Raleigh, NC",          35.7796, -78.6382),
    ("Minneapolis, MN",      44.9778, -93.2650),
    ("Tampa, FL",            27.9506, -82.4572),
    ("New Orleans, LA",      29.9511, -90.0715),
    ("Boston, MA",           42.3601, -71.0589),
    ("Miami, FL",            25.7617, -80.1918),
    ("Detroit, MI",          42.3314, -83.0458),
    ("Pittsburgh, PA",       40.4406, -79.9959),
    ("Cincinnati, OH",       39.1031, -84.5120),
    ("Cleveland, OH",        41.4993, -81.6944),
    ("St. Louis, MO",        38.6270, -90.1994),
    ("Salt Lake City, UT",   40.7608, -111.8910),
    ("Virginia Beach, VA",   36.8529, -75.9780),
]

HEADERS = {"User-Agent": "PolymarketSignalBot/1.0 (contact@clawbot.com.au)"}
cache = {}

for city, lat, lon in CITIES:
    print(f"Fetching grid URL for {city}...", end=" ", flush=True)
    url = f"https://api.weather.gov/points/{lat:.4f},{lon:.4f}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            forecast_url = data["properties"]["forecast"]
            cache[city] = forecast_url
            print(f"✓ {forecast_url}")
    except Exception as e:
        print(f"✗ {e}")
    time.sleep(0.3)  # be polite to NOAA

with open("noaa_grid_cache.json", "w") as f:
    json.dump(cache, f, indent=2)

print(f"\nCached {len(cache)}/{len(CITIES)} cities → noaa_grid_cache.json")
