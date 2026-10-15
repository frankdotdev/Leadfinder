# ⚡ LeadFinder

> **High-accuracy local business lead generator for web designers, SEOs, and digital agencies.**  
> Find businesses with **no website**, a **broken website**, or **only social media profiles**, complete with **verified emails**, phone numbers, and WhatsApp links.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-teal.svg?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/frankdotdev/Leadfinder/pulls)
[![Open Source Love](https://img.shields.io/badge/Open%20Source-%E2%99%A5-ff69b4?style=flat-square)](https://github.com/frankdotdev/Leadfinder)

---

## 💡 Why LeadFinder?

Digital agencies, freelance web developers, and cold outreach specialists spend hours manually browsing Google Maps to find businesses that need a website or a redesign. Existing commercial scrapers cost upwards of **$100+/month**, charge per lead credit, and often report false positives.

**LeadFinder is 100% free, open-source, and runs locally.** It queries live map databases, performs multi-step website health diagnostics, extracts contact emails, and categorizes leads into high-converting outreach buckets.

---

## ✨ Features

- 🗺️ **Dual Map Providers**
  - **OpenStreetMap (Overpass API)**: 100% free, unmetered, and requires no API key or credit card.
  - **Google Places API (New)**: High-precision location grid search for global coverage.

- 🔍 **Multi-Tier Lead Categorization**
  - **No Website**: Zero digital footprint — the highest-converting leads for custom web design pitches.
  - **Social Only**: Businesses using only Facebook, Instagram, TikTok, or Linktree — pitch them on owning their brand and converting followers into customers.
  - **Broken Website**: Detects expired domains, DNS failures (`getaddrinfo` errors), HTTP 404/500 errors, and parked pages (GoDaddy, Sedo, Dan.com, HugeDomains, suspended accounts).
  - **Working Website**: Verifies healthy, responsive sites.

- ✉️ **Deep Email & Contact Extraction**
  - **Cloudflare Email De-obfuscation**: Decodes protected `data-cfemail` addresses automatically.
  - **Deep Crawler**: Scans `/contact`, `/contact-us`, and `/about` subpages if no email is found on the homepage.
  - **Phone & WhatsApp**: Formats phone numbers and generates direct one-click WhatsApp chat links.

- 🛡️ **Zero-False-Positive Engine**
  - **HTTPS-First with HTTP Fallback**: Prevents modern TLS connection drops.
  - **SSL Warning Tolerance**: Validates sites with self-signed or intermediate cert warnings so live sites aren't misclassified as broken.
  - **DNS Apex & WWW Fallback**: Automatically tries both `example.com` and `www.example.com`.
  - **Realistic Browser Emulation**: Headers mimic modern browsers to avoid Cloudflare/Akamai bot blocks.

- 🎨 **Modern, Responsive Dashboard**
  - Built with clean **Lucide SVG icons** and modern typography.
  - Fully responsive on desktop, tablet, and mobile screens.
  - Instant live search and category filter.
  - One-click **Export to CSV**.

---

## 🚀 Quick Start

No Node.js, npm, or heavy build tools required. LeadFinder runs with standard Python.

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
Visit:
```
http://localhost:8000
```

---

## 📖 Usage Guide

### Finding Leads with OpenStreetMap (Free)
1. Select **OpenStreetMap (free, no key)** in the map provider dropdown.
2. Enter a **City** (e.g., `Enugu, Nigeria` or `Austin, Texas`).
3. Enter a **Business type** (e.g., `restaurant`, `salon`, `clinic`, `hotel`, `plumber`, `bakery`).
4. Click **Search**. LeadFinder will query Overpass API, check domains, scrape contacts, and populate the dashboard.

### Finding Leads with Google Places (API Key)
1. Select **Google Places (API key)**.
2. Enter your Google Maps Places API key.
3. Configure the search grid (1 to 10) to subdivide the city for maximum lead extraction.
4. Click **Search**.

---

## 📊 CSV Export Format

Exported CSVs include full lead intelligence:
- `name` - Business name
- `category` - Industry / amenity type
- `address` - Physical street address
- `email` - Primary and secondary extracted emails
- `phone` - Contact phone number
- `website` - Target URL or social link
- `site_status` - `no_website`, `social_only`, `broken`, `working`
- `site_note` - Reason (e.g., `Loads fine`, `DNS lookup failed`, `Domain parked or for sale`, `HTTP 404`)
- `rating` - Google / map rating
- `reviews` - Review count
- `maps_url` - Direct link to location on Google Maps

---

## 🛠️ Architecture

```
leadfinder/
├── static/
│   ├── index.html       # Clean HTML5 UI with Lucide SVG icons & responsive design
│   ├── style.css        # Modern CSS with responsive flex/grid layout
│   └── app.js           # Client-side state, polling, filtering, & CSV export
├── providers.py         # Map providers: OpenStreetMap Overpass & Google Places
├── server.py            # Async verification engine, email extractor, & HTTP API
├── .gitignore           # Git ignore rules
└── README.md            # Documentation
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the project (`https://github.com/frankdotdev/Leadfinder/fork`)
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

If you found LeadFinder helpful, please give it a ⭐️ on GitHub!

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

---

## 👨‍💻 Author & Credits

Built with ❤️ by **[Frank Oge](https://frankoge.com)** of **[Hackverse Technologies](https://hackversetechnologies.vercel.app)**.
