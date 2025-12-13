# 📹 OBS Setup Examples

Ready-to-use OBS configurations for different teaching scenarios.

---

## Basic Classroom Setup

Perfect for starting out.

### Scene: "Main"

**Sources:**
1. **Camera** (Video Capture Device)
   - Your webcam
   - Filters:
     - Color Correction
     - Blur
     - Sharpen

2. **Screen** (Display Capture)
   - Your presentation screen
   - Position behind camera

3. **Overlay** (Image)
   - School logo or graphics
   - Position in corner

4. **Text** (Text GDI+)
   - Class name or topic
   - Position at bottom

### Student Controls:
- Toggle Camera Blur
- Toggle Camera Color Correction
- Show/Hide Overlay
- Show/Hide Text

---

## Science Lab Setup

For demonstrations and experiments.

### Scene 1: "Teacher View"
- Front-facing camera
- Screen share for diagrams

### Scene 2: "Experiment View"
- Overhead camera pointing down
- Filters:
  - Sharpen (for clarity)
  - Color Correction (for lighting)
  - Chroma Key (if using green mat)

### Scene 3: "Microscope View"
- Camera or capture card from microscope
- Magnification overlay
- Labels/annotations

### Student Controls:
- Switch between views
- Toggle magnification
- Show/hide labels
- Zoom in/out

---

## Math/Whiteboard Setup

For problem-solving sessions.

### Scene: "Teaching"

**Sources:**
1. **Document Camera** (overhead view of desk/paper)
   - Filters: Sharpen, Color Correction

2. **Digital Whiteboard** (Screen Capture or iPad input)

3. **Teacher Webcam** (small, in corner)

4. **Step Counter** (Text source)
   - Shows problem steps
   - Students can advance

### Student Controls:
- Switch between document camera and whiteboard
- Next/Previous step
- Show/Hide answer
- Highlight regions (with colored overlays)

---

## Presentation Mode

For lectures and slideshows.

### Scene: "Slides"

**Sources:**
1. **Presentation** (Screen Capture of PowerPoint)
   - Full screen

2. **Teacher PIP** (Picture-in-picture)
   - Small camera view in corner
   - Can be toggled by students

3. **Reaction Overlay** (Image sequence)
   - Fun reactions students can trigger
   - Position: top of screen

4. **Progress Bar** (Color Source with crop)
   - Shows lecture progress
   - Updates automatically

### Student Controls:
- Show/Hide teacher camera
- Trigger reaction overlays
- Show/Hide notes section
- Zoom into slide details

---

## Language Class Setup

For language learning and pronunciation.

### Scene: "Vocabulary"

**Sources:**
1. **Teacher Camera** (large, center)
   - Close-up for pronunciation
   - Filters:
     - Sharpen
     - Color Correction (good lighting)

2. **Word Display** (Text/Image)
   - Current vocabulary word
   - Translation
   - Image representation

3. **Audio Waveform** (Audio visualization)
   - Shows sound levels
   - Helps with pronunciation

### Student Controls:
- Next/Previous word
- Show/Hide translation
- Show/Hide image
- Trigger pronunciation examples (sound effects)

---

## Art/Design Class

For creative demonstrations.

### Scene: "Studio"

**Sources:**
1. **Overhead Camera** (looking down at workspace)
   - Filters:
     - Color Correction
     - Sharpen
     - Crop/Zoom

2. **Reference Image** (Image Source)
   - What you're creating
   - Can cycle through multiple

3. **Teacher Camera** (small, side view)

4. **Timer** (Text)
   - For timed exercises

### Student Controls:
- Zoom in/out on workspace
- Next/Previous reference image
- Different color filters (sepia, B&W, high contrast)
- Start/Stop timer
- Show/Hide teacher view

---

## Music Class

For performance and theory.

### Scene: "Performance"

**Sources:**
1. **Performer Camera** (wide shot)
   - Shows instrument and player

2. **Close-up Camera** (hands/instrument)
   - Detail view of technique

3. **Sheet Music** (Image/PDF)
   - Current piece
   - Can scroll

4. **Metronome Visual** (Animated image)
   - Visual beat indicator

### Student Controls:
- Switch between wide and close-up
- Scroll sheet music
- Start/Stop metronome
- Trigger applause/reactions
- Show/Hide notation guides

---

## Physical Education / Dance

For movement-based classes.

### Scene: "Studio"

**Sources:**
1. **Wide Camera** (full body view)
   - Multiple angles if possible

2. **Mirror Mode** (Horizontal Flip)
   - Toggle for students to mirror movements

3. **Step Counter** (Text)
   - Counts repetitions

4. **Music Visualizer** (Audio spectrum)

### Student Controls:
- Toggle mirror mode
- Switch camera angles
- Reset counter
- Show/Hide form guides (overlay lines/grids)
- Slow motion (if using pre-recorded segments)

