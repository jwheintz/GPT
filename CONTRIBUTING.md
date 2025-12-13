# Contributing to Classroom Control

Thank you for your interest in contributing! This project aims to make classroom interactions more engaging for educators.

## Project Structure

```
classroom-control/
├── web/                    # Web frontend (static files)
│   ├── index.html         # Main student interface
│   ├── style.css          # Styling
│   ├── config.js          # Configuration template
│   └── app.js             # Frontend logic
│
├── local-relay/           # Windows relay application
│   ├── relay.py           # Main application
│   ├── voicemod.py        # VoiceMod integration module
│   ├── config.py          # Configuration template
│   └── requirements.txt   # Python dependencies
│
├── obs-effects/           # Sample OBS browser sources
│   ├── confetti.html
│   ├── emoji-popup.html
│   └── floating-reactions.html
│
├── README.md              # Main documentation
└── GETTING_STARTED.md     # Setup guide
```

## Development Setup

### Web Frontend

The frontend is pure HTML/CSS/JS with no build step:
1. Edit files in `/web`
2. Open `index.html` in browser to test
3. Configure `config.js` with your Supabase details

### Local Relay

1. Create a virtual environment:
   ```bash
   cd local-relay
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy and edit config:
   ```bash
   copy config.py config_local.py
   ```
4. Run:
   ```bash
   python relay.py
   ```

## Areas for Contribution

### High Priority
- [ ] Teacher dashboard (real-time view of incoming commands)
- [ ] Poll result aggregation and display
- [ ] More visual effect templates
- [ ] Integration tests

### Nice to Have
- [ ] Dark mode toggle in web UI
- [ ] Custom themes/branding options
- [ ] Multi-room support
- [ ] Export/import configuration
- [ ] Stream Deck plugin

### VoiceMod Integration
- [ ] Test with actual VoiceMod installation
- [ ] Document available voice IDs
- [ ] Add soundboard support

## Code Style

### Python
- Follow PEP 8
- Use type hints where helpful
- Keep functions focused and documented

### JavaScript
- Use ES6+ features
- Keep it dependency-free (except Supabase client)
- Comment complex logic

### CSS
- Use CSS variables for theming
- Mobile-first responsive design
- Support dark mode via `prefers-color-scheme`

## Testing

Before submitting:
1. Test web interface in Chrome, Firefox, Safari
2. Test on mobile devices
3. Test relay with OBS WebSocket
4. Verify kill switch works

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit PR with clear description

## Questions?

Open an issue for:
- Bug reports
- Feature requests
- Questions about setup
- Ideas for improvement

Thank you for helping make education more interactive! 🎓
