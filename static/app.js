const $ = s => document.querySelector(s);

const ICONS = {
  phone: `<svg class="lucide-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>`,
  mail: `<svg class="lucide-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"></rect><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path></svg>`,
  send: `<svg class="lucide-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`,
  copy: `<svg class="lucide-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path></svg>`,
  edit: `<svg class="lucide-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"></path><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"></path></svg>`,
  mapPin: `<svg class="lucide-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"></path><circle cx="12" cy="10" r="3"></circle></svg>`,
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
  working: ["Has Website (Pitch Upgrades)", r => r.site_status === "working"],
  all: ["All Leads", () => true]
};

const LABEL = {
  no_website: "No website",
  social_only: "Social only",
  broken: "Broken website",
  working: "Has Website"
};

let rows = [];
let tab = "nowebsite";
let timer = null;
let currentSettings = {};
let activeModalLeadId = null;
let toastTimer = null;
const contacted = JSON.parse(localStorage.getItem("contacted") || "{}");

const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
}[c]));

function showToast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.hidden = true; }, 3200);
}

async function copyText(text, label = "Copied to clipboard!") {
  try {
    await navigator.clipboard.writeText(text);
    showToast(label);
  } catch {
    const ta = document.createElement("textarea");
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    ta.remove();
    showToast(label);
  }
}

// Initialize Providers & Settings
Promise.all([
  fetch("/api/providers").then(r => r.json()),
  fetch("/api/settings").then(r => r.json())
])
  .then(([ps, sData]) => {
    $("#provider").innerHTML = ps.map(p => `<option value="${p.id}" data-key="${p.key}">${esc(p.label)}</option>`).join("");
    currentSettings = sData.settings || {};
    syncAutoSendPill(sData.sent_total || 0);
    syncForm();
    render();
  })
  .catch(err => {
    $("#status").textContent = "Failed to initialize: " + err.message;
  });

function syncAutoSendPill(sentTotal) {
  const on = Boolean(currentSettings.auto_send_email);
  $("#quickAutoSend").checked = on;
  $("#autoSendLabel").textContent = on
    ? (currentSettings.dry_run ? "Auto-Email: DRY-RUN" : "Auto-Email: ON")
    : "Auto-Email: OFF";
  if (typeof sentTotal === "number") {
    $("#sentLedgerCount").textContent = `${sentTotal} emails tracked in single-send deduplication ledger`;
  }
}

function syncForm() {
  const opt = $("#provider").selectedOptions[0];
  const needsKey = opt ? opt.dataset.key === "true" : false;
  $("#keyBox").hidden = !needsKey;
  $("#gridBox").hidden = $("#provider").value !== "google";
}

function view() {
  const q = ($("#q").value || "").trim().toLowerCase();
  const cf = $("#contactFilter").value;

  return rows
    .filter(TABS[tab][1])
    .filter(r => {
      if (cf === "has_email") return Boolean(r.email);
      if (cf === "has_dm") return Boolean((r.dm_info && r.dm_info.dm_url) || r.phone || (r.socials && r.socials.length));
      if (cf === "unsent_email") return Boolean(r.email && !["sent", "simulated", "already_sent"].includes(r.email_status));
      return true;
    })
    .filter(r => {
      if (!q) return true;
      const haystack = [
        r.name, r.category, r.address, r.email, r.phone, r.website,
        r.site_note, ...(r.audit_issues || []), r.outreach_subject
      ].join(" ").toLowerCase();
      return haystack.includes(q);
    })
    .sort((a, b) => (b.lead_score || 0) - (a.lead_score || 0) || (b.reviews || 0) - (a.reviews || 0));
}

function buildMailtoHref(r) {
  const primary = (r.email || "").split(",")[0].trim();
  const subj = encodeURIComponent(r.outreach_subject || `Quick question for ${r.name}`);
  const body = encodeURIComponent(r.outreach_body || "");
  return `mailto:${primary}?subject=${subj}&body=${body}`;
}

function buildWhatsAppPitchHref(r) {
  const digits = (r.phone || "").replace(/\D/g, "");
  if (digits.length < 7) return "";
  const text = encodeURIComponent(r.outreach_dm || r.outreach_body || "");
  return `https://wa.me/${digits}?text=${text}`;
}

