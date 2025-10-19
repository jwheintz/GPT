"""Database layer for spaced repetition application."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

DB_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"


@dataclass
class Card:
    """Represents a flash card entry fetched from the database."""

    id: int
    prompt: str
    answer: str
    domain: Optional[str]
    related_topics: Optional[str]
    base_difficulty: Optional[str]
    notes: Optional[str]
    ease_factor: float
    interval_minutes: int
    repetitions: int
    total_reviews: int
    successful_reviews: int
    last_review: Optional[datetime]
    next_review: Optional[datetime]
    last_quality: Optional[int]
    last_difficulty_tag: Optional[str]

    @property
    def success_rate(self) -> float:
        if self.total_reviews == 0:
            return 0.0
        return self.successful_reviews / self.total_reviews

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Card":
        def parse_ts(value: Optional[str]) -> Optional[datetime]:
            if value is None:
                return None
            return datetime.strptime(value, DB_TIMESTAMP_FORMAT)

        return cls(
            id=row["id"],
            prompt=row["prompt"],
            answer=row["answer"],
            domain=row["domain"],
            related_topics=row["related_topics"],
            base_difficulty=row["base_difficulty"],
            notes=row["notes"],
            ease_factor=row["ease_factor"],
            interval_minutes=row["interval_minutes"],
            repetitions=row["repetitions"],
            total_reviews=row["total_reviews"],
            successful_reviews=row["successful_reviews"],
            last_review=parse_ts(row["last_review"]),
            next_review=parse_ts(row["next_review"]),
            last_quality=row["last_quality"],
            last_difficulty_tag=row["last_difficulty_tag"],
        )


class DatabaseManager:
    """Handles database interactions for flash cards."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._create_schema()

    def close(self) -> None:
        self._connection.close()

    def _create_schema(self) -> None:
        with self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    domain TEXT,
                    related_topics TEXT,
                    base_difficulty TEXT,
                    notes TEXT,
                    ease_factor REAL NOT NULL DEFAULT 2.5,
                    interval_minutes INTEGER NOT NULL DEFAULT 0,
                    repetitions INTEGER NOT NULL DEFAULT 0,
                    total_reviews INTEGER NOT NULL DEFAULT 0,
                    successful_reviews INTEGER NOT NULL DEFAULT 0,
                    last_review TEXT,
                    next_review TEXT,
                    last_quality INTEGER,
                    last_difficulty_tag TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def add_card(
        self,
        prompt: str,
        answer: str,
        domain: Optional[str],
        related_topics: Optional[str],
        base_difficulty: Optional[str],
        notes: Optional[str],
    ) -> int:
        now = datetime.utcnow().strftime(DB_TIMESTAMP_FORMAT)
        with self._connection:
            cursor = self._connection.execute(
                """
                INSERT INTO cards (
                    prompt, answer, domain, related_topics, base_difficulty,
                    notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (prompt, answer, domain, related_topics, base_difficulty, notes, now, now),
            )
        return int(cursor.lastrowid)

    def update_card(
        self,
        card_id: int,
        *,
        prompt: Optional[str] = None,
        answer: Optional[str] = None,
        domain: Optional[str] = None,
        related_topics: Optional[str] = None,
        base_difficulty: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        fields = []
        values: list[Optional[str]] = []
        if prompt is not None:
            fields.append("prompt = ?")
            values.append(prompt)
        if answer is not None:
            fields.append("answer = ?")
            values.append(answer)
        if domain is not None:
            fields.append("domain = ?")
            values.append(domain)
        if related_topics is not None:
            fields.append("related_topics = ?")
            values.append(related_topics)
        if base_difficulty is not None:
            fields.append("base_difficulty = ?")
            values.append(base_difficulty)
        if notes is not None:
            fields.append("notes = ?")
            values.append(notes)
        if not fields:
            return
        fields.append("updated_at = ?")
        values.append(datetime.utcnow().strftime(DB_TIMESTAMP_FORMAT))
        values.append(card_id)
        with self._connection:
            self._connection.execute(
                f"UPDATE cards SET {', '.join(fields)} WHERE id = ?",
                values,
            )

    def get_card(self, card_id: int) -> Optional[Card]:
        cursor = self._connection.execute(
            "SELECT * FROM cards WHERE id = ?",
            (card_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return Card.from_row(row)

    def get_cards(self) -> Iterable[Card]:
        cursor = self._connection.execute(
            "SELECT * FROM cards ORDER BY COALESCE(next_review, created_at) ASC"
        )
        return [Card.from_row(row) for row in cursor.fetchall()]

    def due_cards(self, *, domain: Optional[str] = None) -> list[Card]:
        now = datetime.utcnow().strftime(DB_TIMESTAMP_FORMAT)
        query = "SELECT * FROM cards WHERE next_review IS NULL OR next_review <= ?"
        params: list[object] = [now]
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        query += " ORDER BY COALESCE(next_review, created_at) ASC"
        cursor = self._connection.execute(query, params)
        return [Card.from_row(row) for row in cursor.fetchall()]

    def all_domains(self) -> list[str]:
        cursor = self._connection.execute(
            "SELECT DISTINCT domain FROM cards WHERE domain IS NOT NULL AND domain != '' ORDER BY domain"
        )
        return [row[0] for row in cursor.fetchall()]

    def record_review(
        self,
        card_id: int,
        *,
        ease_factor: float,
        interval_minutes: int,
        repetitions: int,
        quality: int,
        success: bool,
        difficulty_tag: str,
    ) -> None:
        now = datetime.utcnow()
        next_review = now + timedelta(minutes=interval_minutes)
        with self._connection:
            self._connection.execute(
                """
                UPDATE cards
                SET
                    ease_factor = ?,
                    interval_minutes = ?,
                    repetitions = ?,
                    total_reviews = total_reviews + 1,
                    successful_reviews = successful_reviews + ?,
                    last_review = ?,
                    next_review = ?,
                    last_quality = ?,
                    last_difficulty_tag = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    ease_factor,
                    interval_minutes,
                    repetitions,
                    1 if success else 0,
                    now.strftime(DB_TIMESTAMP_FORMAT),
                    next_review.strftime(DB_TIMESTAMP_FORMAT),
                    quality,
                    difficulty_tag,
                    now.strftime(DB_TIMESTAMP_FORMAT),
                    card_id,
                ),
            )


from datetime import timedelta  # noqa: E402  (import after class definition for clarity)

__all__ = ["DatabaseManager", "Card", "DB_TIMESTAMP_FORMAT"]
