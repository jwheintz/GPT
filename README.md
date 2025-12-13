# OBS Classroom Control Interface

A web-based control system that allows students to interact with OBS Studio filters and effects during class presentations. The system consists of a local server running on your Windows machine and a web interface that can be embedded in Squarespace.

## Features

- 🌐 **Web-based interface** - No installation required for students
- 🔒 **Password protected** - Secure access control
- ⚡ **Real-time OBS control** - Toggle filters, enable/disable effects
- 🛑 **Emergency stop** - Instantly disable all controls
- 📱 **Responsive design** - Works on desktop and mobile devices
- 🔌 **OBS WebSocket integration** - Direct connection to OBS Studio
- 🎯 **Future-ready** - Placeholder for VoiceMod and other integrations

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│  Squarespace    │  HTTP   │  Local Server    │ WebSocket│  OBS Studio │
│  (Web Frontend) │ ──────> │  (Windows PC)    │ ───────> │  (Filters)  │
└─────────────────┘         └──────────────────┘         └─────────────┘
```

## Prerequisites

### On Your Windows Machine:

1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **OBS Studio 32.x** (64-bit) - [Download OBS](https://obsproject.com/)
3. **OBS WebSocket Plugin** - [Download Plugin](https://github.com/obsproject/obs-websocket/releases)
   - Install the plugin by extracting the files to your OBS installation directory
   - Default WebSocket port: 4455
   - Set a password in OBS: Tools → WebSocket Server Settings

### Network Setup:

- Your Windows machine needs to be accessible from the internet (for Squarespace to connect)
- Options:
  - **Port forwarding** on your router (port 8080)
  - **VPN** connection
  - **Cloud tunnel** (ngrok, Cloudflare Tunnel, etc.)
  - **Public IP** with firewall rules

## Installation

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure OBS WebSocket

1. Open OBS Studio
2. Go to **Tools → WebSocket Server Settings**
3. Enable WebSocket server
4. Set port to `4455` (default)
5. Set a password (remember this!)
6. Click OK

### Step 3: Configure the Server

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` with your settings:
   ```
   OBS_HOST=localhost
   OBS_PORT=4455
   OBS_PASSWORD=your_obs_password_here
   
   SERVER_PORT=8080
   WEB_PASSWORD=your_web_password_here
   
   ALLOWED_ORIGINS=https://your-site.squarespace.com
   ```

### Step 4: Test the Server Locally

1. Start OBS Studio
2. Run the server:
   ```bash
   python server.py
   ```

3. Open `web/index.html` in your browser
4. Update `SERVER_URL` in `web/app.js` to `http://localhost:8080`
5. Test login and filter controls

## Deployment

### Option 1: Embed in Squarespace

1. **Host the web files**:
   - Upload `web/index.html`, `web/style.css`, and `web/app.js` to your Squarespace site
   - Or host them on a CDN/service like GitHub Pages, Netlify, etc.

2. **Update the server URL**:
   - Edit `web/app.js`
   - Change `SERVER_URL` to your public server address:
     ```javascript
     const SERVER_URL = 'https://your-public-ip-or-domain:8080';
     ```

3. **Embed in Squarespace**:
   - Add a Code Block
   - Use an iframe or embed the HTML directly
   - Example iframe:
     ```html
     <iframe src="https://your-site.com/classroom-control/index.html" 
             width="100%" 
             height="800px" 
             frameborder="0">
     </iframe>
     ```

### Option 2: Direct Link

Simply link to your hosted web interface from Squarespace.

## Running the Server

### Windows (Manual)

```bash
python server.py
```

### Windows (Background Service)

Use `start-server.bat` to run in the background, or set up as a Windows service.

### Auto-start on Boot

1. Create a shortcut to `start-server.bat`
2. Place it in Windows Startup folder:
   - Press `Win+R`, type `shell:startup`
   - Copy shortcut there

## Security Considerations

1. **Change default passwords** - Never use default passwords in production
2. **Use HTTPS** - Set up SSL/TLS for the web interface
3. **Firewall rules** - Only allow connections from trusted sources
4. **VPN recommended** - Consider using a VPN for additional security
5. **Regular updates** - Keep Python packages and OBS updated

## Usage

### For Students:

1. Access the web interface (hosted on Squarespace)
2. Enter the password
3. Select Scene → Source → Filter
4. Toggle or enable/disable filters
5. See real-time changes in OBS

### For Instructor:

1. **Emergency Stop**: Click the emergency stop button to instantly disable all controls
2. **Resume**: Use the `/emergency/resume` endpoint with password to resume
3. **Monitor**: Check server logs for activity

## API Endpoints

### Authentication
- `POST /auth` - Authenticate with password

### OBS Control
- `GET /obs/scenes` - Get list of scenes
- `GET /obs/sources?scene=<name>` - Get sources in a scene
- `GET /obs/filters?source=<name>` - Get filters for a source
- `POST /obs/filter/toggle` - Toggle a filter
- `POST /obs/filter/set` - Set filter enabled state
- `POST /obs/filter/settings` - Update filter settings

### Emergency Controls
- `POST /emergency/stop` - Activate emergency stop
- `POST /emergency/resume` - Resume operations

### Status
- `GET /health` - Check server and OBS connection status

## Troubleshooting

### Server won't start
- Check if port 8080 is already in use
- Verify Python and dependencies are installed
- Check firewall settings

### Can't connect to OBS
- Verify OBS WebSocket plugin is installed
- Check OBS WebSocket server is enabled
- Verify password matches in `.env` and OBS settings
- Check OBS is running

### Web interface can't reach server
- Verify server is running
- Check `SERVER_URL` in `app.js` matches your server address
- Check CORS settings in `.env`
- Verify firewall/port forwarding is configured

### Emergency stop not working
- Check password is correct
- Verify server is receiving requests
- Check server logs for errors

## Future Enhancements

- [ ] VoiceMod sound effects integration
- [ ] Scene switching controls
- [ ] Source visibility toggles
- [ ] Custom filter presets
- [ ] Student voting system
- [ ] Analytics and usage tracking
- [ ] Multiple OBS instance support

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review server logs
3. Verify OBS WebSocket connection
4. Test with localhost first before deploying

## License

This project is provided as-is for educational use.
