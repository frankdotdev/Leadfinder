const $ = s => document.querySelector(s);

const ICONS = {
  phone: `<svg class="lucide-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>`,
  mail: `<svg class="lucide-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"></rect><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path></svg>`,
  mapPin: `<svg class="lucide-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"></path><circle cx="12" cy="10" r="3"></circle></svg>`,
  star: `<svg class="lucide-icon star-icon" width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>`,
  globe: `<svg class="lucide-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"></path><path d="M2 12h20"></path></svg>`,
  instagram: `<svg class="lucide-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="20" x="2" y="2" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" x1="17.5" y1="6.5" y2="6.5"></line></svg>`,
  facebook: `<svg class="lucide-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"></path></svg>`,
  twitter: `<svg class="lucide-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z"></path></svg>`,
  linkedin: `<svg class="lucide-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect width="4" height="12" x="2" y="9"></rect><circle cx="4" cy="4" r="2"></circle></svg>`,
  tiktok: `<svg class="lucide-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12a4 4 0 1 0 4 4V4a5 5 0 0 0 5 5"></path></svg>`,
  whatsapp: `<svg class="lucide-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>`,
  external: `<svg class="lucide-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>`
};

const TABS = {
  nowebsite: ["No website", r => r.site_status === "no_website"],
  social_only: ["Social only", r => r.site_status === "social_only"],
  broken: ["Broken website", r => r.site_status === "broken"],
  working: ["Working website", r => r.site_status === "working"],
  all: ["All", () => true]
};

const LABEL = {
  no_website: "No website",
  social_only: "Social only",
  broken: "Broken website",
  working: "Working"
};

let rows = [];
let tab = "nowebsite";
let timer = null;
const contacted = JSON.parse(localStorage.getItem("contacted") || "{}");

const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
}[c]));

fetch("/api/providers")
  .then(r => r.json())
  .then(ps => {
    $("#provider").innerHTML = ps.map(p => `<option value="${p.id}" data-key="${p.key}">${esc(p.label)}</option>`).join("");
    syncForm();
    render();
  })
  .catch(err => {
    $("#status").textContent = "Failed to load map providers: " + err.message;
  });

function syncForm() {
  const opt = $("#provider").selectedOptions[0];
  const needsKey = opt ? opt.dataset.key === "true" : false;
  $("#keyBox").hidden = !needsKey;
  $("#gridBox").hidden = $("#provider").value !== "google";
}

function view() {
  const q = ($("#q").value || "").trim().toLowerCase();
  return rows
    .filter(TABS[tab][1])
    .filter(r => {
      if (!q) return true;
      const haystack = [r.name, r.category, r.address, r.email, r.phone, r.website, r.site_note].join(" ").toLowerCase();
      return haystack.includes(q);
    })
    .sort((a, b) => (b.reviews || 0) - (a.reviews || 0));
}