function render() {
  // Render Tab counts
  $("#tabs").innerHTML = Object.entries(TABS).map(([k, [l, f]]) => {
    const count = rows.filter(f).length;
    return `<button type="button" data-t="${k}" class="${k === tab ? "on" : ""}">${esc(l)} (${count})</button>`;
  }).join("");

  // Summary metrics in status panel
  const totalEmails = rows.filter(r => r.email).length;
  const totalDms = rows.filter(r => (r.dm_info && r.dm_info.dm_url) || r.phone).length;
  const totalSent = rows.filter(r => ["sent", "simulated"].includes(r.email_status)).length;
  $("#statusStats").innerHTML = rows.length > 0
    ? `<span class="stat-pill">✉️ ${totalEmails} with Email</span>
       <span class="stat-pill">💬 ${totalDms} with DM/WhatsApp</span>
       ${totalSent > 0 ? `<span class="stat-pill stat-sent">🚀 ${totalSent} Emailed</span>` : ""}`
    : "";

  const visible = view();
  if (visible.length === 0) {
    $("#rows").innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 36px 14px; color: var(--mute);">
      ${rows.length === 0
        ? "Enter a city and business type above, then click <strong>Find &amp; Enrich Leads</strong>."
        : "No leads match this tab or filter."}
    </td></tr>`;
    return;
  }

  $("#rows").innerHTML = visible.map(r => {
    const score = r.lead_score || 60;
    const scoreClass = score >= 80 ? "score-hot" : score >= 65 ? "score-warm" : "score-ok";

    // Rating & Map
    const ratingHtml = r.rating
      ? `<span class="rating-val">${ICONS.star} ${r.rating}${r.reviews ? ` <small class="dim">(${r.reviews})</small>` : ""}</span>`
      : "";
    const mapHtml = r.maps_url
      ? `<a href="${esc(r.maps_url)}" target="_blank" rel="noopener" class="map-inline-link">${ICONS.mapPin} Maps</a>`
      : "";

    // Phone & 1-Click WhatsApp Pitch + Baileys Verification Badge
    const waPitchHref = buildWhatsAppPitchHref(r);
    const waVerBadge = r.wa_verified === true
      ? `<span class="conf-badge conf-verified" title="Verified registered on WhatsApp via Baileys">WA ✓</span>`
      : (r.wa_verified === false ? `<span class="conf-badge conf-inferred" title="Not registered on WhatsApp (landline)">No WA</span>` : "");
    const waSentBadge = r.wa_status === "sent"
      ? `<span class="email-badge sent">WA Sent ✓</span>`
      : "";
    const waBotBtn = (r.phone && r.wa_verified !== false)
      ? `<button type="button" class="btn-mini btn-wa" data-action="send-wa-bot" data-id="${esc(r.id)}" title="Send via Baileys WhatsApp Bot (with human typing simulation)">${ICONS.whatsapp} ${r.wa_status === "sent" ? "Sent ✓" : "Send WA Bot"}</button>`
      : "";
    const waBadge = waPitchHref
      ? `<a href="${esc(waPitchHref)}" target="_blank" rel="noopener" class="badge-wa" title="Open WhatsApp Web/Desktop with pitch pre-filled">${ICONS.whatsapp} wa.me</a>`
      : "";
    const phoneHtml = r.phone
      ? `<div class="contact-line"><a href="tel:${esc(r.phone)}" class="contact-item">${ICONS.phone} ${esc(r.phone)}</a>${waVerBadge}${waSentBadge}${waBadge}${waBotBtn}</div>`
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
      else if (s.includes("linktr.ee")) { icon = ICONS.globe; label = "Linktree"; }
      return `<a href="${esc(s)}" target="_blank" rel="noopener" class="social-pill">${icon} ${esc(label)}</a>`;
    }).join("");

    // Email & Dispatch Status
    let emailHtml = `<span class="dim">No email found — use Copy &amp; DM →</span>`;
    if (r.email) {
      const allMails = r.email.split(",").map(m => m.trim()).filter(Boolean);
      const primary = allMails[0];
      const secondary = allMails.slice(1);
      const confBadge = r.email_confidence === "domain_inferred"
        ? `<span class="conf-badge conf-inferred" title="${esc(r.email_source || 'MX-Verified Domain Guess')}">Inferred MX</span>`
        : `<span class="conf-badge conf-verified" title="Source: ${esc(r.email_source || 'Verified')}">Verified ✓</span>`;

      let statusBadge = "";
      if (r.email_status === "sent") {
        statusBadge = `<span class="email-badge sent" title="${esc(r.email_status_note)}">✓ Sent</span>`;
      } else if (r.email_status === "simulated") {
        statusBadge = `<span class="email-badge simulated" title="${esc(r.email_status_note)}">✓ Dry-Run Sent</span>`;
      } else if (r.email_status === "replied") {
        statusBadge = `<span class="email-badge sent" title="${esc(r.email_status_note)}">🎉 Replied</span>`;
      } else if (r.email_status === "bounced") {
        statusBadge = `<span class="email-badge err" title="${esc(r.email_status_note)}">⚠ Bounced</span>`;
      } else if (r.email_status === "inferred_hold") {
        statusBadge = `<span class="email-badge already" title="${esc(r.email_status_note)}">Held (Inferred)</span>`;
      } else if (r.email_status === "already_sent") {
        statusBadge = `<span class="email-badge already" title="${esc(r.email_status_note)}">Previously Sent</span>`;
      } else if (r.email_status === "error") {
        statusBadge = `<span class="email-badge err" title="${esc(r.email_status_note)}">SMTP Error</span>`;
      }
      emailHtml = `<div class="email-block">
        <a href="${esc(buildMailtoHref(r))}" class="email-link" title="Open in mail client">${ICONS.mail} ${esc(primary)}</a>
        ${confBadge} ${statusBadge}
        ${r.email_source ? `<span class="site-note">Source: ${esc(r.email_source)}</span>` : ""}
        ${secondary.length > 0 ? `<span class="email-secondary">+${secondary.length} more: ${esc(secondary.join(", "))}</span>` : ""}
      </div>`;
    }

    // Website Status + Live Audit / What They Need
    const statusTag = `<span class="tag ${r.site_status}">${LABEL[r.site_status] || r.site_status}</span>`;
    const cleanUrl = r.website ? r.website.replace(/^https?:\/\/(www\.)?/, "").replace(/\/$/, "") : "";
    const siteUrlHtml = r.website
      ? `<a href="${esc(r.website)}" target="_blank" rel="noopener" class="site-link" title="${esc(r.website)}">${esc(cleanUrl.slice(0, 30))}${cleanUrl.length > 30 ? "…" : ""} ${ICONS.external}</a>`
      : "";
    const siteNoteHtml = r.site_note ? `<span class="site-note">${esc(r.site_note)}</span>` : "";
    const evidenceHtml = r.evidence_quote
      ? `<div class="site-note" style="margin-top:4px; color:var(--ink-secondary);"><strong>${esc(r.evidence_pain || "Evidence")}:</strong> "${esc(r.evidence_quote)}"</div>`
      : "";

    const auditPills = (r.audit_issues || []).map(iss => `<span class="audit-pill">${esc(iss)}</span>`).join("");

    // Outreach Column: Pitch Snippet + Instant Action Buttons
    const dmInfo = r.dm_info || {};
    const hasEmail = Boolean(r.email);
    const isSent = ["sent", "simulated"].includes(r.email_status);

    const sendSmtpBtn = hasEmail
      ? `<button type="button" class="btn-mini ${isSent ? "btn-sent" : "btn-send-smtp"}" data-action="send-smtp" data-id="${esc(r.id)}" title="${isSent ? "Click to re-send via SMTP" : "Send tailored email immediately via SMTP"}">
          ${ICONS.send} ${isSent ? "Sent ✓" : "Send Email"}
        </button>
        <a href="${esc(buildMailtoHref(r))}" class="btn-mini btn-mailto" title="Open pre-filled email in your default Mail app">
          ${ICONS.mail} Mail App
        </a>`
      : "";

    let copyDmBtn = "";
    if (dmInfo.dm_url) {
      const platLabel = dmInfo.platform || "DM";
      copyDmBtn = `<button type="button" class="btn-mini btn-copy-dm" data-action="copy-open-dm" data-id="${esc(r.id)}" title="Copies tailored DM message and opens ${esc(platLabel)} (${esc(dmInfo.handle)}) in a new tab">
        ${ICONS.copy} Copy &amp; Open ${esc(platLabel)}
      </button>`;
    }

    return `<tr class="${contacted[r.id] ? "row-contacted" : ""}">
      <td class="td-done">
        <input type="checkbox" data-id="${esc(r.id)}" ${contacted[r.id] ? "checked" : ""} aria-label="Mark contacted">
      </td>
      <td class="td-biz">
        <div class="biz-header">
          <span class="biz-name">${esc(r.name)}</span>
          <span class="score-badge ${scoreClass}" title="Lead Opportunity Score">${score}</span>
        </div>
        ${r.address ? `<span class="biz-meta">${esc(r.address)}</span>` : ""}
        <div class="biz-tags-row">
          ${r.category ? `<span class="category-tag">${esc(r.category)}</span>` : ""}
          ${r.tech_stack ? `<span class="category-tag" title="Detected CMS / Platform">${esc(r.tech_stack)}</span>` : ""}
          ${r.owner_name ? `<span class="category-tag" title="Extracted Decision-Maker">👤 ${esc(r.owner_name)}</span>` : ""}
          ${ratingHtml}
          ${mapHtml}
        </div>
      </td>
      <td class="td-contacts">
        ${emailHtml}
        ${phoneHtml}
        ${socialLinks ? `<div class="socials-row">${socialLinks}</div>` : ""}
      </td>
      <td class="td-audit">
        <div class="site-wrap">
          <div class="site-top-line">${statusTag} ${siteUrlHtml}</div>
          ${siteNoteHtml}
          ${evidenceHtml}
          ${auditPills ? `<div class="audit-pills-wrap">${auditPills}</div>` : ""}
        </div>
      </td>
      <td class="td-outreach">
        <div class="outreach-box">
          <div class="outreach-preview" data-action="open-pitch" data-id="${esc(r.id)}" title="Click to view or edit full tailored writeup">
            <strong>${esc(r.outreach_subject || "Tailored Pitch")}</strong>
            <p>${esc((r.outreach_dm || r.outreach_body || "").slice(0, 115))}…</p>
          </div>
          <div class="outreach-actions">
            ${sendSmtpBtn}
            ${copyDmBtn}
            <button type="button" class="btn-mini btn-ghost" data-action="copy-pitch" data-id="${esc(r.id)}" title="Copy tailored message to clipboard">
              ${ICONS.copy} Copy
            </button>
            <button type="button" class="btn-mini btn-ghost" data-action="open-pitch" data-id="${esc(r.id)}" title="Customize pitch angle or rewrite">
              ${ICONS.edit} Pitch / Edit
            </button>
          </div>
        </div>
      </td>
    </tr>`;
  }).join("");
}

// Event Listeners
$("#provider").onchange = syncForm;
$("#q").oninput = render;
$("#contactFilter").onchange = render;

$("#tabs").onclick = e => {
  const btn = e.target.closest("button");
  if (btn && btn.dataset.t) {
    tab = btn.dataset.t;
    render();
  }
};

// Quick Auto-Send Toggle in Header
$("#quickAutoSend").onchange = async e => {
  const enabled = e.target.checked;
  if (enabled && !currentSettings.smtp_email && !currentSettings.dry_run) {
    showToast("Configure your SMTP Email & App Password (or enable Dry-Run) to auto-send emails.");
    openSettingsModal();
    e.target.checked = false;
    return;
  }
  try {
    const res = await fetch("/api/settings", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({auto_send_email: enabled})
    });
    const data = await res.json();
    currentSettings = data.settings || currentSettings;
    syncAutoSendPill(data.sent_total);
    showToast(enabled ? "Auto-Email enabled for new leads!" : "Auto-Email paused.");
  } catch (err) {
    showToast("Failed to update setting: " + err.message);
  }
};

// Table Row Delegated Actions
$("#rows").onchange = e => {
  if (e.target.type === "checkbox" && e.target.dataset.id) {
    contacted[e.target.dataset.id] = e.target.checked;
    localStorage.setItem("contacted", JSON.stringify(contacted));
    render();
  }
};

$("#rows").onclick = async e => {
  const actionEl = e.target.closest("[data-action]");
  if (!actionEl) return;
  const action = actionEl.dataset.action;
  const id = actionEl.dataset.id;
  const lead = rows.find(r => r.id === id);
  if (!lead) return;

  if (action === "open-pitch") {
    openPitchModal(lead);
  } else if (action === "copy-pitch") {
    const textToCopy = lead.email ? lead.outreach_body : (lead.outreach_dm || lead.outreach_body);
    await copyText(textToCopy, `Copied pitch for ${lead.name}!`);
  } else if (action === "copy-open-dm") {
    const dmText = lead.outreach_dm || lead.outreach_body;
    await copyText(dmText, `Copied DM for ${lead.name}! Opening ${lead.dm_info?.platform || "profile"}...`);
    contacted[lead.id] = true;
    localStorage.setItem("contacted", JSON.stringify(contacted));
    render();
    if (lead.dm_info && lead.dm_info.dm_url) {
      window.open(lead.dm_info.dm_url, "_blank", "noopener");
    }
  } else if (action === "send-smtp") {
    await sendLeadEmailViaSmtp(lead, actionEl);
  } else if (action === "send-wa-bot") {
    await sendLeadWhatsAppViaBot(lead, actionEl);
  }
};

async function sendLeadWhatsAppViaBot(lead, btnEl) {
  if (!lead.phone) return;
  const orig = btnEl.innerHTML;
  btnEl.disabled = true;
  btnEl.textContent = "Typing...";
  try {
    const res = await fetch("/api/wa/send", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        phone: lead.phone,
        message: lead.outreach_dm || lead.outreach_body,
        name: lead.name,
        force: true,
        throttle: false
      })
    });
    const data = await res.json();
    if (data.ok) {
      lead.wa_status = "sent";
      lead.wa_verified = true;
      contacted[lead.id] = true;
      localStorage.setItem("contacted", JSON.stringify(contacted));
      showToast(`✓ ${data.message}`);
      render();
    } else {
      if (data.status === "not_on_whatsapp") lead.wa_verified = false;
      showToast(data.message || data.error || "WhatsApp send failed");
      if (String(data.error || "").includes("not connected") || String(data.error || "").includes("offline")) {
        openWaModal();
      }
      render();
    }
  } catch (err) {
    showToast("WA Bot error: " + err.message);
    btnEl.disabled = false;
    btnEl.innerHTML = orig;
  }
}

async function sendLeadEmailViaSmtp(lead, btnEl = null) {
  if (!lead.email) {
    showToast("No email address for this business.");
    return false;
  }
  const origHtml = btnEl ? btnEl.innerHTML : "";
  if (btnEl) {
    btnEl.disabled = true;
    btnEl.textContent = "Sending...";
  }
  try {
    const res = await fetch("/api/send-email", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        email: lead.email,
        subject: lead.outreach_subject,
        body: lead.outreach_body,
        name: lead.name,
        force: true,
        meta: {
          category: lead.category || "",
          city: lead.city || "",
          site_status: lead.site_status || "",
          audit_issues: lead.audit_issues || []
        }
      })
    });
    const data = await res.json();
    if (data.ok) {
      lead.email_status = data.status;
      lead.email_status_note = data.message;
      contacted[lead.id] = true;
      localStorage.setItem("contacted", JSON.stringify(contacted));
      showToast(`✓ ${data.message}`);
      render();
      return true;
    } else {
      lead.email_status = "error";
      lead.email_status_note = data.message;
      showToast(data.message || "Failed to send email");
      if (data.status === "unconfigured") openSettingsModal();
      render();
      return false;
    }
  } catch (err) {
    showToast("Error sending email: " + err.message);
    if (btnEl) {
      btnEl.disabled = false;
      btnEl.innerHTML = origHtml;
    }
    return false;
  }
}

// Bulk Send All Unsent Emails
$("#sendAllBtn").onclick = async () => {
  const unsentLeads = view().filter(
    r => r.email && !["sent", "simulated", "already_sent"].includes(r.email_status)
  );
  if (unsentLeads.length === 0) {
    showToast("No unsent email leads in the current view.");
    return;
  }
  if (!currentSettings.smtp_email && !currentSettings.dry_run) {
    showToast("Configure your SMTP credentials (or enable Dry-Run) in Settings first.");
    openSettingsModal();
    return;
  }

  $("#sendAllBtn").disabled = true;
  let sentCount = 0;
  for (let i = 0; i < unsentLeads.length; i++) {
    $("#sendAllText").textContent = `Sending ${i + 1}/${unsentLeads.length}...`;
    const ok = await sendLeadEmailViaSmtp(unsentLeads[i]);
    if (ok) sentCount++;
  }
  $("#sendAllText").textContent = "Email All Unsent";
  $("#sendAllBtn").disabled = false;
  showToast(`Finished! Dispatched ${sentCount} tailored outreach emails.`);
};

// Pitch Modal Logic
function openPitchModal(lead) {
  activeModalLeadId = lead.id;
  $("#pitchModalTitle").textContent = `${lead.name} (${lead.city || ""})`;
  $("#pitchModalStatus").textContent = `${LABEL[lead.site_status] || lead.site_status} • Score ${lead.lead_score || 60}/100`;
  $("#pitchAngleSelect").value = currentSettings.pitch_angle || "auto";

  const issues = lead.audit_issues || [];
  $("#pitchAuditSummary").innerHTML = issues.length > 0
    ? `<strong>Detected Opportunities / Audit Gaps:</strong> ` + issues.map(i => `<span class="audit-pill">${esc(i)}</span>`).join(" ")
    : "";

  $("#pitchSubjectInput").value = lead.outreach_subject || "";
  $("#pitchBodyInput").value = lead.outreach_body || "";
  $("#pitchDmInput").value = lead.outreach_dm || "";

  syncModalFooterLinks(lead);
  $("#pitchModal").hidden = false;
}

function syncModalFooterLinks(lead) {
  lead.outreach_subject = $("#pitchSubjectInput").value;
  lead.outreach_body = $("#pitchBodyInput").value;
  lead.outreach_dm = $("#pitchDmInput").value;

  $("#modalMailtoBtn").href = buildMailtoHref(lead);
  $("#modalMailtoBtn").hidden = !lead.email;
  $("#modalSendSmtpBtn").hidden = !lead.email;

  const waHref = buildWhatsAppPitchHref(lead);
  const waBtn = $("#modalWaBtn");
  if (waHref) {
    waBtn.href = waHref;
    waBtn.hidden = false;
  } else {
    waBtn.hidden = true;
  }

  const dmBtn = $("#modalCopyOpenDmBtn");
  if (lead.dm_info && lead.dm_info.dm_url) {
    dmBtn.textContent = `Copy & Open ${lead.dm_info.platform} DM`;
    dmBtn.hidden = false;
  } else {
    dmBtn.hidden = true;
  }
}

$("#pitchSubjectInput").oninput = () => {
  const lead = rows.find(r => r.id === activeModalLeadId);
  if (lead) { syncModalFooterLinks(lead); render(); }
};
$("#pitchBodyInput").oninput = () => {
  const lead = rows.find(r => r.id === activeModalLeadId);
  if (lead) { syncModalFooterLinks(lead); render(); }
};
$("#pitchDmInput").oninput = () => {
  const lead = rows.find(r => r.id === activeModalLeadId);
  if (lead) { syncModalFooterLinks(lead); render(); }
};

async function triggerPitchRegen(useAi = false) {
  const lead = rows.find(r => r.id === activeModalLeadId);
  if (!lead) return;
  const angle = $("#pitchAngleSelect").value;
  const btn = useAi ? $("#aiRewriteBtn") : $("#regenPitchBtn");
  const prevText = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Generating...";
  try {
    const res = await fetch("/api/regenerate-pitch", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({lead, angle, use_ai: useAi})
    });
    const data = await res.json();
    if (data.ok) {
      $("#pitchSubjectInput").value = data.subject;
      $("#pitchBodyInput").value = data.body;
      $("#pitchDmInput").value = data.dm;
      syncModalFooterLinks(lead);
      render();
      showToast(useAi ? "Pitch polished!" : "Pitch updated for selected angle!");
    }
  } catch (err) {
    showToast("Failed to regenerate pitch: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = prevText;
  }
}

$("#pitchAngleSelect").onchange = () => triggerPitchRegen(false);
$("#regenPitchBtn").onclick = () => triggerPitchRegen(false);
$("#aiRewriteBtn").onclick = () => triggerPitchRegen(true);

$("#modalCopyEmailBtn").onclick = () => copyText($("#pitchBodyInput").value, "Copied email writeup!");
$("#modalCopyDmBtn").onclick = () => copyText($("#pitchDmInput").value, "Copied short DM message!");

$("#modalCopyOpenDmBtn").onclick = async () => {
  const lead = rows.find(r => r.id === activeModalLeadId);
  if (!lead || !lead.dm_info?.dm_url) return;
  await copyText($("#pitchDmInput").value, `Copied DM! Opening ${lead.dm_info.platform}...`);
  contacted[lead.id] = true;
  localStorage.setItem("contacted", JSON.stringify(contacted));
  render();
  window.open(lead.dm_info.dm_url, "_blank", "noopener");
};

$("#modalSendSmtpBtn").onclick = async () => {
  const lead = rows.find(r => r.id === activeModalLeadId);
  if (!lead) return;
  syncModalFooterLinks(lead);
  await sendLeadEmailViaSmtp(lead, $("#modalSendSmtpBtn"));
  $("#modalSendSmtpBtn").textContent = "Send Email Now";
  $("#modalSendSmtpBtn").disabled = false;
};

$("#closePitchModal").onclick = () => { $("#pitchModal").hidden = true; };

// Settings Modal Logic
function openSettingsModal() {
  const s = currentSettings;
  $("#s_sender_name").value = s.sender_name || "";
  $("#s_sender_company").value = s.sender_company || "";
  $("#s_sender_portfolio").value = s.sender_portfolio || "";
  $("#s_sender_phone").value = s.sender_phone || "";
  $("#s_pitch_angle").value = s.pitch_angle || "auto";
  $("#s_custom_offer").value = s.custom_offer || "";
  $("#s_smtp_email").value = s.smtp_email || "";
  $("#s_smtp_password").value = s.smtp_password || "";
  $("#s_smtp_host").value = s.smtp_host || "smtp.gmail.com";
  $("#s_smtp_port").value = s.smtp_port || 465;
  $("#s_imap_host").value = s.imap_host || "imap.gmail.com";
  $("#s_imap_port").value = s.imap_port || 993;
  $("#s_send_delay_sec").value = s.send_delay_sec ?? 8;
  $("#s_daily_send_limit").value = s.daily_send_limit ?? 40;
  $("#s_followup_1_days").value = s.followup_1_days ?? 3;
  $("#s_followup_2_days").value = s.followup_2_days ?? 7;
  $("#s_auto_send_email").checked = Boolean(s.auto_send_email);
  $("#s_auto_send_inferred").checked = Boolean(s.auto_send_inferred);
  $("#s_business_hours_only").checked = Boolean(s.business_hours_only);
  $("#s_include_unsubscribe").checked = s.include_unsubscribe !== false;
  $("#s_dry_run").checked = Boolean(s.dry_run);
  $("#s_serper_api_key").value = s.serper_api_key || "";
  $("#s_tavily_api_key").value = s.tavily_api_key || "";
  $("#s_brave_api_key").value = s.brave_api_key || "";
  $("#s_exa_api_key").value = s.exa_api_key || "";
  $("#s_searxng_url").value = s.searxng_url || "";
  $("#s_hunter_api_key").value = s.hunter_api_key || "";
  $("#s_gemini_api_key").value = s.gemini_api_key || "";
  $("#s_groq_api_key").value = s.groq_api_key || "";
  $("#smtpTestStatus").textContent = "";
  $("#settingsModal").hidden = false;
}

function collectSettingsForm() {
  return {
    sender_name: $("#s_sender_name").value.trim(),
    sender_company: $("#s_sender_company").value.trim(),
    sender_portfolio: $("#s_sender_portfolio").value.trim(),
    sender_phone: $("#s_sender_phone").value.trim(),
    pitch_angle: $("#s_pitch_angle").value,
    custom_offer: $("#s_custom_offer").value.trim(),
    smtp_email: $("#s_smtp_email").value.trim(),
    smtp_password: $("#s_smtp_password").value.trim(),
    smtp_host: $("#s_smtp_host").value.trim() || "smtp.gmail.com",
    smtp_port: parseInt($("#s_smtp_port").value, 10) || 465,
    imap_host: $("#s_imap_host").value.trim() || "imap.gmail.com",
    imap_port: parseInt($("#s_imap_port").value, 10) || 993,
    send_delay_sec: parseInt($("#s_send_delay_sec").value, 10) || 8,
    daily_send_limit: parseInt($("#s_daily_send_limit").value, 10) || 40,
    followup_1_days: parseInt($("#s_followup_1_days").value, 10) || 3,
    followup_2_days: parseInt($("#s_followup_2_days").value, 10) || 7,
    auto_send_email: $("#s_auto_send_email").checked,
    auto_send_inferred: $("#s_auto_send_inferred").checked,
    business_hours_only: $("#s_business_hours_only").checked,
    include_unsubscribe: $("#s_include_unsubscribe").checked,
    dry_run: $("#s_dry_run").checked,
    serper_api_key: $("#s_serper_api_key").value.trim(),
    tavily_api_key: $("#s_tavily_api_key").value.trim(),
    brave_api_key: $("#s_brave_api_key").value.trim(),
    exa_api_key: $("#s_exa_api_key").value.trim(),
    searxng_url: $("#s_searxng_url").value.trim(),
    hunter_api_key: $("#s_hunter_api_key").value.trim(),
    gemini_api_key: $("#s_gemini_api_key").value.trim(),
    groq_api_key: $("#s_groq_api_key").value.trim()
  };
}

$("#openSettingsBtn").onclick = openSettingsModal;
$("#closeSettingsModal").onclick = () => { $("#settingsModal").hidden = true; };
$("#cancelSettingsBtn").onclick = () => { $("#settingsModal").hidden = true; };

$("#settingsForm").onsubmit = async e => {
  e.preventDefault();
  const payload = collectSettingsForm();
  try {
    const res = await fetch("/api/settings", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    currentSettings = data.settings || payload;
    syncAutoSendPill(data.sent_total);
    $("#settingsModal").hidden = true;
    showToast("Settings saved!");
  } catch (err) {
    showToast("Error saving settings: " + err.message);
  }
};

$("#testSmtpBtn").onclick = async () => {
  const settings = collectSettingsForm();
  $("#smtpTestStatus").textContent = "Testing connection...";
  $("#testSmtpBtn").disabled = true;
  try {
    const res = await fetch("/api/test-smtp", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({settings, to: settings.smtp_email})
    });
    const data = await res.json();
    $("#smtpTestStatus").textContent = data.message || (data.ok ? "Connected!" : "Failed");
    $("#smtpTestStatus").style.color = data.ok ? "var(--ok-text)" : "var(--bad-text)";
  } catch (err) {
    $("#smtpTestStatus").textContent = "Error: " + err.message;
  } finally {
    $("#testSmtpBtn").disabled = false;
  }
};

// Live Trace Logs Helpers
let jobLogs = [];

function appendJobLogs(newLogs) {
  if (!newLogs || newLogs.length === 0) return;
  jobLogs.push(...newLogs);
  $("#logCount").textContent = String(jobLogs.length);
  const body = $("#logBody");
  const frag = document.createDocumentFragment();
  for (const item of newLogs) {
    const div = document.createElement("div");
    div.className = "log-line";
    div.innerHTML = `<span class="log-ts">[${esc(item.ts)}]</span><span class="log-lvl-${esc(item.level)}">[${esc(item.level)}]</span><span>${esc(item.msg)}</span>`;
    frag.appendChild(div);
  }
  body.appendChild(frag);
  if (!body.hidden) {
    body.scrollTop = body.scrollHeight;
  }
}

$("#toggleLogBtn").onclick = e => {
  if (e.target.closest("button")) return;
  const body = $("#logBody");
  body.hidden = !body.hidden;
  $("#logChevron").textContent = body.hidden ? "▼" : "▲";
  if (!body.hidden) body.scrollTop = body.scrollHeight;
};

$("#copyLogsBtn").onclick = () => {
  const txt = jobLogs.map(l => `[${l.ts}] [${l.level}] ${l.msg}`).join("\n");
  copyText(txt || "No logs yet.", "Copied diagnostic logs!");
};

$("#clearLogsBtn").onclick = () => {
  jobLogs = [];
  $("#logBody").innerHTML = "";
  $("#logCount").textContent = "0";
};

// Outreach CRM & Follow-Ups Modal Logic
async function loadCrmModal() {
  $("#crmModal").hidden = false;
  $("#crmSummary").textContent = "Loading outreach ledger...";
  try {
    const data = await (await fetch("/api/crm")).json();
    const leads = data.leads || [];
    const dueCount = leads.filter(l => l.followup_due).length;
    const repliedCount = leads.filter(l => l.status === "replied").length;
    const bouncedCount = leads.filter(l => l.status === "bounced").length;
    $("#crmSummary").textContent = `${leads.length} tracked • ${dueCount} follow-up(s) due • ${repliedCount} replied • ${bouncedCount} bounced • Sent today: ${data.sent_today}/${data.daily_limit}`;

    if (leads.length === 0) {
      $("#crmRows").innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 28px; color: var(--mute);">No outreach emails tracked yet.</td></tr>`;
      return;
    }

    $("#crmRows").innerHTML = leads.map(l => {
      const badgeCls = l.status === "replied" ? "replied" : (l.status === "bounced" ? "bounced" : (l.followup_due ? "hold" : ""));
      const statusLabel = l.status === "replied" ? "🎉 Replied" : (l.status === "bounced" ? "⚠ Bounced" : (l.status === "opted_out" ? "Opted Out" : (l.followup_due ? "⏰ Follow-Up Due" : l.status)));
      return `<tr>
        <td>
          <strong>${esc(l.biz_name)}</strong><br>
          <span class="site-note">${esc(l.email)}</span>
          ${l.reply_snippet ? `<div class="site-note" style="color:var(--ok-text); margin-top:4px;">"${esc(l.reply_snippet)}"</div>` : ""}
          ${l.bounce_reason ? `<div class="site-note" style="color:var(--bad-text); margin-top:4px;">${esc(l.bounce_reason)}</div>` : ""}
        </td>
        <td>
          <span class="category-tag">Stage ${l.stage}/3</span>
          <span class="sent-badge ${badgeCls}">${esc(statusLabel)}</span>
        </td>
        <td>
          <div class="site-note">Sent: ${esc(l.sent_at)}</div>
          ${l.next_followup_at ? `<div class="site-note">Next: ${esc(l.next_followup_at)}</div>` : ""}
        </td>
        <td>
          <div style="display:flex; gap:6px; flex-wrap:wrap;">
            ${l.status !== "replied" && l.status !== "bounced" && l.status !== "opted_out" && l.stage < 3
              ? `<button type="button" class="btn-mini btn-send-smtp" data-crm-followup="${esc(l.email)}">Send Follow-Up</button>`
              : ""}
            ${l.status !== "opted_out"
              ? `<button type="button" class="btn-mini btn-ghost" data-crm-optout="${esc(l.email)}">Opt-Out</button>`
              : ""}
          </div>
        </td>
      </tr>`;
    }).join("");
  } catch (err) {
    $("#crmSummary").textContent = "Failed to load CRM: " + err.message;
  }
}

