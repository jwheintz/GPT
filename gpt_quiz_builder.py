#!/usr/bin/env python
"""Quiz Builder with ChatGPT, Gamma integration, and direct XLSX output.

v5.1 additions:
- Gamma API integration to turn the *last generated questions* or truth statements into a Gamma deck.
- Gamma API key, theme ID, folder ID, and template gammaId stored in gptquizbuilder_config.json.
- Non-blocking Gamma generation (background thread + polling, no GUI freeze).
- "Lock to Source Text" switch that makes the provided source text authoritative and disables vendor/deep research.
- Preserves v4 behavior: OpenAI-based question generation, iSpring-compatible XLSX, and truth-statement TXT.
"""

import json
import os
import re
import subprocess
import sys
import threading
import time
import webbrowser
from typing import Optional

# Auto-install missing dependencies (except tkinter, which is stdlib on normal installs)
REQUIRED_MODULES = ["openai", "pandas", "requests"]

for module in REQUIRED_MODULES:
    try:
        __import__(module)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk

import openai
import pandas as pd
import requests


HEADERS = [
    "Question Type",
    "Question Text",
    "Image",
    "Video",
    "Audio",
    "Answer 1",
    "Answer 2",
    "Answer 3",
    "Answer 4",
    "Answer 5",
    "Answer 6",
    "Answer 7",
    "Answer 8",
    "Answer 9",
    "Answer 10",
    "Correct Feedback",
    "Incorrect Feedback",
    "Points",
]

CONFIG_FILE = "gptquizbuilder_config.json"
GAMMA_BASE = "https://public-api.gamma.app/v1.0"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print("Failed to save config:", e)


