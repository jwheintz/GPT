# 🧪 Complete Testing Guide

How to test your Classroom OBS Control System before going live with students.

---

## 📋 Testing Checklist

Use this checklist to verify everything works:

- [ ] OBS WebSocket configured
- [ ] Server starts successfully
- [ ] Server connects to OBS
- [ ] Web interface loads
- [ ] Student login works
- [ ] Teacher login works
- [ ] Buttons trigger OBS effects
- [ ] Kill switch works
- [ ] Works on another device (same network)
- [ ] Works on another device (external network via ngrok)
- [ ] Rate limiting works
- [ ] Activity feed updates

---

## 🎯 Phase 1: Basic Setup Test (5 minutes)

### Step 1: Configure OBS

1. **Open OBS Studio**

2. **Enable WebSocket**:
   - Go to **Tools** → **WebSocket Server Settings**
   - Check "Enable WebSocket server"
   - Set password to something simple for testing (e.g., "test123")
   - Note: Port should be **4455** (default)
   - Click **OK**

3. **Add a test filter**:
   - Right-click your **Camera** (or any video source)
   - Select **Filters**
   - Click **+** (Add)
   - Choose **Color Correction**
   - Name it exactly: `Color Correction`
   - Leave settings at default
   - Click **Close**

✅ **Verify**: You should see the filter listed under your camera source

---

### Step 2: Install Dependencies

Open Command Prompt in the project folder:

```bash
# Navigate to project folder
cd C:\path\to\classroom-obs-control

# Install dependencies
npm install
```

**Expected output:**
```
added 50 packages in 5s
```

✅ **Verify**: No error messages, `node_modules/` folder created

---

### Step 3: Create Configuration

```bash
# Copy the example configuration
copy .env.example .env

# Edit the configuration
notepad .env
```

**In `.env`, change this line:**
```
OBS_PASSWORD=test123
```
(Use the password you set in OBS WebSocket settings)

**Save and close** the file.

✅ **Verify**: `.env` file exists with your OBS password

---

### Step 4: Start the Server

```bash
npm start
```

**Expected output:**
```
🚀 Classroom OBS Control Server
================================
Server running on port 3000

Access the interface at:
  Local: http://localhost:3000

Connecting to OBS...
✓ Connected to OBS WebSocket
```

✅ **Verify**: You see "✓ Connected to OBS WebSocket"

❌ **If you see error:**
```
Failed to connect to OBS: Connection refused
```
→ Check OBS is running and WebSocket is enabled

---

## 🌐 Phase 2: Web Interface Test (5 minutes)

### Step 1: Test Student Interface

1. **Open your web browser**
2. **Go to**: `http://localhost:3000`
3. **You should see**: Login screen with "Classroom Control" title

✅ **Verify**: Login page loads with password field and role selector

---

### Step 2: Test Student Login

1. **Select role**: Student (should be selected by default)
2. **Enter password**: `student123` (default)
3. **Click**: "Enter Classroom"

**Expected result:**
- Login screen disappears
- Control panel appears
- Status indicators show:
  - OBS: Green dot (connected)
  - Server: Green dot (connected)

✅ **Verify**: You see the control panel with buttons

❌ **If login fails:**
- Check you used the default password: `student123`
- Check "Student" role is selected
- Check server console for errors

---

### Step 3: Test a Button

1. **Find the "Color Effect" button** (🎨 icon)
2. **Click it**

**What should happen:**
- Button animates (quick scale down/up)
- Activity feed shows: "✓ Color Correction enabled" (or similar)
- **IN OBS**: The Color Correction filter should toggle on/off

3. **Click it again** - filter should toggle off

✅ **Verify**: 
- Activity feed updates
- Filter toggles in OBS (check OBS filters window)

❌ **If button doesn't work:**
- Check server console for errors
- Make sure filter is named exactly `Color Correction` in OBS
- Make sure source is named exactly `Camera` in OBS

---

### Step 4: Test Teacher Login

1. **Open a new incognito/private browser window** (Ctrl+Shift+N in Chrome)
2. **Go to**: `http://localhost:3000/teacher-panel.html`
3. **Enter teacher password**: `teacher123` (default)

**Expected result:**
- Teacher control panel appears
- Big kill switch visible
- Status shows connected
- Activity monitor shows events

✅ **Verify**: Teacher panel loads with kill switch

---

### Step 5: Test Kill Switch

**In the teacher panel:**

