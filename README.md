# 🎓 Classroom OBS Control System

A web-based interactive control system that allows students to engage with your classroom presentation by triggering OBS filters and effects. Built specifically for educators who want to create an engaging, Twitch-like experience for their students without requiring any software installation on student devices.

## 🚀 NEW USER? [START HERE!](START_HERE.md)

**👉 [Click here to get started in 15 minutes →](QUICK_START.md)**

## ✨ Features

- **🌐 Web-Based Interface**: Students access via any web browser - no installation required
- **🔐 Password Protected**: Separate access levels for teachers and students
- **🎛️ OBS Integration**: Control filters, scenes, sources, and visual effects
- **🚨 Emergency Kill Switch**: Teachers can instantly disable all student controls
- **⚡ Real-Time Updates**: All changes are broadcast to everyone instantly
- **🎨 Beautiful UI**: Modern, responsive design that works on desktop and mobile
- **📊 Activity Feed**: See all actions as they happen in real-time
- **🔒 Rate Limiting**: Prevents spam and ensures smooth operation

## 🎯 Perfect For

- Interactive classroom presentations
- Educational streaming
- Student engagement during lectures
- Remote learning scenarios
- Hybrid classroom environments

## 📋 Prerequisites

Before you begin, make sure you have:

1. **Windows PC** (running OBS Studio)
2. **OBS Studio 32.x** (64-bit) - [Download here](https://obsproject.com/)
3. **Node.js** (v16 or higher) - [Download here](https://nodejs.org/)
4. **OBS WebSocket Plugin** (v5.x) - Built into OBS 28+

## 🚀 Quick Start

### Step 1: Install OBS WebSocket

If you're using OBS Studio 28 or newer, WebSocket is already built-in! 

1. Open OBS Studio
2. Go to **Tools** → **WebSocket Server Settings**
3. Check "Enable WebSocket server"
4. Set a password (you'll need this later)
5. Note the port number (default: 4455)

### Step 2: Set Up the Server

1. **Download or clone this repository** to your Windows computer

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create configuration file**:
   - Copy `.env.example` to `.env`
   - Edit `.env` with your settings:
   ```
   PORT=3000
   OBS_HOST=localhost
   OBS_PORT=4455
   OBS_PASSWORD=your_obs_websocket_password
   ```

4. **Generate password hashes**:
   - Start the server: `npm start`
   - In another terminal or browser, generate hashes:
   ```bash
   curl -X POST http://localhost:3000/api/hash-password -H "Content-Type: application/json" -d "{\"password\":\"your_teacher_password\"}"
   ```
   - Copy the hash and add it to your `.env` file
   - Repeat for student password

5. **Start the server**:
   ```bash
   npm start
   ```

### Step 3: Make Server Accessible to Students

Since students will access this from the internet, you need to expose your local server. You have two options:

#### Option A: Using ngrok (Recommended for testing)

1. **Download ngrok**: [https://ngrok.com/download](https://ngrok.com/download)
2. **Run ngrok**:
   ```bash
   ngrok http 3000
   ```
3. **Copy the URL** (e.g., `https://abc123.ngrok.io`)
4. This URL is what students will use to access the interface

#### Option B: Port Forwarding (For permanent setup)

1. **Configure your router**:
   - Log into your router admin panel
   - Forward port 3000 to your computer's local IP
   - Note your public IP address

2. **Set up Dynamic DNS** (optional but recommended):
   - Use a service like No-IP or DuckDNS
   - This gives you a stable URL even if your IP changes

3. **Configure firewall**:
   - Allow incoming connections on port 3000
   - Add Windows Firewall rule if needed

### Step 4: Host the Web Interface on Squarespace

1. **Upload the web files** to Squarespace:
   - Copy files from the `public/` folder
   - Upload via Squarespace's file manager

2. **Configure the server URL**:
   - When students first load the page, they need to configure the server URL
   - Open browser console and run:
   ```javascript
   configureServerURL()
   ```
   - Enter your ngrok URL or public IP

3. **Add password protection** (Squarespace built-in):
   - Use Squarespace's password protection feature
   - This adds an extra layer of security

## 🎮 Usage Guide

### For Teachers

1. **Log in with teacher password**
2. **Use the Kill Switch**:
   - Toggle anytime to disable/enable student controls
   - Useful for focusing attention or during important moments
3. **Configure Controls**:
   - Click "Show Configuration Panel" to see available OBS sources/filters
   - Customize which effects students can trigger

### For Students

1. **Log in with student password**
2. **Click buttons to trigger effects**:
   - Visual effects (filters, overlays)
   - Scene elements (show/hide sources)
   - Quick reactions (fun visual changes)
3. **Watch the activity feed** to see what others are doing

## ⚙️ Customizing Controls

The default controls are configured in `public/index.html`. To customize:

1. **Add new filter buttons**:
```html
<button class="control-btn effect-btn" 
        data-command="toggle_filter" 
        data-source="YourSourceName" 
        data-filter="YourFilterName">
    <span class="icon">🎨</span>
    <span class="label">Custom Effect</span>
</button>
```

2. **Add scene switching**:
```html
<button class="control-btn scene-btn" 
        data-command="trigger_scene" 
        data-scene="YourSceneName">
    <span class="icon">🎬</span>
    <span class="label">Switch Scene</span>
</button>
```

3. **Source visibility toggle**:
```html
<button class="control-btn" 
        data-command="toggle_source" 
        data-scene="YourSceneName" 
        data-source="YourSourceName">
    <span class="icon">👁️</span>
    <span class="label">Toggle Source</span>
</button>
```

## 🎨 Setting Up OBS Filters

To make the most of this system, add filters to your OBS sources:

1. **Right-click on a source** (e.g., Camera)
2. **Select "Filters"**
3. **Add filters** you want students to control:
   - Color Correction
   - Blur
   - Chroma Key (Green Screen)
   - Sharpen
   - LUT Filter (for color grading)
   - Image Mask/Blend
   - Render Delay
   - Scaling/Aspect Ratio

4. **Name your filters clearly** - these names are used in the interface

## 🔐 Security Best Practices

1. **Change default passwords** immediately
2. **Use strong passwords** for both teacher and student access
3. **Enable Squarespace password protection** as an additional layer
4. **Use HTTPS** (ngrok provides this automatically)
5. **Monitor the activity feed** for unusual behavior
6. **Use the kill switch** if needed
7. **Don't share your public URL widely** - only with your students

## 🔧 Troubleshooting

### Server won't start
- Check if port 3000 is already in use
- Make sure Node.js is installed correctly
- Verify `.env` file exists and is configured

### Can't connect to OBS
- Verify OBS WebSocket is enabled
- Check the port number (default: 4455)
- Confirm the password matches
- Make sure OBS is running

### Students can't connect
- Verify ngrok is running
- Check firewall settings
- Confirm the public URL is correct
- Test the URL yourself first

### Kill switch not working
- Only teachers can toggle the kill switch
- Refresh the page if state is out of sync
- Check browser console for errors

### Effects not triggering
- Verify filter names match exactly (case-sensitive)
- Check source names in OBS
- Ensure OBS WebSocket is connected
- Look at server console for error messages

## 🚀 Future Enhancements

The system is designed to be expandable. Future additions could include:

- **VoiceMod Integration**: Student-triggered sound effects
- **StreamDeck Integration**: Physical button control for teachers
- **Voting System**: Students vote on which effect to apply
- **Timers & Cooldowns**: Limit how often effects can be triggered
- **Custom Animations**: Pre-programmed sequences
- **Point System**: Reward student participation
- **Analytics Dashboard**: Track which effects are most popular

## 📱 Mobile Support

The interface is fully responsive and works great on:
- Smartphones (iOS/Android)
- Tablets
- Desktop browsers
- Even smart TVs with browsers!

## 🤝 Contributing

Have ideas for improvements? Found a bug? Contributions are welcome!

## 📄 License

MIT License - Feel free to use this in your classroom!

## 💡 Tips for Success

1. **Start simple**: Begin with just a few effects, add more as students get comfortable
2. **Set expectations**: Explain the purpose and rules to students beforehand
3. **Use the kill switch**: Don't hesitate to disable controls if needed
4. **Have fun**: This is about engagement - embrace the chaos!
5. **Test first**: Try everything yourself before going live with students
6. **Backup plan**: Always have a way to continue your lesson without the effects

## 📞 Support

If you run into issues:
1. Check the troubleshooting section above
2. Review the server console logs
3. Check browser console (F12) for errors
4. Verify OBS WebSocket connection

## 🎉 Enjoy!

Transform your classroom into an interactive experience. Your students will love being part of the presentation, and you'll love the engagement it creates!

---

**Built for educators, by educators. Happy teaching! 🎓**
