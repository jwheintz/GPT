# 🚀 Advanced Features & Integration

This guide covers advanced features, integrations, and techniques for power users.

## Table of Contents

1. [Stream Deck Integration](#stream-deck-integration)
2. [VoiceMod Integration](#voicemod-integration)
3. [Multiple Camera Support](#multiple-camera-support)
4. [Analytics & Logging](#analytics--logging)
5. [Custom Authentication](#custom-authentication)
6. [Webhooks & External Services](#webhooks--external-services)
7. [Performance Optimization](#performance-optimization)
8. [Backup & Recovery](#backup--recovery)

---

## Stream Deck Integration

Since you're using Stream Deck hardware, you can create a parallel teacher control panel.

### Setup Stream Deck with OBS WebSocket

1. **Install OBS WebSocket plugin** on Stream Deck:
   - Download from Elgato marketplace
   - Or use the generic WebSocket plugin

2. **Configure buttons** to mirror student actions:
   - Toggle filters
   - Switch scenes
   - Emergency kill switch

### Complementary Use

- **Stream Deck**: Personal teacher controls, quick access
- **Web Interface**: Student engagement, public controls
- **Both can coexist** and control the same OBS instance

### Example Stream Deck Actions

Create buttons for:
- **Kill Switch**: Instant disable of student controls
- **Reset All Filters**: Return to default state
- **Scene Presets**: Quick scene changes
- **Emergency Blackout**: Turn off camera instantly

---

## VoiceMod Integration

Extend the system to control VoiceMod voice effects.

### Method 1: VoiceMod API (If Available)

VoiceMod has a REST API for voice control:

```javascript
// Add to server.js
const axios = require('axios');

const VOICEMOD_API = 'http://localhost:59129/v1';

app.post('/api/voicemod', async (req, res) => {
    try {
        const { action, voiceId } = req.body;
        
        if (action === 'selectVoice') {
            await axios.put(`${VOICEMOD_API}/voices/${voiceId}`, {
                enabled: true
            });
        }
        
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});
```

### Method 2: AutoHotkey Integration

Use AutoHotkey to trigger VoiceMod hotkeys:

1. **Install AutoHotkey** on your computer
2. **Create script** (`voicemod-control.ahk`):

```ahk
; VoiceMod Control Script
; Maps HTTP requests to VoiceMod hotkeys

#NoEnv
#SingleInstance Force

; Start HTTP server
Server := ComObjCreate("WinHttp.WinHttpRequest.5.1")

Loop {
    ; Check for command file
    if FileExist("voicemod_command.txt") {
        FileRead, Command, voicemod_command.txt
        FileDelete, voicemod_command.txt
        
        ; Execute command
        if (Command = "robot") {
            Send ^!1  ; Ctrl+Alt+1 for Robot voice
        }
        else if (Command = "cave") {
            Send ^!2  ; Ctrl+Alt+2 for Cave voice
        }
        ; Add more voice mappings
    }
    Sleep, 100
}
```

3. **Call from Node.js**:

```javascript
const fs = require('fs');

function triggerVoiceModVoice(voiceName) {
    fs.writeFileSync('voicemod_command.txt', voiceName);
}

// Add to your WebSocket handler
case 'voicemod_voice':
    triggerVoiceModVoice(params.voice);
    ws.send(JSON.stringify({ 
        type: 'command_success', 
        message: `Voice changed to ${params.voice}` 
    }));
    break;
```

### Add VoiceMod Buttons

```html
<div class="section">
    <div class="section-header">
        <h2>🎤 Voice Effects</h2>
    </div>
    
    <div class="control-grid">
        <button class="control-btn" 
                data-command="voicemod_voice" 
                data-voice="robot">
            <span class="icon">🤖</span>
            <span class="label">Robot Voice</span>
        </button>
        
        <button class="control-btn" 
                data-command="voicemod_voice" 
                data-voice="cave">
            <span class="icon">🌊</span>
            <span class="label">Cave Echo</span>
        </button>
        
        <button class="control-btn" 
                data-command="voicemod_voice" 
                data-voice="chipmunk">
            <span class="icon">🐿️</span>
            <span class="label">Chipmunk</span>
        </button>
    </div>
</div>
```

---

## Multiple Camera Support

Set up controls for multiple cameras or angles.

### OBS Setup

1. Add multiple camera sources:
   - "Main Camera"
   - "Overhead Camera"
   - "Document Camera"

2. Apply different filters to each

### Button Configuration

```html
<!-- Camera 1 Controls -->
<div class="camera-section">
    <h3>Main Camera</h3>
    <div class="control-grid compact">
        <button data-command="toggle_filter" data-source="Main Camera" data-filter="Blur">
            <span class="icon">💫</span>
            <span class="label">Blur</span>
        </button>
        <!-- More filters -->
    </div>
</div>

<!-- Camera 2 Controls -->
<div class="camera-section">
    <h3>Overhead Camera</h3>
    <div class="control-grid compact">
        <button data-command="toggle_filter" data-source="Overhead Camera" data-filter="Sharpen">
            <span class="icon">✨</span>
            <span class="label">Sharpen</span>
        </button>
        <!-- More filters -->
    </div>
</div>
```

### Quick Camera Switching

```javascript
// Add to server.js
case 'switch_camera':
    // Hide all cameras
    const cameras = ['Main Camera', 'Overhead Camera', 'Document Camera'];
    
    for (const camera of cameras) {
        try {
            const itemId = await obs.call('GetSceneItemId', {
                sceneName: params.sceneName,
                sourceName: camera
            });
            
            const shouldShow = camera === params.cameraName;
            
            await obs.call('SetSceneItemEnabled', {
                sceneName: params.sceneName,
                sceneItemId: itemId.sceneItemId,
                sceneItemEnabled: shouldShow
            });
        } catch (err) {
            // Camera might not exist in scene
            console.error(`Could not control ${camera}:`, err.message);
        }
    }
    
    ws.send(JSON.stringify({ 
        type: 'command_success', 
        message: `Switched to ${params.cameraName}` 
    }));
    break;
```

---

## Analytics & Logging

Track usage patterns and popular effects.

### Basic Logging

Add to `server.js`:

```javascript
const fs = require('fs');

// Log all commands
function logCommand(command, params, userRole) {
    const logEntry = {
        timestamp: new Date().toISOString(),
        command: command,
        params: params,
        role: userRole
    };
    
    fs.appendFileSync('command_log.json', JSON.stringify(logEntry) + '\n');
}

// In your command handler
await handleOBSCommand(data.command, data.params, ws);
logCommand(data.command, data.params, isTeacher ? 'teacher' : 'student');
```

### Usage Statistics

Track which effects are most popular:

```javascript
const commandStats = new Map();

function trackCommand(command) {
    const key = `${command.command}_${command.params.filterName || command.params.sceneName}`;
    commandStats.set(key, (commandStats.get(key) || 0) + 1);
}

// API endpoint to view stats
app.get('/api/stats', (req, res) => {
    const stats = Array.from(commandStats.entries())
        .map(([key, count]) => ({ command: key, count }))
        .sort((a, b) => b.count - a.count);
    
    res.json(stats);
});
```

### Export Reports

Generate a report after class:

```javascript
app.get('/api/report', (req, res) => {
    const logs = fs.readFileSync('command_log.json', 'utf8')
        .split('\n')
        .filter(line => line.trim())
        .map(line => JSON.parse(line));
    
    const report = {
        totalCommands: logs.length,
        studentCommands: logs.filter(l => l.role === 'student').length,
        teacherCommands: logs.filter(l => l.role === 'teacher').length,
        mostPopular: getMostPopular(logs),
        timeline: getTimeline(logs)
    };
    
    res.json(report);
});
```

---

## Custom Authentication

Implement more sophisticated authentication.

### Individual Student Accounts

```javascript
// students.json
{
    "student1": {
        "password": "$2a$10$...",
        "name": "John Doe",
        "permissions": ["toggle_filter", "toggle_source"]
    },
    "student2": {
        "password": "$2a$10$...",
        "name": "Jane Smith",
        "permissions": ["toggle_filter"]
    }
}
```

```javascript
// Load students
const students = JSON.parse(fs.readFileSync('students.json'));

// Modify auth handler
if (data.type === 'auth') {
    const username = data.username;
    const password = data.password;
    
    const student = students[username];
    if (student && bcrypt.compareSync(password, student.password)) {
        ws.userData = {
            username: username,
            name: student.name,
            permissions: student.permissions
        };
        isAuthenticated = true;
        
        ws.send(JSON.stringify({ 
            type: 'auth_success', 
            name: student.name,
            permissions: student.permissions
        }));
    }
}
```

### Time-Based Access

Only allow control during certain hours:

```javascript
function isClassTime() {
    const now = new Date();
    const hour = now.getHours();
    const day = now.getDay(); // 0 = Sunday, 1 = Monday, etc.
    
    // Only Monday-Friday, 9am-5pm
    if (day === 0 || day === 6) return false;
    if (hour < 9 || hour >= 17) return false;
    
    return true;
}

// In command handler
if (!isClassTime() && !isTeacher) {
    ws.send(JSON.stringify({ 
        type: 'error', 
        message: 'Controls are only available during class hours' 
    }));
    return;
}
```

---

## Webhooks & External Services

Integrate with other platforms.

### Discord Notifications

Send notifications when students trigger effects:

```javascript
const axios = require('axios');

const DISCORD_WEBHOOK = process.env.DISCORD_WEBHOOK_URL;

async function notifyDiscord(message) {
    if (!DISCORD_WEBHOOK) return;
    
    try {
        await axios.post(DISCORD_WEBHOOK, {
            content: message,
            username: 'Classroom Bot'
        });
    } catch (error) {
        console.error('Discord notification failed:', error.message);
    }
}

// Notify on specific events
broadcastToAll({ type: 'filter_toggled', ... });
await notifyDiscord(`🎨 Student triggered: ${params.filterName}`);
```

### Google Sheets Logging

Log all activities to Google Sheets:

```javascript
const { GoogleSpreadsheet } = require('google-spreadsheet');

async function logToSheets(command, user, timestamp) {
    const doc = new GoogleSpreadsheet(process.env.SHEET_ID);
    await doc.useServiceAccountAuth({
        client_email: process.env.GOOGLE_EMAIL,
        private_key: process.env.GOOGLE_KEY,
    });
    
    await doc.loadInfo();
    const sheet = doc.sheetsByIndex[0];
    
    await sheet.addRow({
        timestamp: timestamp,
        user: user,
        command: command
    });
}
```

---

## Performance Optimization

### Caching OBS State

Reduce API calls by caching state:

```javascript
let obsStateCache = {
    scenes: [],
    filters: {},
    lastUpdate: 0
};

async function getOBSState() {
    const now = Date.now();
    
    // Cache for 30 seconds
    if (now - obsStateCache.lastUpdate < 30000) {
        return obsStateCache;
    }
    
    // Refresh cache
    const scenes = await obs.call('GetSceneList');
    obsStateCache.scenes = scenes.scenes;
    obsStateCache.lastUpdate = now;
    
    return obsStateCache;
}
```

### Connection Pooling

For many simultaneous students:

```javascript
// Increase WebSocket server limits
const wss = new WebSocket.Server({ 
    server,
    maxPayload: 100 * 1024, // 100KB
    perMessageDeflate: true,
    clientTracking: true
});

// Monitor connections
setInterval(() => {
    console.log(`Active connections: ${wss.clients.size}`);
}, 30000);
```

---

## Backup & Recovery

### Auto-Save OBS Scene Configuration

```javascript
async function backupOBSConfig() {
    try {
        const scenes = await obs.call('GetSceneList');
        const config = {
            timestamp: new Date().toISOString(),
            scenes: scenes
        };
        
        fs.writeFileSync(
            `backups/obs_config_${Date.now()}.json`,
            JSON.stringify(config, null, 2)
        );
    } catch (error) {
        console.error('Backup failed:', error);
    }
}

// Backup every hour
setInterval(backupOBSConfig, 3600000);
```

### Restore from Backup

```javascript
async function restoreOBSConfig(backupFile) {
    const config = JSON.parse(fs.readFileSync(backupFile));
    
    // Implement restoration logic
    // (complex - would need to recreate scenes, sources, filters)
    console.log('Restoring from backup:', config.timestamp);
}
```

---

## Security Enhancements

### HTTPS with SSL

For production use without ngrok:

```javascript
const https = require('https');
const fs = require('fs');

const server = https.createServer({
    key: fs.readFileSync('ssl/key.pem'),
    cert: fs.readFileSync('ssl/cert.pem')
}, app);
```

### IP Whitelist

Only allow connections from specific IPs:

```javascript
const ALLOWED_IPS = process.env.ALLOWED_IPS?.split(',') || [];

app.use((req, res, next) => {
    const clientIP = req.ip || req.connection.remoteAddress;
    
    if (ALLOWED_IPS.length > 0 && !ALLOWED_IPS.includes(clientIP)) {
        return res.status(403).json({ error: 'Access denied' });
    }
    
    next();
});
```

---

## Monitoring & Alerts

### Health Check Endpoint

```javascript
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        obsConnected: isOBSConnected,
        activeConnections: wss.clients.size,
        killSwitch: killSwitchActive
    });
});
```

### Email Alerts

Get notified of issues:

```javascript
const nodemailer = require('nodemailer');

async function sendAlert(subject, message) {
    const transporter = nodemailer.createTransporter({
        service: 'gmail',
        auth: {
            user: process.env.EMAIL_USER,
            pass: process.env.EMAIL_PASS
        }
    });
    
    await transporter.sendMail({
        from: process.env.EMAIL_USER,
        to: process.env.ALERT_EMAIL,
        subject: subject,
        text: message
    });
}

// Alert on OBS disconnection
obs.on('ConnectionClosed', () => {
    sendAlert('OBS Disconnected', 'OBS WebSocket connection was lost!');
});
```

---

## Production Deployment

### Running as Windows Service

Use `node-windows` to run as a service:

```bash
npm install -g node-windows
```

Create `install-service.js`:

```javascript
const Service = require('node-windows').Service;

const svc = new Service({
    name: 'Classroom OBS Control',
    description: 'Interactive classroom control system',
    script: 'C:\\ClassroomControl\\server.js'
});

svc.on('install', () => {
    svc.start();
});

svc.install();
```

---

## Testing

### Automated Testing

```javascript
// test/commands.test.js
const assert = require('assert');
const WebSocket = require('ws');

describe('Command System', () => {
    it('should toggle filter', async () => {
        const ws = new WebSocket('ws://localhost:3000');
        
        // Authenticate
        ws.send(JSON.stringify({
            type: 'auth',
            password: 'test_password',
            role: 'student'
        }));
        
        // Send command
        ws.send(JSON.stringify({
            type: 'obs_command',
            command: 'toggle_filter',
            params: {
                sourceName: 'Camera',
                filterName: 'Blur'
            }
        }));
        
        // Verify response
        // ...
    });
});
```

---

**Ready to take your classroom to the next level! 🚀**
