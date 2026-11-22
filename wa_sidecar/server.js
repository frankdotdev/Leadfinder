const http = require("http");
const fs = require("fs");
const path = require("path");
const pino = require("pino");
const QRCode = require("qrcode");
const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
  Browsers,
} = require("@whiskeysockets/baileys");

const PORT = parseInt(process.env.WA_PORT || "3001", 10);
const AUTH_DIR = path.join(__dirname, "auth_info");
const REPLIES_FILE = path.join(__dirname, "replies.json");

let sock = null;
let connState = "disconnected"; // disconnected | connecting | qr | connected
let qrDataUrl = "";
let connectedUser = { phone: "", name: "" };
let lastError = "";
let isStarting = false;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const randBetween = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

function loadReplies() {
  try {
    if (fs.existsSync(REPLIES_FILE)) {
      return JSON.parse(fs.readFileSync(REPLIES_FILE, "utf8"));
    }
  } catch {}
  return {};
}

function saveReply(phoneDigits, text) {
  try {
    const all = loadReplies();
    all[phoneDigits] = {
      text: String(text || "").slice(0, 300),
      ts: new Date().toISOString(),
    };
    fs.writeFileSync(REPLIES_FILE, JSON.stringify(all, null, 2), "utf8");
  } catch {}
}

function cleanDigits(raw) {
  return String(raw || "").replace(/\D/g, "");
}

async function startSocket() {
  if (isStarting) return;
  isStarting = true;
  lastError = "";
  connState = "connecting";

  try {
    if (!fs.existsSync(AUTH_DIR)) fs.mkdirSync(AUTH_DIR, { recursive: true });
    const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
    const { version } = await fetchLatestBaileysVersion();

    sock = makeWASocket({
      version,
      auth: state,
      logger: pino({ level: "silent" }),
      browser: Browsers.macOS("Chrome"),
      printQRInTerminal: true,
      markOnlineOnConnect: false, // Keep natural presence until actually sending
      syncFullHistory: false,
    });

    sock.ev.on("creds.update", saveCreds);

    sock.ev.on("connection.update", async (update) => {
      const { connection, lastDisconnect, qr } = update;

      if (qr) {
        connState = "qr";
        try {
          qrDataUrl = await QRCode.toDataURL(qr, { width: 280, margin: 2 });
        } catch {
          qrDataUrl = "";
        }
      }

      if (connection === "open") {
        connState = "connected";
        qrDataUrl = "";
        lastError = "";
        const rawId = sock.user?.id || "";
        connectedUser = {
          phone: rawId.split(":")[0].split("@")[0],
          name: sock.user?.name || "WhatsApp Connected",
        };
        console.log(`[WA Sidecar] Connected as ${connectedUser.name} (${connectedUser.phone})`);
      }

      if (connection === "close") {
        const statusCode = lastDisconnect?.error?.output?.statusCode;
        const loggedOut = statusCode === DisconnectReason.loggedOut;
        connState = "disconnected";
        qrDataUrl = "";
        connectedUser = { phone: "", name: "" };

        if (loggedOut) {
          lastError = "Logged out from WhatsApp. Clear auth and scan QR again.";
          console.log("[WA Sidecar] Logged out.");
        } else {
          lastError = `Disconnected (code ${statusCode || "unknown"}), reconnecting...`;
          setTimeout(() => startSocket(), 4000);
        }
      }
    });

    // Listen for incoming replies so LeadFinder stops follow-ups automatically
    sock.ev.on("messages.upsert", ({ messages, type }) => {
      if (type !== "notify") return;
      for (const msg of messages || []) {
        if (msg.key?.fromMe) continue;
        const jid = msg.key?.remoteJid || "";
        if (!jid.endsWith("@s.whatsapp.net")) continue;
        const digits = jid.split("@")[0];
        const text =
          msg.message?.conversation ||
          msg.message?.extendedTextMessage?.text ||
          msg.message?.imageMessage?.caption ||
          "[media/reply]";
        saveReply(digits, text);
      }
    });
  } catch (err) {
    connState = "disconnected";
    lastError = String(err?.message || err);
    console.error("[WA Sidecar] Error:", lastError);
  } finally {
    isStarting = false;
  }
}

