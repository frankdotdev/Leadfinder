"""Map providers. To add one: write a generator that yields biz(...) dicts, then register it in PROVIDERS.
Everything after collection (website checks, contacts, dashboard) is provider-independent."""
import json
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

APP_UA = "LeadFinder/1.1 (https://github.com/frankdotdev/Leadfinder; leadfinder-app@gmail.com)"
DATA_DIR = (Path(__file__).parent / "data").resolve()
GEOCACHE_FILE = DATA_DIR / "geocache.json"

# Local cache loader
def _load_geocache():
    if GEOCACHE_FILE.is_file():
        try:
            return json.loads(GEOCACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_geocache(cache_dict):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        GEOCACHE_FILE.write_text(json.dumps(cache_dict, indent=2), encoding="utf-8")
    except Exception:
        pass


def biz(id, name, category="", address="", phone="", website="", rating=None, reviews=None,
        maps_url="", email="", socials=(), city="", wikidata_id=""):
    return dict(id=str(id), name=name, category=category, address=address, phone=phone,
                website=website or "", rating=rating, reviews=reviews, maps_url=maps_url,
                email=email or "", socials=list(dict.fromkeys(socials)), city=city,
                wikidata_id=wikidata_id or "")


def http(url, data=None, headers=None, form=False, timeout=20):
    h = {
        "User-Agent": APP_UA,
        **(headers or {})
    }
    body = None
    if data is not None:
        body = urllib.parse.urlencode(data).encode() if form else json.dumps(data).encode()
        h["Content-Type"] = "application/x-www-form-urlencoded" if form else "application/json"
    try:
        req = urllib.request.Request(url, body, h)
        # Try default SSL context; urllib wraps SSL errors inside URLError(reason=SSLError),
        # so catch both ssl.SSLError and URLError with an SSL reason and retry unverified.
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except (ssl.SSLError, urllib.error.URLError) as e:
            reason = getattr(e, "reason", e)
            if isinstance(e, ssl.SSLError) or isinstance(reason, ssl.SSLError) or "CERTIFICATE_VERIFY_FAILED" in str(reason):
                ctx = ssl._create_unverified_context()
                with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                    return json.load(r)
            raise
    except urllib.error.HTTPError as e:
        host = urllib.parse.urlparse(url).netloc
        raise RuntimeError(f"{host} returned HTTP {e.code}: {e.read()[:200].decode('utf-8', 'ignore')}")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        host = urllib.parse.urlparse(url).netloc
        err_msg = getattr(e, "reason", e)
        raise RuntimeError(f"Connection to {host} failed: {err_msg}")


def normalize_bbox(s, n, w, e, lat, lon):
    """
    Calculates an optimal search bounding box for commercial businesses around a location.
    - If bbox is too small (pinpoint), expands to ~12km box.
    - If bbox is overly large (entire county/state > 18km), focuses on the central commercial core
      (+/- 0.075 deg = ~16km across) to prevent Overpass timeouts in massive cities like London, Manchester, Toronto.
    """
    lat_span = n - s
    lon_span = e - w
    if lat_span < 0.05 or lon_span < 0.05:
        s = lat - 0.075
        n = lat + 0.075
        w = lon - 0.075
        e = lon + 0.075
    elif lat_span > 0.15 or lon_span > 0.15:
        s = lat - 0.075
        n = lat + 0.075
        w = lon - 0.075
        e = lon + 0.075
    return s, n, w, e


def geocode(location_query, log=None):
    """
    Intelligent dynamic geocoder:
    - Works for ANY place in the world (city, town, suburb, borough, neighborhood, or state).
    - If user enters a State or Region (e.g. 'Texas', 'Bavaria', 'Ontario'), it detects the place type
      and automatically identifies the primary commercial city/hub in that region instead of empty rural centroid.
    - Caches results to disk for zero-latency repeat searches.
    Returns (lat, lon, s, n, w, e, display_name).
    """
    query = (location_query or "").strip()
    if not query:
        raise ValueError("Please enter a city or location.")

    # 1. Direct coordinates input check (e.g. "53.3811, -1.4701" or "30.26, -97.74")
    m = re.match(r"^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$", query)
    if m:
        lat, lon = float(m.group(1)), float(m.group(2))
        return lat, lon, lat - 0.075, lat + 0.075, lon - 0.075, lon + 0.075, f"{lat:.4f}, {lon:.4f}"

    clean_key = query.lower().strip()
    cache = _load_geocache()
    if clean_key in cache:
        item = cache[clean_key]
        if isinstance(item, dict):
            s, n, w, e, name = item["s"], item["n"], item["w"], item["e"], item["name"]
            lat = item.get("lat", (s + n) / 2)
            lon = item.get("lon", (w + e) / 2)
            if log: log(f"Located '{name}' from local map cache")
            return lat, lon, s, n, w, e, name

    last_network_err = None

    # 2. Query Nominatim OpenStreetMap (Best geographical classification)
    try:
        if log: log(f"Looking up '{query}' on global map...")
        nom_url = f"https://nominatim.openstreetmap.org/search?format=json&limit=5&addressdetails=1&q={urllib.parse.quote(query)}"
        d = http(nom_url, headers={"User-Agent": APP_UA}, timeout=8)
        if d and len(d) > 0:
            top = d[0]
            lat = float(top["lat"])
            lon = float(top["lon"])
            raw_s, raw_n, raw_w, raw_e = map(float, top["boundingbox"])
            addr_type = top.get("addresstype") or top.get("type") or ""
            display_name = top.get("display_name", query)
            short_name = display_name.split(",")[0].strip()

            # Smart Region / State Detection:
            # If the user searched an entire state, province, or country (e.g. 'Texas', 'California', 'Bavaria')
            is_broad_region = (
                addr_type in ("state", "province", "region", "country", "territory", "county")
                or (raw_n - raw_s) > 1.2
                or (raw_e - raw_w) > 1.2
            )

            if is_broad_region:
                if log: log(f"'{short_name}' is a broad {addr_type}. Finding major commercial city in {short_name}...")
                try:
                    # Dynamically find the primary commercial city in that region
                    city_search_url = f"https://nominatim.openstreetmap.org/search?format=json&limit=1&addressdetails=1&q=city+in+{urllib.parse.quote(short_name)}"
                    city_res = http(city_search_url, headers={"User-Agent": APP_UA}, timeout=6)
                    if city_res and len(city_res) > 0:
                        c_top = city_res[0]
                        c_lat = float(c_top["lat"])
                        c_lon = float(c_top["lon"])
                        c_s, c_n, c_w, c_e = map(float, c_top["boundingbox"])
                        c_display = c_top.get("display_name", "")
                        c_city = c_display.split(",")[0].strip()
                        resolved_title = f"{c_city}, {short_name}"
                        if log: log(f"Targeting major commercial center: {resolved_title}")
                        s, n, w, e = normalize_bbox(c_s, c_n, c_w, c_e, c_lat, c_lon)
                        cache[clean_key] = {"lat": c_lat, "lon": c_lon, "s": s, "n": n, "w": w, "e": e, "name": resolved_title}
                        _save_geocache(cache)
                        return c_lat, c_lon, s, n, w, e, resolved_title
                except Exception:
                    pass

            # Regular City / Town / Neighborhood / Suburb
            s, n, w, e = normalize_bbox(raw_s, raw_n, raw_w, raw_e, lat, lon)
            parts = [p.strip() for p in display_name.split(",") if p.strip()]
            resolved_title = ", ".join(parts[:2]) if len(parts) >= 2 else short_name
            if log: log(f"Located {resolved_title}")
            cache[clean_key] = {"lat": lat, "lon": lon, "s": s, "n": n, "w": w, "e": e, "name": resolved_title}
            _save_geocache(cache)
            return lat, lon, s, n, w, e, resolved_title
    except Exception as e:
        last_network_err = e

    # 3. Fallback to Open-Meteo Global Geocoding API
    try:
        if log: log(f"Locating '{query}' via Open-Meteo...")
        om_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(query)}&count=5&language=en&format=json"
        data = http(om_url, timeout=7)
        if data and data.get("results"):
            res_list = data["results"]
            chosen = res_list[0]
            for candidate in res_list:
                f_code = candidate.get("feature_code", "")
                if f_code.startswith("PPL"): # Populated place / city
                    chosen = candidate
                    break
            lat = float(chosen["latitude"])
            lon = float(chosen["longitude"])
            name_parts = [chosen.get("name", query)]
            if chosen.get("admin1"): name_parts.append(chosen["admin1"])
            if chosen.get("country"): name_parts.append(chosen["country"])
            resolved_title = ", ".join(name_parts[:2])
            s, n, w, e = lat - 0.075, lat + 0.075, lon - 0.075, lon + 0.075
            if log: log(f"Located {resolved_title}")
            cache[clean_key] = {"lat": lat, "lon": lon, "s": s, "n": n, "w": w, "e": e, "name": resolved_title}
            _save_geocache(cache)
            return lat, lon, s, n, w, e, resolved_title
    except Exception as e:
        last_network_err = e

    # 4. Fallback to Photon Komoot (OSM Full-Text index)
    try:
        if log: log(f"Locating '{query}' via Photon...")
        photon_url = f"https://photon.komoot.io/api/?q={urllib.parse.quote(query)}&limit=3"
        d = http(photon_url, timeout=7)
        if d and d.get("features"):
            feat = d["features"][0]
            lon, lat = feat["geometry"]["coordinates"]
            props = feat.get("properties", {})
            name = props.get("name") or query
            state = props.get("state") or props.get("country") or ""
            resolved_title = f"{name}, {state}" if state else name
            s, n, w, e = lat - 0.075, lat + 0.075, lon - 0.075, lon + 0.075
            cache[clean_key] = {"lat": lat, "lon": lon, "s": s, "n": n, "w": w, "e": e, "name": resolved_title}
            _save_geocache(cache)
            return lat, lon, s, n, w, e, resolved_title
    except Exception as e:
        last_network_err = e

    err_str = str(last_network_err or "")
    if "11001" in err_str or "getaddrinfo failed" in err_str:
        raise ValueError(
            f"Could not locate '{query}': Network DNS error ([Errno 11001] getaddrinfo failed). "
            f"Please check your internet connection or enter coordinates (e.g. 53.38, -1.47)."
        )

    raise ValueError(
        f"Could not find '{query}'. Try 'City, Country' (e.g. 'Sheffield, UK' or 'Austin, Texas') or coordinates (e.g. 53.38, -1.47)."
    )


