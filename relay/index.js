/*
Relay server:
- Students send HTTP POST /api/command
- Your studio agent holds an outbound WebSocket connection to /ws/agent
- Relay forwards validated commands to the agent for a given room

Security model (practical for Squarespace embed):
- Rely on Squarespace page password/members area for primary access control.
- Relay also requires a per-room STUDENT_TOKEN (rotatable) and supports a hard LOCK.
- Agent uses a separate AGENT_TOKEN.

This is intentionally small and self-hostable.
*/

require('dotenv').config();

const http = require('http');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const morgan = require('morgan');

const WebSocket = require('ws');

const {
  RELAY_PORT = '8787',
  RELAY_BASE_URL = '',
  CORS_ORIGINS = '',
  ROOM_ID = 'classroom',
  STUDENT_TOKEN = 'change-me-student-token',
  AGENT_TOKEN = 'change-me-agent-token',
  ADMIN_TOKEN = 'change-me-admin-token',
  MAX_COMMANDS_PER_MINUTE = '60',
  // Server-side allowlist so students can only trigger approved actions.
  // Relative paths are resolved from process.cwd().
  ALLOWLIST_PATH = 'relay/allowlist.json'
} = process.env;

const MAX_PER_MIN = Math.max(5, Number(MAX_COMMANDS_PER_MINUTE) || 60);

const app = express();
app.disable('x-powered-by');
app.use(helmet());
app.use(express.json({ limit: '32kb' }));
app.use(morgan('tiny'));

const allowOrigins = CORS_ORIGINS
  .split(',')
  .map((s) => s.trim())
  .filter(Boolean);

app.use(
  cors({
    origin: (origin, cb) => {
      // Allow non-browser tools and same-origin.
      if (!origin) return cb(null, true);
      if (allowOrigins.length === 0) return cb(null, true);
      if (allowOrigins.includes(origin)) return cb(null, true);
      return cb(new Error('CORS blocked'));
    }
  })
);

/**
 * In-memory state (single-instance relay).
 * If you need multi-instance HA, swap this for Redis.
 */
const state = {
  roomId: ROOM_ID,
  studentToken: STUDENT_TOKEN,
  agentToken: AGENT_TOKEN,
  adminToken: ADMIN_TOKEN,
  locked: false,
  lastRotateAt: null
};

function readAllowlistFile() {
  const p = path.isAbsolute(ALLOWLIST_PATH) ? ALLOWLIST_PATH : path.join(process.cwd(), ALLOWLIST_PATH);
  const raw = fs.readFileSync(p, 'utf8');
  const json = JSON.parse(raw);
  const allowed = Array.isArray(json?.allowed) ? json.allowed : [];
  return {
    path: p,
    roomId: typeof json?.roomId === 'string' ? json.roomId : state.roomId,
    allowed: allowed
      .filter((x) => typeof x?.type === 'string' && x.type.length > 0 && x.payload && typeof x.payload === 'object')
      .map((x) => ({ type: x.type, payload: x.payload }))
  };
}

let allowlist;
try {
  allowlist = readAllowlistFile();
  // eslint-disable-next-line no-console
  console.log(`[relay] allowlist loaded: ${allowlist.allowed.length} actions from ${allowlist.path}`);
} catch (e) {
  allowlist = { path: ALLOWLIST_PATH, roomId: state.roomId, allowed: [] };
  // eslint-disable-next-line no-console
  console.warn('[relay] allowlist NOT loaded; all student commands will be blocked:', e?.message || e);
}

function deepEqual(a, b) {
  if (a === b) return true;
  if (typeof a !== typeof b) return false;
  if (a == null || b == null) return false;
  if (typeof a !== 'object') return false;
  if (Array.isArray(a) || Array.isArray(b)) return false;
  const ak = Object.keys(a).sort();
  const bk = Object.keys(b).sort();
  if (ak.length !== bk.length) return false;
  for (let i = 0; i < ak.length; i++) {
    if (ak[i] !== bk[i]) return false;
    if (!deepEqual(a[ak[i]], b[bk[i]])) return false;
  }
  return true;
}

function isAllowed(type, payload) {
  // roomId mismatch means config drift; still enforce allowed list.
  const list = allowlist?.allowed || [];
  return list.some((x) => x.type === type && deepEqual(x.payload, payload || {}));
}

/** roomId -> { ws, connectedAt, lastSeenAt } */
const agents = new Map();

/** basic ip+room rate-limit bucket */
const rate = new Map();
function rateKey(req) {
  const ip = req.headers['x-forwarded-for']?.toString().split(',')[0]?.trim() || req.socket.remoteAddress;
  return `${ip || 'unknown'}:${state.roomId}`;
}
function takeToken(key) {
  const now = Date.now();
  const windowMs = 60_000;
  const entry = rate.get(key) || { windowStart: now, count: 0 };
  if (now - entry.windowStart > windowMs) {
    entry.windowStart = now;
    entry.count = 0;
  }
  entry.count += 1;
  rate.set(key, entry);
  return entry.count <= MAX_PER_MIN;
}

function requireAdmin(req, res, next) {
  const auth = (req.headers.authorization || '').toString();
  const token = auth.startsWith('Bearer ') ? auth.slice('Bearer '.length) : '';
  if (!token || token !== state.adminToken) {
    return res.status(401).json({ ok: false, error: 'unauthorized' });
  }
  return next();
}

