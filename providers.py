"""Map providers. To add one: write a generator that yields biz(...) dicts, then register it in PROVIDERS.
Everything after collection (website checks, contacts, dashboard) is provider-independent."""
import json, re, urllib.request, urllib.parse, urllib.error

def biz(id, name, category="", address="", phone="", website="", rating=None, reviews=None,
        maps_url="", email="", socials=(), city="", wikidata_id=""):
    return dict(id=str(id), name=name, category=category, address=address, phone=phone,
                website=website or "", rating=rating, reviews=reviews, maps_url=maps_url,
                email=email or "", socials=list(dict.fromkeys(socials)), city=city,
                wikidata_id=wikidata_id or "")

def http(url, data=None, headers=None, form=False, timeout=60):
    h = {"User-Agent": "LeadFinder/1.0 (local tool; +https://leadfinder.local)", **(headers or {})}
    body = None
    if data is not None:
        body = urllib.parse.urlencode(data).encode() if form else json.dumps(data).encode()
        h["Content-Type"] = "application/x-www-form-urlencoded" if form else "application/json"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, body, h), timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{url.split('/')[2]} returned {e.code}: {e.read()[:300].decode('utf-8', 'ignore')}")

def geocode(city):
    d = http("https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" + urllib.parse.quote(city))
    if not d: raise ValueError(f"Could not find '{city}'. Try 'City, Country'.")
    s, n, w, e = map(float, d[0]["boundingbox"])
    lat, lon = float(d[0]["lat"]), float(d[0]["lon"])
    # If bounding box is overly large (e.g. an entire province > 0.45 deg), clamp to city radius
    if (n - s) > 0.45 or (e - w) > 0.45:
        s = max(s, lat - 0.15)
        n = min(n, lat + 0.15)
        w = max(w, lon - 0.15)
        e = min(e, lon + 0.15)
    return s, n, w, e

def google(p, log):
    if not p.get("key"): raise ValueError("Google needs an API key (Places API New enabled).")
    s, n, w, e = geocode(p["city"]); g = max(1, min(int(p.get("grid") or 4), 10))
    fields = ("places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,"
              "places.rating,places.userRatingCount,places.googleMapsUri,places.primaryTypeDisplayName,nextPageToken")
    for i in range(g):
        for j in range(g):
            log(f"Google: area {i*g+j+1} of {g*g}")
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
                              x.get("userRatingCount"), x.get("googleMapsUri", ""), city=p["city"])
                token = d.get("nextPageToken")
                if not token: break

OSM_TAGS = {
    "restaurant": '["amenity"="restaurant"]',
    "food": '["amenity"~"restaurant|fast_food|cafe"]',
    "eatery": '["amenity"~"restaurant|fast_food"]',
    "fast food": '["amenity"="fast_food"]',
    "cafe": '["amenity"="cafe"]',
    "coffee": '["amenity"="cafe"]',
    "bar": '["amenity"~"bar|pub"]',
    "pub": '["amenity"="pub"]',
    "lounge": '["amenity"~"bar|nightclub"]',
    "hotel": '["tourism"~"hotel|guest_house|motel|resort"]',
    "resort": '["tourism"~"hotel|resort"]',
    "motel": '["tourism"="motel"]',
    "lodging": '["tourism"~"hotel|guest_house|hostel"]',
    "pharmacy": '["amenity"="pharmacy"]',
    "chemist": '["amenity"="pharmacy"]',
    "drugstore": '["amenity"="pharmacy"]',
    "clinic": '["amenity"~"clinic|doctors"]',
    "doctor": '["amenity"="doctors"]',
    "hospital": '["amenity"="hospital"]',
    "dentist": '["amenity"="dentist"]',
    "dental": '["amenity"="dentist"]',
    "school": '["amenity"~"school|college"]',
    "college": '["amenity"="college"]',
    "bank": '["amenity"="bank"]',
    "salon": '["shop"~"hairdresser|beauty"]',
    "barber": '["shop"="hairdresser"]',
    "spa": '["shop"~"beauty|massage"]',
    "supermarket": '["shop"="supermarket"]',
    "grocery": '["shop"~"supermarket|convenience|grocery"]',
    "bakery": '["shop"="bakery"]',
    "gym": '["leisure"="fitness_centre"]',
    "fitness": '["leisure"="fitness_centre"]',
    "car": '["shop"~"car|car_repair"]',
    "mechanic": '["shop"="car_repair"]',
    "boutique": '["shop"="clothes"]',
    "clothes": '["shop"="clothes"]',
    "fashion": '["shop"="clothes"]',
    "electronics": '["shop"="electronics"]',
    "lawyer": '["office"="lawyer"]',
    "real estate": '["office"="estate_agent"]',
    "plumber": '["craft"="plumber"]',
}

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

URL_REGEX = re.compile(r'https?://[^\s"\'<>]+', re.I)

def osm(p, log):
    s, n, w, e = geocode(p["city"]); bb = f"({s},{w},{n},{e})"
    cat = p["category"].lower().strip()
    tag = next((t for k, t in OSM_TAGS.items() if k in cat), None)
    q = f"nwr{tag}{bb};" if tag else f'nwr["name"~"{cat.replace(chr(34), "")}",i]{bb};'
    log("OpenStreetMap: querying Overpass API...")
    
    query_data = f"[out:json][timeout:90];({q});out center tags;"
    d = None
    last_err = None
    for srv in OVERPASS_SERVERS:
        try:
            d = http(srv, {"data": query_data}, form=True, timeout=90)
            if d and "elements" in d:
                break
        except Exception as err:
            last_err = err
            continue

    if not d:
        raise RuntimeError(f"Overpass API error: {last_err or 'Failed to fetch OpenStreetMap data'}")

    for x in d.get("elements", []):
        t = x.get("tags", {})
        name = t.get("name") or t.get("official_name")
        if not name: continue
        c = x.get("center") or x
        addr = " ".join(filter(None, [t.get("addr:housenumber"), t.get("addr:street"), t.get("addr:suburb"), t.get("addr:city")]))
        
        # Comprehensive website tag detection
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

        # If website not found in standard tags, inspect note/description for embedded URLs
        if not website:
            extra_text = " ".join(filter(None, [t.get("description"), t.get("note"), t.get("comment"), t.get("source")]))
            m = URL_REGEX.search(extra_text)
            if m: website = m.group(0).strip()

        # Comprehensive social tags detection
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

        yield biz(f"{x['type']}{x['id']}", name, category, addr, phone, website,
                  maps_url=maps_url, email=email, socials=soc, city=p.get("city", ""),
                  wikidata_id=wikidata_id)

PROVIDERS = {"osm": {"fn": osm, "key": False, "label": "OpenStreetMap (free, no key)"},
             "google": {"fn": google, "key": True, "label": "Google Places (API key)"}}
