import json
import re
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import outreach
import providers

STATIC = (Path(__file__).parent / "static").resolve()
TYPES = {".html": "text/html", ".css": "text/css", ".js": "text/javascript"}
JOBS, POOL = {}, ThreadPoolExecutor(12)

SOCIAL = re.compile(
    r"facebook\.com|instagram\.com|linktr\.ee|wa\.me|twitter\.com|//x\.com|tiktok\.com|youtube\.com|linkedin\.com|threads\.net",
    re.I,
)

PARKED = re.compile(
    r"domain (is )?(for sale|parked|expired)|buy this domain|inquire about this domain|"
    r"domain may be for sale|this domain has expired|renew (your )?domain|"
    r"hugedomains|godaddy\.com/park|sedo\.com|dan\.com|afternic\.com|bodis\.com|parkingcrew|"
    r"account suspended|cgi-sys/suspendedpage\.cgi|cgi-sys/defaultwebpage\.cgi|"
    r"apache2 (ubuntu|debian) default page|welcome to nginx|iis windows server|cpanel default page",
    re.I,
)

MAILTO = re.compile(r"mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", re.I)
CF_EMAIL = re.compile(r'data-cfemail="([0-9a-fA-F]+)"')
REFRESH_URL = re.compile(
    r'<meta[^>]+http-equiv=[\'"]refresh[\'"][^>]+content=[\'"]\d+;\s*url=([^\'"]+)[\'"]', re.I
)
CONTACT_LINK = re.compile(
    r'href=[\'"]([^\'"]*(?:/contact|/about|contact-us|about-us|reach-us|get-in-touch|support|enquir|book|booking|find-us|location|privacy|gdpr|terms|impressum|imprint|legal|team|our-team)[^\'"]*)[\'"]',
    re.I,
)
SOC = re.compile(
    r"https?://(?:www\.)?(?:instagram\.com|facebook\.com|linktr\.ee|wa\.me|twitter\.com|x\.com|tiktok\.com|linkedin\.com)/[\w./?=&-]+",
    re.I,
)

DIRECTORIES = (
    "tripadvisor.", "booking.com", "hotels.com", "hotels.ng", "facebook.com", "instagram.com",
    "linkedin.com", "twitter.com", "x.com", "yellowpages.", "yelp.com", "expedia.com",
    "foursquare.com", "mapquest.com", "wikipedia.org", "wikidata.org", "jumia.",
    "vconnect.com", "finelib.com", "businesslist.com.ng", "connectnigeria.com",
    "indeed.", "glassdoor.", "ziprecruiter.", "monster.", "simplyhired.", "careerbuilder.",
    "grubhub.", "doordash.", "ubereats.", "seamless.", "postmates.", "toasttab.", "chownow.",
    "menupages.", "allmenus.", "zomato.", "opentable.", "resy.", "just-eat.", "deliveroo.",
    "fresha.", "booksy.", "vagaro.", "styleseat.", "treatwell.", "mindbodyonline.",
    "bbb.org", "manta.", "chamberofcommerce.", "nextdoor.", "reddit.", "pinterest.",
    "patch.com", "groupon.", "angi.", "thumbtack.", "houzz.", "porch.", "homeadvisor.",
    "crunchbase.", "bloomberg.", "dnb.com", "zoominfo.", "apollo.io", "rocketreach.",
    "whitepages.", "spokeo.", "superpages.", "citysearch.", "local.com", "hotfrog.",
    "brownbook.", "ezlocal.", "cylex.", "find-open.", "restaurantji.", "sirved.", "sluurpy.",
    "wanderboat.", "loc8nearme.", "mapcarta.", "wikimapia.", "openstreetmap.",
    "yell.com", "thomsonlocal.", "checkatrade.", "bark.com", "trustpilot.",
    "botw.org", "healthgrades.", "zocdoc.", "vitals.", "webmd.", "ratemds.", "wellness.",
    "bizapedia.", "opencorporates.", "yellowbook.", "dexknows.", "sharecare.", "doximity.",
    "npidb.", "hipaaspace.", "maps.apple.", "apple.com", "w3.org", "youtube.com", "tiktok.com",
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Upgrade-Insecure-Requests": "1",
}

SSL_DEFAULT = ssl.create_default_context()
SSL_UNVERIFIED = ssl._create_unverified_context()


