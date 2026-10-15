import json, re, threading, uuid, ssl, urllib.request, urllib.error, urllib.parse
from concurrent.futures import ThreadPoolExecutor
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import providers

STATIC = (Path(__file__).parent / "static").resolve()
TYPES = {".html": "text/html", ".css": "text/css", ".js": "text/javascript"}
JOBS, POOL = {}, ThreadPoolExecutor(12)

SOCIAL = re.compile(
    r"facebook\.com|instagram\.com|linktr\.ee|wa\.me|twitter\.com|//x\.com|tiktok\.com|youtube\.com|linkedin\.com|threads\.net",
    re.I
)

PARKED = re.compile(
    r"domain (is )?(for sale|parked|expired)|buy this domain|inquire about this domain|"
    r"domain may be for sale|this domain has expired|renew (your )?domain|"
    r"hugedomains|godaddy\.com/park|sedo\.com|dan\.com|afternic\.com|bodis\.com|parkingcrew|"
    r"account suspended|cgi-sys/suspendedpage\.cgi|cgi-sys/defaultwebpage\.cgi|"
    r"apache2 (ubuntu|debian) default page|welcome to nginx|iis windows server|cpanel default page",
    re.I
)

EMAIL = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", re.I)
MAILTO = re.compile(r'mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', re.I)
CF_EMAIL = re.compile(r'data-cfemail="([0-9a-fA-F]+)"')
REFRESH_URL = re.compile(r'<meta[^>]+http-equiv=[\'"]refresh[\'"][^>]+content=[\'"]\d+;\s*url=([^\'"]+)[\'"]', re.I)
CONTACT_LINK = re.compile(r'href=[\'"]([^\'"]*(?:/contact|/about|contact-us|about-us|reach-us)[^\'"]*)[\'"]', re.I)
SOC = re.compile(r"https?://(?:www\.)?(?:instagram\.com|facebook\.com|wa\.me|twitter\.com|x\.com|tiktok\.com|linkedin\.com)/[\w./?=&-]+", re.I)

DIRECTORIES = (
    "tripadvisor.", "booking.com", "hotels.com", "hotels.ng", "facebook.com", "instagram.com",
    "linkedin.com", "twitter.com", "x.com", "yellowpages.", "yelp.com", "expedia.com",
    "foursquare.com", "mapquest.com", "wikipedia.org", "wikidata.org", "jumia.",
    "vconnect.com", "finelib.com", "businesslist.com.ng", "connectnigeria.com"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Upgrade-Insecure-Requests": "1"
}

SSL_DEFAULT = ssl.create_default_context()
SSL_UNVERIFIED = ssl._create_unverified_context()

def decode_cf(cf_hex):
    try:
        k = int(cf_hex[:2], 16)
        return "".join([chr(int(cf_hex[i:i+2], 16) ^ k) for i in range(2, len(cf_hex), 2)])
    except Exception:
        return ""

def clean_emails(raw_list):
    valid = []
    bad_exts = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js")
    bad_prefixes = ("example@", "user@", "email@", "test@", "name@", "info@wix.com",
                    "support@wix.com", "sentry@", "noreply@", "domain@", "bootstrap@")
    for m in raw_list:
        m = m.strip().lower().rstrip(".")
        if any(m.endswith(ext) for ext in bad_exts): continue
        if any(m.startswith(p) for p in bad_prefixes): continue
        parts = m.split("@")
        if len(parts) != 2: continue
        domain_parts = parts[1].split(".")
        if len(domain_parts) < 2 or len(domain_parts[-1]) < 2: continue
        if m not in valid: valid.append(m)
    return valid

