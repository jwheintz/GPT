# 🎨 Customization Guide

Learn how to customize your Classroom OBS Control System to match your specific needs, OBS setup, and teaching style.

## Table of Contents

1. [Customizing Button Controls](#customizing-button-controls)
2. [Styling the Interface](#styling-the-interface)
3. [Adding New Command Types](#adding-new-command-types)
4. [Configuring Rate Limits](#configuring-rate-limits)
5. [Creating Custom Layouts](#creating-custom-layouts)
6. [Advanced OBS Integration](#advanced-obs-integration)

---

## Customizing Button Controls

The default interface includes several example buttons, but you'll want to customize these to match your OBS setup.

### Understanding Button Data Attributes

Buttons use HTML data attributes to specify what they do:

```html
<button class="control-btn" 
        data-command="command_type" 
        data-source="SourceName" 
        data-filter="FilterName"
        data-scene="SceneName">
    <span class="icon">🎨</span>
    <span class="label">Button Label</span>
</button>
```

### Available Commands

#### 1. Toggle Filter
Toggles a filter on/off for a source.

```html
<button class="control-btn effect-btn" 
        data-command="toggle_filter" 
        data-source="Camera" 
        data-filter="Color Correction">
    <span class="icon">🎨</span>
    <span class="label">Color Effect</span>
</button>
```

**Requirements:**
- `data-source`: Name of the OBS source (e.g., "Camera", "Screen Capture")
- `data-filter`: Name of the filter on that source

#### 2. Toggle Source Visibility
Shows or hides a source in a scene.

```html
<button class="control-btn scene-btn" 
        data-command="toggle_source" 
        data-scene="Main" 
        data-source="Overlay">
    <span class="icon">📊</span>
    <span class="label">Toggle Overlay</span>
</button>
```

**Requirements:**
- `data-scene`: Name of the scene
- `data-source`: Name of the source in that scene

#### 3. Switch Scene
Changes the current OBS scene.

```html
<button class="control-btn scene-btn" 
        data-command="trigger_scene" 
        data-scene="Presentation">
    <span class="icon">🎬</span>
    <span class="label">Switch to Presentation</span>
</button>
```

**Requirements:**
- `data-scene`: Name of the scene to switch to

### Finding Your OBS Names

To find the exact names used in OBS:

1. **Source Names**: Look in your Sources list in OBS
2. **Filter Names**: Right-click source → Filters → see filter names
3. **Scene Names**: Look in the Scenes list in OBS

**Important**: Names are case-sensitive! "Camera" ≠ "camera"

### Example Customizations

#### Add a Zoom Effect

1. In OBS, add a "Scaling/Aspect Ratio" filter to your Camera
2. Name it "Zoom"
3. Add this button:

```html
<button class="control-btn effect-btn" 
        data-command="toggle_filter" 
        data-source="Camera" 
        data-filter="Zoom">
    <span class="icon">🔍</span>
    <span class="label">Zoom In</span>
</button>
```

#### Add a "Raise Hand" Indicator

1. Add an image source in OBS called "Hand Icon"
2. Hide it by default
3. Add this button:

```html
<button class="control-btn" 
        data-command="toggle_source" 
        data-scene="Main" 
        data-source="Hand Icon">
    <span class="icon">✋</span>
    <span class="label">Raise Hand</span>
</button>
```

#### Subject-Specific Scenes

```html
<!-- Math Mode -->
<button class="control-btn" 
        data-command="trigger_scene" 
        data-scene="Math Workspace">
    <span class="icon">➕</span>
    <span class="label">Math Mode</span>
</button>

<!-- Science Mode -->
<button class="control-btn" 
        data-command="trigger_scene" 
        data-scene="Lab Setup">
    <span class="icon">🔬</span>
    <span class="label">Science Mode</span>
</button>
```

### Organizing Buttons by Section

Edit `public/index.html` to add new sections:

```html
<div class="section">
    <div class="section-header">
        <h2>🔬 Science Effects</h2>
        <p class="section-desc">Chemistry-themed visual effects</p>
    </div>
    
    <div class="control-grid">
        <!-- Your science-themed buttons here -->
    </div>
</div>
```

### Icons

Use emoji icons or change them to text. Here are some suggestions:

- Effects: 🎨 ✨ 💫 ⭐ 🌟 ✨ 
- Actions: 👆 👇 👈 👉 👍 👎
- Science: 🔬 🧪 ⚗️ 🧬 🔭
- Math: ➕ ➖ ✖️ ➗ 📐 📏
- Literature: 📚 📖 ✍️ 📝
- Music: 🎵 🎶 🎤 🎸 🎹
- Art: 🎨 🖌️ 🖍️ 🎭
- Tech: 💻 🖥️ ⌨️ 🖱️
- General: 🎯 🎮 🎲 🎪

---

## Styling the Interface

### Changing Colors

Edit `public/styles.css` and modify the CSS variables:

```css
:root {
    --primary-color: #4f46e5;      /* Main accent color */
    --primary-hover: #4338ca;      /* Hover state */
    --secondary-color: #10b981;    /* Success/connected color */
    --danger-color: #ef4444;       /* Kill switch/error color */
    --warning-color: #f59e0b;      /* Warning messages */
    --background: #0f172a;         /* Main background */
    --surface: #1e293b;            /* Card backgrounds */
    --surface-hover: #334155;      /* Hover states */
    --text-primary: #f1f5f9;       /* Main text color */
    --text-secondary: #94a3b8;     /* Secondary text */
    --border: #334155;             /* Border color */
}
```

### Custom Button Styles

Add custom button classes:

```css
/* Add to styles.css */
.control-btn.red-theme {
    border-color: #ef4444;
}

.control-btn.red-theme:hover {
    border-color: #dc2626;
    box-shadow: 0 8px 20px rgba(239, 68, 68, 0.3);
}

.control-btn.green-theme {
    border-color: #10b981;
}

.control-btn.green-theme:hover {
    border-color: #059669;
    box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
}
```

Then use in HTML:

```html
<button class="control-btn red-theme" ...>
```

### School Branding

Add your school logo and colors:

1. **Add logo to header**:

```html
<!-- In index.html, modify the header -->
<div class="header-left">
    <img src="your-school-logo.png" alt="Logo" style="height: 40px; margin-right: 15px;">
    <div>
        <h1>🎓 Your School Name</h1>
        <p class="role-badge" id="role-badge">Student</p>
    </div>
</div>
```

2. **Use school colors**:

```css
:root {
    --primary-color: #your-school-primary;
    --secondary-color: #your-school-secondary;
}
```

---

## Adding New Command Types

Want to add completely new functionality? You'll need to modify both the server and client.

### Example: Adding a "Pulse Filter" Command

This will temporarily enable a filter, then disable it after a delay.

#### 1. Server Side (`server.js`)

Add a new command handler:

```javascript
case 'pulse_filter':
    // Enable filter
    await obs.call('SetSourceFilterEnabled', {
        sourceName: params.sourceName,
        filterName: params.filterName,
        filterEnabled: true
    });
    
    ws.send(JSON.stringify({ 
        type: 'command_success', 
        message: `${params.filterName} pulsed!` 
    }));
    
    // Disable after 3 seconds
    setTimeout(async () => {
        try {
            await obs.call('SetSourceFilterEnabled', {
                sourceName: params.sourceName,
                filterName: params.filterName,
                filterEnabled: false
            });
        } catch (err) {
            console.error('Failed to disable filter:', err);
        }
    }, 3000);
    break;
```

#### 2. Client Side (`public/index.html`)

Add a button:

```html
<button class="control-btn" 
        data-command="pulse_filter" 
        data-source="Camera" 
        data-filter="Flash">
    <span class="icon">⚡</span>
    <span class="label">Flash Effect</span>
</button>
```

No changes needed to `app.js` - it automatically handles new commands!

### Example: Adding Audio Controls

If you want to control VoiceMod or audio sources:

#### Server Side

```javascript
case 'toggle_audio':
    const audioStatus = await obs.call('GetInputMute', {
        inputName: params.sourceName
    });
    
    await obs.call('SetInputMute', {
        inputName: params.sourceName,
        inputMuted: !audioStatus.inputMuted
    });
    
    ws.send(JSON.stringify({ 
        type: 'command_success', 
        message: `Audio ${!audioStatus.inputMuted ? 'muted' : 'unmuted'}` 
    }));
    break;
```

#### Client Side

```html
<button class="control-btn" 
        data-command="toggle_audio" 
        data-source="Microphone">
    <span class="icon">🎤</span>
    <span class="label">Toggle Mic</span>
</button>
```

---

## Configuring Rate Limits

Prevent spam by adjusting rate limits in `server.js`:

```javascript
// At the top of server.js
const RATE_LIMIT_WINDOW = 5000;          // 5 seconds
const MAX_REQUESTS_PER_WINDOW = 10;      // 10 requests per window
```

**Recommendations:**
- **Elementary students**: Lower to 5 requests per 10 seconds
- **Middle/High school**: Default settings usually fine
- **College**: Can increase to 20 requests per 5 seconds
- **Teacher access**: No rate limiting (already excluded)

---

## Creating Custom Layouts

### Two-Column Layout

For more buttons, create a two-column layout:

```html
<div class="section">
    <div class="section-header">
        <h2>🎨 All Effects</h2>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <!-- Left Column -->
        <div class="control-grid">
            <!-- Left side buttons -->
        </div>
        
        <!-- Right Column -->
        <div class="control-grid">
            <!-- Right side buttons -->
        </div>
    </div>
</div>
```

### Compact Mode

For many buttons, create a compact grid:

```css
/* Add to styles.css */
.control-grid.compact {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
}

.control-grid.compact .control-btn {
    padding: 15px 10px;
}

.control-grid.compact .icon {
    font-size: 30px;
}

.control-grid.compact .label {
    font-size: 12px;
}
```

```html
<div class="control-grid compact">
    <!-- Your buttons -->
</div>
```

### Subject Tabs

Create tabbed interface for different subjects:

```html
<div class="section">
    <div class="tabs">
        <button class="tab active" onclick="showTab('math')">Math</button>
        <button class="tab" onclick="showTab('science')">Science</button>
        <button class="tab" onclick="showTab('art')">Art</button>
    </div>
    
    <div id="math-tab" class="tab-content">
        <!-- Math buttons -->
    </div>
    
    <div id="science-tab" class="tab-content" style="display: none;">
        <!-- Science buttons -->
    </div>
    
    <div id="art-tab" class="tab-content" style="display: none;">
        <!-- Art buttons -->
    </div>
</div>
```

Add JavaScript:

```javascript
// Add to app.js
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').style.display = 'block';
    event.target.classList.add('active');
}
```

---

## Advanced OBS Integration

### Using Complex Filter Settings

Instead of just toggling, modify filter settings:

```javascript
// In server.js, add this command
case 'set_color_temperature':
    await obs.call('SetSourceFilterSettings', {
        sourceName: params.sourceName,
        filterName: 'Color Correction',
        filterSettings: {
            color_temperature: params.temperature
        }
    });
    break;
```

### Creating Filter Presets

Set up multiple filters at once:

```javascript
// Server side
case 'apply_preset':
    const presets = {
        'warm': {
            'Color Correction': { color_temperature: 6500 },
            'Saturation': { saturation: 1.2 }
        },
        'cool': {
            'Color Correction': { color_temperature: 9000 },
            'Saturation': { saturation: 0.8 }
        }
    };
    
    const preset = presets[params.presetName];
    for (const [filterName, settings] of Object.entries(preset)) {
        await obs.call('SetSourceFilterSettings', {
            sourceName: params.sourceName,
            filterName: filterName,
            filterSettings: settings
        });
    }
    break;
```

### Animating Transitions

Gradually change a value over time:

```javascript
case 'animate_filter':
    const steps = 30;
    const duration = 2000; // 2 seconds
    const delay = duration / steps;
    
    for (let i = 0; i <= steps; i++) {
        setTimeout(async () => {
            const value = params.startValue + (params.endValue - params.startValue) * (i / steps);
            await obs.call('SetSourceFilterSettings', {
                sourceName: params.sourceName,
                filterName: params.filterName,
                filterSettings: {
                    [params.property]: value
                }
            });
        }, i * delay);
    }
    break;
```

---

## Configuration File

For easier management, create a configuration file:

**`config.json`:**

```json
{
    "buttons": [
        {
            "section": "Visual Effects",
            "buttons": [
                {
                    "label": "Color Effect",
                    "icon": "🎨",
                    "command": "toggle_filter",
                    "source": "Camera",
                    "filter": "Color Correction"
                },
                {
                    "label": "Blur Effect",
                    "icon": "💫",
                    "command": "toggle_filter",
                    "source": "Camera",
                    "filter": "Blur"
                }
            ]
        }
    ]
}
```

Then generate buttons dynamically (requires additional JavaScript).

---

## Tips for Customization

1. **Start with the basics** - get the default setup working first
2. **Test incrementally** - add one button at a time
3. **Name consistently** - use clear, descriptive names in OBS
4. **Document your setup** - keep notes on what buttons do what
5. **Backup your files** - before making major changes
6. **Use version control** - git is your friend!

---

## Need Help?

- Check the main [README.md](README.md) for basics
- Review [SETUP_GUIDE.md](SETUP_GUIDE.md) for installation
- See [ADVANCED.md](ADVANCED.md) for advanced features

**Happy customizing! 🎨**
