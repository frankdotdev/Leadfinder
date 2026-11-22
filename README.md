# ⚡ LeadFinder

> **High-accuracy autonomous local business lead generator, evidence-based website audit engine, and compliant cold outreach CRM for digital agencies, web developers, SEOs, and consultants.**  
> Find businesses with **no website**, a **broken website**, or **only social media profiles**, extract **verbatim operational evidence**, discover **MX-verified emails & WhatsApp numbers**, and run **anti-spam outreach & two-way IMAP follow-up sequences** with **zero external pip dependencies**.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Dependencies: Zero](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Stdlib)-success?style=flat-square)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-teal.svg?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/frankdotdev/Leadfinder/pulls)
[![Open Source Love](https://img.shields.io/badge/Open%20Source-%E2%99%A5-ff69b4?style=flat-square)](https://github.com/frankdotdev/Leadfinder)

---

## 💡 Why LeadFinder?

Digital agencies, freelance web developers, and cold outreach specialists spend hours manually browsing Google Maps to find local businesses needing web design, automation, or SEO. Commercial scrapers charge **$100+/month**, cap results behind credits, guess bouncing emails, and send generic templates.

**LeadFinder is 100% free, open-source, and runs locally with ZERO pip dependencies.** It queries multi-provider map & search APIs, crawls live sites safely with SSRF protection, verifies email domains via DNS-over-HTTPS MX lookups, grounds pitches in verbatim website quotes without hallucination, and tracks replies/bounces via two-way IMAP sync.

---

## ✨ Key Capabilities

### 🗺️ Multi-Provider Discovery & Resilient Geocoding
- **OpenStreetMap (Overpass 4-Quadrant Grid + Circuit Breaker):** Queries `node` and `way` elements across 4 city quadrants (`SW`, `SE`, `NW`, `NE`) with automatic failover across global Overpass mirrors. If mirrors are overloaded (`502`), a circuit breaker trips immediately and switches to the **5-Zone × Synonym Photon Multi-Grid** + **Nominatim Bounded Search** to break the 50-result cap and return **100–300+ businesses**.
- **Serper.dev Google Maps (2,500 free):** Optional Google Maps Places discovery returning websites, phones, ratings, and review counts.
- **Google Places API (New):** Optional grid search for global commercial coverage.
- **Multi-Engine Web Search Failover:** Optional **Serper**, **Tavily** (1,000 free/mo), **Brave Search**, **Exa AI**, and self-hosted **SearXNG** support with automatic failover to rate-limited DuckDuckGo HTML, DDG Lite, and Bing.
- **Smart State & Region Detection:** Searching broad states/provinces (e.g. `Texas`, `Ontario`, `Bavaria`) automatically targets their primary commercial hub instead of an empty rural centroid.

### 🔍 Deep Email Hunting, MX Verification & Relevance Guards
- **DNS-over-HTTPS MX Verification:** Every discovered email domain is checked against Google DNS / Cloudflare DNS (`MX` records) so nonexistent domains and dead mail servers are rejected before saving.
- **Role-Based Email Prioritization:** Automatically ranks B2B role inboxes (`procurement@`, `info@`, `contact@`, `enquiries@`, `bookings@`, `orders@`, `appointments@`) ahead of personal addresses.
- **Business Relevance & Duplicate Guards:** Search-snippet emails are strictly validated against business-name tokens and proximity; emails appearing across multiple unrelated businesses are automatically dropped as directory leaks.
- **Confidence Badges & Anti-Bounce Hold:** Distinguishes `Verified ✓` scraped emails from `Inferred MX` domain guesses, holding inferred guesses from Auto-Email by default (`auto_send_inferred: false`).
- **SSRF-Protected Deep Crawler:** Blocks private/loopback/cloud metadata IPs (`127.0.0.0/8`, `10.0.0.0/8`, `169.254.169.254`) at the DNS level while crawling homepages, `/contact`, `/about`, `/privacy`, `/terms`, `/impressum`, `/enquiries`, and `/booking` pages, plus JSON-LD schemas and Cloudflare `data-cfemail` attributes.

### 🔬 Evidence-Based Research & Live Website Audits
- **Verbatim Quote Extraction:** Extracts real operational sentences from crawled pages (e.g. `"call us to book"`, `"fill out the form"`, `"custom cakes"`) and verifies the exact quote exists verbatim before citing it in outreach.
- **Tech Stack & Decision-Maker Detection:** Identifies `WordPress`, `Wix`, `Squarespace`, `Shopify`, `GoDaddy Builder`, `Webflow`, `Weebly`, and extracts owner/doctor/founder names (`Dr. ...`, JSON-LD `founder`).
- **9-Point Technical & Conversion Audit:** Diagnoses SSL/HTTP errors, slow mobile load (>2.8s), missing mobile viewport, missing WhatsApp/AI chat widgets, missing online booking systems, missing `LocalBusiness` JSON-LD schema, missing meta descriptions, missing Meta/Google retargeting pixels, and outdated copyright years.
- **Prompt-Injection Containment:** When using optional **Gemini 2.5 Flash** or **Groq Llama 3.3 70B** AI polish, scraped website text is sandboxed inside `<untrusted_page>` XML tags.

### 🛡️ Anti-Spam Safeguards, Two-Way IMAP Triage & Follow-Up CRM
- **Deliverability & Sending Safeguards:**
  - Plain-text conversational formatting (zero tracking pixels or spammy HTML) with spam-trigger phrase cleaning.
  - Proper `Message-ID`, `Date`, `Reply-To`, and `List-Unsubscribe` headers + polite opt-out footer.
  - Configurable **Send Delay** (default `8s`), **Daily Warmup Cap** (default `40/day`), and optional **Business-Hours Safeguard** (Mon–Fri, 08:00–17:00).
- **Two-Way IMAP Auto-Triage (`CRM & Follow-Ups`):**
  - Connects via `imaplib` (read-only) to detect **Human Replies** (stops follow-ups), **Out-of-Office** auto-replies (defers follow-up by 3 days), **Opt-Out / Unsubscribe** replies (permanently suppresses), and **Bounces / NDRs** (`mailer-daemon` permanent suppression).
- **3-Stage Threaded Follow-Up Sequences:** Automatically schedules and sends `Re:` threaded Follow-Up 1 (Day 3) and Follow-Up 2 (Day 7) with `In-Reply-To` headers.
- **Live Trace & Diagnostic Logs:** Real-time collapsible terminal panel streaming geocoding, Overpass/Photon counts, MX verification results, and SMTP/WhatsApp statuses.

### 💬 Optional WhatsApp Baileys Sidecar (Anti-Ban Architecture)
- **Live `onWhatsApp()` Number Verification:** Checks discovered phone numbers against WhatsApp before messaging (`WA ✓` vs `No WA`), automatically filtering out landlines.
- **Human Presence & Typing Simulation:** Simulates `available` presence, realistic `composing` ("typing...") duration scaled to message length, and `paused` state before dispatching.
- **Anti-Ban Safeguards:** Enforces a strict daily warmup cap (default `15/day`), random jittered delays (`90–210s`), business-hours window (Mon–Fri 08:00–17:00), spintax phrasing variation, and single-send/reply suppression (`data/sent_whatsapp.json`).
- **In-Browser QR Login & Reply Sync:** Scan QR codes directly inside the **WhatsApp Bot** modal and sync incoming replies/opt-outs automatically.

---

## 🚀 Quick Start

**Zero external pip packages required.** LeadFinder runs out-of-the-box on standard Python 3.10+.

### 1. Clone the repository
```bash
git clone https://github.com/frankdotdev/Leadfinder.git
cd Leadfinder
```

### 2. Run the server
```bash
python server.py
```

### 3. Open your browser
Visit `http://127.0.0.1:8000`.

### 4. (Optional) Start the WhatsApp Baileys Sidecar
Requires **Node.js**. To enable live `onWhatsApp` number verification and automated WhatsApp outreach:
```bash
cd wa_sidecar
npm install
node server.js
```
*(Or double-click `wa_sidecar\start_wa.bat` on Windows.)* Then click **WhatsApp Bot** in the dashboard header to scan your QR code using a secondary, warmed-up WhatsApp number.

---

## 📖 Usage Guide

### Finding & Auditing Leads
1. Select **OpenStreetMap (free, no key)** (or **Serper.dev Google Maps** / **Google Places** if you have an API key).
2. Enter a **City** (e.g., `Toronto`, `London`, `Chicago`, `Miami`, `Austin`, `Manchester`).
3. Enter a **Business type** (e.g., `bakery`, `clinic`, `salon`, `restaurant`, `dentist`, `plumber`, `gym`).
4. Click **Find & Enrich Leads** and open **Live Trace & Diagnostic Logs** to monitor discovery and verification in real time.

### Configuring Search, AI & Outreach Settings
Click **Outreach & SMTP Settings** in the top bar (or configure via `.env`):
- **Identity & Pitch Angle:** Name, company, portfolio URL, default pitch angle, or custom offer.
- **SMTP & IMAP:** Gmail/Workspace email + [Google App Password](https://myaccount.google.com/apppasswords), `smtp.gmail.com:465`, `imap.gmail.com:993`.
- **Safeguards & Follow-Ups:** Send delay, daily cap, business-hours guard, `List-Unsubscribe` toggle, and Follow-Up Day 1/Day 2 intervals.
- **Optional Keys:** `SERPER_API_KEY`, `TAVILY_API_KEY`, `BRAVE_SEARCH_API_KEY`, `EXA_API_KEY`, `SEARXNG_URL`, `HUNTER_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`.

---

## 🛠️ Architecture

```
leadfinder/
├── static/
│   ├── index.html       # Dashboard, Live Trace Drawer, Pitch Modal, CRM Modal, & Settings
│   ├── style.css        # Responsive design tokens & dark terminal log styles
│   └── app.js           # Client state, live log streaming, CRM sync, & CSV export
├── providers.py         # Multi-tier map discovery (4-Quad Overpass, Photon Grid, Nominatim, Serper, Google)
├── outreach.py          # SSRF guard, DoH MX check, evidence extraction, SMTP safeguards & IMAP triage
├── server.py            # Async enrichment pipeline, duplicate guard, & REST API
├── wa_sidecar/
│   ├── package.json     # Optional Baileys WhatsApp Web sidecar dependencies
│   ├── server.js        # Local HTTP bridge for QR auth, onWhatsApp check, typing sim & replies
│   └── start_wa.bat     # 1-click Windows launcher for WhatsApp sidecar
├── data/
│   ├── geocache.json    # Local coordinate cache
│   ├── settings.json    # Persisted outreach, search & safeguard configuration
│   ├── sent_emails.json # Persistent email CRM, suppression & follow-up ledger
│   └── sent_whatsapp.json # Persistent WhatsApp single-send & reply ledger
├── .gitignore
└── README.md
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

---

## 👨‍💻 Author & Credits

Built with ❤️ by **[Frank Oge](https://frankoge.com)** of **[Hackverse Technologies](https://hackversetechnologies.vercel.app)**.
