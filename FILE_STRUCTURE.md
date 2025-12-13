# 📁 Project File Structure

Complete overview of all files in the Classroom OBS Control System.

```
classroom-obs-control/
│
├── 📄 Core Application Files
│   ├── server.js                 ⭐ Main Node.js server (WebSocket + OBS integration)
│   ├── package.json              ⭐ Dependencies and npm scripts
│   └── .env.example              ⭐ Configuration template (copy to .env)
│
├── 🌐 Web Interface (public/)
│   ├── index.html                ⭐ Student control panel
│   ├── teacher-panel.html        ⭐ Dedicated teacher interface
│   ├── styles.css                ⭐ All styling (easily customizable)
│   └── app.js                    ⭐ Client-side WebSocket logic
│
├── 🚀 Quick Start Files
│   ├── start-server.bat          💻 Windows: Start server with one click
│   └── start-with-ngrok.bat      💻 Windows: Start server + ngrok together
│
├── 📚 Essential Documentation
│   ├── README.md                 📖 Complete overview and features
│   ├── QUICK_START.md            ⚡ 15-minute setup guide
│   └── SETUP_GUIDE.md            📖 Comprehensive step-by-step setup
│
├── 🎨 Customization & Advanced
│   ├── CUSTOMIZATION.md          🎨 How to customize buttons, styles, commands
│   ├── ADVANCED.md               🚀 VoiceMod, analytics, Stream Deck integration
│   └── obs-setup-examples.md     📹 Ready-to-use OBS configurations
│
├── ℹ️ Reference & Help
│   ├── FAQ.md                    ❓ Common questions answered
│   ├── PROJECT_SUMMARY.md        📋 Complete project overview
│   └── FILE_STRUCTURE.md         📁 This file!
│
└── 🔧 Configuration
    ├── .env                      🔒 Your configuration (create from .env.example)
    ├── .gitignore                🚫 Files to exclude from git
    └── node_modules/             📦 Dependencies (created by npm install)
```

---

## File Details

### Core Application

#### `server.js` (Main Server)
**Purpose:** The brain of the system  
**What it does:**
- Runs the WebSocket server
- Connects to OBS via WebSocket
- Handles authentication (teacher/student)
- Processes commands and sends to OBS
- Implements kill switch
- Rate limiting and security

**When to edit:** Adding new OBS commands, changing rate limits, adding integrations

---

#### `package.json`
**Purpose:** Node.js project configuration  
**What it does:**
- Lists all dependencies
- Defines npm scripts
- Project metadata

**When to edit:** Adding new npm packages, changing project info

---

#### `.env.example` → `.env`
**Purpose:** Server configuration  
**What it contains:**
```env
PORT=3000                          # Server port
OBS_HOST=localhost                 # OBS location
OBS_PORT=4455                      # OBS WebSocket port
OBS_PASSWORD=your_password         # OBS WebSocket password
TEACHER_PASSWORD_HASH=...          # Hashed teacher password
STUDENT_PASSWORD_HASH=...          # Hashed student password
```

**When to edit:** First setup, changing passwords, changing ports

---

### Web Interface

#### `public/index.html` (Student Interface)
**Purpose:** The interface students see  
**What it contains:**
- Login form
- Control buttons
- Activity feed
- Status indicators

**When to edit:** ⭐ **Most common edit** - Customizing buttons for your OBS setup

**Example customization:**
```html
<button class="control-btn" 
        data-command="toggle_filter" 
        data-source="YourSourceName" 
        data-filter="YourFilterName">
    <span class="icon">🎨</span>
    <span class="label">Your Button</span>
</button>
```

---

#### `public/teacher-panel.html` (Teacher Interface)
**Purpose:** Dedicated teacher control panel  
**What it contains:**
- Large kill switch
- System status dashboard
- Activity monitor
- Manual controls
- Configuration options

**When to edit:** Adding teacher-only controls, customizing dashboard

---

#### `public/styles.css` (Styling)
**Purpose:** All visual styling  
**Easy customization via CSS variables:**
```css
:root {
    --primary-color: #4f46e5;      /* Change main color */
    --background: #0f172a;         /* Change background */
    --text-primary: #f1f5f9;       /* Change text color */
}
```

**When to edit:** Changing colors, layout, fonts, sizes

---

#### `public/app.js` (Client Logic)
**Purpose:** Client-side JavaScript  
**What it does:**
- WebSocket connection management
- Authentication handling
- Button click processing
- Activity feed updates
- Auto-reconnection

**When to edit:** Adding custom client-side logic, new UI behaviors

---

### Quick Start Scripts

#### `start-server.bat`
**Purpose:** Easy server start on Windows  
**Usage:** Double-click to start server  
**Does:** Runs `npm start` in a nice terminal window

---

#### `start-with-ngrok.bat`
**Purpose:** Start server + ngrok together  
**Usage:** Double-click to start both  
**Does:** 
1. Starts server in background
2. Starts ngrok tunnel
3. Shows public URL

**Requirement:** `ngrok.exe` must be in same folder

---

### Documentation Files

#### `README.md` ⭐ Start Here
- Complete feature overview
- Installation instructions
- Usage guide
- Customization basics
- Troubleshooting

**Best for:** Understanding what the system does

---