$("#openCrmBtn").onclick = loadCrmModal;
$("#closeCrmModal").onclick = () => { $("#crmModal").hidden = true; };

$("#syncImapBtn").onclick = async () => {
  const btn = $("#syncImapBtn");
  btn.disabled = true;
  btn.textContent = "Syncing IMAP...";
  try {
    const res = await fetch("/api/crm/sync-imap", {method: "POST", headers: {"Content-Type": "application/json"}, body: "{}"});
    const data = await res.json();
    showToast(data.message || "IMAP sync complete");
    await loadCrmModal();
  } catch (err) {
    showToast("IMAP sync error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Check Replies & Bounces (IMAP)";
  }
};

$("#sendDueFollowupsBtn").onclick = async () => {
  const btn = $("#sendDueFollowupsBtn");
  btn.disabled = true;
  btn.textContent = "Sending Due...";
  try {
    const res = await fetch("/api/crm/send-followups", {method: "POST", headers: {"Content-Type": "application/json"}, body: "{}"});
    const data = await res.json();
    showToast(data.message || "Done");
    await loadCrmModal();
  } catch (err) {
    showToast("Follow-up error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Send Due Follow-Ups";
  }
};

$("#crmRows").onclick = async e => {
  const fuBtn = e.target.closest("[data-crm-followup]");
  if (fuBtn) {
    const em = fuBtn.dataset.crmFollowup;
    fuBtn.disabled = true;
    fuBtn.textContent = "Sending...";
    const res = await fetch("/api/crm/send-followups", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({email: em})});
    const data = await res.json();
    showToast(data.message || "Follow-up sent");
    await loadCrmModal();
    return;
  }
  const optBtn = e.target.closest("[data-crm-optout]");
  if (optBtn) {
    const em = optBtn.dataset.crmOptout;
    await fetch("/api/crm/status", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({email: em, status: "opted_out"})});
    showToast(`Marked ${em} as opted out`);
    await loadCrmModal();
  }
};

