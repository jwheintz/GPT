"""GUI application entry point for the spaced repetition tool."""
from __future__ import annotations

import tkinter as tk
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import ttk, messagebox
from typing import Optional

from .database import Card, DatabaseManager
from .scheduler import Quality, ReviewResult, schedule_review


class SpacedRepetitionApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Concept Pulse - Spaced Repetition")
        self.root.geometry("960x640")

        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        self.db = DatabaseManager(data_dir / "cards.db")

        self.current_card: Optional[Card] = None
        self.answer_visible = False
        self.domain_filter = tk.StringVar(value="All domains")
        self.status_var = tk.StringVar()
        self.editing_card_id: Optional[int] = None

        self._build_ui()
        self._refresh_domains()
        self._load_due_cards()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # UI construction helpers
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        review_frame = ttk.Frame(notebook)
        manage_frame = ttk.Frame(notebook)

        notebook.add(review_frame, text="Review queue")
        notebook.add(manage_frame, text="Manage cards")

        self._build_review_tab(review_frame)
        self._build_manage_tab(manage_frame)

        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _build_review_tab(self, container: ttk.Frame) -> None:
        top_bar = ttk.Frame(container)
        top_bar.pack(fill=tk.X, pady=5)

        ttk.Label(top_bar, text="Domain filter:").pack(side=tk.LEFT)
        domain_menu = ttk.OptionMenu(
            top_bar,
            self.domain_filter,
            self.domain_filter.get(),
            command=lambda _: self._load_due_cards(),
        )
        domain_menu.pack(side=tk.LEFT, padx=5)
        self.domain_menu = domain_menu

        ttk.Button(top_bar, text="Refresh", command=self._load_due_cards).pack(side=tk.LEFT, padx=5)

        card_frame = ttk.LabelFrame(container, text="Card")
        card_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.prompt_label = ttk.Label(card_frame, text="Add some cards to begin.", wraplength=600, font=("Segoe UI", 14, "bold"))
        self.prompt_label.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.answer_text = tk.Text(card_frame, height=8, wrap=tk.WORD, state=tk.DISABLED, font=("Segoe UI", 12))
        self.answer_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        control_bar = ttk.Frame(card_frame)
        control_bar.pack(fill=tk.X, pady=5)

        self.show_answer_btn = ttk.Button(control_bar, text="Show answer", command=self._toggle_answer)
        self.show_answer_btn.pack(side=tk.LEFT, padx=5)

        buttons_frame = ttk.Frame(card_frame)
        buttons_frame.pack(fill=tk.X, pady=5)

        ttk.Button(buttons_frame, text="Again", command=lambda: self._record_quality(0)).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Hard", command=lambda: self._record_quality(1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Good", command=lambda: self._record_quality(2)).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Easy", command=lambda: self._record_quality(3)).pack(side=tk.LEFT, padx=5)

        info_frame = ttk.LabelFrame(container, text="Card metadata")
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        self.metadata_vars = {
            "domain": tk.StringVar(value="Domain: -"),
            "difficulty": tk.StringVar(value="Difficulty tag: -"),
            "base": tk.StringVar(value="Initial difficulty: -"),
            "related": tk.StringVar(value="Related topics: -"),
            "success": tk.StringVar(value="Recall success: -"),
            "next": tk.StringVar(value="Next review: -"),
            "last": tk.StringVar(value="Last review: -"),
        }

        for key in ["domain", "base", "related", "difficulty", "success", "last", "next"]:
            ttk.Label(info_frame, textvariable=self.metadata_vars[key]).pack(anchor=tk.W, padx=10, pady=2)

    def _build_manage_tab(self, container: ttk.Frame) -> None:
        form = ttk.LabelFrame(container, text="Add or update card")
        form.pack(fill=tk.X, padx=5, pady=5)

        self.prompt_entry = self._create_labeled_entry(form, "Prompt / concept:")
        self.answer_entry = self._create_labeled_entry(form, "Answer / explanation:", multiline=True, height=4)
        self.domain_entry = self._create_labeled_entry(form, "Domain / certification focus:")
        self.related_entry = self._create_labeled_entry(form, "Related topics (comma separated):")
        self.difficulty_entry = self._create_labeled_entry(form, "Initial difficulty tag (e.g. Easy/Moderate/Hard):")
        self.notes_entry = self._create_labeled_entry(form, "Notes:", multiline=True, height=3)

        buttons_row = ttk.Frame(form)
        buttons_row.pack(fill=tk.X, pady=5)

        ttk.Button(buttons_row, text="Save card", command=self._save_card).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_row, text="Clear", command=self._clear_form).pack(side=tk.LEFT, padx=5)

        table_frame = ttk.LabelFrame(container, text="All cards")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("prompt", "domain", "difficulty", "success", "next")
        self.cards_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.cards_tree.heading("prompt", text="Prompt")
        self.cards_tree.heading("domain", text="Domain")
        self.cards_tree.heading("difficulty", text="Last difficulty")
        self.cards_tree.heading("success", text="Success rate")
        self.cards_tree.heading("next", text="Next review")
        self.cards_tree.column("prompt", width=260)
        self.cards_tree.column("domain", width=120)
        self.cards_tree.column("difficulty", width=140)
        self.cards_tree.column("success", width=120)
        self.cards_tree.column("next", width=160)
        self.cards_tree.pack(fill=tk.BOTH, expand=True)

        self.cards_tree.bind("<<TreeviewSelect>>", self._on_card_selected)

    # ------------------------------------------------------------------
    # Event handlers and actions
    # ------------------------------------------------------------------
    def _load_due_cards(self) -> None:
        domain = None if self.domain_filter.get() == "All domains" else self.domain_filter.get()
        due_cards = self.db.due_cards(domain=domain)
        if not due_cards:
            self.current_card = None
            self.prompt_label.configure(text="No cards are currently due. Add more cards or wait for scheduled reviews.")
            self._set_answer_text("")
            self._update_metadata()
            self.status_var.set("Review queue empty.")
            return

        self.current_card = due_cards[0]
        self.answer_visible = False
        self._display_card(self.current_card)
        self.status_var.set(f"Loaded {len(due_cards)} due card(s).")

    def _display_card(self, card: Card) -> None:
        self.prompt_label.configure(text=card.prompt)
        self._set_answer_text("Answer hidden. Click 'Show answer'.")
        self.show_answer_btn.configure(text="Show answer")
        self._update_metadata(card)

    def _toggle_answer(self) -> None:
        if not self.current_card:
            return
        self.answer_visible = not self.answer_visible
        if self.answer_visible:
            self._set_answer_text(self.current_card.answer)
            self.show_answer_btn.configure(text="Hide answer")
        else:
            self._set_answer_text("Answer hidden. Click 'Show answer'.")
            self.show_answer_btn.configure(text="Show answer")

    def _record_quality(self, quality: Quality) -> None:
        if not self.current_card:
            messagebox.showinfo("Review", "No card to review right now.")
            return
        if not self.answer_visible:
            if not messagebox.askyesno("Confirm", "Reveal the answer before grading?", default=messagebox.NO):
                return
            self._toggle_answer()

        result: ReviewResult = schedule_review(self.current_card, quality)
        self.db.record_review(
            self.current_card.id,
            ease_factor=result.ease_factor,
            interval_minutes=result.interval_minutes,
            repetitions=result.repetitions,
            quality=result.quality,
            success=result.success,
            difficulty_tag=result.difficulty_tag,
        )
        self.status_var.set(
            f"Recorded review ({result.difficulty_tag}). Next in {self._format_interval(result.interval_minutes)}."
        )
        self._refresh_domains()
        self._refresh_cards_table()
        self._load_due_cards()

    def _save_card(self) -> None:
        prompt = self._get_widget_text(self.prompt_entry)
        answer = self._get_widget_text(self.answer_entry)
        domain = self.domain_entry.get().strip()
        related = self.related_entry.get().strip()
        difficulty = self.difficulty_entry.get().strip()
        notes = self._get_widget_text(self.notes_entry)

        if not prompt or not answer:
            messagebox.showerror("Validation", "Prompt and answer are required.")
            return

        if self.editing_card_id is not None:
            self.db.update_card(
                self.editing_card_id,
                prompt=prompt,
                answer=answer,
                domain=domain or None,
                related_topics=related or None,
                base_difficulty=difficulty or None,
                notes=notes or None,
            )
            messagebox.showinfo("Saved", "Card updated successfully.")
        else:
            self.db.add_card(prompt, answer, domain or None, related or None, difficulty or None, notes or None)
            messagebox.showinfo("Saved", "Card saved successfully.")
        self._clear_form()
        self._refresh_domains()
        self._refresh_cards_table()
        self._load_due_cards()

    def _clear_form(self) -> None:
        self._set_text_widget(self.prompt_entry, "")
        self._set_text_widget(self.answer_entry, "")
        self.domain_entry.delete(0, tk.END)
        self.related_entry.delete(0, tk.END)
        self.difficulty_entry.delete(0, tk.END)
        self._set_text_widget(self.notes_entry, "")
        self.editing_card_id = None
        self.cards_tree.selection_remove(self.cards_tree.selection())

    def _on_card_selected(self, event: tk.Event[tk.Widget]) -> None:
        selection = self.cards_tree.selection()
        if not selection:
            return
        card_id = int(selection[0])
        card = self.db.get_card(card_id)
        if not card:
            return
        self.editing_card_id = card.id
        self._set_text_widget(self.prompt_entry, card.prompt)
        self._set_text_widget(self.answer_entry, card.answer)
        self.domain_entry.delete(0, tk.END)
        if card.domain:
            self.domain_entry.insert(0, card.domain)
        self.related_entry.delete(0, tk.END)
        if card.related_topics:
            self.related_entry.insert(0, card.related_topics)
        self.difficulty_entry.delete(0, tk.END)
        if card.base_difficulty:
            self.difficulty_entry.insert(0, card.base_difficulty)
        self._set_text_widget(self.notes_entry, card.notes or "")

    def _on_close(self) -> None:
        self.db.close()
        self.root.destroy()

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _refresh_domains(self) -> None:
        domains = ["All domains", *self.db.all_domains()]
        menu = self.domain_menu["menu"]
        menu.delete(0, "end")
        for domain in domains:
            menu.add_command(label=domain, command=lambda value=domain: self.domain_filter.set(value) or self._load_due_cards())
        if self.domain_filter.get() not in domains:
            self.domain_filter.set("All domains")

    def _refresh_cards_table(self) -> None:
        for row in self.cards_tree.get_children():
            self.cards_tree.delete(row)
        for card in self.db.get_cards():
            success_rate = f"{card.success_rate * 100:.0f}%" if card.total_reviews else "-"
            next_review = card.next_review.strftime("%Y-%m-%d %H:%M") if card.next_review else "Not scheduled"
            self.cards_tree.insert(
                "",
                tk.END,
                iid=str(card.id),
                values=(card.prompt[:60], card.domain or "-", card.last_difficulty_tag or "-", success_rate, next_review),
            )

    def _update_metadata(self, card: Optional[Card] = None) -> None:
        if not card:
            for var in self.metadata_vars.values():
                var.set(var.get().split(":")[0] + ": -")
            return

        self.metadata_vars["domain"].set(f"Domain: {card.domain or '-'}")
        self.metadata_vars["base"].set(f"Initial difficulty: {card.base_difficulty or '-'}")
        self.metadata_vars["related"].set(f"Related topics: {card.related_topics or '-'}")
        self.metadata_vars["difficulty"].set(f"Last difficulty tag: {card.last_difficulty_tag or '-'}")
        self.metadata_vars["success"].set(
            f"Recall success: {card.success_rate * 100:.0f}% over {card.total_reviews} review(s)"
            if card.total_reviews
            else "Recall success: -"
        )
        self.metadata_vars["last"].set(
            f"Last review: {card.last_review.strftime('%Y-%m-%d %H:%M') if card.last_review else '-'}"
        )
        next_review_text = "-"
        if card.next_review:
            delta = card.next_review - datetime.utcnow()
            if delta.total_seconds() <= 0:
                next_review_text = "Due now"
            else:
                next_review_text = self._format_timedelta(delta)
        self.metadata_vars["next"].set(f"Next review: {next_review_text}")

    def _set_answer_text(self, text: str) -> None:
        self.answer_text.configure(state=tk.NORMAL)
        self.answer_text.delete("1.0", tk.END)
        self.answer_text.insert("1.0", text)
        self.answer_text.configure(state=tk.DISABLED)

    def _set_text_widget(self, widget: tk.Text | ttk.Entry, value: str) -> None:
        if isinstance(widget, tk.Text):
            widget.delete("1.0", tk.END)
            widget.insert("1.0", value)
        else:
            widget.delete(0, tk.END)
            widget.insert(0, value)

    @staticmethod
    def _get_widget_text(widget: tk.Text | ttk.Entry) -> str:
        if isinstance(widget, tk.Text):
            return widget.get("1.0", tk.END).strip()
        return widget.get().strip()

    def _create_labeled_entry(
        self,
        container: ttk.Frame,
        label: str,
        *,
        multiline: bool = False,
        height: int = 2,
    ) -> tk.Text | ttk.Entry:
        frame = ttk.Frame(container)
        frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(frame, text=label).pack(anchor=tk.W)
        if multiline:
            widget = tk.Text(frame, height=height, wrap=tk.WORD)
            widget.pack(fill=tk.X, expand=True)
            return widget
        entry = ttk.Entry(frame)
        entry.pack(fill=tk.X, expand=True)
        return entry

    def _format_interval(self, minutes: int) -> str:
        return self._format_timedelta(timedelta(minutes=minutes))

    @staticmethod
    def _format_timedelta(delta: timedelta) -> str:
        total_minutes = int(max(delta.total_seconds(), 0) // 60)
        if total_minutes < 60:
            return f"{total_minutes} minute(s)"
        hours = total_minutes // 60
        if hours < 24:
            return f"{hours} hour(s)"
        days = hours // 24
        if days < 30:
            return f"{days} day(s)"
        months = days // 30
        if months < 12:
            return f"{months} month(s)"
        years = months // 12
        return f"{years} year(s)"


def main() -> None:
    root = tk.Tk()
    app = SpacedRepetitionApp(root)
    app._refresh_cards_table()
    root.mainloop()


if __name__ == "__main__":
    main()
