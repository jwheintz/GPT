"""Scheduling logic for spaced repetition reviews."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .database import Card

Quality = Literal[0, 1, 2, 3]


@dataclass
class ReviewResult:
    """Represents the outcome of applying a review rating to a card."""

    ease_factor: float
    interval_minutes: int
    repetitions: int
    quality: Quality
    success: bool
    difficulty_tag: str


_DIFFICULTY_TAGS: dict[Quality, str] = {
    0: "Forgotten",
    1: "Struggled",
    2: "Successful Recall",
    3: "Effortless Recall",
}


def _clamp(value: float, *, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def schedule_review(card: Card, quality: Quality) -> ReviewResult:
    """Calculate the next scheduling parameters based on the given quality."""

    ease_factor = card.ease_factor
    repetitions = card.repetitions
    interval_minutes = card.interval_minutes if card.interval_minutes > 0 else 10

    ease_factor = ease_factor + (quality - 2) * 0.12
    ease_factor = _clamp(ease_factor, min_value=1.3, max_value=3.5)

    if quality < 2:
        repetitions = 0
        interval_minutes = 20
    else:
        repetitions += 1
        if repetitions == 1:
            interval_minutes = 12 * 60  # 12 hours
        elif repetitions == 2:
            interval_minutes = 24 * 60  # 1 day
        else:
            interval_minutes = int(interval_minutes * ease_factor)
            if quality == 3:
                interval_minutes = int(interval_minutes * 1.2)

        interval_minutes = max(interval_minutes, 30)

    difficulty_tag = _DIFFICULTY_TAGS[quality]
    success = quality >= 2
    return ReviewResult(
        ease_factor=ease_factor,
        interval_minutes=interval_minutes,
        repetitions=repetitions,
        quality=quality,
        success=success,
        difficulty_tag=difficulty_tag,
    )


__all__ = ["ReviewResult", "schedule_review", "Quality"]