def google(p, log):
    if not p.get("key"): raise ValueError("Google needs an API key (Places API New enabled).")
    lat, lon, s, n, w, e, resolved_name = geocode(p["city"], log)
    g = max(1, min(int(p.get("grid") or 4), 10))
    fields = ("places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,"
              "places.rating,places.userRatingCount,places.googleMapsUri,places.primaryTypeDisplayName,nextPageToken")
    for i in range(g):
        for j in range(g):
            log(f"Google Places: area {i*g+j+1} of {g*g} in {resolved_name}")
            cell = {"rectangle": {"low": {"latitude": s+(n-s)*i/g, "longitude": w+(e-w)*j/g},
                                  "high": {"latitude": s+(n-s)*(i+1)/g, "longitude": w+(e-w)*(j+1)/g}}}
            token = None
            for _ in range(3):
                body = {"textQuery": p["category"], "locationRestriction": cell, "pageSize": 20}
                if token: body["pageToken"] = token
                d = http("https://places.googleapis.com/v1/places:searchText", body,
                         {"X-Goog-Api-Key": p["key"], "X-Goog-FieldMask": fields})
                for x in d.get("places", []):
                    yield biz(x["id"], x.get("displayName", {}).get("text", ""),
                              x.get("primaryTypeDisplayName", {}).get("text", ""), x.get("formattedAddress", ""),
                              x.get("nationalPhoneNumber", ""), x.get("websiteUri", ""), x.get("rating"),
                              x.get("userRatingCount"), x.get("googleMapsUri", ""), city=resolved_name)
                token = d.get("nextPageToken")
                if not token: break

