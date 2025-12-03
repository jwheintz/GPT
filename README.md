# GPT Quiz Builder

A Tkinter desktop tool that uses OpenAI to generate multiple-choice quizzes, exports them to iSpring-compatible XLSX files, and can produce Gamma decks or truth-statement text files for instructors. The Windows-friendly `AutoQuizv5.1.pyw` launcher starts the GUI directly for double-click use.

## Status
- Single-user desktop utility; tested with Python 3.8–3.11. Requires a display for the GUI (Tkinter).

## Quick links
- Contributing: CONTRIBUTING.md
- Getting started: GETTING_STARTED.md
- Issues: https://github.com/jwheintz/GPT/issues

## Prerequisites
- Python ≥ 3.8 with Tkinter available (included in standard installers).
- `pip` for installing Python packages.
- An OpenAI API key (and optionally a Gamma API key) stored in `gptquizbuilder_config.json` via the GUI.

## Setup
```bash
git clone https://github.com/jwheintz/GPT.git
cd GPT
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install openai pandas requests
```

## Running the app
- **Windows (double-click):** launch `AutoQuizv5.1.pyw`. The first run will prompt for your OpenAI key; click **Save Settings** to persist it.
- **Command line (any OS):**
  ```bash
  python gpt_quiz_builder.py
  ```
- Provide a display when running on Linux/macOS (e.g., from a desktop session or with `DISPLAY` configured). The app will exit early with a clear message if no display is available.

## How to test quickly
- Run a bytecode smoke test (does not make network calls):
  ```bash
  python -m compileall gpt_quiz_builder.py AutoQuizv5.1.pyw
  ```
- Manual functional check:
  1. Start the GUI (`AutoQuizv5.1.pyw` or `python gpt_quiz_builder.py`).
  2. Enter your OpenAI API key and click **Save Settings**.
  3. Set an Area of Focus and a small question count (e.g., 2) and click **Generate Full Quiz**.
  4. Confirm an Excel file (default `full_quiz.xlsx`) is created and opens with 4-column options per question.
  5. (Optional) Click **Generate Truth Statements TXT** to create a summary text file.

## Troubleshooting
- If the GUI refuses to start, confirm you have a graphical session (Tkinter cannot render headless without X forwarding).
- If OpenAI calls fail, re-check that the API key is valid and the selected model (`gpt-4` or `gpt-3.5-turbo`) is available to your account.
- Gamma deck generation is optional; leave those fields blank if you do not use Gamma.
