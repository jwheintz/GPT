# ⚡ Quick Start Guide

Get up and running in 15 minutes!

## Prerequisites Checklist

Before you start, make sure you have:

- [ ] Windows 10/11 computer
- [ ] OBS Studio 32.x installed
- [ ] Node.js installed (v16+)
- [ ] OBS WebSocket enabled
- [ ] 15 minutes of time

---

## Step 1: Configure OBS (3 minutes)

1. **Open OBS Studio**

2. **Enable WebSocket**:
   - Go to **Tools** → **WebSocket Server Settings**
   - Check "Enable WebSocket server"
   - Set a password (e.g., "classroom123")
   - Click OK

3. **Add a filter to test**:
   - Right-click your Camera source
   - Click **Filters**
   - Click **+** → **Color Correction**
   - Name it "Color Correction"
   - Click Close

---

## Step 2: Install the Server (5 minutes)

1. **Open Command Prompt** in this folder

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create your configuration**:
   ```bash
   copy .env.example .env
   notepad .env
   ```

4. **Edit these two lines** in `.env`:
   ```
   OBS_PASSWORD=classroom123
   ```
   (Use the password you set in OBS)

5. **Save and close** the file

---

## Step 3: Test Locally (3 minutes)

1. **Start the server**:
   ```bash
   npm start
   ```
   
   You should see:
   ```
   ✓ Connected to OBS WebSocket
   ```

2. **Open your browser** to:
   ```
   http://localhost:3000
   ```

3. **Log in**:
   - Select "Student"
   - Password: `student123`
   - Click "Enter Classroom"

4. **Try clicking a button** - watch OBS to see the filter toggle!

---

## Step 4: Make It Public (4 minutes)

### Option A: Using ngrok (Easiest)

1. **Download ngrok**:
   - Go to https://ngrok.com/download
   - Extract `ngrok.exe` to this folder

2. **Start ngrok**:
   ```bash
   ngrok http 3000
   ```

3. **Copy the URL** (e.g., `https://abc123.ngrok.io`)

4. **Share with students**:
   ```
   URL: https://abc123.ngrok.io
   Password: student123
   ```

### Option B: Use the easy batch file

Double-click `start-with-ngrok.bat` - it does everything automatically!

---

## Step 5: Try It Out!

1. **Open the ngrok URL on your phone** (using cellular data, not WiFi)

2. **Log in with student password**

3. **Click a button** - see it work on your computer!

---

## Default Passwords

**Teacher:** `teacher123`
**Student:** `student123`

**⚠️ CHANGE THESE IMMEDIATELY FOR PRODUCTION USE!**

See the full [README.md](README.md) for how to generate secure password hashes.

---

## Troubleshooting Quick Fixes

### "Cannot connect to OBS"
- ✓ Is OBS running?
- ✓ Is WebSocket enabled? (Tools → WebSocket Server Settings)
- ✓ Did you enter the correct password in `.env`?

### "npm: command not found"
- ✓ Install Node.js from https://nodejs.org/

### "Students can't connect"
- ✓ Is ngrok running?
- ✓ Are you sharing the HTTPS URL (not the HTTP one)?
- ✓ Did they enter the correct password?

### "Buttons don't do anything"
- ✓ Check the filter name matches exactly (case-sensitive)
- ✓ Check the source name matches exactly
- ✓ Look at the server console for error messages

---

## Next Steps

Now that it's working:

1. **Read [CUSTOMIZATION.md](CUSTOMIZATION.md)** - Learn how to add your own buttons
2. **Read [SETUP_GUIDE.md](SETUP_GUIDE.md)** - Set up properly for classroom use
3. **Change passwords** - Generate secure passwords for your class
4. **Add more filters** - Experiment with different OBS effects
5. **Test with friends** - Make sure everything works smoothly

---

## Pro Tips

1. **Keep the server running** - Leave it on during class
2. **Use the kill switch** - Press it when you need focus
3. **Start simple** - Add more buttons gradually
4. **Have a backup** - Be ready to teach without it if needed
5. **Have fun!** - Your students will love it

---

## Getting Help

- Check the main [README.md](README.md)
- Review [SETUP_GUIDE.md](SETUP_GUIDE.md)
- Look at the server console for errors
- Check the browser console (F12) for errors

---

**You're ready to go! 🎉**

Now go make your classroom interactive! Your students will love being part of the show.