OSM_TAGS = {
    "restaurant": '["amenity"~"restaurant|fast_food|cafe|bistro|food_court|diner"]',
    "food": '["amenity"~"restaurant|fast_food|cafe|bistro|food_court|diner"]',
    "eatery": '["amenity"~"restaurant|fast_food|cafe|bistro"]',
    "fast food": '["amenity"="fast_food"]',
    "cafe": '["amenity"~"cafe|coffee_shop"]',
    "coffee": '["amenity"~"cafe|coffee_shop"]',
    "bar": '["amenity"~"bar|pub|lounge"]',
    "pub": '["amenity"~"pub|bar"]',
    "lounge": '["amenity"~"bar|nightclub|lounge"]',
    "hotel": '["tourism"~"hotel|guest_house|motel|resort|hostel|bed_and_breakfast"]',
    "resort": '["tourism"~"hotel|resort"]',
    "motel": '["tourism"="motel"]',
    "lodging": '["tourism"~"hotel|guest_house|hostel|bed_and_breakfast"]',
    "pharmacy": '["amenity"="pharmacy"]',
    "chemist": '["amenity"="pharmacy"]',
    "drugstore": '["amenity"="pharmacy"]',
    "clinic": '["amenity"~"clinic|doctors|hospital|dentist|healthcare"]',
    "doctor": '["amenity"~"doctors|clinic|healthcare"]',
    "hospital": '["amenity"="hospital"]',
    "dentist": '["amenity"="dentist"]',
    "dental": '["amenity"="dentist"]',
    "physio": '["healthcare"~"physiotherapist|rehabilitation"]',
    "school": '["amenity"~"school|college|kindergarten"]',
    "college": '["amenity"~"college|university"]',
    "bank": '["amenity"="bank"]',
    "salon": '["shop"~"hairdresser|beauty|cosmetics|hair"]',
    "hair": '["shop"~"hairdresser|hair"]',
    "hairdresser": '["shop"="hairdresser"]',
    "beauty": '["shop"~"beauty|cosmetics|hairdresser"]',
    "barber": '["shop"~"hairdresser|barber"]',
    "spa": '["shop"~"beauty|massage|spa"]',
    "massage": '["shop"~"massage|beauty"]',
    "supermarket": '["shop"="supermarket"]',
    "grocery": '["shop"~"supermarket|convenience|grocery|greengrocer"]',
    "bakery": '["shop"="bakery"]',
    "baker": '["shop"="bakery"]',
    "pastry": '["shop"="bakery"]',
    "gym": '["leisure"~"fitness_centre|sports_centre"]',
    "fitness": '["leisure"~"fitness_centre|sports_centre"]',
    "car": '["shop"~"car|car_repair"]',
    "mechanic": '["shop"="car_repair"]',
    "auto": '["shop"~"car|car_repair|auto_parts"]',
    "boutique": '["shop"~"clothes|boutique"]',
    "clothes": '["shop"="clothes"]',
    "fashion": '["shop"~"clothes|boutique|fashion"]',
    "electronics": '["shop"="electronics"]',
    "lawyer": '["office"="lawyer"]',
    "attorney": '["office"="lawyer"]',
    "legal": '["office"="lawyer"]',
    "accountant": '["office"="accountant"]',
    "real estate": '["office"="estate_agent"]',
    "estate agent": '["office"="estate_agent"]',
    "plumber": '["craft"="plumber"]',
    "electrician": '["craft"="electrician"]',
    "contractor": '["craft"~"plumber|electrician|builder|carpenter"]',
}

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

