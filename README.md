# LearnHero Loop

LearnHero Loop is a lightweight study companion that blends spaced repetition with a Pomodoro workflow. Teachers and students can capture new "anchors" during focus blocks, automatically schedule follow-up recalls, and work through interleaved review cards in the same dashboard.

## Status
- **Stage:** Prototype (work-in-progress)
- **Stack:** Vite, React, TypeScript, Tailwind CSS
- **Roadmap:** polish responsive layout, add quiz accuracy tracking, and enable cloud sync/export options

## Quick links
- [Getting started](GETTING_STARTED.md)
- [Contributing](CONTRIBUTING.md)
- [Issue tracker](https://github.com/jwheintz/GPT/issues)

## Running the app locally
1. **Install prerequisites**
   - Node.js ≥ 18 (includes npm)
2. **Install dependencies**
   ```bash
   npm install
   ```
3. **Start the dev server**
   ```bash
   npm run dev
   ```
   Vite will print a local URL (typically http://localhost:5173). Open it in your browser to use the app.
4. **Create a production build** *(optional)*
   ```bash
   npm run build
   npm run preview
   ```

## Features
- Pomodoro timer with configurable work, short break, and long break durations.
- Local-storage backed anchor notebook: add topics during focus blocks and tag them for later.
- Spaced repetition engine that seeds four starter recall cards (+1d, +3d, +7d, +21d) and adapts interval lengths based on your feedback (Hard/OK/Easy).
- Interleaved review queue that balances cards across tags to avoid topic fatigue.
- JSON export so you can back up or transfer your study data.

## Tips for students & teachers
- Keep the timer running: anchors can only be added during work sessions to encourage focus time.
- Use short minute durations (e.g., 1/1/2) while experimenting—update them in **Settings**.
- Review cards frequently: once a card is graded, the next recall is scheduled automatically.
- Export data before clearing your browser storage or switching devices.

## Testing
Run the build to ensure TypeScript type checks and Tailwind styles compile correctly:
```bash
npm run build
```

## Support
Questions or ideas? Open an issue in the tracker linked above or reach out through the GitHub project discussions.