#### `QUICK_START.md` ⚡ Fastest Setup
- 15-minute setup guide
- Minimal steps to get running
- Essential troubleshooting
- Quick reference

**Best for:** Getting started ASAP

---

#### `SETUP_GUIDE.md` 📖 Complete Setup
- Step-by-step instructions
- Every detail explained
- Network configuration
- Testing procedures
- Going live checklist

**Best for:** First-time setup, thorough understanding

---

#### `CUSTOMIZATION.md` 🎨 Make It Yours
- Adding/changing buttons
- Styling customization
- Creating new commands
- Layout modifications
- Templates and examples

**Best for:** Tailoring to your needs

---

#### `ADVANCED.md` 🚀 Power Features
- Stream Deck integration
- VoiceMod integration
- Multiple cameras
- Analytics and logging
- Custom authentication
- Performance optimization
- Production deployment

**Best for:** Advanced users, expansions

---

#### `obs-setup-examples.md` 📹 OBS Config
- Scene setups for different subjects
- Filter recommendations
- Naming conventions
- Subject-specific templates
- Best practices

**Best for:** Setting up OBS for your class

---

#### `FAQ.md` ❓ Questions & Answers
- Common questions
- Troubleshooting
- Best practices
- Age group recommendations
- Cost information

**Best for:** Specific questions

---

#### `PROJECT_SUMMARY.md` 📋 Overview
- What you've built
- Architecture explanation
- Key features
- Deployment options
- Success metrics

**Best for:** Big picture understanding

---

## What to Edit for Your Class

### Must Edit (Essential)

1. **`.env` file** (create from `.env.example`)
   - OBS password
   - Teacher/student passwords

2. **`public/index.html`**
   - Button configurations
   - Source names
   - Filter names
   - Scene names

### Should Edit (Recommended)

3. **`public/styles.css`**
   - Colors to match school
   - Add school logo
   - Adjust layout

4. **`public/teacher-panel.html`**
   - Teacher controls
   - Quick actions

### Might Edit (Advanced)

5. **`server.js`**
   - Add new command types
   - Change rate limits
   - Add integrations

6. **`.bat` files**
   - Adjust for your folder paths
   - Add custom startup logic

---

## What NOT to Edit

❌ Don't modify:
- `package.json` (unless adding packages)
- `node_modules/` (auto-generated)
- `.git/` (version control)

---

## File Sizes (Approximate)

```
server.js           ~15 KB    Core server logic
index.html          ~10 KB    Student interface
teacher-panel.html  ~12 KB    Teacher interface
styles.css          ~8 KB     All styling
app.js              ~10 KB    Client logic
README.md           ~25 KB    Main documentation
SETUP_GUIDE.md      ~20 KB    Setup instructions
CUSTOMIZATION.md    ~15 KB    Customization guide
ADVANCED.md         ~18 KB    Advanced features
FAQ.md              ~15 KB    Questions & answers
```

**Total project:** ~200 KB (plus node_modules)

---

## Workflow: Making Changes

### Adding a New Button

1. **Add filter in OBS**
   - Right-click source → Filters → Add filter
   - Name it clearly

2. **Add button in HTML**
   - Edit `public/index.html`
   - Add button with correct data attributes

3. **Test**
   - Refresh browser
   - Click button
   - Verify in OBS

### Changing Colors/Theme

1. **Edit CSS variables**
   - Open `public/styles.css`
   - Modify `:root` variables
   
2. **Test**
   - Refresh browser
   - Check all screens

### Adding New Command Type

1. **Add server handler**
   - Edit `server.js`
   - Add case in switch statement

2. **Add button**
   - Edit HTML files
   - Add button with new command

3. **Test thoroughly**

---

## Backup Recommendation

**Files to backup regularly:**
- `.env` (your configuration)
- `public/index.html` (your customizations)
- `public/teacher-panel.html` (teacher customizations)
- `public/styles.css` (your theme)
- `server.js` (if you added custom code)

**How to backup:**
```bash
# Create a backup folder
mkdir backups
mkdir backups/backup-2024-01-01

# Copy important files
copy .env backups/backup-2024-01-01/
copy public/index.html backups/backup-2024-01-01/
copy public/styles.css backups/backup-2024-01-01/
copy server.js backups/backup-2024-01-01/
```

---

## Dependencies (node_modules/)

After running `npm install`, you'll have:

- **express** - Web server framework
- **ws** - WebSocket server
- **obs-websocket-js** - OBS communication
- **bcryptjs** - Password hashing
- **dotenv** - Environment variable loading
- **cors** - Cross-origin resource sharing

All are free, open-source, and well-maintained.

---

## Quick Reference

| Task | File to Edit |
|------|-------------|
| Change button controls | `public/index.html` |
| Change colors/theme | `public/styles.css` |
| Change passwords | `.env` |
| Add new OBS command | `server.js` |
| Customize teacher panel | `public/teacher-panel.html` |
| Adjust rate limiting | `server.js` (top section) |

---

## File Access URLs

When server is running at `http://localhost:3000`:

- **Student Interface:** `http://localhost:3000/`
- **Teacher Panel:** `http://localhost:3000/teacher-panel.html`
- **Server Status API:** `http://localhost:3000/api/status`
- **Password Hash Generator:** `http://localhost:3000/api/hash-password` (POST)

---

**Now you know where everything is! Start with QUICK_START.md to get running. 🚀**