// Close modals on backdrop click
window.onclick = e => {
  if (e.target === $("#pitchModal")) $("#pitchModal").hidden = true;
  if (e.target === $("#settingsModal")) $("#settingsModal").hidden = true;
  if (e.target === $("#crmModal")) $("#crmModal").hidden = true;
  if (e.target === $("#waModal")) closeWaModal();
};

// Search Form Submission
$("#f").onsubmit = async e => {
  e.preventDefault();
  clearInterval(timer);
  rows = [];
  jobLogs = [];
  $("#logBody").innerHTML = "";
  $("#logCount").textContent = "0";
  render();
  $("#go").disabled = true;
  $("#status").textContent = "Initializing search & deep contact hunter...";

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
        const j = await (await fetch(`/api/job/${id}?since=${rows.length}&log_since=${jobLogs.length}`)).json();
        if (j.logs && j.logs.length > 0) {
          appendJobLogs(j.logs);
        }
        if (j.results && j.results.length > 0) {
          rows.push(...j.results);
          render();
        }
        const sentNote = j.sent_count > 0 ? ` • ${j.sent_count} auto-emailed` : "";
        $("#status").textContent = j.error
          ? "Error: " + j.error
          : `${j.msg}: ${j.found} discovered, ${rows.length} audited & pitched${sentNote}`;

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

// CSV Export with full outreach intelligence
$("#csv").onclick = () => {
  const currentRows = view();
  if (currentRows.length === 0) {
    showToast("No leads to export in the current view.");
    return;
  }
  const cols = [
    "name", "category", "address", "email", "phone", "socials", "website",
    "site_status", "site_note", "audit_issues", "lead_score", "rating",
    "reviews", "maps_url", "email_status", "outreach_subject", "outreach_body"
  ];
  const headerRow = cols.join(",");
  const dataRows = currentRows.map(r => {
    return cols.map(c => {
      let val = r[c] ?? "";
      if (Array.isArray(val)) val = val.join(" | ");
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


// WhatsApp Baileys Sidecar Modal Logic
let waPollTimer = null;

async function refreshWaStatus() {
  try {
    const st = await (await fetch("/api/wa/status")).json();
    const label = $("#waBtnLabel");
    if (st.connected) {
      label.textContent = `WA: Connected (${st.phone || "OK"})`;
      $("#waConnStatus").textContent = `Connected as ${st.name || "WhatsApp"} (${st.phone}) • Sent today: ${st.sent_today ?? 0}/${st.daily_limit ?? 15}`;
      $("#waConnStatus").style.color = "var(--ok-text)";
      $("#waQrImg").hidden = true;
    } else if (st.state === "qr" && st.qr_data_url) {
      label.textContent = "WA: Scan QR";
      $("#waConnStatus").textContent = "Scan this QR code in WhatsApp → Linked Devices:";
      $("#waConnStatus").style.color = "var(--ink)";
      $("#waQrImg").src = st.qr_data_url;
      $("#waQrImg").hidden = false;
    } else if (st.state === "offline") {
      label.textContent = "WhatsApp Bot";
      $("#waConnStatus").textContent = st.error || "Sidecar offline. Run wa_sidecar\\start_wa.bat first.";
      $("#waConnStatus").style.color = "var(--bad-text)";
      $("#waQrImg").hidden = true;
    } else {
      label.textContent = `WA: ${st.state || "Disconnected"}`;
      $("#waConnStatus").textContent = st.error || `Status: ${st.state || "Disconnected"}. Click Connect to generate QR.`;
      $("#waConnStatus").style.color = "var(--mute)";
      $("#waQrImg").hidden = true;
    }
  } catch {}
}

function openWaModal() {
  const s = currentSettings;
  $("#s_wa_daily_limit").value = s.wa_daily_limit ?? 15;
  $("#s_wa_delay_min_sec").value = s.wa_delay_min_sec ?? 90;
  $("#s_wa_delay_max_sec").value = s.wa_delay_max_sec ?? 210;
  $("#s_wa_business_hours_only").checked = s.wa_business_hours_only !== false;
  $("#s_wa_auto_send").checked = Boolean(s.wa_auto_send);
  $("#waModal").hidden = false;
  refreshWaStatus();
  clearInterval(waPollTimer);
  waPollTimer = setInterval(refreshWaStatus, 2500);
}

function closeWaModal() {
  $("#waModal").hidden = true;
  clearInterval(waPollTimer);
}

$("#openWaBtn").onclick = openWaModal;
$("#closeWaModal").onclick = closeWaModal;

$("#waConnectBtn").onclick = async () => {
  await fetch("/api/wa/connect", {method: "POST", headers: {"Content-Type": "application/json"}, body: "{}"});
  showToast("Starting WhatsApp connection... waiting for QR.");
  setTimeout(refreshWaStatus, 1000);
};

$("#waLogoutBtn").onclick = async () => {
  await fetch("/api/wa/logout", {method: "POST", headers: {"Content-Type": "application/json"}, body: "{}"});
  showToast("Disconnected WhatsApp session.");
  refreshWaStatus();
};

$("#waSyncRepliesBtn").onclick = async () => {
  const res = await (await fetch("/api/wa/sync-replies", {method: "POST", headers: {"Content-Type": "application/json"}, body: "{}"})).json();
  showToast(res.message || res.error || "Synced WA replies");
};

$("#saveWaSettingsBtn").onclick = async () => {
  const payload = {
    wa_daily_limit: parseInt($("#s_wa_daily_limit").value, 10) || 15,
    wa_delay_min_sec: parseInt($("#s_wa_delay_min_sec").value, 10) || 90,
    wa_delay_max_sec: parseInt($("#s_wa_delay_max_sec").value, 10) || 210,
    wa_business_hours_only: $("#s_wa_business_hours_only").checked,
    wa_auto_send: $("#s_wa_auto_send").checked,
  };
  const res = await (await fetch("/api/settings", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  })).json();
  currentSettings = res.settings || {...currentSettings, ...payload};
  showToast("WhatsApp anti-ban settings saved!");
};

// Check WA sidecar status once on page load
refreshWaStatus();