class GPTQuizBuilder:
    """Tkinter GUI to generate fixed-schema XLSX quizzes via OpenAI and decks via Gamma."""

    # ----------------------------------------------------------
    # 34-Criterion Quality Rubric (constant on the class)
    # ----------------------------------------------------------
    QUALITY_RUBRIC_34 = """
You MUST obey the following quality criteria when generating the question:

1. Target the requested Bloom level and DOK level; do not drift into simpler recall if a higher level is requested.
2. Match the requested difficulty band (easy/medium/hard) by adjusting reasoning steps and distractor strength.
3. Use a single, clear stem that asks ONE question and includes all necessary information.
4. Avoid double negatives and tricky wording; no "Which is NOT uncommon…" constructions.
5. Avoid irrelevant or extraneous scenario details that increase cognitive load without testing anything.
6. Use neutral, inclusive language; avoid culture-specific references unless inherently part of the topic.
7. If scenario-based, give only as much context as needed (brief vs rich) for the scenario depth requested.
8. All answer options must be homogeneous in type and level of detail (e.g., all actions, all controls, all definitions).
9. Never use "All of the above" or "None of the above".
10. Provide exactly one best answer; in scenario-best questions, other options may be partly correct but less appropriate.
11. Make distractors plausible enough that a weak candidate might choose them, but clearly inferior for a strong candidate.
12. Base distractors on real misconceptions or common errors whenever possible.
13. Avoid silly, obviously wrong, or irrelevant distractors.
14. Ensure the question tests the intended concept, not reading tricks or obscure trivia.
15. For foundational facts, test essential vocabulary or "gatekeeping" facts that unlock higher-level reasoning.
16. For core concepts and challenger items, emphasize discrimination between strong and weak candidates.
17. Keep the question aligned with realistic exam objectives for the given domain.
18. Avoid near-duplicate items; assume this question sits in a larger bank and should not repeat trivial patterns.
19. Avoid bias and stereotypes; do not tie technical competence to demographic traits.
20. Avoid gratuitous trauma or emotionally charged content unless strictly necessary to the domain.
21. Use technical details that are realistic and standard for the domain (ports, protocols, frameworks, etc.).
22. Do NOT invent standards, tools, regulations, or crypto parameters that do not exist.
23. For scenario-best questions, it is acceptable that more than one option is partially correct, but only one should be clearly BEST or FIRST.
24. Match the requested question style (definition, scenario-best-action, troubleshooting, calculation).
25. When explanations are requested, first explain why the correct option is correct in terms of principles and scenario details.
26. Then, for each distractor, explain why it might be tempting based on a misconception, and why it is actually wrong or inferior.
27. When metacognitive support is requested, show the perspective shift: how a mistaken viewpoint leads to the wrong option and how to correct it.
28. Include a brief transfer insight where requested: how this reasoning pattern applies to similar future questions.
29. Ensure formatting: option texts must NOT include labels like "A)", "B)", etc.; keep options as clean answer phrases only, and use the output schema to indicate which option is keyed.
30. Avoid contradictions between the stem, options, and explanation; everything must be internally consistent.
31. Use field-correct terminology for the specified domain and avoid outdated or misleading usage unless explicitly tested.
32. Do not overload the stem with multiple separate tasks; keep it to one main decision or concept.
33. Keep numeric details (ports, subnets, risk formulas) correct and consistent with widely accepted references.
34. Always err on the side of correctness and clarity over cleverness; prioritize a high-quality exam item over creativity.
""".strip()

    # ----------------------------------------------------------
    # Quality dial block (Bloom / DOK / scenario depth / metacog)
    # ----------------------------------------------------------
    def build_quality_dials_block(
        self,
        difficulty: str,
        bloom_band: str,
        question_style: str,
        metacog_mode: str = "full",
    ) -> str:
        """Map simple dials into a tuned quality block."""

        difficulty = (difficulty or "medium").lower().strip()
        bloom_band = (bloom_band or "core").lower().strip()
        question_style = (question_style or "definition").lower().strip()
        metacog_mode = (metacog_mode or "full").lower().strip()

        # Bloom + DOK mapping
        if bloom_band == "foundational":
            bloom = "Remember/Understand"
            dok = 1 if difficulty == "easy" else 2
        elif bloom_band == "core":
            bloom = "Apply" if difficulty != "hard" else "Analyze"
            dok = 2 if difficulty != "hard" else 3
        else:  # "decision"
            bloom = "Analyze/Evaluate"
            dok = 2 if difficulty == "medium" else 3

        # Scenario depth
        if question_style in ("scenario", "scenario-best", "troubleshooting"):
            if difficulty == "hard":
                scenario_depth = "rich (multi-step, realistic scenario)"
            elif difficulty == "medium":
                scenario_depth = "brief (short, focused scenario)"
            else:
                scenario_depth = "minimal (only one or two sentences of context)"
        else:
            scenario_depth = "minimal (no unnecessary scenario text)"

        # Distractor strength
        if difficulty == "easy":
            distractors = "moderately plausible but clearly wrong for a prepared student"
        elif difficulty == "medium":
            distractors = "plausible and often based on common misconceptions"
        else:
            distractors = "highly plausible; all options realistic, only one clearly best"

        # Explanation / metacognition
        if metacog_mode == "none":
            explanation = (
                "Provide only a very short explanation for the best answer; "
                "do not include separate distractor rationales."
            )
        elif metacog_mode == "light":
            explanation = (
                "Provide brief rationales for the best answer and one short sentence for why each distractor is inferior."
            )
        else:  # "full"
            explanation = (
                "Provide detailed rationales: first explain why the keyed option is the best available answer; then, for EACH distractor, "
                "explain (1) why it might be tempting based on a misconception, and (2) why it is actually wrong or inferior. "
                "Include a brief transfer insight on how to avoid this mistake in similar questions."
            )

        lines = [
            f"- Target Bloom level: {bloom}.",
            f"- Target Depth of Knowledge (DOK): {dok}.",
            f"- Scenario depth: {scenario_depth}.",
            f"- Target distractor strength: {distractors}.",
            f"- Metacognitive / explanation mode: {explanation}",
            "",
            "MANDATORY QUALITY RUBRIC:",
            self.QUALITY_RUBRIC_34,
        ]

        return "\n".join(lines)

    # ----------------------------------------------------------
    # Optional: build a single-question JSON prompt (for other tools)
    # ----------------------------------------------------------
    def build_question_prompt(
        self,
        topic: str,
        difficulty: str,
        question_style: str,
        bloom_band: str = "core",
        metacog_mode: str = "full",
        domain: str = "information security",
    ) -> str:
        """Build a single-question MCQ prompt that returns a JSON object."""

        quality_block = self.build_quality_dials_block(
            difficulty=difficulty,
            bloom_band=bloom_band,
            question_style=question_style,
            metacog_mode=metacog_mode,
        )

        prompt = f"""
You are an expert exam item writer for the domain of {domain}.

Generate ONE multiple-choice question (MCQ) with the following parameters:

- Topic: {topic}
- Difficulty: {difficulty}
- Question style: {question_style}

QUALITY DIALS AND RUBRIC:
{quality_block}

OUTPUT FORMAT (VERY IMPORTANT):
Return ONLY a JSON object with the structure:
{{
  "stem": "the question stem as a single clear sentence or short paragraph",
  "options": [
    {{"label": "A", "text": "option A text", "is_correct": false}},
    {{"label": "B", "text": "option B text", "is_correct": false}},
    {{"label": "C", "text": "option C text", "is_correct": false}},
    {{"label": "D", "text": "option D text", "is_correct": false}}
  ],
  "explanation": "an explanation string consistent with the explanation/metacognition instructions above"
}}

Do NOT include any extra commentary, prose, or markdown outside the JSON object.
""".strip()

        return prompt

    # ----------------------------------------------------------
    # GUI init
    # ----------------------------------------------------------
    def __init__(self, master):
        self.api_key = None
        self.selected_model = tk.StringVar(value="gpt-4")
        self.master = master
        self.master.title("GPT Quiz Builder")
        self.status_var = tk.StringVar(value="Waiting for input...")

        # Config for Gamma, etc.
        self.config = load_config()

        # Holds last generated questions and truth statements
        self.last_questions = []
        self.last_truth_statements = []

        # Logging panel
        self.log_frame = tk.Frame(master)
        self.log_frame.grid(row=98, column=0, columnspan=4, padx=5, pady=(10, 0))
        self.log_text = tk.Text(self.log_frame, height=10, width=110, bg="#f5f5f5", fg="black")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.log_scroll = tk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.log_scroll.set)

        self.splash = tk.Label(master, textvariable=self.status_var, font=("Segoe UI", 10, "italic"), fg="blue")
        self.splash.grid(row=99, column=0, columnspan=4, pady=(10, 0), sticky="w")

        self.questions = []

        # Topic + count
        tk.Label(master, text="Area of Focus:").grid(row=0, column=0, sticky="e")
        self.topic = tk.Entry(master, width=60)
        self.topic.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        tk.Label(master, text="# of Questions:").grid(row=1, column=0, sticky="e")
        self.qcount = tk.Entry(master, width=10)
        self.qcount.grid(row=1, column=1, sticky="w")

        # Bloom levels
        tk.Label(master, text="Bloom Levels:").grid(row=2, column=0, sticky="ne")
        self.bloom_levels = {
            "Remember": tk.BooleanVar(),
            "Understand": tk.BooleanVar(),
            "Apply": tk.BooleanVar(),
            "Analyze": tk.BooleanVar(),
            "Evaluate": tk.BooleanVar(),
            "Create": tk.BooleanVar(),
        }
        self.bloom_scales = {}
        for i, (level, var) in enumerate(self.bloom_levels.items()):
            chk = tk.Checkbutton(
                master,
                text=level,
                variable=var,
                command=lambda lvl=level: self.on_bloom_check_change(lvl),
            )
            chk.grid(row=2 + i, column=1, sticky="w")
            scale = tk.Scale(
                master,
                from_=0,
                to=100,
                orient="horizontal",
                length=200,
                state="disabled",
                command=lambda val, lvl=level: self.on_bloom_slider_change(lvl, val),
            )
            scale.grid(row=2 + i, column=2, sticky="w")
            self.bloom_scales[level] = scale

        # Optional source text
        tk.Label(master, text="Source Text (optional):").grid(row=8, column=0, sticky="ne")
        self.source_text = tk.Text(master, height=5, width=60)
        self.source_text.grid(row=8, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        # Deep research + vendor lock + lock-to-source
        self.deep_research = tk.BooleanVar()
        self.deep_research_check = tk.Checkbutton(
            master, text="Enable Deep Research", variable=self.deep_research
        )
        self.deep_research_check.grid(row=9, column=1, sticky="w")

        self.vendor_locked = tk.BooleanVar()
        self.vendor_check = tk.Checkbutton(
            master,
            text="Strict Vendor Adherence",
            variable=self.vendor_locked,
            command=self.toggle_vendor,
        )
        self.vendor_check.grid(row=10, column=1, sticky="w")

        tk.Label(master, text="Vendor (if locked):").grid(row=11, column=0, sticky="e")
        self.vendor_entry = tk.Entry(master, width=30, state="disabled")
        self.vendor_entry.grid(row=11, column=1, sticky="w")

        self.lock_to_source = tk.BooleanVar(value=bool(self.config.get("lock_to_source", False)))
        self.lock_to_source_check = tk.Checkbutton(
            master,
            text="Lock to Source Text (authoritative)",
            variable=self.lock_to_source,
            command=self.on_lock_to_source_toggle,
        )
        self.lock_to_source_check.grid(row=9, column=2, sticky="w")

        # Buttons
        tk.Button(master, text="Generate Full Quiz", command=self.generate_quiz).grid(row=12, column=0, pady=10, sticky="w")

        # Model choice
        tk.Label(master, text="OpenAI Model:").grid(row=13, column=0, sticky="e")
        model_menu = tk.OptionMenu(master, self.selected_model, "gpt-4", "gpt-3.5-turbo")
        model_menu.grid(row=13, column=1, sticky="w")

        # Output filename
        tk.Label(master, text="Output Filename:").grid(row=14, column=0, sticky="e")
        self.output_file = tk.Entry(master, width=30)
        self.output_file.insert(0, "full_quiz.xlsx")
        self.output_file.grid(row=14, column=1, sticky="w")

        # Progress bar
        self.progress = ttk.Progressbar(master, orient="horizontal", length=500, mode="determinate")
        style = ttk.Style()
        style.theme_use("default")
        style.configure("work.Horizontal.TProgressbar", troughcolor="#f0f0f0", background="#0078D7")
        style.configure("done.Horizontal.TProgressbar", troughcolor="#f0f0f0", background="green")
        style.configure("error.Horizontal.TProgressbar", troughcolor="#f0f0f0", background="red")
        self.progress.configure(style="work.Horizontal.TProgressbar")
        self.progress.grid(row=15, column=0, columnspan=4, pady=(5, 5))

        # File helpers
        tk.Button(master, text="Open Output File", command=self.open_output).grid(row=16, column=0, pady=(5, 0), sticky="w")
        tk.Button(
            master,
            text="Generate Truth Statements TXT",
            command=self.generate_truth_statements,
        ).grid(row=16, column=1, pady=(5, 0), sticky="w")

        # Gamma integration controls
        tk.Label(master, text="Gamma API Key:").grid(row=17, column=0, sticky="e")
        self.gamma_key_var = tk.StringVar(value=self.config.get("gamma_key", ""))
        self.gamma_key_entry = tk.Entry(master, width=40, textvariable=self.gamma_key_var, show="*")
        self.gamma_key_entry.grid(row=17, column=1, columnspan=2, sticky="w")

        tk.Button(master, text="Save Settings", command=self.save_settings).grid(row=17, column=3, sticky="w")

        tk.Label(master, text="Gamma Theme ID (optional):").grid(row=18, column=0, sticky="e")
        self.gamma_theme_var = tk.StringVar(value=self.config.get("gamma_theme_id", ""))
        tk.Entry(master, width=30, textvariable=self.gamma_theme_var).grid(row=18, column=1, sticky="w")

        tk.Label(master, text="Gamma Folder ID (optional):").grid(row=19, column=0, sticky="e")
        self.gamma_folder_var = tk.StringVar(value=self.config.get("gamma_folder_id", ""))
        tk.Entry(master, width=30, textvariable=self.gamma_folder_var).grid(row=19, column=1, sticky="w")

        tk.Label(master, text="Template gammaId (optional):").grid(row=20, column=0, sticky="e")
        self.gamma_template_var = tk.StringVar(value=self.config.get("gamma_template_id", ""))
        tk.Entry(master, width=30, textvariable=self.gamma_template_var).grid(row=20, column=1, sticky="w")

        # Gamma source choice
        tk.Label(master, text="Gamma Source:").grid(row=21, column=0, sticky="e")
        self.gamma_source_var = tk.StringVar(value="questions")  # "questions" or "truth"

        tk.Radiobutton(
            master,
            text="Quiz questions",
            variable=self.gamma_source_var,
            value="questions",
        ).grid(row=21, column=1, sticky="w")

        tk.Radiobutton(
            master,
            text="Truth statements",
            variable=self.gamma_source_var,
            value="truth",
        ).grid(row=21, column=2, sticky="w")

        self.gamma_button = tk.Button(
            master,
            text="Generate Gamma Deck from Current Source",
            command=self.on_generate_gamma_deck,
        )
        self.gamma_button.grid(row=22, column=0, columnspan=2, pady=(5, 5), sticky="w")

        self.master.update()
        self.on_lock_to_source_toggle()
        self.load_api_key()

    # ----------------------- Utility Methods -----------------------

    def log(self, msg: str):
        try:
            self.log_text.insert(tk.END, str(msg) + "\n")
            self.log_text.see(tk.END)
        except Exception as e:
            print("[LOG ERROR]", e)

    def open_output(self):
        filename = self.output_file.get().strip() or "full_quiz.xlsx"
        if os.path.exists(filename):
            try:
                os.startfile(filename)
            except Exception as e:
                messagebox.showerror("Open Error", f"Could not open {filename}: {e}")
        else:
            messagebox.showwarning("File Not Found", f"Could not find: {filename}")

    def toggle_vendor(self):
        if self.lock_to_source.get():
            self.vendor_entry.config(state="disabled")
            return
        self.vendor_entry.config(state="normal" if self.vendor_locked.get() else "disabled")

    def on_lock_to_source_toggle(self):
        locked = self.lock_to_source.get()
        if locked:
            # Disable vendor adherence
            self.vendor_locked.set(False)
            if hasattr(self, "vendor_check"):
                self.vendor_check.config(state="disabled")
            self.vendor_entry.config(state="disabled")
            # Disable deep research
            self.deep_research.set(False)
            if hasattr(self, "deep_research_check"):
                self.deep_research_check.config(state="disabled")
        else:
            if hasattr(self, "vendor_check"):
                self.vendor_check.config(state="normal")
            if hasattr(self, "deep_research_check"):
                self.deep_research_check.config(state="normal")
            self.vendor_entry.config(state="normal" if self.vendor_locked.get() else "disabled")

    def get_bloom_weights(self):
        """Return (weights dict, total_weight) based on enabled Bloom sliders."""
        weights = {}
        total_weight = 0
        for level, var in self.bloom_levels.items():
            if var.get():
                scale = self.bloom_scales.get(level)
                if scale is not None:
                    val = int(scale.get())
                    if val > 0:
                        weights[level] = val
                        total_weight += val
        return weights, total_weight

    def on_bloom_slider_change(self, level, _value):
        """Enforce a global cap of 100 across all enabled Bloom sliders."""
        total = 0
        for lvl, var in self.bloom_levels.items():
            if var.get():
                scale = self.bloom_scales.get(lvl)
                if scale is not None:
                    total += int(scale.get())

        if total > 100:
            overflow = total - 100
            scale = self.bloom_scales.get(level)
            if scale is not None:
                current = int(scale.get())
                adjusted = max(0, current - overflow)
                if adjusted != current:
                    scale.set(adjusted)

    def on_bloom_check_change(self, level):
        """Enable/disable the associated slider when a Bloom level is toggled."""
        scale = self.bloom_scales.get(level)
        if not scale:
            return
        if self.bloom_levels[level].get():
            scale.configure(state="normal")
        else:
            scale.configure(state="disabled")
            scale.set(0)
            self.on_bloom_slider_change(level, 0)

    def save_settings(self):
        """Persist Gamma config (and anything else you want) to JSON."""
        self.config["gamma_key"] = self.gamma_key_var.get().strip()
        self.config["gamma_theme_id"] = self.gamma_theme_var.get().strip()
        self.config["gamma_folder_id"] = self.gamma_folder_var.get().strip()
        self.config["gamma_template_id"] = self.gamma_template_var.get().strip()
        self.config["lock_to_source"] = bool(self.lock_to_source.get())
        if self.api_key:
            self.config["openai_api_key"] = self.api_key
        save_config(self.config)
        self.log("Settings saved to gptquizbuilder_config.json")

    # ----------------------- Prompt & API -----------------------
    def build_prompt(self, count: int) -> str:
        topic = self.topic.get().strip()
        lock_to_source = self.lock_to_source.get()

        # Vendor only applies when NOT locked to source
        vendor = self.vendor_entry.get().strip() if (self.vendor_locked.get() and not lock_to_source) else None
        source = self.source_text.get("1.0", tk.END).strip()
        research = self.deep_research.get()

        # If lock is enabled but no source text, warn and behave as if unlocked
        if lock_to_source and not source:
            self.log("Lock to Source is enabled but no source text was provided; proceeding without lock.")
            lock_to_source = False

        weights, total_weight = self.get_bloom_weights()

        prompt = f"Generate {count} multiple-choice questions on {topic}."

        # Bloom distribution hint
        if weights and total_weight > 0 and count > 0:
            raw_counts = {}
            remainders = []
            for level, w in weights.items():
                exact = w * count / total_weight
                base = int(exact)
                raw_counts[level] = base
                remainders.append((exact - base, level))

            current_sum = sum(raw_counts.values())
            diff = count - current_sum

            if diff > 0:
                remainders.sort(reverse=True)
                idx = 0
                while diff > 0 and idx < len(remainders):
                    lvl = remainders[idx][1]
                    raw_counts[lvl] += 1
                    diff -= 1
                    idx += 1
            elif diff < 0:
                remainders.sort()
                idx = 0
                while diff < 0 and idx < len(remainders):
                    lvl = remainders[idx][1]
                    if raw_counts[lvl] > 0:
                        raw_counts[lvl] -= 1
                        diff += 1
                    idx += 1

            nonzero = {lvl: c for lvl, c in raw_counts.items() if c > 0}
            if nonzero:
                prompt += " Use the following approximate Bloom distribution across these questions: "
                parts = [f"{lvl}: {c}" for lvl, c in nonzero.items()]
                prompt += "; ".join(parts) + ". "
                prompt += (
                    "For each question, include a \"bloom\" field set to one of these Bloom levels: "
                    + ", ".join(nonzero.keys())
                    + ". "
                )

        if vendor:
            prompt += f" Use terminology and structure consistent with {vendor} materials."

        if source:
            if lock_to_source:
                prompt += (
                    "\n\nYou MUST treat the following source text as your ONLY authoritative corpus. "
                    "Do NOT introduce facts, terminology, examples, or numbers that cannot be directly justified from it. "
                    "If the source text is ambiguous or incomplete for a question, say so briefly in the explanation "
                    "rather than inventing details. Use this source text exclusively when writing stems, options, and explanations.\n"
                    "SOURCE_TEXT:\n" + source + "\n"
                )
            else:
                prompt += f" Base questions primarily on this source text: {source}"

        if research and not lock_to_source:
            prompt += " Perform deep research to ensure accuracy."

        # Quality dials for the batch (coarse defaults)
        difficulty_dial = "medium"
        bloom_band = "core"
        question_style = "scenario"
        metacog_mode = "full"

        quality_block = self.build_quality_dials_block(
            difficulty=difficulty_dial,
            bloom_band=bloom_band,
            question_style=question_style,
            metacog_mode=metacog_mode,
        )

        prompt += "\n\nQUALITY DIALS AND RUBRIC:\n" + quality_block + "\n\n"
        prompt += (
            "Stems should, when appropriate, explicitly ask for the best/most appropriate/most effective option "
            "rather than simply 'which is correct'. In explanations and feedback, prefer wording like 'best available answer' "
            "over absolute 'correct/incorrect' language.\n\n"
        )

        # JSON schema requirement
        prompt += (
            " Each question must include exactly 4 answer options, with 1 best answer (the keyed/scored option) "
            "and 3 plausible distractors. Return JSON only, in this exact shape: "
            "[{\"question\": str, \"options\": [str, str, str, str], \"correct\": str, "
            "\"feedback_correct\": str, \"feedback_incorrect\": str, \"bloom\": str}]."
        )

        return prompt

    def call_openai(self, prompt: str) -> Optional[str]:
        openai.api_key = self.api_key
        try:
            response = openai.chat.completions.create(
                model=self.selected_model.get(),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            content = response.choices[0].message.content
            self.log("API call succeeded. Raw response (truncated to 1000 chars):")
            self.log(content[:1000] + ("..." if len(content) > 1000 else ""))
            return content
        except Exception as e:
            self.log("API Error: " + str(e))
            messagebox.showerror("API Error", str(e))
            return None

    def parse_questions(self, response: str):
        try:
            parsed = json.loads(response)
            if not isinstance(parsed, list):
                self.log("Parsing error: Top-level JSON is not a list.")
                return []
            if not parsed:
                self.log("Warning: No questions parsed from API response.")
            return parsed
        except Exception as e:
            self.log("Parsing error: " + str(e))
            self.log("Raw response was: " + response)
            messagebox.showerror("Parsing Error", str(e))
            return []

    def write_to_csv(self, questions):
        """Convert list[dict] to fixed-schema XLSX.
        Ensures exactly 18 columns per row as required by HEADERS.
        """
        if not questions:
            self.log("write_to_csv called with empty question list; nothing to write.")
            return

        def _strip_option_label(text: str) -> str:
            """Remove leading A)/B)/C)/D) style labels from an option, if present."""
            if not isinstance(text, str):
                return str(text)
            return re.sub(r"^\s*[A-D]\s*[\)\.\:\-]\s*", "", text).strip()

        filename = self.output_file.get().strip() or "full_quiz.xlsx"
        rows = []

        for idx, q in enumerate(questions, start=1):
            question = q.get("question") or q.get("Question")
            raw_options = q.get("options") or []
            raw_correct = q.get("correct") or q.get("CorrectAnswer")

            options = [_strip_option_label(opt) for opt in raw_options]
            correct = _strip_option_label(raw_correct) if raw_correct else None

            if not question or not correct or not options:
                self.log(f"Skipping question {idx}: missing question text, options, or keyed best answer.")
                continue

            if correct not in options:
                options = [correct] + [opt for opt in options if opt != correct]

            distractors = [opt for opt in options if opt != correct]
            if len(distractors) < 3:
                pad_needed = 3 - len(distractors)
                distractors += [f"Option {chr(ord('A') + i)}" for i in range(pad_needed)]
            distractors = distractors[:3]

            feedback_correct = (
                q.get("correct_feedback")
                or q.get("feedback_correct")
                or q.get("CorrectFeedback")
                or "This is the best available answer for this question."
            )
            feedback_incorrect = (
                q.get("incorrect_feedback")
                or q.get("feedback_incorrect")
                or q.get("IncorrectFeedback")
                or "Review the scenario and reasoning to identify the best available answer."
            )

            answers = ["*" + correct] + distractors
            if len(answers) < 10:
                answers += [""] * (10 - len(answers))

            row = [
                q.get("type", "MC"),
                question,
                "",
                "",
                "",
            ] + answers + [
                feedback_correct,
                feedback_incorrect,
                q.get("points", 1),
            ]

            if len(row) != len(HEADERS):
                self.log(f"Row length mismatch for question {idx}: got {len(row)}, expected {len(HEADERS)}. Skipping.")
                continue

            rows.append(row)

        if not rows:
            self.log("No valid rows to write after processing questions.")
            return

        df = pd.DataFrame(rows, columns=HEADERS)
        df.to_excel(filename, index=False)
        self.log(f"Wrote {len(rows)} questions to {filename}")

    def generate_quiz(self):
        self.log("[Full Quiz Generation Started]")
        try:
            total = int(self.qcount.get())
        except Exception:
            messagebox.showerror("Input Error", "Enter a valid number of questions.")
            return

        if total < 1 or total > 250:
            messagebox.showerror("Input Error", "Number of questions must be between 1 and 250.")
            return

        self.progress.configure(style="work.Horizontal.TProgressbar")
        self.progress["value"] = 0
        self.progress["maximum"] = total

        all_questions = []
        written = 0

        for i in range(0, total, 10):
            chunk = min(10, total - i)
            self.status_var.set(f"Generating questions {i + 1} to {i + chunk}...")
            self.master.update_idletasks()

            prompt = self.build_prompt(chunk)
            self.log(f"[Model: {self.selected_model.get()}] Prompt submitted:")
            self.log(prompt[:500] + ("..." if len(prompt) > 500 else ""))

            response = self.call_openai(prompt)
            if not response:
                self.log("No response from API for this chunk; skipping.")
                continue

            qchunk = self.parse_questions(response)
            if not qchunk:
                self.log("Parsed zero questions from this chunk; skipping.")
                continue

            for q in qchunk:
                all_questions.append(q)
                written += 1
                self.progress["value"] = min(written, total)
                self.master.update_idletasks()

            self.log(f"Collected {written}/{total} questions so far")

        if not all_questions:
            self.status_var.set("No questions generated. Check logs.")
            self.progress["value"] = 0
            self.progress.configure(style="error.Horizontal.TProgressbar")
            self.log("[Quiz Generation Finished With 0 Questions]")
            messagebox.showwarning("Quiz Incomplete", "No questions were generated.")
            return

        self.last_questions = all_questions

        self.write_to_csv(all_questions)

        self.progress["value"] = total
        self.progress.configure(style="done.Horizontal.TProgressbar")
        self.status_var.set("Quiz completed and saved. Check the Excel file.")
        self.log("[Quiz Generation Complete]")
        messagebox.showinfo("Quiz Complete", f"{len(all_questions)} questions exported to Excel.")

    def generate_truth_statements(self):
        """Generate a TXT file of per-question 'truth statements' for Gamma or other uses."""
        if not self.last_questions:
            messagebox.showwarning(
                "No Questions",
                "No questions are cached. Generate a full quiz first.",
            )
            self.log("Truth statement generation aborted: last_questions is empty.")
            return

        base_name = self.output_file.get().strip() or "full_quiz.xlsx"
        root, _ext = os.path.splitext(base_name)
        txt_file = root + "_truth.txt"

        payload = [
            {
                "question": q.get("question") or q.get("Question"),
                "correct": q.get("correct") or q.get("CorrectAnswer"),
                "feedback_correct": q.get("correct_feedback")
                or q.get("feedback_correct")
                or q.get("CorrectFeedback"),
            }
            for q in self.last_questions
        ]

        payload = [p for p in payload if p["question"] and p["correct"]]
        if not payload:
            messagebox.showwarning(
                "No Usable Questions",
                "Cached questions are missing question text or keyed answers.",
            )
            self.log("Truth statement generation aborted: payload empty after filtering.")
            return

        prompt = (
            "You are preparing 'truth slides' for an instructor's deck. "
            "You are given a JSON array of multiple-choice questions, each with a stem, the keyed best answer, "
            "and sometimes a brief correct-feedback note. For EACH question, produce exactly ONE 'truth statement' "
            "in medium detail: a single sentence or short paragraph that states the key idea a student should remember. "
            "Do NOT mention answer letters or options; just express the core concept as a declarative statement. "
            "Number the statements Q1:, Q2:, etc., in the same order as the input questions.\n\n"
        )

        payload_json = json.dumps(payload, ensure_ascii=False)
        full_prompt = prompt + "QUESTIONS_JSON:\n" + payload_json

        self.status_var.set("Generating truth statements TXT...")
        self.master.update_idletasks()

        result = self.call_openai(full_prompt)
        if not result:
            self.status_var.set("Truth statement generation failed. See log.")
            return

        truth_lines = []
        for line in result.splitlines():
            line = line.strip()
            if not line:
                continue
            m = re.match(r"^Q\d+\s*[:\-]\s*(.+)$", line)
            if m:
                truth_lines.append(m.group(1).strip())
            else:
                truth_lines.append(line)

        self.last_truth_statements = truth_lines
        self.log(f"Cached {len(self.last_truth_statements)} truth statements in memory.")

        try:
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(result)
            self.log(f"Truth statements written to {txt_file}")
            self.status_var.set("Truth statements TXT created.")
            messagebox.showinfo(
                "Truth Statements Ready",
                f"Truth statements have been written to:\n{txt_file}",
            )
        except Exception as e:
            self.log("Failed to write truth TXT: " + str(e))
            messagebox.showerror("File Error", f"Could not write truth TXT: {e}")

    # ----------------------- Gamma integration -----------------------

    def build_gamma_payload_from_questions(self):
        """Build a Gamma /generations payload from the cached questions."""
        if not self.last_questions:
            raise ValueError("No cached questions. Generate a quiz first.")

        subset = self.last_questions[:10]
        blocks = []

        for idx, q in enumerate(subset, start=1):
            question = q.get("question") or q.get("Question")
            correct = q.get("correct") or q.get("CorrectAnswer")
            fb = (
                q.get("correct_feedback")
                or q.get("feedback_correct")
                or q.get("CorrectFeedback")
                or ""
            )
            if not question or not correct:
                continue

            block = (
                f"Concept: CET/GRC exam prep concept Q{idx}\n"
                f"Question: {question}\n"
                f"Keyed best answer: {correct}\n"
                f"Key idea for students: {fb or 'Explain succinctly why this answer is best and what concept it represents.'}\n"
            )
            blocks.append(block)

        if not blocks:
            raise ValueError("No usable questions for Gamma deck generation.")

        return self._assemble_gamma_payload("\n\n".join(blocks), title="Quiz-derived concepts")

    def build_gamma_payload_from_truth(self):
        if not self.last_truth_statements:
            raise ValueError("No cached truth statements. Generate them first.")

        lines = []
        for idx, statement in enumerate(self.last_truth_statements, start=1):
            lines.append(f"Truth {idx}: {statement}")

        return self._assemble_gamma_payload("\n".join(lines), title="Truth statements deck")

    def _assemble_gamma_payload(self, body_text: str, title: str):
        payload: dict[str, object] = {
            "title": title,
            "content": body_text,
        }

        theme_id = self.gamma_theme_var.get().strip()
        folder_id = self.gamma_folder_var.get().strip()
        template_id = self.gamma_template_var.get().strip()

        if theme_id:
            payload["themeId"] = theme_id
        if folder_id:
            payload["folderId"] = folder_id
        if template_id:
            payload["template"] = {"gammaId": template_id}

        return payload

    def on_generate_gamma_deck(self):
        gamma_key = self.gamma_key_var.get().strip()
        if not gamma_key:
            messagebox.showerror("Gamma Key Missing", "Provide a Gamma API key before generating a deck.")
            return

        source_choice = self.gamma_source_var.get()
        try:
            if source_choice == "truth":
                payload = self.build_gamma_payload_from_truth()
            else:
                payload = self.build_gamma_payload_from_questions()
        except ValueError as exc:
            messagebox.showwarning("Cannot Generate Gamma Deck", str(exc))
            self.log(str(exc))
            return

        thread = threading.Thread(
            target=self._gamma_worker,
            args=(gamma_key, payload),
            daemon=True,
        )
        thread.start()
        self.status_var.set("Gamma deck generation started in background...")
        self.log("Gamma generation submitted in background thread.")

    def _gamma_worker(self, gamma_key: str, payload: dict):
        try:
            generation_id = self._start_gamma_generation(gamma_key, payload)
            if not generation_id:
                self.status_var.set("Gamma generation failed to start.")
                return
            self.status_var.set("Gamma generation in progress (polling)...")
            url = self._poll_gamma_generation(gamma_key, generation_id)
            if url:
                self.status_var.set("Gamma deck ready; opening in browser.")
                self.log(f"Gamma share URL: {url}")
                try:
                    webbrowser.open(url)
                except Exception as exc:  # pragma: no cover - best effort
                    self.log(f"Failed to open browser automatically: {exc}")
                    messagebox.showinfo("Gamma Deck Ready", f"Open this link manually:\n{url}")
            else:
                self.status_var.set("Gamma generation did not provide a share URL.")
        except Exception as exc:  # pragma: no cover - defensive
            self.log(f"Gamma generation error: {exc}")
            messagebox.showerror("Gamma Error", str(exc))

    def _start_gamma_generation(self, gamma_key: str, payload: dict) -> Optional[str]:
        headers = {
            "Authorization": f"Bearer {gamma_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(f"{GAMMA_BASE}/generations", headers=headers, json=payload, timeout=30)
        except Exception as exc:
            self.log(f"Gamma request failed to send: {exc}")
            return None

        if resp.status_code != 200:
            self.log(f"Gamma generation failed: {resp.status_code} {resp.text}")
            return None

        try:
            data = resp.json()
        except Exception as exc:  # pragma: no cover - unlikely
            self.log(f"Gamma response parse error: {exc}")
            return None

        generation_id = data.get("generationId") or data.get("id")
        if not generation_id:
            self.log("Gamma response missing generation ID.")
            return None

        self.log(f"Gamma generation started with ID: {generation_id}")
        return generation_id

    def _poll_gamma_generation(self, gamma_key: str, generation_id: str) -> Optional[str]:
        headers = {
            "Authorization": f"Bearer {gamma_key}",
        }
        for _ in range(30):
            try:
                resp = requests.get(f"{GAMMA_BASE}/generations/{generation_id}", headers=headers, timeout=20)
            except Exception as exc:
                self.log(f"Gamma polling error: {exc}")
                time.sleep(3)
                continue

            if resp.status_code != 200:
                self.log(f"Gamma polling status {resp.status_code}: {resp.text}")
                time.sleep(3)
                continue

            try:
                data = resp.json()
            except Exception:
                time.sleep(3)
                continue

            status = data.get("status") or data.get("state")
            share_url = data.get("shareUrl") or data.get("url")

            self.log(f"Gamma status: {status or 'unknown'}")
            if share_url:
                return share_url
            if status in {"failed", "error"}:
                raise RuntimeError(f"Gamma generation failed: {data}")
            if status == "completed" and not share_url:
                # Completed but no URL yet; keep polling briefly
                time.sleep(2)
            else:
                time.sleep(3)

        self.log("Gamma polling timed out without a share URL.")
        return None

    # ----------------------- API Key helpers -----------------------

    def load_api_key(self):
        env_key = os.environ.get("OPENAI_API_KEY")
        config_key = self.config.get("openai_api_key")
        self.api_key = env_key or config_key
        if self.api_key:
            return

        api_key = simpledialog.askstring(
            "OpenAI API Key",
            "Enter your OpenAI API key (will be saved locally):",
            show="*",
        )
        if api_key:
            self.api_key = api_key.strip()
            self.config["openai_api_key"] = self.api_key
            save_config(self.config)
        else:
            messagebox.showwarning(
                "API Key Required",
                "You must provide an OpenAI API key to generate questions.",
            )


# ----------------------- Entrypoint -----------------------

def main():
    try:
        root = tk.Tk()
    except tk.TclError as e:
        message = (
            "GUI could not be initialized because no display is available. "
            "Run this script in an environment with an X11/GUI display (or set $DISPLAY) to launch the Tkinter interface."
        )
        print(message)
        print("Underlying error:", e)
        sys.exit(1)

    app = GPTQuizBuilder(root)
    root.mainloop()


if __name__ == "__main__":
    main()
