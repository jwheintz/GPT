# ⚡ Quick Reference Cheat Sheet

One-page reference for the Classroom OBS Control System.

---

## 🚀 Getting Started (5 Steps)

```bash
# 1. Install dependencies
npm install

# 2. Create configuration
copy .env.example .env

# 3. Edit .env with your OBS password
notepad .env

# 4. Start server
npm start

# 5. Open browser
http://localhost:3000
```

**Default Passwords:**
- Teacher: `teacher123`
- Student: `student123`

⚠️ **CHANGE THESE!**

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `server.js` | Main server (don't edit unless advanced) |
| `.env` | Your passwords and settings ⭐ |
| `public/index.html` | Student buttons ⭐⭐⭐ |
| `public/styles.css` | Colors and theme |
| `public/teacher-panel.html` | Teacher controls |

⭐ = Edit this file

---

## 🎨 Adding a Button

**In OBS:**
1. Add filter to source
2. Name it clearly (e.g., "Blur", "Color Correction")

**In `public/index.html`:**
```html
<button class="control-btn" 
        data-command="toggle_filter" 
        data-source="Camera" 
        data-filter="Blur">
    <span class="icon">💫</span>
    <span class="label">Blur Effect</span>
</button>
```

**Match the names EXACTLY** (case-sensitive!)

---

## 🎯 Common Commands

### Toggle Filter
```html
<button data-command="toggle_filter" 
        data-source="Camera" 
        data-filter="ColorCorrection">
```

### Toggle Source Visibility
```html
<button data-command="toggle_source" 
        data-scene="Main" 
        data-source="Overlay">
```

### Switch Scene
```html
<button data-command="trigger_scene" 
        data-scene="SceneName">
```

---

## 🎨 Changing Colors

**Edit `public/styles.css`:**

```css
:root {
    --primary-color: #4f46e5;    /* Main buttons */
    --secondary-color: #10b981;  /* Success/connected */
    --danger-color: #ef4444;     /* Kill switch */
    --background: #0f172a;       /* Main background */
    --text-primary: #f1f5f9;     /* Text color */
}
```

---

## 🔒 Changing Passwords

**1. Start server:**
```bash
npm start
```

**2. Generate hash (Windows PowerShell):**
```powershell
Invoke-RestMethod -Uri http://localhost:3000/api/hash-password -Method Post -Body '{"password":"YourNewPassword"}' -ContentType "application/json"
```

**3. Copy hash to `.env`:**
```env
TEACHER_PASSWORD_HASH=$2a$10$abc123...
STUDENT_PASSWORD_HASH=$2a$10$xyz789...
```

**4. Restart server**

---

## 🌐 Making It Public

### Option 1: ngrok (Easiest)
```bash
# Download ngrok from ngrok.com
# Then run:
ngrok http 3000

# Share the URL: https://abc123.ngrok.io
```

### Option 2: Batch File
```bash
# Just double-click:
start-with-ngrok.bat
```

---

## 🔧 OBS Setup Checklist

- [ ] OBS Studio 28+ installed
- [ ] Tools → WebSocket Server Settings
- [ ] Enable WebSocket server ✓
- [ ] Enable Authentication ✓
- [ ] Set password (remember it!)
- [ ] Port: 4455 (default)
- [ ] Add filters to sources
- [ ] Name filters clearly

---

## 🐛 Troubleshooting

### "Cannot connect to OBS"
```bash
✓ Is OBS running?
✓ Is WebSocket enabled?
✓ Password correct in .env?
✓ Port 4455 correct?
```

### "Students can't connect"
```bash
✓ Is server running?
✓ Is ngrok running?
✓ Using HTTPS URL from ngrok?
✓ Correct student password?
```

### "Button doesn't work"
```bash
✓ Filter name matches EXACTLY?
✓ Source name matches EXACTLY?
✓ Filter exists in OBS?
✓ Check server console for errors
```

### "Password doesn't work"
```bash
✓ Using PASSWORD HASH in .env (not plain text)?
✓ No typos?
✓ Selected correct role (teacher/student)?
```

---

## 📋 Pre-Class Checklist

Before students arrive:

- [ ] OBS is running
- [ ] Server is running (`npm start`)
- [ ] ngrok is running (if using)
- [ ] Test the URL yourself
- [ ] Kill switch is OFF
- [ ] Passwords are ready
- [ ] URL is ready to share

---

## ⌨️ Keyboard Shortcuts

| Action | Command |
|--------|---------|
| Start server | `npm start` |
| Stop server | `Ctrl + C` |
| View logs | (Check terminal) |
| Open in browser | `http://localhost:3000` |

---

## 📞 URLs

| What | URL |
|------|-----|
| Student interface | `http://localhost:3000/` |
| Teacher panel | `http://localhost:3000/teacher-panel.html` |
| Server status | `http://localhost:3000/api/status` |

Replace `localhost:3000` with your ngrok URL for students.

---

## 🎯 During Class

**Starting:**
1. Start with kill switch ON
2. Explain system to students
3. Demo an effect
4. Turn kill switch OFF

**If chaos:**
1. Hit kill switch (big red button)
2. Students see "Controls disabled"
3. Re-enable when ready

**Ending:**
1. Thank students
2. Kill switch ON
3. Can leave server running

---

## 🎨 Common Icons

```
🎨 Color/Art        💫 Blur/Magic      ✨ Sparkle
🌈 Rainbow          🎮 Gaming          ⚫ Grayscale
🔍 Zoom             📊 Overlay         🖼️ Image
📝 Text             ⭐ Logo            🎬 Scene
👁️ Visibility       🔇 Mute            🔊 Sound
✅ Correct          ❌ Wrong           💭 Thinking
```

---

## 📖 Documentation Quick Links

- **Getting started?** → `QUICK_START.md`
- **Full setup?** → `SETUP_GUIDE.md`
- **Customizing?** → `CUSTOMIZATION.md`
- **Advanced features?** → `ADVANCED.md`
- **Questions?** → `FAQ.md`
- **OBS help?** → `obs-setup-examples.md`

---

## 🆘 Emergency Commands

### Stop Everything
```bash
Ctrl + C    (in server terminal)
```

### Restart Server
```bash
npm start
```

### Reset Kill Switch
```
Open teacher panel → Toggle kill switch OFF
```

### Check If Running
```bash
http://localhost:3000/api/status
```

---

## 💡 Pro Tips

1. **Test before class** - Always!
2. **Use kill switch liberally** - It's there for a reason
3. **Start simple** - Add buttons gradually
4. **Name clearly in OBS** - Makes configuration easier
5. **Have backup plan** - Be ready to teach without it
6. **Students love it** - But you're in control!

---

## 📊 Default Rate Limits

- **Students:** 10 commands per 5 seconds
- **Teachers:** No limits
- **Kill switch:** Instant disable

Change in `server.js` if needed.

---

## 🔐 Security Best Practices

✓ Change default passwords
✓ Use strong passwords
✓ Don't share teacher password
✓ Use kill switch when needed
✓ Monitor activity feed
✓ Use HTTPS (ngrok provides this)

---

## 📞 Support

1. Check error messages in:
   - Server terminal
   - Browser console (F12)

2. Review documentation:
   - FAQ.md for common issues
   - SETUP_GUIDE.md for setup problems

3. Verify:
   - OBS is running
   - WebSocket is enabled
   - Names match exactly
   - Passwords are correct

---

## 🎉 Quick Win

**Get running in 60 seconds:**

```bash
npm install && copy .env.example .env && npm start
```

Then open `http://localhost:3000` and login with `student123`!

(Still need to configure OBS, but server works!)

---

**Keep this sheet handy during class! 📌**

Print it out or keep it on a second monitor for quick reference.

**Happy teaching! 🎓**