URL_REGEX = re.compile(r'https?://[^\s"\'<>]+', re.I)

def parse_osm_element(x, city):
    t = x.get("tags", {})
    name = t.get("name") or t.get("official_name")
    if not name: return None
    c = x.get("center") or x
    addr = " ".join(filter(None, [t.get("addr:housenumber"), t.get("addr:street"), t.get("addr:suburb"), t.get("addr:city")]))
    
    website = (
        t.get("website") or 
        t.get("contact:website") or 
        t.get("url") or 
        t.get("contact:url") or 
        t.get("brand:website") or 
        t.get("operator:website") or 
        t.get("website:menu") or 
        t.get("menu") or ""
    ).strip()

    if not website:
        extra_text = " ".join(filter(None, [t.get("description"), t.get("note"), t.get("comment"), t.get("source")]))
        m = URL_REGEX.search(extra_text)
        if m: website = m.group(0).strip()

    soc = []
    for k in ("contact:facebook", "facebook", "facebook:url",
              "contact:instagram", "instagram", "instagram:url",
              "contact:twitter", "twitter", "contact:x", "x",
              "contact:tiktok", "tiktok",
              "contact:linkedin", "linkedin",
              "contact:youtube", "youtube",
              "contact:whatsapp", "whatsapp"):
        v = t.get(k)
        if v:
            v = v.strip()
            if not v.startswith("http"):
                if "facebook" in k: v = "https://facebook.com/" + v.lstrip("@")
                elif "instagram" in k: v = "https://instagram.com/" + v.lstrip("@")
                elif "twitter" in k or "x" in k: v = "https://twitter.com/" + v.lstrip("@")
                elif "tiktok" in k: v = "https://tiktok.com/@" + v.lstrip("@")
                elif "linkedin" in k: v = "https://linkedin.com/company/" + v.lstrip("@")
                elif "whatsapp" in k: v = "https://wa.me/" + re.sub(r"\D", "", v)
            soc.append(v)

    phone = (t.get("phone") or t.get("contact:phone") or t.get("contact:mobile") or t.get("mobile") or "").strip()
    email = (t.get("email") or t.get("contact:email") or t.get("operator:email") or "").strip()
    category = next((t[k] for k in ("amenity", "shop", "office", "tourism", "craft", "healthcare", "leisure") if k in t), "")
    wikidata_id = t.get("wikidata", "").strip()

    maps_url = ""
    if c.get("lat") and c.get("lon"):
        maps_url = f"https://www.google.com/maps/search/?api=1&query={c.get('lat')},{c.get('lon')}"

    return biz(f"{x.get('type', 'node')}{x['id']}", name, category, addr, phone, website,
               maps_url=maps_url, email=email, socials=soc, city=city,
               wikidata_id=wikidata_id)

