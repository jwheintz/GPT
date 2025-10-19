# Concept Pulse

Concept Pulse is a desktop spaced-repetition program focused on long term retention of certification and domain-specific concepts. Create flash cards, tag them by difficulty, and track recall performance over weeks and months using a simple adaptive review queue.

## Status

Early preview – the core features for adding cards, reviewing material, and tracking success rates are implemented.

## Features

* Guided review flow with "Again", "Hard", "Good", and "Easy" ratings inspired by SM-2.
* Difficulty and recall tagging with automatic success-rate tracking for each card.
* Domain filtering to focus on the topics that matter for your current certification path.
* SQLite-backed storage saved in `data/cards.db` for durability.

## Requirements

* Python 3.9+
* Tkinter (bundled with the standard Python installer on Windows, macOS, and most Linux distributions)

Optional but recommended:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

## Running the application

```bash
python -m app.main
```

The first launch creates a `data/cards.db` file. Add new cards from the **Manage cards** tab, then work through the due queue under **Review queue**.

## Development notes

Static compilation checks:

```bash
python -m compileall app
```

## Getting help

Please open an issue at https://github.com/jwheintz/GPT/issues with details about your environment and the steps that led to the problem.
