# 📖 Complete Setup Guide

This guide will walk you through every step of setting up your Classroom OBS Control System, from installation to first use.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [OBS Studio Setup](#obs-studio-setup)
3. [Server Installation](#server-installation)
4. [Network Configuration](#network-configuration)
5. [Web Interface Setup](#web-interface-setup)
6. [Testing](#testing)
7. [Going Live](#going-live)

---

## System Requirements

### Your Teaching Computer (Windows)
- Windows 10 or 11 (64-bit)
- OBS Studio 32.x (latest)
- Node.js v16 or higher
- Stable internet connection
- At least 4GB RAM
- Router access (for port forwarding, if needed)

### Student Devices
- Any device with a modern web browser
- Internet connection
- **No software installation required!**

---

## OBS Studio Setup

### 1. Install OBS Studio

1. Download OBS Studio from [obsproject.com](https://obsproject.com/)
2. Choose the Windows 64-bit installer
3. Run the installer with default settings
4. Launch OBS Studio

### 2. Configure WebSocket Server

OBS Studio 28+ has WebSocket built-in:

1. In OBS, click **Tools** → **WebSocket Server Settings**
2. **Check** "Enable WebSocket server"
3. Set Server Port: `4455` (default - remember this!)
4. **Check** "Enable Authentication"
5. Set a password (write this down securely!)
6. Click **OK**

### 3. Set Up Your Scene

Create a basic scene for testing:

1. Create a new scene called "Main"
2. Add sources:
   - **Video Capture Device** (your webcam) - name it "Camera"
   - **Image** or **Color Source** for background - name it "Background"
   - **Text** source - name it "Text"
   - **Image** for a logo - name it "Logo"

### 4. Add Filters to Your Camera

Right-click on your "Camera" source → **Filters**

Add these filters (students will control these):

1. **Color Correction**
   - Add Filter → Color Correction
   - Leave at default settings
   - Click **Close**

2. **Blur**
   - Add Filter → Blur
   - Set to desired blur amount
   - Click **Close**

3. **Chroma Key** (Green Screen)
   - Add Filter → Chroma Key
   - Configure for your green screen if you have one
   - Click **Close**

4. **Sharpen**
   - Add Filter → Sharpen
   - Set to moderate sharpening
   - Click **Close**

**Important**: Filter names must match exactly what's in the HTML file (case-sensitive).

### 5. Test Your Setup

1. Make sure OBS is running
2. Verify WebSocket server is enabled (check Tools menu)
3. Note your WebSocket password

---

## Server Installation

### 1. Install Node.js

1. Go to [nodejs.org](https://nodejs.org/)
2. Download the **LTS version** (Long Term Support)
3. Run the installer
4. Choose default options
5. Verify installation:
   - Open Command Prompt
   - Type: `node --version`
   - Should show version number (e.g., v18.17.0)

### 2. Download the Classroom Control System

1. Download or clone this repository to your computer
2. Extract to a memorable location, e.g., `C:\ClassroomControl`

### 3. Install Dependencies

Open Command Prompt in the project folder:

```bash
cd C:\ClassroomControl
npm install
```

This will install all required packages. It may take a few minutes.

### 4. Configure Environment Variables

1. Copy `.env.example` to `.env`
   ```bash
   copy .env.example .env
   ```

2. Open `.env` in Notepad
   ```bash
   notepad .env
   ```

3. Update the values:
   ```
   PORT=3000
   OBS_HOST=localhost
   OBS_PORT=4455
   OBS_PASSWORD=your_obs_websocket_password_here
   ```

4. Save and close

### 5. Generate Secure Passwords

You need to create password hashes for teacher and student access.

1. Start the server temporarily:
   ```bash
   npm start
   ```

2. Open a new Command Prompt and generate hashes:

   **Teacher Password:**
   ```bash
   curl -X POST http://localhost:3000/api/hash-password -H "Content-Type: application/json" -d "{\"password\":\"your_strong_teacher_password\"}"
   ```

   **Student Password:**
   ```bash
   curl -X POST http://localhost:3000/api/hash-password -H "Content-Type: application/json" -d "{\"password\":\"your_student_password\"}"
   ```

   If curl is not available on your system, you can use PowerShell:
   ```powershell
   Invoke-RestMethod -Uri http://localhost:3000/api/hash-password -Method Post -Body '{"password":"your_password"}' -ContentType "application/json"
   ```

3. Copy each hash output

4. Stop the server (Ctrl+C)

5. Open `.env` again and paste the hashes:
   ```
   TEACHER_PASSWORD_HASH=$2a$10$xGZVxEV8jKv...
   STUDENT_PASSWORD_HASH=$2a$10$1NfWLVYQqxN...
   ```

6. Save the file

### 6. Test Server Locally

1. Start the server:
   ```bash
   npm start
   ```

2. You should see:
   ```
   🚀 Classroom OBS Control Server
   ================================
   Server running on port 3000
   
   Access the interface at:
     Local: http://localhost:3000
   
   Connecting to OBS...
   ✓ Connected to OBS WebSocket
   ```

3. Open a browser and go to `http://localhost:3000`

4. Test login with your teacher password

5. Verify you can see the control panel

---

## Network Configuration

To let students access your system, you need to expose your server to the internet.

### Option A: Using ngrok (Easiest - Recommended for Testing)

ngrok creates a secure tunnel to your local server.

1. **Sign up for ngrok** (free):
   - Go to [ngrok.com](https://ngrok.com/)
   - Create a free account

2. **Download ngrok**:
   - Download for Windows
   - Extract `ngrok.exe` to your project folder

3. **Authenticate ngrok**:
   ```bash
   ngrok authtoken YOUR_AUTH_TOKEN_FROM_NGROK_DASHBOARD
   ```

4. **Start ngrok**:
   ```bash
   ngrok http 3000
   ```

5. **Copy the URL** shown in the ngrok terminal:
   ```
   Forwarding: https://abc123xyz.ngrok.io -> http://localhost:3000
   ```

6. **This is your public URL** - share this with students!

**Pros:**
- Super easy setup
- Automatic HTTPS
- No router configuration needed
- Free tier available

**Cons:**
- URL changes every time you restart (unless you pay for a static URL)
- Free tier has session limits

### Option B: Port Forwarding (For Permanent Setup)

This creates a permanent way for students to access your system.

#### 1. Find Your Local IP Address

```bash
ipconfig
```

Look for "IPv4 Address" under your active network connection (e.g., `192.168.1.100`)

#### 2. Configure Your Router

1. Open your router's admin panel (usually `192.168.1.1` or `192.168.0.1`)
2. Log in (check your router's manual for default credentials)
3. Find **Port Forwarding** section (might be under Advanced Settings)
4. Add a new rule:
   - **Service Name**: ClassroomControl
   - **External Port**: 3000
   - **Internal IP**: Your computer's local IP (e.g., 192.168.1.100)
   - **Internal Port**: 3000
   - **Protocol**: TCP
5. Save the rule

#### 3. Find Your Public IP

Go to [whatismyip.com](https://www.whatismyip.com/) and note your public IP address.

#### 4. Test Access

From another device (not on your home network, like your phone on cellular):
```
http://YOUR_PUBLIC_IP:3000
```

#### 5. Set Up Dynamic DNS (Optional but Recommended)

Your public IP may change. Dynamic DNS gives you a stable address.

1. **Sign up for a DDNS service** (free options):
   - [No-IP](https://www.noip.com/)
   - [DuckDNS](https://www.duckdns.org/)
   - [Dynu](https://www.dynu.com/)

2. **Create a hostname** (e.g., `myclassroom.ddns.net`)

3. **Install the DDNS client** on your computer (follow their instructions)

4. **Use this hostname** instead of your IP address

#### 6. Configure Windows Firewall

1. Open **Windows Defender Firewall**
2. Click **Advanced Settings**
3. Click **Inbound Rules** → **New Rule**
4. Select **Port** → Click **Next**
5. Select **TCP** and enter **3000** → Click **Next**
6. Select **Allow the connection** → Click **Next**
7. Check all profiles → Click **Next**
8. Name it "ClassroomControl" → Click **Finish**

---

## Web Interface Setup

### Option 1: Self-Host (Included in Server)

The web interface is already included and served by the server at:
```
http://your-server-url:3000
```

Students can access directly - no additional hosting needed!

### Option 2: Host on Squarespace

If you want to host the web interface separately (with Squarespace's password protection):

1. **Export the web files**:
   - Copy all files from the `public/` folder
   - You need: `index.html`, `styles.css`, `app.js`

2. **Upload to Squarespace**:
   - In Squarespace, go to **Pages**
   - Add a new **blank page**
   - Use a **Code Block** to embed the HTML
   - Or use the **File Upload** feature

3. **Configure server URL**:
   - Students need to configure the server URL once
   - On the page, open browser console (F12)
   - Run: `configureServerURL()`
   - Enter your ngrok or public IP URL

4. **Add password protection**:
   - In Squarespace, go to page settings
   - Enable **Password Protection**
   - Set a password for the page
   - This adds a layer before students can even see the interface

---

## Testing

Before going live with students, test everything:

### 1. Test Server Connection

1. Start OBS
2. Start the server: `npm start`
3. Verify "Connected to OBS WebSocket" message
4. Open `http://localhost:3000`

### 2. Test Teacher Access

1. Log in with teacher password
2. Verify you see teacher controls
3. Test kill switch:
   - Toggle it ON
   - Open a new incognito window
   - Log in as student
   - Verify buttons are disabled

### 3. Test Student Access

1. Log in with student password
2. Try clicking effect buttons
3. Watch OBS - filters should toggle
4. Check activity feed for messages

### 4. Test from Another Device

1. Connect phone/tablet to same WiFi
2. Access via your local IP: `http://192.168.1.100:3000`
3. Test logging in and triggering effects

### 5. Test Public Access

1. Start ngrok or configure port forwarding
2. Access from a device NOT on your network
3. Test the full workflow

---

## Going Live

### Pre-Class Checklist

□ OBS is running with WebSocket enabled
□ Server is running (`npm start`)
□ ngrok is running (if using ngrok)
□ Test access URL yourself
□ Public URL is ready to share
□ Passwords are written down somewhere safe
□ Kill switch is OFF
□ All filters are set up in OBS

### Share with Students

**If using ngrok:**
```
Students, please go to: https://abc123xyz.ngrok.io
Student Password: [your student password]
```

**If using port forwarding/DDNS:**
```
Students, please go to: http://myclassroom.ddns.net:3000
Student Password: [your student password]
```

### During Class

1. **Start with kill switch ON** - explain the system first
2. **Show a demo** - trigger an effect yourself
3. **Set expectations** - explain when they can/can't use it
4. **Turn off kill switch** - let them try
5. **Monitor activity feed** - see what's happening
6. **Use kill switch as needed** - don't hesitate to disable if needed

### After Class

1. Stop ngrok (if running)
2. You can leave the server running for next time
3. Or stop it with Ctrl+C

---

## Troubleshooting

### "Cannot connect to OBS"
- ✓ OBS is running
- ✓ WebSocket is enabled in OBS
- ✓ Port 4455 is correct
- ✓ Password matches

### "Server won't start"
- ✓ Port 3000 is not in use
- ✓ `.env` file exists
- ✓ Node.js is installed

### "Students can't connect"
- ✓ ngrok is running
- ✓ Port forwarding is configured
- ✓ Firewall allows connections
- ✓ Using correct public URL

### "Effects don't work"
- ✓ Filter names match exactly (case-sensitive)
- ✓ Source names match exactly
- ✓ Filters exist in OBS
- ✓ OBS WebSocket is connected

---

## Tips for Success

1. **Practice before your first class** - run through everything
2. **Have a backup plan** - be ready to continue without the system if needed
3. **Start simple** - enable just a few effects at first
4. **Set clear rules** - tell students when/how to use it
5. **Use the kill switch liberally** - better safe than chaotic
6. **Have fun!** - this is about engagement and fun

---

## Next Steps

- Read the main [README.md](README.md) for feature details
- Check [CUSTOMIZATION.md](CUSTOMIZATION.md) for customizing effects
- Review [ADVANCED.md](ADVANCED.md) for advanced features

**You're ready to go! Happy teaching! 🎓**
