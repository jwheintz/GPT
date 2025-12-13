# Quick Setup Guide

## 1. Install OBS WebSocket Plugin

1. Download the latest OBS WebSocket plugin from: https://github.com/obsproject/obs-websocket/releases
2. Extract the files
3. Copy the files to your OBS installation directory:
   - `obs-websocket.dll` → `C:\Program Files\obs-studio\obs-plugins\64bit\`
   - `obs-websocket.pdb` → `C:\Program Files\obs-studio\obs-plugins\64bit\`
4. Restart OBS Studio

## 2. Configure OBS WebSocket

1. Open OBS Studio
2. Go to **Tools → WebSocket Server Settings**
3. Check **Enable WebSocket server**
4. Set **Server Port**: `4455`
5. Set **Server Password**: (choose a strong password)
6. Click **OK**

## 3. Install Python Dependencies

Open Command Prompt or PowerShell and run:

```bash
pip install -r requirements.txt
```

If you get permission errors, try:
```bash
pip install --user -r requirements.txt
```

## 4. Configure Server

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Open `.env` in Notepad and update:
   - `OBS_PASSWORD` - The password you set in OBS WebSocket settings
   - `WEB_PASSWORD` - Password students will use to access the web interface
   - `ALLOWED_ORIGINS` - Your Squarespace domain (or `*` for testing)

## 5. Test Locally

1. Start OBS Studio
2. Create a test scene with a source that has filters
3. Run the server:
   ```bash
   python server.py
   ```
   Or double-click `start-server.bat`

4. Open `web/index.html` in your browser
5. Update `SERVER_URL` in `web/app.js` to `http://localhost:8080`
6. Test login and filter controls

## 6. Deploy Web Interface

### Option A: Host on Squarespace

1. Upload `web/` folder contents to Squarespace
2. Update `SERVER_URL` in `web/app.js` to your public server address
3. Embed or link to the HTML file

### Option B: Host Elsewhere

Upload `web/` folder to:
- GitHub Pages
- Netlify
- Your own web server
- Any static hosting service

## 7. Make Server Publicly Accessible

Choose one method:

### Method 1: Port Forwarding
1. Log into your router
2. Forward port 8080 to your Windows machine's local IP
3. Use your public IP address in `SERVER_URL`

### Method 2: ngrok (Easiest for Testing)
1. Download ngrok: https://ngrok.com/
2. Run: `ngrok http 8080`
3. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
4. Use this URL in `SERVER_URL`

### Method 3: Cloudflare Tunnel
1. Install cloudflared
2. Run: `cloudflared tunnel --url http://localhost:8080`
3. Use the provided URL

## 8. Security Checklist

- [ ] Changed default passwords
- [ ] Set strong OBS WebSocket password
- [ ] Set strong web interface password
- [ ] Configured `ALLOWED_ORIGINS` in `.env`
- [ ] Using HTTPS (via ngrok/Cloudflare/etc.)
- [ ] Firewall configured (only allow necessary ports)
- [ ] Tested emergency stop functionality

## Common Issues

**"Connection refused"**
- Server not running
- Wrong port number
- Firewall blocking connection

**"OBS not connected"**
- OBS Studio not running
- WebSocket plugin not installed
- Wrong password in `.env`
- WebSocket server not enabled in OBS

**"CORS error" in browser**
- Update `ALLOWED_ORIGINS` in `.env`
- Restart server after changing `.env`

**"Module not found"**
- Run `pip install -r requirements.txt`
- Check Python version (need 3.8+)

## Next Steps

1. Test all functionality locally
2. Set up public access
3. Deploy web interface
4. Test from student device
5. Train students on how to use it
6. Have fun teaching!