1. **Toggle the kill switch ON** (click the switch)
2. **What should happen:**
   - Switch turns red
   - Status shows "DISABLED"

**In the student panel (other window):**
3. **Try clicking a button**
4. **What should happen:**
   - Warning banner appears: "Controls are currently disabled"
   - Buttons are grayed out
   - Activity feed shows: "Commands are currently disabled by teacher"

5. **Back in teacher panel, toggle kill switch OFF**

**In student panel:**
6. **Buttons should become active again**
7. **Try clicking a button - should work now**

✅ **Verify**: Kill switch blocks student commands, unblocking restores them

---

## 📱 Phase 3: Mobile/Remote Device Test (10 minutes)

### Step 1: Find Your Computer's IP Address

**On Windows:**
```bash
ipconfig
```

Look for "IPv4 Address" under your active network (e.g., `192.168.1.100`)

✅ **Write it down**: `192.168.1.___`

---

### Step 2: Test from Phone/Tablet (Same WiFi)

1. **On your phone**, connect to the **same WiFi** as your computer
2. **Open browser** on phone
3. **Go to**: `http://192.168.1.100:3000` (use YOUR IP address)
4. **Login as student**

**Expected result:**
- Login page loads
- Interface is mobile-friendly
- Buttons are large and touchable

5. **Click a button** - should trigger effect in OBS

✅ **Verify**: 
- Mobile interface works
- Buttons trigger OBS effects
- Activity feed updates

❌ **If can't connect:**
- Check phone is on same WiFi
- Check Windows Firewall (see troubleshooting below)
- Try accessing from computer browser first: `http://192.168.1.100:3000`

---

### Step 3: Configure Windows Firewall (If needed)

If mobile device can't connect:

1. **Open Windows Defender Firewall**
2. **Click "Advanced Settings"**
3. **Click "Inbound Rules"** → **"New Rule"**
4. Select **"Port"** → Click **Next**
5. Select **"TCP"**, enter **3000** → Click **Next**
6. Select **"Allow the connection"** → Click **Next**
7. Check all profiles → Click **Next**
8. Name: "Classroom OBS Control" → Click **Finish**

Now try connecting from phone again.

---

## 🌍 Phase 4: Public Access Test (15 minutes)

Test making it accessible from outside your network (like students at home).

### Step 1: Install ngrok

1. **Go to**: https://ngrok.com/download
2. **Download** ngrok for Windows
3. **Extract** `ngrok.exe` to your project folder
4. **Sign up** for free ngrok account
5. **Copy your auth token** from ngrok dashboard

**Authenticate ngrok:**
```bash
ngrok authtoken YOUR_TOKEN_HERE
```

---

### Step 2: Start ngrok

**Make sure server is running**, then in a NEW command prompt:

```bash
ngrok http 3000
```

**Expected output:**
```
Forwarding  https://abc123xyz.ngrok.io -> http://localhost:3000
```

✅ **Copy the HTTPS URL** (e.g., `https://abc123xyz.ngrok.io`)

---

### Step 3: Test from External Network

**Best test**: Use your phone on **cellular data** (not WiFi)

1. **Turn off WiFi** on your phone
2. **Open the ngrok URL** in browser
3. **Login as student**
4. **Click a button**

**Expected result:**
- Page loads (might be slightly slower than local)
- Login works
- Buttons trigger OBS effects
- Activity feed updates

✅ **Verify**: Everything works from external network

---

## 🧪 Phase 5: Advanced Testing (Optional)

### Test Rate Limiting

**Purpose**: Verify students can't spam buttons

1. **Login as student**
2. **Click buttons rapidly** (10+ times in a row)
3. **What should happen:**
   - First 10 commands work
   - Then you see: "Rate limit exceeded. Please wait a moment."
   - Wait 5 seconds
   - Should work again

✅ **Verify**: Rate limiting prevents spam

---

### Test Multiple Students

**Purpose**: Verify multiple connections work

1. **Open 3-4 browser tabs/windows** (or use different devices)
2. **Login as student in each**
3. **Click buttons from different tabs**
4. **What should happen:**
   - All activity shows in all tabs
   - Activity feed updates everywhere
   - All commands work

✅ **Verify**: Multiple students can control simultaneously

---

### Test Reconnection

**Purpose**: Verify auto-reconnect works

1. **Login as student**
2. **Stop the server** (Ctrl+C in server window)
3. **What should happen:**
   - Status dot turns red (disconnected)
   - Message: "Connection lost. Reconnecting..."

