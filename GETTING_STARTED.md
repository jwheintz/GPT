# 🎓 Getting Started Guide

This comprehensive guide walks you through setting up Classroom Control from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Supabase Setup](#supabase-setup)
3. [OBS Configuration](#obs-configuration)
4. [Web Frontend Setup](#web-frontend-setup)
5. [Local Relay Installation](#local-relay-installation)
6. [Squarespace Hosting](#squarespace-hosting)
7. [Testing Everything](#testing-everything)
8. [Creating OBS Effects](#creating-obs-effects)

---

## Prerequisites

Before you begin, make sure you have:

- ✅ Windows 10/11 PC
- ✅ OBS Studio 32.x (64-bit) installed - [Download OBS](https://obsproject.com)
- ✅ Python 3.9 or newer - [Download Python](https://python.org)
- ✅ A Squarespace website (or other hosting)
- ✅ About 30 minutes for initial setup

---

## Supabase Setup

Supabase is a free service that acts as a bridge between your web interface and local PC.

### Step 1: Create Account

1. Go to [supabase.com](https://supabase.com)
2. Click **Start your project**
3. Sign up with GitHub or email

### Step 2: Create Project

1. Click **New Project**
2. Choose your organization
3. Enter project details:
   - **Name**: `classroom-control` (or anything you like)
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to you
4. Click **Create new project**
5. Wait 1-2 minutes for setup

### Step 3: Create Database Tables

1. In your project dashboard, click **SQL Editor** (left sidebar)
2. Click **New Query**
3. Open the file `local-relay/supabase_setup.sql` from this project
4. Copy ALL the contents
5. Paste into Supabase SQL Editor
6. Click **Run** (or press Ctrl+Enter)
7. You should see "Success. No rows returned"

### Step 4: Get Your API Keys

1. Click **Settings** (gear icon) → **API**
2. Copy these values (you'll need them twice):

   | Value | Where to Find |
   |-------|---------------|
   | **Project URL** | Under "Project URL" - looks like `https://abcdefg.supabase.co` |
   | **anon public key** | Under "Project API keys" - the `anon` key (long string) |

⚠️ **Keep these keys safe** but note they are meant to be public (hence "anon" key)

---

## OBS Configuration

### Enable WebSocket Server

OBS 28+ has a built-in WebSocket server. Here's how to enable it:

1. Open OBS Studio
2. Go to **Tools** → **WebSocket Server Settings**
3. Check ✅ **Enable WebSocket server**
4. Settings:
   - **Server Port**: `4455` (default, leave as-is)
   - **Enable Authentication**: Recommended ✅
   - **Server Password**: Set a password (you'll need this for the relay)
5. Click **Apply** or **OK**

### Verify It's Working

1. In the WebSocket Server Settings, you should see "Server Status: Listening"
2. Note the port number (default 4455)

---

## Web Frontend Setup

### Step 1: Configure Settings

1. Navigate to the `web` folder in this project
2. Open `config.js` in a text editor (Notepad++, VS Code, etc.)
3. Replace the placeholder values:

```javascript
const CONFIG = {
    // Paste your Supabase values here
    SUPABASE_URL: 'https://YOUR-PROJECT-ID.supabase.co',
    SUPABASE_ANON_KEY: 'your-very-long-anon-key-here',
    
    // Set your class password
    CLASS_PASSWORD: 'myclass2024',  // Students will enter this
    
    // Cooldown between actions (milliseconds)
    ACTION_COOLDOWN: 3000,  // 3 seconds - adjust as needed
    
    // ... rest of config
};
```

4. Save the file

### Step 2: Test Locally (Optional)

You can test the web interface locally before uploading:

1. Open the `web` folder
2. Double-click `index.html` to open in browser
3. Enter your password
4. You should see the control panel (with "Demo mode" since Supabase isn't fully configured yet)

---

## Local Relay Installation

### Step 1: Install Python Dependencies

1. Open **Command Prompt** or **PowerShell**
2. Navigate to the local-relay folder:
   ```cmd
   cd path\to\classroom-control\local-relay
   ```
3. Install required packages:
   ```cmd
   pip install -r requirements.txt
   ```

### Step 2: Create Local Configuration

1. Copy the config template:
   ```cmd
   copy config.py config_local.py
   ```
2. Open `config_local.py` in a text editor
3. Update the settings:

```python
# Supabase Configuration (same values as web config)
SUPABASE_URL = "https://YOUR-PROJECT-ID.supabase.co"
SUPABASE_KEY = "your-very-long-anon-key-here"

# OBS WebSocket Configuration
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = "your-obs-websocket-password"  # From OBS settings
```

### Step 3: Test the Relay

1. Make sure OBS is running with WebSocket enabled
2. Run the relay:
   ```cmd
   python relay.py
   ```
3. You should see:
   ```
   ==================================================
     Classroom Control - Local Relay
   ==================================================
   
   Connected to OBS at localhost:4455
   Connected to Supabase
   Started listening for commands
   
   ✅ Relay is running!
   ```

4. Look for the system tray icon (should be green)

---

## Squarespace Hosting

There are several ways to add the web interface to Squarespace:

### Option A: Code Block (Easiest)

1. In Squarespace, create a new page
2. Add a **Code Block**
3. Paste the contents of `index.html`
4. In the same page, add the CSS and JS via Code Injection:
   - Go to **Settings** → **Advanced** → **Code Injection**
   - Add the CSS in the **Header** section:
     ```html
     <style>
     /* Paste contents of style.css here */
     </style>
     ```
   - Add the JS in the **Footer** section:
     ```html
     <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
     <script>
     /* Paste contents of config.js here */
     </script>
     <script>
     /* Paste contents of app.js here */
     </script>
     ```

### Option B: Custom Page with Files

1. Upload `style.css`, `config.js`, and `app.js` to Squarespace
2. Note their URLs after upload
3. Update `index.html` to reference those URLs:
   ```html
   <link rel="stylesheet" href="https://your-site.squarespace.com/s/style.css">
   <script src="https://your-site.squarespace.com/s/config.js"></script>
   <script src="https://your-site.squarespace.com/s/app.js"></script>
   ```
4. Paste the modified HTML into a Code Block

### Option C: Subdomain/External Hosting

For more control, host the files on:
- GitHub Pages (free)
- Netlify (free)
- Vercel (free)

Then link to it from Squarespace or use an iframe.

### Adding Squarespace Password Protection

For an additional layer of security:

1. Go to the page with your control panel
2. Click **Settings** (gear icon)
3. Under **General**, find **Password**
4. Enable page password and set it

Now students need BOTH the Squarespace password AND your class code!

---

## Testing Everything

### Full System Test

1. **Start OBS** with WebSocket enabled
2. **Run the relay**: `python relay.py`
3. **Open the web interface** in a browser
4. **Enter the class password**
5. **Click an effect button**
6. **Watch the relay console** - you should see:
   ```
   Executing command: confetti (category: visual)
   ```

### Testing Without OBS Sources

The relay will log errors if sources don't exist, but won't crash. This is normal until you create your OBS effects.

---

## Creating OBS Effects

### Visual Effect: Confetti Example

1. In OBS, click **+** under Sources
2. Select **Browser**
3. Name it exactly: `Confetti`
4. Set the URL to a confetti animation:
   - Free option: `https://embed.lottiefiles.com/animation/confetti`
   - Or create your own HTML animation
5. Set dimensions (e.g., 1920x1080)
6. Click **OK**
7. **IMPORTANT**: Click the 👁️ eye icon to **hide** the source by default

### Sound Effect: Ding Example

1. In OBS, click **+** under Sources
2. Select **Media Source**
3. Name it exactly: `SFX_Ding`
4. Set the local file to a .mp3 or .wav sound effect
5. Uncheck "Loop"
6. Click **OK**

### Emoji Overlay Example

For reaction emojis, create Browser sources with simple HTML:

1. Create a new Browser source named `Reaction_Fire`
2. Set URL to a local HTML file or use this inline:
   ```
   data:text/html,<div style="font-size:200px;text-align:center;padding-top:40vh">🔥</div>
   ```
3. Make it transparent (custom CSS: `body { background: transparent; }`)

---

## Tips for Best Results

### Organizing OBS Sources

- Create a **folder/group** named "Classroom Effects"
- Put all effect sources in this folder
- Keep them hidden by default
- The relay will show/hide them automatically

### Recommended Effect Durations

| Effect Type | Suggested Duration |
|-------------|-------------------|
| Quick reactions | 1-2 seconds |
| Celebrations | 3-4 seconds |
| "Slow down" requests | 5+ seconds |
| Sound effects | Match audio length |

### Student Guidelines

Share these with your class:
- Use effects to engage, not to distract
- Respect the cooldown period
- The teacher can pause effects at any time
- Be appropriate and educational!

---

## Troubleshooting

### "Demo mode" in web interface
- Check that `config.js` has correct Supabase credentials
- Verify tables exist in Supabase (SQL Editor → run setup script again)

### Relay shows "Failed to connect to OBS"
- Make sure OBS is running
- Verify WebSocket is enabled (Tools → WebSocket Server Settings)
- Check password matches in both OBS and `config_local.py`
- Try port 4455 (default)

### Effects not showing in OBS
- Source names must match EXACTLY (case-sensitive)
- Source must exist in your current scene
- Try manually showing/hiding the source to verify it works

### Commands not being received
- Check relay console for errors
- Verify Supabase credentials match between web and relay
- Try inserting a test command directly in Supabase SQL Editor

---

## Next Steps

Once basic setup works:

1. **Customize effects** - Add your own visual and sound effects
2. **Brand the interface** - Modify CSS to match your style
3. **Create scenes** - Design OBS scenes with effect placeholders
4. **Test with students** - Do a dry run before going live

Happy teaching! 🎓