def parse_nominatim_results(items, category_fallback, city):
    results = []
    for x in items:
        tags = x.get("extratags", {})
        name = x.get("name") or tags.get("name") or x.get("display_name", "").split(",")[0].strip()
        if not name: continue
        addr_dict = x.get("address", {})
        addr = " ".join(filter(None, [
            addr_dict.get("house_number"),
            addr_dict.get("road"),
            addr_dict.get("suburb"),
            addr_dict.get("city") or addr_dict.get("town") or addr_dict.get("state")
        ]))
        website = (
            tags.get("website") or
            tags.get("contact:website") or
            tags.get("url") or
            tags.get("contact:url") or ""
        ).strip()
        soc = []
        for k in ("contact:facebook", "facebook", "contact:instagram", "instagram",
                  "contact:twitter", "twitter", "contact:whatsapp", "whatsapp"):
            v = tags.get(k)
            if v:
                v = v.strip()
                if not v.startswith("http"):
                    if "facebook" in k: v = "https://facebook.com/" + v.lstrip("@")
                    elif "instagram" in k: v = "https://instagram.com/" + v.lstrip("@")
                    elif "twitter" in k: v = "https://twitter.com/" + v.lstrip("@")
                    elif "whatsapp" in k: v = "https://wa.me/" + re.sub(r"\D", "", v)
                soc.append(v)
        phone = (tags.get("phone") or tags.get("contact:phone") or tags.get("contact:mobile") or "").strip()
        email = (tags.get("email") or tags.get("contact:email") or "").strip()
        lat, lon = x.get("lat"), x.get("lon")
        maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}" if lat and lon else ""
        item_cat = x.get("type") or category_fallback
        b = biz(f"nom{x.get('osm_id', x.get('place_id'))}", name, item_cat, addr, phone, website,
                maps_url=maps_url, email=email, socials=soc, city=city, wikidata_id=tags.get("wikidata", ""))
        results.append(b)
    return results