function render() {
  // Render Tab counts
  $("#tabs").innerHTML = Object.entries(TABS).map(([k, [l, f]]) => {
    const count = rows.filter(f).length;
    return `<button type="button" data-t="${k}" class="${k === tab ? "on" : ""}">${l} (${count})</button>`;
  }).join("");

  const visible = view();
  if (visible.length === 0) {
    $("#rows").innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 32px 14px; color: var(--mute);">
      ${rows.length === 0 ? "Pick a city and business type, then click Search." : "No businesses match this tab or filter."}
    </td></tr>`;
    return;
  }

  $("#rows").innerHTML = visible.map(r => {
    // Phone & WhatsApp
    const rawDigits = (r.phone || "").replace(/\D/g, "");
    const wa = rawDigits.length >= 7
      ? `<a href="https://wa.me/${rawDigits}" target="_blank" rel="noopener" class="badge-wa" title="Open WhatsApp chat">${ICONS.whatsapp} WhatsApp</a>`
      : "";
    
    const phoneHtml = r.phone
      ? `<a href="tel:${esc(r.phone)}" class="contact-item">${ICONS.phone} ${esc(r.phone)}${wa}</a>`
      : "";

    // Social Links
    const socialLinks = (r.socials || []).map(s => {
      let icon = ICONS.globe;
      let label = s.replace(/https?:\/\/(www\.)?/, "").split("/")[0];
      if (s.includes("instagram.com")) { icon = ICONS.instagram; label = "Instagram"; }
      else if (s.includes("facebook.com")) { icon = ICONS.facebook; label = "Facebook"; }
      else if (s.includes("twitter.com") || s.includes("x.com")) { icon = ICONS.twitter; label = "X"; }
      else if (s.includes("linkedin.com")) { icon = ICONS.linkedin; label = "LinkedIn"; }
      else if (s.includes("tiktok.com")) { icon = ICONS.tiktok; label = "TikTok"; }
      return `<a href="${esc(s)}" target="_blank" rel="noopener" class="contact-item">${icon} ${label}</a>`;
    });

    const contactHtml = [phoneHtml, ...socialLinks].filter(Boolean).join("") || `<span class="dim">–</span>`;

    // Email
    let emailHtml = `<span class="dim">–</span>`;
    if (r.email) {
      const allMails = r.email.split(",").map(m => m.trim()).filter(Boolean);
      if (allMails.length > 0) {
        const primary = allMails[0];
        const secondary = allMails.slice(1);
        emailHtml = `<a href="mailto:${esc(primary)}" class="email-link" title="Send email to ${esc(primary)}">${ICONS.mail} ${esc(primary)}</a>` +
          (secondary.length > 0 ? `<span class="email-secondary">+${secondary.length} more: ${esc(secondary.join(", "))}</span>` : "");
      }
    }

    // Website & Status
    const statusTag = `<span class="tag ${r.site_status}">${LABEL[r.site_status] || r.site_status}</span>`;
    const cleanUrl = r.website ? r.website.replace(/^https?:\/\/(www\.)?/, "").replace(/\/$/, "") : "";
    const siteUrlHtml = r.website
      ? `<a href="${esc(r.website)}" target="_blank" rel="noopener" class="site-link" title="${esc(r.website)}">${esc(cleanUrl.slice(0, 32))}${cleanUrl.length > 32 ? "…" : ""} ${ICONS.external}</a>`
      : "";
    const siteNoteHtml = r.site_note ? `<span class="site-note">${esc(r.site_note)}</span>` : "";

    const websiteHtml = `<div class="site-wrap">${statusTag}${siteUrlHtml}${siteNoteHtml}</div>`;

    // Map Link
    const mapHtml = r.maps_url
      ? `<a href="${esc(r.maps_url)}" target="_blank" rel="noopener" class="map-link">${ICONS.mapPin} Map</a>`
      : `<span class="dim">–</span>`;

    // Rating
    const ratingHtml = r.rating
      ? `<span class="rating-val">${ICONS.star} ${r.rating}</span>${r.reviews ? `<br><small class="dim">(${r.reviews} reviews)</small>` : ""}`
      : `<span class="dim">–</span>`;

    return `<tr>
      <td class="td-done">
        <input type="checkbox" data-id="${esc(r.id)}" ${contacted[r.id] ? "checked" : ""} aria-label="Mark contacted">
      </td>
      <td>
        <span class="biz-name">${esc(r.name)}</span>
        ${r.address ? `<span class="biz-meta">${esc(r.address)}</span>` : ""}
        ${r.category ? `<span class="category-tag">${esc(r.category)}</span>` : ""}
      </td>
      <td>${emailHtml}</td>
      <td><div class="contacts-wrap">${contactHtml}</div></td>
      <td>${websiteHtml}</td>
      <td>${ratingHtml}</td>
      <td>${mapHtml}</td>
    </tr>`;
  }).join("");
}

$("#provider").onchange = syncForm;
$("#q").oninput = render;

$("#tabs").onclick = e => {
  const btn = e.target.closest("button");
  if (btn && btn.dataset.t) {
    tab = btn.dataset.t;
    render();
  }
};

$("#rows").onchange = e => {
  if (e.target.dataset.id) {
    contacted[e.target.dataset.id] = e.target.checked;
    localStorage.setItem("contacted", JSON.stringify(contacted));
  }
};

$("#f").onsubmit = async e => {
  e.preventDefault();
  clearInterval(timer);
  rows = [];
  render();
  $("#go").disabled = true;
  $("#status").textContent = "Initializing search...";

  const body = {
    provider: $("#provider").value,
    key: $("#key").value,
    city: $("#city").value,
    category: $("#cat").value,
    grid: $("#grid").value
  };

  try {
    const res = await fetch("/api/start", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(body)
    });
    const {id} = await res.json();

    timer = setInterval(async () => {
      try {
        const j = await (await fetch(`/api/job/${id}?since=${rows.length}`)).json();
        if (j.results && j.results.length > 0) {
          rows.push(...j.results);
          render();
        }
        $("#status").textContent = j.error
          ? "Error: " + j.error
          : `${j.msg}: ${j.found} discovered, ${rows.length} verified`;

        if (j.done) {
          clearInterval(timer);
          $("#go").disabled = false;
        }
      } catch (pollErr) {
        $("#status").textContent = "Error checking progress: " + pollErr.message;
      }
    }, 1200);
  } catch (err) {
    $("#status").textContent = "Failed to start search: " + err.message;
    $("#go").disabled = false;
  }
};

$("#csv").onclick = () => {
  const currentRows = view();
  if (currentRows.length === 0) {
    alert("No leads to export in the current view.");
    return;
  }
  const cols = [
    "name", "category", "address", "email", "phone", "website",
    "site_status", "site_note", "rating", "reviews", "maps_url"
  ];
  const headerRow = cols.join(",");
  const dataRows = currentRows.map(r => {
    return cols.map(c => {
      const val = r[c] ?? "";
      return `"${String(val).replace(/"/g, '""')}"`;
    }).join(",");
  });

  const csvContent = [headerRow, ...dataRows].join("\n");
  const blob = new Blob([csvContent], {type: "text/csv;charset=utf-8;"});
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `leads-${tab}-${new Date().toISOString().slice(0, 10)}.csv`;
  link.click();
};