def fetch_page(url, timeout=8):
    """Fetches a URL trying HTTPS, unverified SSL, HTTP, and www fallback.
    Returns (html, final_url, note, is_working, status_code)"""
    parsed = urllib.parse.urlparse(url)
    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc or parsed.path
    path = parsed.path if parsed.netloc else ""
    if path and not path.startswith("/"): path = "/" + path
    if parsed.query: path += "?" + parsed.query

    variations = []
    variations.append(f"https://{netloc}{path}")
    variations.append(f"http://{netloc}{path}")
    if not netloc.startswith("www.") and "." in netloc:
        variations.append(f"https://www.{netloc}{path}")
        variations.append(f"http://www.{netloc}{path}")
    elif netloc.startswith("www."):
        non_www = netloc[4:]
        variations.append(f"https://{non_www}{path}")

    last_exc = None
    for target in variations:
        for use_unverified in (False, True):
            try:
                ctx = SSL_UNVERIFIED if use_unverified else SSL_DEFAULT
                req = urllib.request.Request(target, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                    code = resp.getcode()
                    html = resp.read(350000).decode("utf-8", "ignore")
                    final_url = resp.geturl() or target
                    note = "Loads fine" + (" (SSL warning)" if use_unverified else "")
                    return html, final_url, note, True, code
            except urllib.error.HTTPError as e:
                # If protected/rate limited, the site is active and working
                if e.code in (401, 403, 429):
                    return "", target, f"HTTP {e.code} (Protected / Active)", True, e.code
                # 404, 410, 500, etc.
                last_exc = e
                break  # Don't retry unverified if server responded with HTTP error
            except ssl.SSLCertVerificationError as e:
                last_exc = e
                if not use_unverified:
                    continue  # Retry with unverified SSL
                break
            except Exception as e:
                last_exc = e
                break

    # If all variations failed
    if isinstance(last_exc, urllib.error.HTTPError):
        return "", url, f"HTTP {last_exc.code}", False, last_exc.code
    
    err_str = str(getattr(last_exc, "reason", last_exc))
    if "getaddrinfo failed" in err_str or "11001" in err_str:
        return "", url, "DNS lookup failed (Domain not found)", False, None
    if "10061" in err_str or "refused" in err_str.lower():
        return "", url, "Connection refused (Server down)", False, None
    if "timed out" in err_str.lower():
        return "", url, "Connection timed out", False, None
    return "", url, f"{type(last_exc).__name__}: {err_str[:45]}", False, None

def discover_online(biz_name, city):
    """Searches DuckDuckGo HTML for business name + city to discover candidate website & socials."""
    if not biz_name: return "", []
    try:
        q = f"{biz_name} {city}".strip()
        data = urllib.parse.urlencode({"q": q}).encode()
        req = urllib.request.Request(
            "https://html.duckduckgo.com/html/",
            data=data,
            headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded", "Referer": "https://html.duckduckgo.com/"}
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            html = resp.read(250000).decode("utf-8", "ignore")
            uddg_links = re.findall(r'href=["\'](?:https?:)?//duckduckgo\.com/l/\?uddg=([^"\'&]+)', html)
            links = [urllib.parse.unquote(u) for u in uddg_links]
            if not links:
                links = re.findall(r'<a[^>]+class=[\'"][^\'"]*result__url[^\'"]*[\'"][^>]+href=[\'"]([^\'"]+)[\'"]', html)
            
            candidate_site = None
            candidate_soc = []
            for link in links:
                l_lower = link.lower()
                if SOCIAL.search(l_lower):
                    candidate_soc.append(link)
                elif not any(d in l_lower for d in DIRECTORIES):
                    if not candidate_site:
                        candidate_site = link
            return candidate_site or "", candidate_soc
    except Exception:
        return "", []

def query_wikidata(qid):
    """Fetches official website and email from Wikidata claims P856 and P968."""
    if not qid: return "", ""
    try:
        url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={qid}&format=json&props=claims"
        req = urllib.request.Request(url, headers={"User-Agent": "LeadFinder/1.0"})
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.load(r)
            entity = data.get("entities", {}).get(qid, {})
            claims = entity.get("claims", {})
            website = claims.get("P856", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value", "")
            email = claims.get("P968", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value", "")
            return website, email
    except Exception:
        return "", ""

def check_site(url, biz_name="", city="", wikidata_id=""):
    """
    Returns (status, note, socials, emails, verified_url).
    status: working | broken | social_only | no_website
    """
    url = (url or "").strip()
    socials = []
    emails = []

    # If business has a wikidata tag, inspect for official website & email
    if not url and wikidata_id:
        wiki_web, wiki_mail = query_wikidata(wikidata_id)
        if wiki_web: url = wiki_web
        if wiki_mail: emails.append(wiki_mail)

    # If still no URL, try fast online discovery
    if not url:
        discovered_url, discovered_soc = discover_online(biz_name, city)
        socials.extend(discovered_soc)
        if discovered_url:
            url = discovered_url

    # If truly no URL found
    if not url:
        if socials:
            return "social_only", "Social profile only", list(dict.fromkeys(socials)), "", ""
        return "no_website", "No website found", [], "", ""

    # If URL is a social profile
    if SOCIAL.search(url):
        socials.append(url)
        return "social_only", "Social profile only", list(dict.fromkeys(socials)), "", url

    # Fetch and verify regular website
    html, final_url, note, is_working, code = fetch_page(url)

    if not is_working:
        return "broken", note, list(dict.fromkeys(socials)), "", url

    # Check for HTML meta-refresh redirect (1 hop)
    refresh_match = REFRESH_URL.search(html)
    if refresh_match:
        redirect_target = refresh_match.group(1).strip()
        if not redirect_target.startswith("http"):
            redirect_target = urllib.parse.urljoin(final_url, redirect_target)
        r_html, r_final, r_note, r_working, r_code = fetch_page(redirect_target, timeout=5)
        if r_working and r_html:
            html, final_url = r_html, r_final

    # Check for Parked Domain / For Sale / Default page
    if PARKED.search(html):
        return "broken", "Domain parked or for sale", list(dict.fromkeys(socials)), "", final_url

    # Check for empty response
    if len(html.strip()) < 80 and not code:
        return "broken", "Empty page response", list(dict.fromkeys(socials)), "", final_url

    # Extract emails
    raw_mails = []
    # 1. mailto: links
    raw_mails.extend(MAILTO.findall(html))
    # 2. Cloudflare email obfuscation
    for cf_hex in CF_EMAIL.findall(html):
        decoded = decode_cf(cf_hex)
        if decoded: raw_mails.append(decoded)
    # 3. Standard regex on HTML
    raw_mails.extend(EMAIL.findall(html))

    # 4. If no emails on homepage, check /contact or /about subpage
    if not raw_mails:
        contact_match = CONTACT_LINK.search(html)
        if contact_match:
            sub_url = contact_match.group(1).strip()
            if not sub_url.startswith("http"):
                sub_url = urllib.parse.urljoin(final_url, sub_url)
            try:
                sub_req = urllib.request.Request(sub_url, headers=HEADERS)
                with urllib.request.urlopen(sub_req, timeout=4, context=SSL_UNVERIFIED) as s_resp:
                    s_html = s_resp.read(250000).decode("utf-8", "ignore")
                    raw_mails.extend(MAILTO.findall(s_html))
                    for cf_hex in CF_EMAIL.findall(s_html):
                        decoded = decode_cf(cf_hex)
                        if decoded: raw_mails.append(decoded)
                    raw_mails.extend(EMAIL.findall(s_html))
                    socials.extend(SOC.findall(s_html))
            except Exception:
                pass

    # Extract socials from page
    socials.extend(SOC.findall(html))

    valid_emails = clean_emails(emails + raw_mails)
    clean_socials = list(dict.fromkeys(socials))[:5]
    email_str = ", ".join(valid_emails[:3])

    return "working", note, clean_socials, email_str, final_url

def enrich(job, b):
    status, note, soc, mail, verified_url = check_site(
        b["website"],
        biz_name=b.get("name", ""),
        city=b.get("city", ""),
        wikidata_id=b.get("wikidata_id", "")
    )
    b["site_status"] = status
    b["site_note"] = note
    if verified_url and not b["website"]:
        b["website"] = verified_url
    b["socials"] = list(dict.fromkeys(b["socials"] + soc))
    b["email"] = b["email"] or mail
    job["results"].append(b)

def run(job, p):
    try:
        seen = set()
        for b in providers.PROVIDERS[p["provider"]]["fn"](p, lambda m: job.update(msg=m)):
            if b["id"] in seen: continue
            seen.add(b["id"])
            job["found"] = len(seen)
            job["futs"].append(POOL.submit(enrich, job, b))
        job["msg"] = "Checking websites"
        for f in job["futs"]: f.result()
        job["msg"] = "Done"
    except Exception as e:
        job["error"] = str(e)
    job["done"] = True

class H(BaseHTTPRequestHandler):
    def reply(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/api/providers":
            return self.reply(200, [{"id": k, "label": v["label"], "key": v["key"]} for k, v in providers.PROVIDERS.items()])
        if u.path.startswith("/api/job/"):
            j = JOBS.get(u.path.split("/")[-1])
            if not j: return self.reply(404, {"error": "Unknown job"})
            since = int(urllib.parse.parse_qs(u.query).get("since", [0])[0])
            return self.reply(200, {k: j[k] for k in ("msg", "found", "done", "error")} | {"results": j["results"][since:]})
        f = (STATIC / ("index.html" if u.path == "/" else u.path.lstrip("/"))).resolve()
        if f.is_file() and STATIC in f.parents:
            return self.reply(200, f.read_bytes(), TYPES.get(f.suffix, "application/octet-stream"))
        self.reply(404, {"error": "Not found"})

    def do_POST(self):
        p = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        jid = uuid.uuid4().hex[:8]
        JOBS[jid] = job = {"results": [], "futs": [], "msg": "Starting", "found": 0, "done": False, "error": None}
        threading.Thread(target=run, args=(job, p), daemon=True).start()
        self.reply(200, {"id": jid})

    def log_message(self, *a): pass

if __name__ == "__main__":
    print("LeadFinder running at http://localhost:8000")
    ThreadingHTTPServer(("127.0.0.1", 8000), H).serve_forever()