def parse_photon_results(features, category_fallback, city, center_lat=None, center_lon=None):
    results = []
    for feat in features:
        props = feat.get("properties", {})
        name = props.get("name")
        if not name:
            continue

        osm_key = str(props.get("osm_key") or "").lower()
        osm_val = str(props.get("osm_value") or "").lower()

        # Reject non-commercial entities (roads, paths, bus stops, guideposts, natural features)
        if osm_key in ("information", "highway", "barrier", "natural", "waterway", "place", "landuse", "boundary"):
            continue
        if osm_val in ("guidepost", "path", "footway", "cycleway", "track", "bench", "waste_basket", "shelter", "crossing", "traffic_signals"):
            continue

        geom = feat.get("geometry", {})
        coords = geom.get("coordinates") or [None, None]
        lon, lat = coords[0], coords[1]

        # Ensure location is within reasonable city radius (< 25km ~ 0.22 degrees) from searched center
        if center_lat is not None and center_lon is not None and lat is not None and lon is not None:
            if abs(lat - center_lat) > 0.22 or abs(lon - center_lon) > 0.22:
                continue

        addr_parts = [
            props.get("housenumber"),
            props.get("street"),
            props.get("district") or props.get("suburb"),
            props.get("city") or props.get("town") or props.get("state"),
            props.get("postcode")
        ]
        addr = " ".join([p for p in addr_parts if p])
        osm_id = props.get("osm_id") or abs(hash(name))
        cat = props.get("osm_value") or props.get("osm_key") or category_fallback
        
        maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}" if lat and lon else ""
        results.append(biz(
            f"pho{osm_id}",
            name,
            cat,
            addr,
            phone="",
            website="",
            maps_url=maps_url,
            city=city
        ))
    return results

def _overpass_query(query_data, log, timeout=28):
    """Tries Overpass mirrors in order, logging exact errors/remarks for diagnostics."""
    for srv in OVERPASS_SERVERS:
        srv_name = urllib.parse.urlparse(srv).netloc
        try:
            d = http(srv, {"data": query_data}, form=True, timeout=timeout)
            if not isinstance(d, dict):
                log(f"WARN: {srv_name} returned non-JSON response")
                continue
            if d.get("remark") and not d.get("elements"):
                log(f"WARN: {srv_name} remark: {str(d['remark'])[:120]}")
                continue
            elems = d.get("elements")
            if elems is not None:
                return elems, srv_name
        except Exception as ex:
            log(f"WARN: {srv_name} failed ({str(ex)[:100]})")
            continue
    return None, ""


PHOTON_SYNONYMS = {
    "clinic": ["clinic", "medical center", "doctor", "dentist"],
    "dentist": ["dentist", "dental clinic", "dental"],
    "bakery": ["bakery", "pastry", "bakeshop"],
    "salon": ["salon", "hairdresser", "barber", "beauty salon"],
    "restaurant": ["restaurant", "bistro", "diner", "cafe"],
    "hotel": ["hotel", "inn", "guest house"],
    "gym": ["gym", "fitness", "health club"],
    "plumber": ["plumber", "plumbing"],
    "lawyer": ["lawyer", "attorney", "law firm"],
}