def decode_cf(cf_hex):
    try:
        k = int(cf_hex[:2], 16)
        return "".join([chr(int(cf_hex[i : i + 2], 16) ^ k) for i in range(2, len(cf_hex), 2)])
    except Exception:
        return ""


def fetch_page(url, timeout=8):
    """Fetches a URL trying HTTPS, unverified SSL, HTTP, and www fallback.
    Returns (html, final_url, note, is_working, status_code, elapsed_sec)"""
    parsed = urllib.parse.urlparse(url)
    netloc = parsed.netloc or parsed.path
    path = parsed.path if parsed.netloc else ""
    if path and not path.startswith("/"):
        path = "/" + path
    if parsed.query:
        path += "?" + parsed.query

    variations = [
        f"https://{netloc}{path}",
        f"http://{netloc}{path}",
    ]
    if not netloc.startswith("www.") and "." in netloc:
        variations.append(f"https://www.{netloc}{path}")
        variations.append(f"http://www.{netloc}{path}")
    elif netloc.startswith("www."):
        non_www = netloc[4:]
        variations.append(f"https://{non_www}{path}")

    last_exc = None
    for target in variations:
        if not outreach.is_safe_public_url(target):
            return "", url, "Blocked unsafe/private URL (SSRF protection)", False, None, 0.0
        for use_unverified in (False, True):
            t0 = time.time()
            try:
                ctx = SSL_UNVERIFIED if use_unverified else SSL_DEFAULT
                req = urllib.request.Request(target, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                    elapsed = round(time.time() - t0, 2)
                    code = resp.getcode()
                    html = resp.read(350000).decode("utf-8", "ignore")
                    final_url = resp.geturl() or target
                    note = "Loads fine" + (" (SSL warning)" if use_unverified else "")
                    return html, final_url, note, True, code, elapsed
            except urllib.error.HTTPError as e:
                elapsed = round(time.time() - t0, 2)
                if e.code in (401, 403, 429):
                    return "", target, f"HTTP {e.code} (Protected / Active)", True, e.code, elapsed
                last_exc = e
                break
            except ssl.SSLCertVerificationError as e:
                last_exc = e
                if not use_unverified:
                    continue
                break
            except Exception as e:
                last_exc = e
                break

    if isinstance(last_exc, urllib.error.HTTPError):
        return "", url, f"HTTP {last_exc.code}", False, last_exc.code, 0.0

    err_str = str(getattr(last_exc, "reason", last_exc))
    if "getaddrinfo failed" in err_str or "11001" in err_str:
        return "", url, "DNS lookup failed (Domain not found)", False, None, 0.0
    if "10061" in err_str or "refused" in err_str.lower():
        return "", url, "Connection refused (Server down)", False, None, 0.0
    if "timed out" in err_str.lower() or "10060" in err_str:
        return "", url, "Connection timed out", False, None, 0.0
    return "", url, f"{type(last_exc).__name__}: {err_str[:45]}", False, None, 0.0


def discover_online(biz_name, city):
    """Searches web via outreach engine to discover candidate website, socials, and snippet emails."""
    if not biz_name:
        return "", [], []
    try:
        q = f'"{biz_name}" {city}'.strip()
        html = outreach.search_web_snippets(q, timeout=4)
        if not html:
            return "", [], []

        snippet_emails = outreach.extract_emails_from_text(html)
        uddg_links = re.findall(r'href=["\'](?:https?:)?//duckduckgo\.com/l/\?uddg=([^"\'&]+)', html)
        links = [urllib.parse.unquote(u) for u in uddg_links]
        if not links:
            links = re.findall(
                r'<a[^>]+class=[\'"][^\'"]*result__url[^\'"]*[\'"][^>]+href=[\'"]([^\'"]+)[\'"]', html
            )
        if not links:
            links = re.findall(r'href=[\'"](https?://[^\'"\s>]+)[\'"]', html)

        candidate_site = None
        candidate_soc = []
        for link in links:
            l_lower = link.lower()
            if any(k in l_lower for k in ("duckduckgo.com", "bing.com", "google.com", "microsoft.com", "yahoo.com")):
                continue
            if SOCIAL.search(l_lower):
                clean_s = link.split("?")[0].rstrip("/")
                if "/p/" not in clean_s and "/posts/" not in clean_s and clean_s not in candidate_soc:
                    candidate_soc.append(clean_s)
            elif not any(d in l_lower for d in DIRECTORIES):
                if not candidate_site:
                    candidate_site = link
        return candidate_site or "", candidate_soc, snippet_emails
    except Exception:
        return "", [], []


def query_wikidata(qid):
    """Fetches official website and email from Wikidata claims P856 and P968."""
    if not qid:
        return "", ""
    try:
        url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={qid}&format=json&props=claims"
        req = urllib.request.Request(url, headers={"User-Agent": "LeadFinder/1.1"})
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.load(r)
            entity = data.get("entities", {}).get(qid, {})
            claims = entity.get("claims", {})
            website = (
                claims.get("P856", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value", "")
            )
            email = (
                claims.get("P968", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value", "")
            )
            if email.startswith("mailto:"):
                email = email[7:]
            return website, email
    except Exception:
        return "", ""


def extract_page_emails(html):
    raw_mails = []
    raw_mails.extend(MAILTO.findall(html))
    for cf_hex in CF_EMAIL.findall(html):
        decoded = decode_cf(cf_hex)
        if decoded:
            raw_mails.append(decoded)
    raw_mails.extend(outreach.extract_emails_from_text(html))
    return raw_mails


def add_log(job, msg, level="INFO"):
    """Thread-safe timestamped diagnostic log appender for live UI tracing."""
    if not job:
        return
    txt = str(msg or "").strip()
    if txt.startswith("OK: "):
        level = "OK"
        txt = txt[4:]
    elif txt.startswith("WARN: "):
        level = "WARN"
        txt = txt[6:]
    elif txt.startswith("ERR: "):
        level = "ERR"
        txt = txt[5:]
    entry = {"ts": time.strftime("%H:%M:%S"), "level": level, "msg": txt}
    lock = job.get("_lock")
    if lock:
        with lock:
            job["logs"].append(entry)
    else:
        job["logs"].append(entry)


def _mx_filter(emails_list, biz_name="", log_fn=None):
    """Filters out emails whose domain has no valid MX mail server."""
    verified = []
    for em in outreach.filter_valid_emails(emails_list):
        has_mx, reason = outreach.verify_email_mx(em)
        if has_mx:
            verified.append(em)
        elif log_fn:
            log_fn(f"WARN: [{biz_name}] Dropped {em} ({reason})")
    return verified


def check_site(url, biz_name="", city="", wikidata_id="", category="", existing_socials=(), existing_phone="", settings=None, log_fn=None):
    """
    Performs full website verification, live technical/conversion audit, tech-stack & owner detection,
    MX-verified email hunting, and social discovery.
    Returns dict with status, note, socials, email, verified_url, audit_issues, phone, email_confidence, email_source, tech_stack, owner_name.
    """
    s = settings or outreach.get_settings()
    url = (url or "").strip()
    socials = list(existing_socials or [])
    emails = []
    discovered_phone = existing_phone or ""
    email_source = ""
    email_confidence = ""

    # 1. Check Wikidata if available
    if not url and wikidata_id:
        wiki_web, wiki_mail = query_wikidata(wikidata_id)
        if wiki_web:
            url = wiki_web
        if wiki_mail:
            emails.append(wiki_mail)
            email_source = "Wikidata"

    # 2. If still no URL, run online discovery
    if not url:
        discovered_url, discovered_soc, snippet_mails = discover_online(biz_name, city)
        socials.extend(discovered_soc)
        for sm in snippet_mails:
            if outreach.is_email_relevant_to_business(sm, biz_name, "", ""):
                emails.append(sm)
                email_source = email_source or "Search Snippet"
        if discovered_url:
            url = discovered_url

    # 3. If no website OR social-only URL: hunt emails, socials & phone with strict relevance
    if not url or SOCIAL.search(url):
        if url and SOCIAL.search(url):
            socials.append(url)
        hunted_mails, hunted_soc, hunted_phone = outreach.hunt_emails_without_website(
            biz_name, city, socials, discovered_phone
        )
        if hunted_mails:
            emails.extend(hunted_mails)
            email_source = email_source or "Directory / Social Snippet"
        socials.extend(hunted_soc)
        if hunted_phone and not discovered_phone:
            discovered_phone = hunted_phone

        clean_mails = _mx_filter(emails, biz_name, log_fn)
        clean_socs = list(dict.fromkeys(socials))[:5]
        email_str = ", ".join(clean_mails[:3])
        if email_str:
            email_confidence = "verified_scraped"

        if clean_socs or (url and SOCIAL.search(url)):
            return {
                "status": "social_only",
                "note": "Social profile only — needs a dedicated website",
                "socials": clean_socs,
                "email": email_str,
                "verified_url": url if (url and SOCIAL.search(url)) else (clean_socs[0] if clean_socs else ""),
                "audit_issues": ["No Dedicated Website", "Relying on Social Links Only"],
                "phone": discovered_phone,
                "email_confidence": email_confidence,
                "email_source": email_source,
                "tech_stack": "",
                "owner_name": "",
            }
        return {
            "status": "no_website",
            "note": "No website found — prime web design prospect",
            "socials": [],
            "email": email_str,
            "verified_url": "",
            "audit_issues": ["Zero Web Presence", "Missing Google Maps Website"],
            "phone": discovered_phone,
            "email_confidence": email_confidence,
            "email_source": email_source,
            "tech_stack": "",
            "owner_name": "",
        }

    # 4. Fetch and verify regular website
    html, final_url, note, is_working, code, elapsed_sec = fetch_page(url)

    if not is_working:
        hunted_mails, hunted_soc, hunted_phone = outreach.hunt_emails_without_website(
            biz_name, city, socials, discovered_phone
        )
        if hunted_mails:
            emails.extend(hunted_mails)
            email_source = email_source or "Snippet Fallback"
        socials.extend(hunted_soc)
        if hunted_phone and not discovered_phone:
            discovered_phone = hunted_phone
        clean_mails = _mx_filter(emails, biz_name, log_fn)
        return {
            "status": "broken",
            "note": note,
            "socials": list(dict.fromkeys(socials))[:5],
            "email": ", ".join(clean_mails[:3]),
            "verified_url": url,
            "audit_issues": [f"Broken Site ({note})"],
            "phone": discovered_phone,
            "email_confidence": "verified_scraped" if clean_mails else "",
            "email_source": email_source,
            "tech_stack": "",
            "owner_name": "",
        }

    # Check HTML meta-refresh redirect (1 hop)
    refresh_match = REFRESH_URL.search(html)
    if refresh_match:
        redirect_target = refresh_match.group(1).strip()
        if not redirect_target.startswith("http"):
            redirect_target = urllib.parse.urljoin(final_url, redirect_target)
        r_html, r_final, r_note, r_working, r_code, r_elapsed = fetch_page(redirect_target, timeout=5)
        if r_working and r_html:
            html, final_url, elapsed_sec = r_html, r_final, r_elapsed

    # Check Parked Domain / Default server page
    if PARKED.search(html):
        hunted_mails, hunted_soc, hunted_phone = outreach.hunt_emails_without_website(
            biz_name, city, socials, discovered_phone
        )
        clean_mails = _mx_filter(emails + hunted_mails, biz_name, log_fn)
        socials.extend(hunted_soc)
        return {
            "status": "broken",
            "note": "Domain parked or for sale",
            "socials": list(dict.fromkeys(socials))[:5],
            "email": ", ".join(clean_mails[:3]),
            "verified_url": final_url,
            "audit_issues": ["Expired / Parked Domain"],
            "phone": discovered_phone or hunted_phone,
            "email_confidence": "verified_scraped" if clean_mails else "",
            "email_source": "Snippet Fallback" if clean_mails else "",
            "tech_stack": "",
            "owner_name": "",
        }

    if len(html.strip()) < 80 and not code:
        return {
            "status": "broken",
            "note": "Empty page response",
            "socials": list(dict.fromkeys(socials))[:5],
            "email": "",
            "verified_url": final_url,
            "audit_issues": ["Blank / Broken Page"],
            "phone": discovered_phone,
            "email_confidence": "",
            "email_source": "",
            "tech_stack": "",
            "owner_name": "",
        }

    # 5. Extract emails, tech stack & owner name from working homepage
    raw_mails = extract_page_emails(html)
    if raw_mails:
        email_source = "Website Homepage"
    socials.extend(SOC.findall(html))
    tech_stack = outreach.detect_tech_stack(html)
    owner_name = outreach.extract_decision_maker(html)
    evidence_quote, evidence_pain = outreach.extract_evidence_quote(html)

    # 6. Crawl up to 4 high-value subpages (/contact, /about, /privacy, /impressum, /terms, /booking, /enquiries)
    if not raw_mails or not owner_name or not evidence_quote:
        contact_links = list(dict.fromkeys(CONTACT_LINK.findall(html)))[:4]
        for sub_raw in contact_links:
            sub_url = sub_raw.strip()
            if not sub_url.startswith("http"):
                sub_url = urllib.parse.urljoin(final_url, sub_url)
            if not outreach.is_safe_public_url(sub_url):
                continue
            try:
                sub_req = urllib.request.Request(sub_url, headers=HEADERS)
                with urllib.request.urlopen(sub_req, timeout=3.5, context=SSL_UNVERIFIED) as s_resp:
                    s_html = s_resp.read(250000).decode("utf-8", "ignore")
                    if not owner_name:
                        owner_name = outreach.extract_decision_maker(s_html)
                    if not evidence_quote:
                        evidence_quote, evidence_pain = outreach.extract_evidence_quote(s_html)
                    if not raw_mails:
                        sub_emails = extract_page_emails(s_html)
                        if sub_emails:
                            raw_mails.extend(sub_emails)
                            email_source = f"Website Subpage ({urllib.parse.urlparse(sub_url).path[:24] or '/contact'})"
                    socials.extend(SOC.findall(s_html))
                    if raw_mails and owner_name and evidence_quote:
                        break
            except Exception:
                pass

    valid_emails = _mx_filter(emails + raw_mails, biz_name, log_fn)
    if valid_emails:
        email_confidence = "verified_scraped"

    # 7. Site-restricted search if still no email
    if not valid_emails:
        site_search_mails = _mx_filter(outreach.hunt_site_search_emails(final_url, biz_name), biz_name, log_fn)
        if site_search_mails:
            valid_emails.extend(site_search_mails)
            email_confidence = "verified_scraped"
            email_source = "Indexed Site Search"

    # 8. Optional Hunter.io domain search
    if not valid_emails and s.get("hunter_api_key"):
        hunter_mails = _mx_filter(outreach.query_hunter_domain(final_url, s["hunter_api_key"]), biz_name, log_fn)
        if hunter_mails:
            valid_emails.extend(hunter_mails)
            email_confidence = "verified_scraped"
            email_source = "Hunter.io"

    # 9. Relevance-checked snippet search
    if not valid_emails:
        hunted_mails, hunted_soc, hunted_phone = outreach.hunt_emails_without_website(
            biz_name, city, socials, discovered_phone
        )
        hunted_verified = _mx_filter(hunted_mails, biz_name, log_fn)
        if hunted_verified:
            valid_emails.extend(hunted_verified)
            email_confidence = "verified_scraped"
            email_source = "Web Snippet"
        socials.extend(hunted_soc)
        if hunted_phone and not discovered_phone:
            discovered_phone = hunted_phone

    # 10. Conservative MX-verified domain email inference (marked inferred, NOT auto-sent by default!)
    if not valid_emails:
        candidates = outreach.derive_domain_emails(final_url, category=category)
        if candidates:
            valid_emails.extend(candidates[:1])
            email_confidence = "domain_inferred"
            email_source = "MX-Verified Domain Guess"

    # 11. Live Technical, SEO & Conversion Audit
    audit_issues = outreach.audit_working_website(html, final_url, note, elapsed_sec, category)

    clean_socials = list(dict.fromkeys(socials))[:5]
    valid_emails = outreach.sort_emails_by_role(valid_emails)
    email_str = ", ".join(valid_emails[:3])

    return {
        "status": "working",
        "note": note,
        "socials": clean_socials,
        "email": email_str,
        "verified_url": final_url,
        "audit_issues": audit_issues,
        "phone": discovered_phone,
        "email_confidence": email_confidence,
        "email_source": email_source,
        "tech_stack": tech_stack,
        "owner_name": owner_name,
        "evidence_quote": evidence_quote,
        "evidence_pain": evidence_pain,
    }


def enrich(job, b, settings):
    log_fn = lambda m: add_log(job, m)
    info = check_site(
        b["website"],
        biz_name=b.get("name", ""),
        city=b.get("city", ""),
        wikidata_id=b.get("wikidata_id", ""),
        category=b.get("category", ""),
        existing_socials=b.get("socials", ()),
        existing_phone=b.get("phone", ""),
        settings=settings,
        log_fn=log_fn,
    )
    b["site_status"] = info["status"]
    b["site_note"] = info["note"]
    b["audit_issues"] = info["audit_issues"]
    b["tech_stack"] = info["tech_stack"]
    b["owner_name"] = info["owner_name"]
    b["evidence_quote"] = info.get("evidence_quote", "")
    b["evidence_pain"] = info.get("evidence_pain", "")
    b["email_confidence"] = info["email_confidence"]
    b["email_source"] = info["email_source"]

    if info["verified_url"] and not b["website"]:
        b["website"] = info["verified_url"]
    if info["phone"] and not b.get("phone"):
        b["phone"] = info["phone"]
    b["socials"] = list(dict.fromkeys((b.get("socials") or []) + info["socials"]))[:5]

    # Combine OSM email (if any) with discovered email, checking MX
    if b.get("email"):
        osm_mails = _mx_filter(b["email"].split(","), b.get("name", ""), log_fn)
        disc_mails = info["email"].split(",") if info["email"] else []
        combined = outreach.filter_valid_emails(osm_mails + disc_mails)
        b["email"] = ", ".join(combined[:3])
        if osm_mails:
            b["email_confidence"] = "verified_scraped"
            b["email_source"] = "OpenStreetMap Tag"
    else:
        b["email"] = info["email"]

    # Cross-Lead Duplicate Email Guard:
    # If the exact same email appears on >= 2 DIFFERENT business names in this search,
    # it is almost certainly a directory/aggregator leak — drop it!
    primary_email = (b["email"] or "").split(",")[0].strip().lower()
    if primary_email:
        norm_biz = re.sub(r"[^a-z0-9]", "", (b.get("name") or "").lower())[:12]
        with job["_lock"]:
            seen_map = job["seen_emails"].setdefault(primary_email, set())
            if len(seen_map) >= 2 and norm_biz not in seen_map:
                add_log(job, f"Removed repeated/directory email {primary_email} from '{b.get('name')}'", "WARN")
                b["email"] = ""
                b["email_confidence"] = ""
                b["email_source"] = ""
                primary_email = ""
            else:
                seen_map.add(norm_biz)

    b["dm_info"] = outreach.resolve_dm_channel(b["socials"], b.get("phone", ""))
    b["lead_score"] = outreach.calculate_lead_score(b)

    pitch = outreach.generate_ai_outreach(b, settings)
    b["outreach_subject"] = pitch["subject"]
    b["outreach_body"] = pitch["body"]
    b["outreach_dm"] = pitch["dm"]

    b["email_status"] = ""
    b["email_status_note"] = ""

    if primary_email:
        add_log(job, f"[{b.get('name')}] Found {primary_email} via {b.get('email_source') or 'Web'} ({b.get('email_confidence')})", "OK")
        ledger_rec = outreach.get_sent_ledger().get(primary_email)
        if ledger_rec:
            l_stat = ledger_rec.get("status", "sent")
            b["email_status"] = "bounced" if l_stat == "bounced" else ("replied" if l_stat == "replied" else "already_sent")
            b["email_status_note"] = f"Ledger: {l_stat} ({primary_email})"
        elif settings.get("auto_send_email"):
            if b.get("email_confidence") == "domain_inferred" and not settings.get("auto_send_inferred"):
                b["email_status"] = "inferred_hold"
                b["email_status_note"] = f"Inferred email ({primary_email}) held from auto-send to protect bounce rate"
                add_log(job, f"[{b.get('name')}] Held inferred email {primary_email} from auto-send (anti-bounce)", "WARN")
            else:
                res = outreach.send_smtp_email(
                    primary_email,
                    b["outreach_subject"],
                    b["outreach_body"],
                    biz_name=b.get("name", ""),
                    force=False,
                    throttle=True,
                    meta={
                        "category": b.get("category", ""),
                        "city": b.get("city", ""),
                        "site_status": b.get("site_status", ""),
                        "audit_issues": b.get("audit_issues", []),
                    },
                )
                b["email_status"] = res["status"]
                b["email_status_note"] = res["message"]
                if res.get("ok") and res["status"] in ("sent", "simulated"):
                    with job["_lock"]:
                        job["sent_count"] = job.get("sent_count", 0) + 1
                    add_log(job, f"[{b.get('name')}] {res['message']}", "OK")
                elif not res.get("ok"):
                    add_log(job, f"[{b.get('name')}] {res['message']}", "ERR")

    # Optional WhatsApp Baileys number check & anti-ban auto-send
    b["wa_verified"] = None
    b["wa_status"] = ""
    if b.get("phone") and job.get("wa_connected"):
        is_wa = outreach.wa_check_number(b["phone"])
        b["wa_verified"] = is_wa
        if is_wa is False:
            add_log(job, f"[{b.get('name')}] {b['phone']} is NOT on WhatsApp (landline/invalid)", "WARN")
        elif is_wa is True:
            add_log(job, f"[{b.get('name')}] {b['phone']} verified on WhatsApp", "OK")
            if settings.get("wa_auto_send"):
                w_res = outreach.send_whatsapp_message(
                    b["phone"],
                    b.get("outreach_dm") or b.get("outreach_body"),
                    biz_name=b.get("name", ""),
                    force=False,
                    throttle=True,
                )
                b["wa_status"] = w_res.get("status", "")
                if w_res.get("ok") and w_res.get("status") == "sent":
                    add_log(job, f"[{b.get('name')}] WhatsApp sent to {b['phone']}", "OK")
                elif not w_res.get("ok"):
                    add_log(job, f"[{b.get('name')}] WA skipped/err: {w_res.get('message')}", "WARN")

    with job["_lock"]:
        job["results"].append(b)


def run(job, p):
    try:
        settings = outreach.get_settings()
        wa_st = outreach.wa_get_status()
        job["wa_connected"] = bool(wa_st.get("connected"))
        if job["wa_connected"]:
            add_log(job, f"WhatsApp Baileys connected ({wa_st.get('phone')}) — live number verification active", "OK")
        add_log(job, f"Starting search: '{p.get('category')}' in '{p.get('city')}' via {p.get('provider')}", "INFO")
        seen = set()

        def on_provider_log(m):
            job["msg"] = m
            add_log(job, m, "INFO")

        for b in providers.PROVIDERS[p["provider"]]["fn"](p, on_provider_log):
            if b["id"] in seen:
                continue
            seen.add(b["id"])
            job["found"] = len(seen)
            job["futs"].append(POOL.submit(enrich, job, b, settings))

        job["msg"] = f"Enriching {len(seen)} leads (auditing sites, verifying MX & drafting pitches)"
        add_log(job, job["msg"], "INFO")
        for f in job["futs"]:
            f.result()
        job["msg"] = "Done"
        add_log(job, f"Completed: {len(job['results'])} leads audited, {job.get('sent_count', 0)} emails sent.", "OK")
    except Exception as e:
        err_msg = str(e)
        if "10060" in err_msg:
            job["error"] = "Network timeout (WinError 10060): Unable to reach map server. Please check your internet connection."
        else:
            job["error"] = err_msg
        add_log(job, f"Job failed: {job['error']}", "ERR")
    job["done"] = True


class H(BaseHTTPRequestHandler):
    def reply(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length))

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/api/providers":
            return self.reply(
                200,
                [{"id": k, "label": v["label"], "key": v["key"]} for k, v in providers.PROVIDERS.items()],
            )
        if u.path == "/api/settings":
            s = outreach.get_settings()
            ledger = outreach.get_sent_ledger()
            return self.reply(200, {
                "settings": s,
                "sent_total": len(ledger),
                "sent_today": outreach.count_emails_sent_today(),
            })
        if u.path == "/api/crm":
            s = outreach.get_settings()
            return self.reply(200, {
                "leads": outreach.get_crm_leads(),
                "sent_today": outreach.count_emails_sent_today(),
                "daily_limit": int(s.get("daily_send_limit") or 40),
            })
        if u.path == "/api/wa/status":
            s = outreach.get_settings()
            st = outreach.wa_get_status()
            st["sent_today"] = outreach.count_wa_sent_today()
            st["daily_limit"] = int(s.get("wa_daily_limit") or 15)
            return self.reply(200, st)
        if u.path.startswith("/api/job/"):
            j = JOBS.get(u.path.split("/")[-1])
            if not j:
                return self.reply(404, {"error": "Unknown job"})
            qs = urllib.parse.parse_qs(u.query)
            since = int(qs.get("since", [0])[0])
            log_since = int(qs.get("log_since", [0])[0])
            with j["_lock"]:
                res_slice = j["results"][since:]
                log_slice = j["logs"][log_since:]
                payload = {
                    "msg": j["msg"],
                    "found": j["found"],
                    "done": j["done"],
                    "error": j["error"],
                    "sent_count": j["sent_count"],
                    "results": res_slice,
                    "logs": log_slice,
                }
            return self.reply(200, payload)
        f = (STATIC / ("index.html" if u.path == "/" else u.path.lstrip("/"))).resolve()
        if f.is_file() and STATIC in f.parents:
            return self.reply(200, f.read_bytes(), TYPES.get(f.suffix, "application/octet-stream"))
        self.reply(404, {"error": "Not found"})

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        try:
            p = self.read_json()
        except Exception as e:
            return self.reply(400, {"error": f"Invalid JSON: {e}"})

        if u.path == "/api/settings":
            updated = outreach.save_settings(p)
            ledger = outreach.get_sent_ledger()
            return self.reply(200, {"ok": True, "settings": updated, "sent_total": len(ledger)})

        if u.path == "/api/send-email":
            res = outreach.send_smtp_email(
                p.get("email", ""),
                p.get("subject", ""),
                p.get("body", ""),
                biz_name=p.get("name", ""),
                force=bool(p.get("force", True)),
                meta=p.get("meta"),
            )
            return self.reply(200 if res.get("ok") else 400, res)

        if u.path == "/api/test-smtp":
            if p.get("settings"):
                outreach.save_settings(p["settings"])
            s = outreach.get_settings()
            target = (p.get("to") or s.get("smtp_email") or "").strip()
            if not target:
                return self.reply(400, {"ok": False, "message": "Enter your SMTP Email first."})
            res = outreach.send_smtp_email(
                target,
                "LeadFinder SMTP Test — Connected!",
                f"Hi {s.get('sender_name', 'there')},\n\nYour LeadFinder auto-outreach SMTP connection is working properly!\n\n— LeadFinder",
                biz_name="SMTP Test",
                force=True,
            )
            return self.reply(200 if res.get("ok") else 400, res)

        if u.path == "/api/crm/sync-imap":
            res = outreach.check_imap_inbox()
            return self.reply(200 if res.get("ok") else 400, res)

        if u.path == "/api/crm/send-followups":
            res = outreach.send_due_followups(target_email=p.get("email"))
            return self.reply(200, res)

        if u.path == "/api/crm/status":
            ok = outreach.mark_lead_status(p.get("email", ""), p.get("status", "opted_out"))
            return self.reply(200 if ok else 404, {"ok": ok})

        if u.path == "/api/wa/connect":
            return self.reply(200, outreach.wa_sidecar_request("/connect", {}, timeout=5))

        if u.path == "/api/wa/logout":
            return self.reply(200, outreach.wa_sidecar_request("/logout", {}, timeout=5))

        if u.path == "/api/wa/sync-replies":
            res = outreach.sync_whatsapp_replies()
            return self.reply(200 if res.get("ok") else 400, res)

        if u.path == "/api/wa/send":
            res = outreach.send_whatsapp_message(
                p.get("phone", ""),
                p.get("message", ""),
                biz_name=p.get("name", ""),
                force=bool(p.get("force", True)),
                throttle=bool(p.get("throttle", False)),
            )
            return self.reply(200 if res.get("ok") else 400, res)

        if u.path == "/api/regenerate-pitch":
            lead = p.get("lead") or {}
            angle = p.get("angle") or "auto"
            use_ai = bool(p.get("use_ai", False))
            pitch = (
                outreach.generate_ai_outreach(lead, angle_override=angle)
                if use_ai
                else outreach.generate_outreach(lead, angle_override=angle)
            )
            return self.reply(200, {"ok": True, **pitch})

        # Default: /api/start
        jid = uuid.uuid4().hex[:8]
        JOBS[jid] = job = {
            "results": [],
            "logs": [],
            "seen_emails": {},
            "futs": [],
            "_lock": threading.Lock(),
            "msg": "Starting",
            "found": 0,
            "sent_count": 0,
            "done": False,
            "error": None,
        }
        threading.Thread(target=run, args=(job, p), daemon=True).start()
        self.reply(200, {"id": jid})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print("LeadFinder running at http://localhost:8000")
    ThreadingHTTPServer(("127.0.0.1", 8000), H).serve_forever()
