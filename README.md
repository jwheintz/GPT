# 🎓 Classroom Control

**A lightweight, Twitch-style interaction system for educators** - Give your students a way to send reactions, effects, and responses directly to your stream or recording!

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![OBS](https://img.shields.io/badge/OBS-32.x-purple.svg)

## ✨ Features

- **🌐 Web Interface** - Students interact through any browser, no installation required
- **🔐 Password Protected** - Simple class code keeps your controls private
- **⏸️ Kill Switch** - Instantly stop all incoming effects with one click
- **🎬 OBS Integration** - Control sources, filters, and media directly
- **📱 Mobile Friendly** - Works great on phones and tablets
- **🎨 Customizable** - Map any effect to your OBS setup
- **🔊 Sound Effects Ready** - Built-in support for audio triggers
- **📊 Quick Polls** - Students can respond to questions visually
- **🛡️ Anti-Spam** - Rate limiting and automatic spam detection

## 🏗️ Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Student Web   │      │    Supabase     │      │  Your Windows   │
│    Interface    │─────▶│  (Free Cloud)   │─────▶│   PC + OBS      │
│  (Squarespace)  │      │  Message Relay  │      │  Local Relay    │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

1. **Web Frontend** (hosted on Squarespace) - Password-protected buttons students click
2. **Supabase** (free tier) - Real-time message broker in the cloud
3. **Local Relay** (Windows app) - Receives messages, controls OBS via WebSocket

## 📋 Requirements

- **Windows PC** with OBS Studio 32.x (64-bit)
- **Free Supabase account** - [supabase.com](https://supabase.com)
- **Python 3.9+** (for the local relay app)
- **Squarespace website** (or any static hosting)

### Compatible With
- ✅ Bit Composer
- ✅ Stream Deck
- ✅ OBS WebSocket (built-in to OBS 28+)
- 🔜 VoiceMod (coming soon)

## 🚀 Quick Start

### Step 1: Set Up Supabase (5 minutes)

1. Create a free account at [supabase.com](https://supabase.com)
2. Create a new project (remember your database password)
3. Go to **SQL Editor** → **New Query**
4. Copy & paste the contents of `local-relay/supabase_setup.sql`
5. Click **Run** to create the tables
6. Go to **Settings** → **API** and copy:
   - Project URL (looks like `https://xxxxx.supabase.co`)
   - `anon` public key

### Step 2: Configure the Web Frontend (5 minutes)

1. Open `web/config.js`
2. Replace the placeholder values:
   ```javascript
   SUPABASE_URL: 'https://YOUR-PROJECT.supabase.co',
   SUPABASE_ANON_KEY: 'your-anon-key-here',
   CLASS_PASSWORD: 'your-secret-class-code',
   ```
3. Upload all files in `/web` to your Squarespace site:
   - Go to your Squarespace site → **Settings** → **Advanced** → **Code Injection**
   - Or create a **Code Block** page and paste the HTML
   - Or use **Files** to upload and link them

### Step 3: Set Up OBS (10 minutes)

1. **Enable WebSocket Server** in OBS:
   - Go to **Tools** → **WebSocket Server Settings**
   - Check **Enable WebSocket server**
   - Set a password (recommended) or leave blank
   - Default port is 4455

2. **Create Effect Sources** in OBS:
   - Create **Browser Sources** for visual effects (confetti, thumbs up, etc.)
   - Create **Media Sources** for sound effects
   - Name them to match the config (e.g., "Confetti", "ThumbsUp", "SFX_Ding")
   - Make sure sources are **hidden by default** (eye icon off)

### Step 4: Run the Local Relay (5 minutes)

1. Open Command Prompt in the `local-relay` folder
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create your local config:
   ```bash
   copy config.py config_local.py
   ```
4. Edit `config_local.py` with your settings:
   ```python
   SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
   SUPABASE_KEY = "your-anon-key-here"
   OBS_PASSWORD = "your-obs-websocket-password"
   ```
5. Run the relay:
   ```bash
   python relay.py
   ```
6. Look for the system tray icon (green = connected)

## 🎮 Using the System

### For Students
1. Go to your class website
2. Enter the class code
3. Click effect buttons to send reactions!

### For Teachers
- **System Tray Icon**: Shows connection status
  - 🟢 Green = All connected
  - 🟡 Yellow = OBS disconnected
  - 🔴 Red = System paused

- **Kill Switch**: Double-click tray icon or right-click → "Pause" to stop ALL incoming effects instantly

- **Keyboard Shortcut** (console mode): Press `P` + Enter to toggle pause

## 📁 Project Structure

```
classroom-control/
├── web/                      # Web frontend (upload to Squarespace)
│   ├── index.html           # Main page
│   ├── style.css            # Styling
│   ├── config.js            # Configuration (edit this!)
│   └── app.js               # Application logic
│
├── local-relay/              # Windows relay app
│   ├── relay.py             # Main application
│   ├── config.py            # Default configuration
│   ├── config_local.py      # Your local settings (create this)
│   ├── requirements.txt     # Python dependencies
│   └── supabase_setup.sql   # Database setup script
│
└── README.md                 # This file
```

## ⚙️ Configuration Reference

### Web Config (`web/config.js`)

| Setting | Description |
|---------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | Your Supabase anon/public key |
| `CLASS_PASSWORD` | Password students need to join |
| `ACTION_COOLDOWN` | Milliseconds between allowed actions |
| `CATEGORIES` | Enable/disable effect categories |

### Local Config (`local-relay/config_local.py`)

| Setting | Description |
|---------|-------------|
| `SUPABASE_URL` | Same as web config |
| `SUPABASE_KEY` | Same as web config |
| `OBS_HOST` | OBS WebSocket host (default: localhost) |
| `OBS_PORT` | OBS WebSocket port (default: 4455) |
| `OBS_PASSWORD` | OBS WebSocket password |
| `VISUAL_EFFECTS` | Map actions to OBS sources |
| `SOUND_EFFECTS` | Map actions to media sources |
| `COMMAND_RATE_LIMIT` | Min ms between commands |
| `SPAM_THRESHOLD` | Auto-pause after this many rapid commands |

## 🎨 Customizing Effects

### Adding a New Visual Effect

1. Create a source in OBS (e.g., Browser Source named "Rainbow")
2. Add it to `config_local.py`:
   ```python
   VISUAL_EFFECTS = {
       # ... existing effects ...
       "rainbow": {
           "type": "source",
           "source_name": "Rainbow",
           "duration": 3000,  # Show for 3 seconds
       },
   }
   ```
3. Add a button in `web/index.html`:
   ```html
   <button class="effect-btn" data-action="rainbow" data-category="visual">
       <span class="effect-icon">🌈</span>
       <span class="effect-name">Rainbow</span>
   </button>
   ```

### Adding Filter Effects

```python
FILTER_EFFECTS = {
    "grayscale": {
        "type": "filter",
        "source_name": "Webcam",       # Source with the filter
        "filter_name": "Grayscale",     # Filter name in OBS
        "duration": 5000,               # How long to apply
    },
}
```

## 🔧 Troubleshooting

### "Connection failed" in web interface
- Check that Supabase URL and key are correct
- Make sure tables were created (run the SQL setup)

### OBS sources not showing
- Verify source names match exactly (case-sensitive)
- Check that sources exist in your current scene
- Make sure OBS WebSocket is enabled and password matches

### System tray icon is yellow
- OBS WebSocket connection failed
- Check OBS is running and WebSocket is enabled
- Verify port (default 4455) isn't blocked

### Commands seem delayed
- Normal delay is ~500ms to 1 second
- Check your internet connection
- Supabase free tier has some latency

## 🔜 Roadmap

- [ ] VoiceMod integration for voice effects
- [ ] Counter display for poll results
- [ ] Custom CSS themes
- [ ] Teacher dashboard for real-time monitoring
- [ ] Multiple class/room support
- [ ] Integration with Stream Deck

## 📄 License

MIT License - Feel free to use and modify for your classroom!

## 🙏 Credits

Built for educators who want to make their classes more engaging without the complexity of full streaming platforms.

---

**Need help?** Open an issue or check the [Getting Started Guide](GETTING_STARTED.md)