async function checkNumbers(phones) {
  if (!sock || connState !== "connected") {
    throw new Error("WhatsApp is not connected.");
  }
  const results = {};
  for (const raw of phones || []) {
    const d = cleanDigits(raw);
    if (d.length < 7) {
      results[raw] = { exists: false, jid: "" };
      continue;
    }
    try {
      const [res] = await sock.onWhatsApp(d);
      results[raw] = {
        exists: Boolean(res?.exists),
        jid: res?.jid || "",
      };
    } catch {
      results[raw] = { exists: false, jid: "" };
    }
  }
  return results;
}

async function sendHumanLikeMessage(phone, message) {
  if (!sock || connState !== "connected") {
    throw new Error("WhatsApp sidecar is not connected. Scan QR code first.");
  }
  const d = cleanDigits(phone);
  if (d.length < 7) {
    throw new Error("Invalid phone number.");
  }

  // 1. Verify the number is actually registered on WhatsApp (skips landlines!)
  const [waInfo] = await sock.onWhatsApp(d);
  if (!waInfo || !waInfo.exists) {
    return { ok: false, status: "not_on_whatsapp", message: `${phone} is not registered on WhatsApp (landline or invalid).` };
  }
  const jid = waInfo.jid;

  // 2. Simulate natural human presence & typing
  try {
    await sock.presenceSubscribe(jid);
    await sock.sendPresenceUpdate("available", jid);
    await sleep(randBetween(1200, 2400));

    await sock.sendPresenceUpdate("composing", jid);
    const typingMs = Math.min(11000, Math.max(3500, String(message).length * 42)) + randBetween(400, 1400);
    await sleep(typingMs);

    await sock.sendPresenceUpdate("paused", jid);
    await sleep(randBetween(400, 900));
  } catch {
    // Non-fatal if presence update fails
  }

  // 3. Dispatch message
  const sent = await sock.sendMessage(jid, { text: String(message) });
  return {
    ok: true,
    status: "sent",
    jid,
    messageId: sent?.key?.id || "",
    message: `WhatsApp sent to ${phone}`,
  };
}

function readJson(req) {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", (chunk) => (body += chunk));
    req.on("end", () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (e) {
        reject(e);
      }
    });
  });
}

function reply(res, code, obj) {
  const data = JSON.stringify(obj);
  res.writeHead(code, { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(data) });
  res.end(data);
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === "GET" && req.url === "/status") {
      return reply(res, 200, {
        connected: connState === "connected",
        state: connState,
        phone: connectedUser.phone,
        name: connectedUser.name,
        qr_data_url: qrDataUrl,
        error: lastError,
      });
    }

    if (req.method === "GET" && req.url === "/replies") {
      return reply(res, 200, { ok: true, replies: loadReplies() });
    }

    if (req.method === "POST" && req.url === "/connect") {
      if (connState !== "connected" && !isStarting) {
        startSocket();
      }
      return reply(res, 200, { ok: true, state: connState });
    }

    if (req.method === "POST" && req.url === "/logout") {
      try {
        if (sock) await sock.logout();
      } catch {}
      try {
        fs.rmSync(AUTH_DIR, { recursive: true, force: true });
      } catch {}
      sock = null;
      connState = "disconnected";
      qrDataUrl = "";
      connectedUser = { phone: "", name: "" };
      return reply(res, 200, { ok: true, state: "disconnected" });
    }

    if (req.method === "POST" && req.url === "/check") {
      const { phones } = await readJson(req);
      const results = await checkNumbers(phones);
      return reply(res, 200, { ok: true, results });
    }

    if (req.method === "POST" && req.url === "/send") {
      const { phone, message } = await readJson(req);
      const result = await sendHumanLikeMessage(phone, message);
      return reply(res, result.ok ? 200 : 400, result);
    }

    reply(res, 404, { error: "Not found" });
  } catch (err) {
    reply(res, 500, { ok: false, error: String(err?.message || err) });
  }
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`LeadFinder WhatsApp Sidecar listening on http://127.0.0.1:${PORT}`);
  // Auto-connect if auth credentials already exist
  if (fs.existsSync(path.join(AUTH_DIR, "creds.json"))) {
    startSocket();
  }
});
