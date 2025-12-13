/*
Studio agent (runs on your Windows OBS machine):
- Makes an outbound WebSocket connection to the relay.
- Receives commands and applies them to OBS via OBS WebSocket.
- Has a local PANIC lock you can toggle instantly.

This is intended to be run by you (not students).
*/

require('dotenv').config();

const WebSocket = require('ws');
const express = require('express');

const { OBSWebSocket } = require('obs-websocket-js');

const {
  RELAY_WS_URL = 'ws://localhost:8787/ws/agent',
  ROOM_ID = 'classroom',
  AGENT_TOKEN = 'change-me-agent-token',

  OBS_WS_URL = 'ws://127.0.0.1:4455',
  OBS_WS_PASSWORD = '',

  // Local kill-switch HTTP server (for Stream Deck / quick toggle)
  LOCAL_CONTROL_PORT = '39200',
  LOCAL_CONTROL_TOKEN = 'change-me-local-control-token',

  // Optional: start locked
  PANIC_LOCKED = 'false'
} = process.env;

let panicLocked = PANIC_LOCKED.toLowerCase() === 'true';

const obs = new OBSWebSocket();
let obsConnected = false;

async function connectObs() {
  if (obsConnected) return;
  try {
    await obs.connect(OBS_WS_URL, OBS_WS_PASSWORD || undefined);
    obsConnected = true;
    // eslint-disable-next-line no-console
    console.log('[agent] connected to OBS WebSocket');
  } catch (e) {
    obsConnected = false;
    // eslint-disable-next-line no-console
    console.error('[agent] OBS connect failed:', e?.message || e);
  }
}

obs.on('ConnectionClosed', () => {
  obsConnected = false;
  // eslint-disable-next-line no-console
  console.warn('[agent] OBS connection closed');
});

function wsUrl() {
  const u = new URL(RELAY_WS_URL);
  u.searchParams.set('room', ROOM_ID);
  u.searchParams.set('token', AGENT_TOKEN);
  return u.toString();
}

function safeBool(v) {
  return !!v;
}

async function applyCommand(cmd) {
  if (panicLocked) {
    return { ok: false, error: 'panic_locked' };
  }

  // Ensure OBS connection (best effort)
  if (!obsConnected) await connectObs();
  if (!obsConnected) return { ok: false, error: 'obs_offline' };

  const { type, payload } = cmd;

  try {
    switch (type) {
      case 'scene.set': {
        // payload: { sceneName }
        if (!payload?.sceneName) return { ok: false, error: 'missing_sceneName' };
        await obs.call('SetCurrentProgramScene', { sceneName: String(payload.sceneName) });
        return { ok: true };
      }

      case 'filter.enable': {
        // payload: { sourceName, filterName }
        if (!payload?.sourceName || !payload?.filterName) return { ok: false, error: 'missing_sourceName_or_filterName' };
        await obs.call('SetSourceFilterEnabled', {
          sourceName: String(payload.sourceName),
          filterName: String(payload.filterName),
          filterEnabled: true
        });
        return { ok: true };
      }

      case 'filter.disable': {
        if (!payload?.sourceName || !payload?.filterName) return { ok: false, error: 'missing_sourceName_or_filterName' };
        await obs.call('SetSourceFilterEnabled', {
          sourceName: String(payload.sourceName),
          filterName: String(payload.filterName),
          filterEnabled: false
        });
        return { ok: true };
      }

      case 'filter.toggle': {
        if (!payload?.sourceName || !payload?.filterName) return { ok: false, error: 'missing_sourceName_or_filterName' };
        const { filters } = await obs.call('GetSourceFilterList', { sourceName: String(payload.sourceName) });
        const f = (filters || []).find((x) => x.filterName === payload.filterName);
        if (!f) return { ok: false, error: 'filter_not_found' };
        await obs.call('SetSourceFilterEnabled', {
          sourceName: String(payload.sourceName),
          filterName: String(payload.filterName),
          filterEnabled: !safeBool(f.filterEnabled)
        });
        return { ok: true };
      }

      case 'input.muteToggle': {
        // payload: { inputName }
        if (!payload?.inputName) return { ok: false, error: 'missing_inputName' };
        await obs.call('ToggleInputMute', { inputName: String(payload.inputName) });
        return { ok: true };
      }

      case 'hotkey.trigger': {
        // payload: { hotkeyName }
        if (!payload?.hotkeyName) return { ok: false, error: 'missing_hotkeyName' };
        await obs.call('TriggerHotkeyByName', { hotkeyName: String(payload.hotkeyName) });
        return { ok: true };
      }

      default:
        return { ok: false, error: 'unknown_command_type' };
    }
  } catch (e) {
    return { ok: false, error: 'obs_error', message: e?.message || String(e) };
  }
}

