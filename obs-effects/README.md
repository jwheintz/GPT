# 🎬 OBS Effect Templates

These HTML files can be used as **Browser Sources** in OBS to create visual effects triggered by the Classroom Control system.

## Setup Instructions

### Method 1: Local Files

1. Copy these HTML files to a folder on your computer
2. In OBS, add a **Browser Source**
3. Check "Local file" and select the HTML file
4. Set dimensions (e.g., 1920x1080)
5. Name the source to match your config (e.g., "Confetti")

### Method 2: URL Parameters

Some effects accept URL parameters:

```
file:///C:/path/to/emoji-popup.html?emoji=🎉
file:///C:/path/to/floating-reactions.html?emoji=🔥&count=15
```

## Available Effects

### `confetti.html`
Colorful confetti falling from the top of the screen.
- Duration: ~3-4 seconds
- Best for: Celebrations, correct answers, achievements

### `emoji-popup.html`
Single large emoji that pops in with animation.
- Parameter: `?emoji=👍` (any emoji)
- Duration: Continuous float animation
- Best for: Quick reactions, thumbs up, hearts

### `floating-reactions.html`
Multiple emojis floating up from the bottom.
- Parameters: `?emoji=❤️&count=10`
- Duration: ~3 seconds
- Best for: Love reactions, fire, stars

## Creating Custom Effects

### Basic Template

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { 
            background: transparent;  /* Important! */
            overflow: hidden;
        }
        /* Your styles here */
    </style>
</head>
<body>
    <!-- Your content here -->
    <script>
        // Your animation code here
    </script>
</body>
</html>
```

### Tips

1. **Always use `background: transparent`** in body styles
2. **Set overflow: hidden** to prevent scrollbars
3. **Self-contained** - don't rely on external resources
4. **Auto-cleanup** - remove elements after animation
5. **Test in OBS** before going live

## OBS Source Settings

For best results, configure your Browser Source with:

- **Width**: Match your canvas (e.g., 1920)
- **Height**: Match your canvas (e.g., 1080)
- **FPS**: 60 (for smooth animations)
- **Custom CSS**: Leave empty (styles are in HTML)
- **Shutdown source when not visible**: ✅ Checked
- **Refresh browser when scene becomes active**: ✅ Checked

## Matching Config Names

Make sure your OBS source names match the `config_local.py` settings:

```python
VISUAL_EFFECTS = {
    "confetti": {
        "type": "source",
        "source_name": "Confetti",  # <- Must match OBS source name exactly
        "duration": 3000,
    },
}
```

## More Resources

- [OBS Browser Source Documentation](https://obsproject.com/wiki/Sources-Guide#browser-source)
- [Lottie Animations](https://lottiefiles.com/) - Free animated graphics
- [CSS Animation Examples](https://animate.style/) - Pre-built CSS animations