def osm(p, log):
    city_input = p.get("city", "").strip()
    cat_input = p.get("category", "").strip()
    lat, lon, s, n, w, e, resolved_name = geocode(city_input, log)
    cat = cat_input.lower().strip()
    tag = next((t for k, t in OSM_TAGS.items() if k in cat), None)
    safe_cat = cat.replace('"', "")

    # Subdivide bbox into a 2x2 grid so dense metros execute fast
    mid_lat = (s + n) / 2.0
    mid_lon = (w + e) / 2.0
    quadrants = [
        (s, w, mid_lat, mid_lon, "SW"),
        (s, mid_lon, mid_lat, e, "SE"),
        (mid_lat, w, n, mid_lon, "NW"),
        (mid_lat, mid_lon, n, e, "NE"),
    ]

    seen_ids = set()
    count = 0
    overpass_ok = False

    log(f"Querying OpenStreetMap Overpass (4-quadrant grid) for '{cat}' in {resolved_name}...")
    for idx, (qs, qw, qn, qe, qlabel) in enumerate(quadrants):
        bb = f"({qs},{qw},{qn},{qe})"
        q = (
            f"node{tag}{bb};\nway{tag}{bb};\n"
            if tag
            else f'node["name"~"{safe_cat}",i]{bb};\nway["name"~"{safe_cat}",i]{bb};\n'
        )
        query_data = f"[out:json][timeout:14];(\n{q});\nout body center 250;\n"
        elems, srv_name = _overpass_query(query_data, log, timeout=15)
        if elems is not None:
            overpass_ok = True
            q_added = 0
            for x in elems:
                b = parse_osm_element(x, resolved_name)
                if b and b["id"] not in seen_ids:
                    seen_ids.add(b["id"])
                    count += 1
                    q_added += 1
                    yield b
            log(f"OK: Quadrant {qlabel} ({srv_name}) returned {len(elems)} raw -> {q_added} named businesses")
        elif idx == 0:
            # Circuit breaker: if all Overpass mirrors failed/timed out on Quadrant 1,
            # fail fast instead of wasting 4+ minutes retrying dead mirrors on Q2-Q4!
            log("WARN: Overpass mirrors overloaded/502 on Q1; fast-switching to Multi-Grid Photon + Nominatim.")
            break

    if count > 0:
        log(f"OK: Overpass total collected: {count} unique businesses in {resolved_name}")
        return

    # Fallback 1: Multi-Point + Synonym Photon OSM Grid (ultra-fast ~0.4s per request, breaks 50-lead cap!)
    seen_names = set()
    photon_terms = next((syns for k, syns in PHOTON_SYNONYMS.items() if k in cat), [cat])
    photon_points = [
        (lat, lon, "Center"),
        (lat + 0.05, lon - 0.05, "NW"),
        (lat + 0.05, lon + 0.05, "NE"),
        (lat - 0.05, lon - 0.05, "SW"),
        (lat - 0.05, lon + 0.05, "SE"),
    ]
    log(f"Querying Photon OSM Multi-Grid ({len(photon_points)} zones × {len(photon_terms)} terms) around {resolved_name}...")
    for p_lat, p_lon, z_label in photon_points:
        for term in photon_terms:
            try:
                photon_url = (
                    "https://photon.komoot.io/api/?"
                    + urllib.parse.urlencode({
                        "q": term,
                        "lat": f"{p_lat:.4f}",
                        "lon": f"{p_lon:.4f}",
                        "limit": 100,
                    })
                )
                photon_data = http(photon_url, timeout=7)
                if photon_data and photon_data.get("features"):
                    results = parse_photon_results(photon_data["features"], term, resolved_name, center_lat=lat, center_lon=lon)
                    for b in results:
                        nk = b["name"].lower().strip()
                        if b["id"] not in seen_ids and nk not in seen_names:
                            seen_ids.add(b["id"])
                            seen_names.add(nk)
                            count += 1
                            yield b
            except Exception:
                continue
    log(f"OK: Photon Multi-Grid collected {count} unique businesses in {resolved_name}")

    # Fallback 2: Nominatim bounded search (up to 50)
    if count < 80:
        try:
            log(f"Supplementing with Nominatim bounded index for '{cat}' in {resolved_name}...")
            nom_url = (
                "https://nominatim.openstreetmap.org/search?"
                + urllib.parse.urlencode({
                    "q": cat,
                    "format": "json",
                    "limit": 50,
                    "addressdetails": 1,
                    "extratags": 1,
                    "viewbox": f"{w},{n},{e},{s}",
                    "bounded": 1,
                })
            )
            nom_data = http(nom_url, headers={"User-Agent": APP_UA}, timeout=8)
            if nom_data:
                results = parse_nominatim_results(nom_data, cat, resolved_name)
                n_added = 0
                for b in results:
                    nk = b["name"].lower().strip()
                    if b["id"] not in seen_ids and nk not in seen_names:
                        seen_ids.add(b["id"])
                        seen_names.add(nk)
                        count += 1
                        n_added += 1
                        yield b
                log(f"OK: Nominatim added {n_added} more results (total: {count})")
        except Exception as ex:
            log(f"WARN: Nominatim fallback skipped: {str(ex)[:80]}")

    if count > 0:
        return

    if count == 0:
        raise RuntimeError(
            f"No {cat_input} listings found around {resolved_name}. Try checking the spelling or searching a nearby town."
        )

