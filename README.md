# Classroom OBS Control Interface

Short description
- A password-protected, Squarespace-embeddable web UI for students that relays “small on-screen changes” back to your local Windows studio machine, where a lightweight agent applies them to OBS via OBS WebSocket.

Status
- Alpha prototype: relay + agent + static web UI, with a hard “lock/kill switch” and token rotation.

Quick links
- Web UI (embed): `web/index.html`
- Relay server: `relay/index.js`
- Studio agent: `agent/index.js`
- Contributing: CONTRIBUTING.md
- Issues: https://github.com/jwheintz/GPT/issues

Quickstart (this repo)
1. Prerequisites
   - Node.js >= 18
   - OBS Studio 28+ (you’re on 32.x) with OBS WebSocket enabled (Settings → WebSocket Server)

2. Install dependencies
```bash
npm install
```

3. Configure env
- Copy `.env.example` to `.env` and change tokens/passwords.

4. Run the relay (host this somewhere public)
```bash
npm run relay
```

5. Run the studio agent (on your Windows OBS machine)
```bash
npm run agent
```

6. Use the Squarespace web UI
- Upload or embed `web/index.html` into a password-protected Squarespace page (via a Code Block or iframe).
- In the page, set:
  - Relay API URL (e.g. `https://your-relay.example.com`)
  - Student token (your `STUDENT_TOKEN`)

Safety (recommended)
- The relay **blocks everything** unless it matches `relay/allowlist.json`.
- Edit `relay/allowlist.json` to your exact OBS source/filter/scene/input names.

Admin “stop everything now”
- Relay hard lock (blocks all student commands immediately):
```bash
curl -X POST http://localhost:8787/api/admin/lock \\
  -H \"Authorization: Bearer <ADMIN_TOKEN>\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"locked\":true}'
```
- Agent local panic (ignores commands even if relay is unlocked):
```bash
curl -X POST http://127.0.0.1:39200/panic \\
  -H \"Authorization: Bearer <LOCAL_CONTROL_TOKEN>\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"locked\":true}'
```

7. Need help?
- Open an issue at https://github.com/jwheintz/GPT/issues and include:
  - OS/version
  - Steps to reproduce
  - Logs or error output

Roadmap ideas (next)
- Add “rooms” per class period and a short join code
- Add a teacher dashboard to lock/rotate without curl
- Add VoiceMod triggers (via hotkeys or local HTTP bridge) and Stream Deck “panic” button integrations