4. **Restart server**: `npm start`
5. **What should happen:**
   - Status dot turns green
   - Reconnects automatically
   - Can click buttons again

✅ **Verify**: Auto-reconnection works

---

### Test Custom Buttons

**Purpose**: Verify you can add your own buttons

1. **In OBS**, add a new filter:
   - Right-click Camera → Filters
   - Add → Blur
   - Name it exactly: `Blur`

2. **Edit `public/index.html`**:
   - Find the section with buttons
   - Add this button:
```html
<button class="control-btn effect-btn" 
        data-command="toggle_filter" 
        data-source="Camera" 
        data-filter="Blur">
    <span class="icon">💫</span>
    <span class="label">Blur Effect</span>
</button>
```

3. **Refresh browser**
4. **Click the new button**
5. **In OBS, verify the Blur filter toggles**

✅ **Verify**: Custom buttons work

---

## 📊 Test Results Checklist

After completing all tests:

```
BASIC FUNCTIONALITY
✓ Server starts and connects to OBS
✓ Web interface loads
✓ Student login works
✓ Teacher login works
✓ Buttons trigger OBS effects
✓ Kill switch blocks students
✓ Kill switch unblocks students

LOCAL NETWORK
✓ Works on same WiFi from phone
✓ Works on same WiFi from tablet
✓ Mobile interface looks good

PUBLIC ACCESS
✓ ngrok creates public URL
✓ Works from external network
✓ Works on cellular data

ADVANCED
✓ Rate limiting prevents spam
✓ Multiple students work simultaneously
✓ Auto-reconnect works
✓ Custom buttons work
```

---

## 🐛 Common Issues & Solutions

### Issue: "Cannot connect to OBS"

**Symptoms**: Server shows "Failed to connect to OBS"

**Solutions:**
1. Check OBS is running
2. Go to Tools → WebSocket Server Settings
3. Verify "Enable WebSocket server" is checked
4. Check port is 4455
5. Check password in `.env` matches OBS
6. Restart OBS after changing settings

---

### Issue: "Button doesn't do anything"

**Symptoms**: Click button, nothing happens in OBS

**Solutions:**
1. Check server console for errors
2. Verify filter exists in OBS
3. Verify filter name matches EXACTLY (case-sensitive)
4. Verify source name matches EXACTLY
5. Try this test button:
```html
data-source="Camera" data-filter="Color Correction"
```

**Debug**: Check server console, it will show the exact error

---

### Issue: "Can't connect from phone"

**Symptoms**: Phone browser can't load page

**Solutions:**
1. Verify phone is on **same WiFi**
2. Check you're using the right IP address:
   ```bash
   ipconfig
   ```
3. Check Windows Firewall (see Phase 3, Step 3)
4. Try from computer first: `http://192.168.1.100:3000`
5. Make sure server is running

---

### Issue: "Password doesn't work"

**Symptoms**: "Invalid password" message

**Solutions:**
1. Default passwords are:
   - Student: `student123`
   - Teacher: `teacher123`
2. Make sure you're using the hash in `.env`, not plain text
3. Check you selected the right role (Student vs Teacher)
4. Try restarting the server

---

### Issue: "ngrok URL doesn't work"

**Symptoms**: Can't access via ngrok URL

**Solutions:**
1. Check ngrok is running (separate window)
2. Use the **HTTPS** URL, not HTTP
3. Check server is running
4. Try accessing locally first
5. Check ngrok free tier limits (might be expired)

---

## ✅ You're Ready!

If you've completed these tests and everything works, you're ready to use it with students!

### Before First Class:

1. ✅ All tests pass
2. ✅ Changed default passwords (see SETUP_GUIDE.md)
3. ✅ Customized buttons for your OBS setup
4. ✅ Tested from multiple devices
5. ✅ Know how to use kill switch
6. ✅ Have backup lesson plan

---

## 🎓 Testing with a Friend First

**Highly Recommended**: Before using with a full class:

1. **Share URL with a colleague or friend**
2. **Have them login as student**
3. **Let them try all buttons**
4. **Practice using kill switch**
5. **Get their feedback**

This gives you confidence before going live with students!

---

## 📞 Still Having Issues?

1. Check server console for error messages
2. Check browser console (F12) for errors
3. Review FAQ.md for common problems
4. Verify OBS WebSocket is working (test in OBS WebSocket settings)
5. Try restarting: OBS → Server → Browser

---

**Once everything tests successfully, you're ready to transform your classroom! 🎉**

See QUICK_START.md for going live with students.
