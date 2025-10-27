# Concept Pulse

Concept Pulse is a desktop spaced-repetition program focused on long term retention of certification and domain-specific concepts. Create flash cards, tag them by difficulty, and track recall performance over weeks and months using a simple adaptive review queue.

## Status

Early preview – the core features for adding cards, reviewing material, and tracking success rates are implemented.

## Features

* Guided review flow with "Again", "Hard", "Good", and "Easy" ratings inspired by SM-2.
* Difficulty and recall tagging with automatic success-rate tracking for each card.
* Domain filtering to focus on the topics that matter for your current certification path.
* SQLite-backed storage saved in `data/cards.db` for durability.

## Quick start (step-by-step)

1. **Install Python 3.9 or newer.**
   * Windows & macOS: download the official installer from https://www.python.org/downloads/ and keep the "Install launcher" / "Add Python to PATH" boxes checked.
   * Linux: install via your package manager (e.g. `sudo apt install python3 python3-venv python3-pip`).
2. **Make sure Tkinter is available.** It is bundled with the standard installer on Windows and macOS. On Debian/Ubuntu-based Linux you may need `sudo apt install python3-tk`.
3. **Get the project files.** Either clone with Git (`git clone https://github.com/jwheintz/GPT.git`) or download the ZIP from GitHub and unzip it.
4. **Open a terminal inside the project folder.** (On Windows: `Shift + Right Click` → *Open PowerShell window here*; macOS/Linux: `cd` into the folder.)
5. **Create a virtual environment (recommended):**

   ```bash
   python -m venv .venv
   ```

6. **Activate the virtual environment:**
   * Windows PowerShell: `.venv\Scripts\Activate.ps1`
   * Windows Command Prompt: `.venv\Scripts\activate.bat`
   * macOS/Linux: `source .venv/bin/activate`
7. **Start the app:**

   ```bash
   python -m app.main
   ```

   Keep the terminal window open while you use the GUI. If a firewall prompt appears the first time you run Python, allow it to communicate on private networks so the GUI can open.
8. **(Optional) Create a desktop shortcut:** on Windows you can make a shortcut pointing to `pythonw.exe -m app.main` with the *Start in* field set to the project folder so the console window stays hidden.

The first launch creates a `data/cards.db` file. Add new cards from the **Manage cards** tab, then work through the due queue under **Review queue**. Your review history is saved automatically when you close the app.

## Development notes

Static compilation checks:

```bash
python -m compileall app
```

## Getting help

Please open an issue at https://github.com/jwheintz/GPT/issues with details about your environment and the steps that led to the problem.