def serper_maps(p, log):
    """Google Maps discovery via Serper.dev (2,500 free queries/mo, returns websites, phones & ratings)."""
    api_key = (p.get("key") or "").strip()
    if not api_key:
        settings_file = DATA_DIR / "settings.json"
        if settings_file.is_file():
            try:
                api_key = json.loads(settings_file.read_text(encoding="utf-8")).get("serper_api_key", "").strip()
            except Exception:
                pass
    if not api_key:
        raise ValueError("Serper.dev requires an API key (paste in API key box or save in Settings).")

    city_input = (p.get("city") or "").strip()
    cat_input = (p.get("category") or "").strip()
    lat, lon, s, n, w, e, resolved_name = geocode(city_input, log)
    seen = set()

    for page in range(1, 5):
        log(f"Serper Google Maps: fetching page {page} for '{cat_input}' in {resolved_name}...")
        try:
            d = http(
                "https://google.serper.dev/places",
                {"q": f"{cat_input} in {resolved_name}", "ll": f"@{lat},{lon},12z", "page": page},
                headers={"X-API-KEY": api_key},
                timeout=12,
            )
        except Exception as ex:
            log(f"WARN: Serper page {page} failed: {str(ex)[:90]}")
            break

        places = d.get("places") or []
        if not places:
            break

        added = 0
        for x in places:
            cid = str(x.get("cid") or x.get("placeId") or f"serp_{abs(hash(x.get('title', '') + x.get('address', '')))}")
            if cid in seen:
                continue
            seen.add(cid)
            added += 1
            maps_url = f"https://www.google.com/maps/place/?q=place_id:{x['placeId']}" if x.get("placeId") else ""
            yield biz(
                cid,
                x.get("title", ""),
                x.get("type") or cat_input,
                x.get("address", ""),
                x.get("phoneNumber", ""),
                x.get("website", ""),
                x.get("rating"),
                x.get("ratingCount"),
                maps_url=maps_url,
                city=resolved_name,
            )
        log(f"OK: Serper page {page} returned {added} businesses (total: {len(seen)})")
        if len(places) < 10:
            break


PROVIDERS = {
    "osm": {"fn": osm, "key": False, "label": "OpenStreetMap (free, no key)"},
    "serper": {"fn": serper_maps, "key": True, "label": "Serper.dev Google Maps (2,500 free)"},
    "google": {"fn": google, "key": True, "label": "Google Places (API key)"},
}