---

## Gaming/Esports Class

For competitive gaming instruction.

### Scene: "Gameplay"

**Sources:**
1. **Game Capture** (primary)
   - The game being played

2. **Player Cam** (small, corner)
   - Teacher/student playing

3. **Minimap Zoom** (Crop filter)
   - Enlarged game minimap

4. **Stats Overlay** (Text/Graphics)
   - Game statistics

### Student Controls:
- Toggle player cam
- Switch between players (if multiple)
- Show/Hide stat overlay
- Trigger highlight markers
- Instant replay (if pre-recorded)

---

## General Tips for Any Setup

### Filter Recommendations

**Camera Filters:**
- Color Correction - Always useful
- Sharpen - For clarity
- Blur - For occasional privacy/fun
- Chroma Key - If using green screen
- LUT - For consistent color grading

**Fun Filters Students Can Toggle:**
- Render Delay - Creates echo effect
- Scroll - Animated movement
- 3D Effect - Adds depth
- Invert Polarity - Negative effect
- Scaling/Aspect Ratio - Zoom/distort

### Scene Organization

Create scenes for different activities:
- **Start** - Welcome screen
- **Teaching** - Main instruction
- **Activity** - Student work time
- **Break** - Break screen
- **End** - Closing/homework

Students can trigger scene changes!

### Naming Conventions

Use clear, consistent names:
- ✅ "Camera" not "Video Capture Device 1"
- ✅ "Color Effect" not "Color Correction Filter"
- ✅ "Main Screen" not "Display Capture (Monitor 1)"

This makes configuration easier!

### Testing Checklist

Before class, test:
- [ ] All filters work
- [ ] All scene switches work
- [ ] Names match in HTML file
- [ ] Students can trigger everything
- [ ] Kill switch disables all controls
- [ ] OBS doesn't lag with filters on

---

## Customization Templates

### Template 1: Minimal Setup (3 buttons)

```html
<div class="control-grid">
    <!-- Toggle camera blur for privacy -->
    <button class="control-btn" 
            data-command="toggle_filter" 
            data-source="Camera" 
            data-filter="Blur">
        <span class="icon">💫</span>
        <span class="label">Blur Camera</span>
    </button>
    
    <!-- Toggle overlay/logo -->
    <button class="control-btn" 
            data-command="toggle_source" 
            data-scene="Main" 
            data-source="Overlay">
        <span class="icon">⭐</span>
        <span class="label">Show Logo</span>
    </button>
    
    <!-- Fun color effect -->
    <button class="control-btn" 
            data-command="toggle_filter" 
            data-source="Camera" 
            data-filter="Color Correction">
        <span class="icon">🎨</span>
        <span class="label">Color Effect</span>
    </button>
</div>
```

### Template 2: Scene Switcher (4 scenes)

```html
<div class="control-grid">
    <button data-command="trigger_scene" data-scene="Intro">
        <span class="icon">🎬</span>
        <span class="label">Intro</span>
    </button>
    
    <button data-command="trigger_scene" data-scene="Teaching">
        <span class="icon">📚</span>
        <span class="label">Teaching</span>
    </button>
    
    <button data-command="trigger_scene" data-scene="Activity">
        <span class="icon">✏️</span>
        <span class="label">Activity</span>
    </button>
    
    <button data-command="trigger_scene" data-scene="Break">
        <span class="icon">☕</span>
        <span class="label">Break</span>
    </button>
</div>
```

### Template 3: Interactive Quiz

Create sources for correct/incorrect:

```html
<div class="control-grid">
    <button data-command="toggle_source" 
            data-scene="Quiz" 
            data-source="Correct Mark">
        <span class="icon">✅</span>
        <span class="label">Correct!</span>
    </button>
    
    <button data-command="toggle_source" 
            data-scene="Quiz" 
            data-source="Wrong Mark">
        <span class="icon">❌</span>
        <span class="label">Try Again</span>
    </button>
    
    <button data-command="toggle_source" 
            data-scene="Quiz" 
            data-source="Think Bubble">
        <span class="icon">💭</span>
        <span class="label">Thinking...</span>
    </button>
</div>
```

---

## Recommended OBS Plugins

Enhance your setup with these plugins:

1. **Move Transition** - Smooth animations
2. **Source Record** - Record individual sources
3. **Directory Watch Media** - Auto-updating images
4. **Text Animation** - Animated text effects
5. **Gradient Source** - Custom backgrounds

Download from: https://obsproject.com/forum/resources/

---

## Need More Ideas?

Check out:
- [CUSTOMIZATION.md](CUSTOMIZATION.md) - Button customization
- [ADVANCED.md](ADVANCED.md) - Advanced integrations
- OBS Forums - Community setups
- YouTube - "OBS for education" tutorials

**Happy streaming! 🎥**
