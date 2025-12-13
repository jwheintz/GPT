# Quick Start Guide

## 5-Minute Setup

### 1. Install OBS WebSocket Plugin (2 min)
- Download from: https://github.com/obsproject/obs-websocket/releases
- Extract to OBS plugins folder
- Enable in OBS: Tools → WebSocket Server Settings

### 2. Install Python Dependencies (1 min)
```bash
pip install -r requirements.txt
```

### 3. Configure (1 min)
```bash
copy .env.example .env
```
Edit `.env`:
- Set `OBS_PASSWORD` (from OBS settings)
- Set `WEB_PASSWORD` (for students)

### 4. Test (1 min)
```bash
python test_obs_connection.py
python server.py
```

Open `web/index.html` in browser, update `SERVER_URL` in `app.js` to `http://localhost:8080`

## File Structure

```
.
├── server.py              # Main server (runs on Windows)
├── requirements.txt       # Python dependencies
├── config.json           # Configuration (optional)
├── .env                  # Environment variables (create from .env.example)
├── start-server.bat      # Windows startup script
├── test_obs_connection.py  # Test OBS connection
├── web/
│   ├── index.html        # Web interface
│   ├── style.css         # Styles
│   └── app.js            # Frontend logic
└── README.md             # Full documentation
```

## Key Commands

**Start server:**
```bash
python server.py
```

**Test OBS connection:**
```bash
python test_obs_connection.py
```

**Windows startup:**
Double-click `start-server.bat`

## Important URLs

- Local server: `http://localhost:8080`
- Health check: `http://localhost:8080/health`
- Web interface: Open `web/index.html` in browser

## Next Steps

1. ✅ Test locally
2. 🔄 Set up public access (ngrok/port forwarding)
3. 🌐 Deploy web interface to Squarespace
4. 🎓 Share with students!

## Troubleshooting

**Can't connect to OBS?**
- Run `python test_obs_connection.py`
- Check OBS WebSocket is enabled
- Verify password in `.env`

**Server won't start?**
- Check port 8080 is free
- Verify Python dependencies installed
- Check `.env` file exists

**Web interface errors?**
- Update `SERVER_URL` in `web/app.js`
- Check CORS settings in `.env`
- Verify server is running

## Support

See `SETUP.md` for detailed setup instructions.
See `README.md` for full documentation.