function requireStudent(req, res, next) {
  const auth = (req.headers.authorization || '').toString();
  const token = auth.startsWith('Bearer ') ? auth.slice('Bearer '.length) : '';
  if (!token || token !== state.studentToken) {
    return res.status(401).json({ ok: false, error: 'unauthorized' });
  }
  if (state.locked) {
    return res.status(423).json({ ok: false, error: 'locked' });
  }
  return next();
}

app.get('/health', (_req, res) => {
  res.json({
    ok: true,
    roomId: state.roomId,
    locked: state.locked,
    agentConnected: agents.has(state.roomId),
    allowlistCount: allowlist?.allowed?.length || 0
  });
});

// Student -> relay -> agent
app.post('/api/command', requireStudent, (req, res) => {
  const key = rateKey(req);
  if (!takeToken(key)) {
    return res.status(429).json({ ok: false, error: 'rate_limited' });
  }

  const { type, payload, nonce } = req.body || {};
  if (typeof type !== 'string' || type.length < 1 || type.length > 80) {
    return res.status(400).json({ ok: false, error: 'invalid_type' });
  }
  if (payload != null && typeof payload !== 'object') {
    return res.status(400).json({ ok: false, error: 'invalid_payload' });
  }
  if (!isAllowed(type, payload || {})) {
    return res.status(403).json({ ok: false, error: 'not_allowed' });
  }

  const agent = agents.get(state.roomId);
  if (!agent?.ws || agent.ws.readyState !== WebSocket.OPEN) {
    return res.status(503).json({ ok: false, error: 'agent_offline' });
  }

  const msg = {
    v: 1,
    t: 'command',
    roomId: state.roomId,
    id: crypto.randomUUID(),
    type,
    payload: payload || {},
    nonce: typeof nonce === 'string' ? nonce.slice(0, 64) : undefined,
    ts: Date.now()
  };

  agent.ws.send(JSON.stringify(msg));
  return res.json({ ok: true, forwarded: true, id: msg.id });
});

// Admin controls
app.post('/api/admin/lock', requireAdmin, (req, res) => {
  const { locked } = req.body || {};
  if (typeof locked !== 'boolean') {
    return res.status(400).json({ ok: false, error: 'locked must be boolean' });
  }
  state.locked = locked;
  res.json({ ok: true, locked: state.locked });
});

app.post('/api/admin/rotate-student-token', requireAdmin, (_req, res) => {
  const newToken = crypto.randomBytes(18).toString('base64url');
  state.studentToken = newToken;
  state.lastRotateAt = Date.now();
  res.json({ ok: true, studentToken: newToken, lastRotateAt: state.lastRotateAt });
});

app.get('/api/admin/status', requireAdmin, (_req, res) => {
  res.json({
    ok: true,
    roomId: state.roomId,
    locked: state.locked,
    agentConnected: agents.has(state.roomId),
    lastRotateAt: state.lastRotateAt,
    allowlistCount: allowlist?.allowed?.length || 0,
    allowlistPath: allowlist?.path || ALLOWLIST_PATH
  });
});

// HTTP server + WebSocket upgrade
const server = http.createServer(app);

const wss = new WebSocket.Server({ noServer: true });

function parseQuery(url) {
  try {
    const u = new URL(url, RELAY_BASE_URL || 'http://localhost');
    return Object.fromEntries(u.searchParams.entries());
  } catch {
    return {};
  }
}

server.on('upgrade', (req, socket, head) => {
  if (!req.url || !req.url.startsWith('/ws/agent')) {
    socket.destroy();
    return;
  }

  const q = parseQuery(req.url);
  const roomId = (q.room || '').toString();
  const token = (q.token || '').toString();
  if (roomId !== state.roomId || token !== state.agentToken) {
    socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
    socket.destroy();
    return;
  }

  wss.handleUpgrade(req, socket, head, (ws) => {
    wss.emit('connection', ws, req);
  });
});

wss.on('connection', (ws) => {
  const now = Date.now();
  // Single agent per room (new connection kicks old)
  const existing = agents.get(state.roomId);
  if (existing?.ws && existing.ws.readyState === WebSocket.OPEN) {
    try {
      existing.ws.close(4000, 'Replaced by new agent connection');
    } catch {}
  }

  agents.set(state.roomId, { ws, connectedAt: now, lastSeenAt: now });

  ws.on('message', (raw) => {
    const entry = agents.get(state.roomId);
    if (entry) entry.lastSeenAt = Date.now();

    // Optional: handle agent acks/logs (kept permissive)
    let msg;
    try {
      msg = JSON.parse(raw.toString('utf8'));
    } catch {
      return;
    }

    if (msg?.t === 'pong') return;
    // Future: store telemetry.
  });

  ws.on('close', () => {
    const entry = agents.get(state.roomId);
    if (entry?.ws === ws) agents.delete(state.roomId);
  });
});

// Ping keepalive
setInterval(() => {
  const entry = agents.get(state.roomId);
  if (!entry?.ws) return;
  if (entry.ws.readyState !== WebSocket.OPEN) return;
  try {
    entry.ws.send(JSON.stringify({ v: 1, t: 'ping', ts: Date.now() }));
  } catch {}
}, 15_000).unref();

server.listen(Number(RELAY_PORT), () => {
  // eslint-disable-next-line no-console
  console.log(`[relay] listening on :${RELAY_PORT} room=${state.roomId} locked=${state.locked}`);
});