function startLocalControl() {
  const app = express();
  app.use(express.json({ limit: '8kb' }));

  function requireLocal(req, res, next) {
    const auth = (req.headers.authorization || '').toString();
    const token = auth.startsWith('Bearer ') ? auth.slice('Bearer '.length) : '';
    if (!token || token !== LOCAL_CONTROL_TOKEN) return res.status(401).json({ ok: false });
    return next();
  }

  app.get('/status', (_req, res) => {
    res.json({ ok: true, panicLocked, obsConnected });
  });

  app.post('/panic', requireLocal, (req, res) => {
    const { locked } = req.body || {};
    if (typeof locked !== 'boolean') return res.status(400).json({ ok: false, error: 'locked must be boolean' });
    panicLocked = locked;
    // eslint-disable-next-line no-console
    console.warn(`[agent] PANIC ${panicLocked ? 'ENABLED' : 'DISABLED'}`);
    res.json({ ok: true, panicLocked });
  });

  app.listen(Number(LOCAL_CONTROL_PORT), '127.0.0.1', () => {
    // eslint-disable-next-line no-console
    console.log(`[agent] local control on http://127.0.0.1:${LOCAL_CONTROL_PORT}`);
  });
}

function startRelayConnection() {
  let ws;
  let closed = false;

  const connect = () => {
    if (closed) return;
    const url = wsUrl();
    ws = new WebSocket(url);

    ws.on('open', () => {
      // eslint-disable-next-line no-console
      console.log('[agent] connected to relay');
      ws.send(JSON.stringify({ v: 1, t: 'hello', roomId: ROOM_ID, ts: Date.now() }));
    });

    ws.on('message', async (raw) => {
      let msg;
      try {
        msg = JSON.parse(raw.toString('utf8'));
      } catch {
        return;
      }

      if (msg?.t === 'ping') {
        try {
          ws.send(JSON.stringify({ v: 1, t: 'pong', ts: Date.now() }));
        } catch {}
        return;
      }

      if (msg?.t !== 'command') return;

      const result = await applyCommand(msg);
      // Best-effort ack
      try {
        ws.send(JSON.stringify({ v: 1, t: 'ack', id: msg.id, ok: result.ok, error: result.error, ts: Date.now() }));
      } catch {}

      if (!result.ok) {
        // eslint-disable-next-line no-console
        console.warn('[agent] command failed:', msg.type, result);
      }
    });

    ws.on('close', (code, reason) => {
      // eslint-disable-next-line no-console
      console.warn('[agent] relay disconnected:', code, reason?.toString?.() || '');
      setTimeout(connect, 1500).unref();
    });

    ws.on('error', (e) => {
      // eslint-disable-next-line no-console
      console.error('[agent] relay error:', e?.message || e);
      try {
        ws.close();
      } catch {}
    });
  };

  connect();

  return () => {
    closed = true;
    try {
      ws?.close();
    } catch {}
  };
}

function wireStdinPanicToggle() {
  if (!process.stdin.isTTY) return;
  process.stdin.setRawMode(true);
  process.stdin.resume();
  process.stdin.on('data', (buf) => {
    const s = buf.toString('utf8');
    if (s === 'p' || s === 'P') {
      panicLocked = !panicLocked;
      // eslint-disable-next-line no-console
      console.warn(`[agent] PANIC ${panicLocked ? 'ENABLED' : 'DISABLED'} (via keyboard)`);
    }
    // Ctrl+C
    if (buf.length === 1 && buf[0] === 3) process.exit(0);
  });
}

(async function main() {
  // eslint-disable-next-line no-console
  console.log('[agent] starting…');
  startLocalControl();
  wireStdinPanicToggle();
  await connectObs();
  startRelayConnection();
})();
