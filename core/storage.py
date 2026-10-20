"""
Хранение списка мелодий (songs.json) рядом с приложением / exe-файлом.
Не зависит от PyQt — чистая бизнес-логика, как в core/ из wifi-monitor.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Optional

ALLOWED_KEYS = set("qwertyu" + "asdfghj")


@dataclass
class Song:
    name: str
    sequence: str
    default_interval: int = 500
    intervals: Optional[List[int]] = None
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def get_interval(self, index: int) -> int:
        if self.intervals and index < len(self.intervals):
            return int(self.intervals[index])
        return int(self.default_interval)

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "sequence": self.sequence,
            "defaultInterval": self.default_interval,
            "intervals": self.intervals,
        }

    @staticmethod
    def from_json(data: dict) -> "Song":
        return Song(
            id=data.get("id") or uuid.uuid4().hex,
            name=data.get("name", "Без названия"),
            sequence=data.get("sequence", ""),
            default_interval=int(data.get("defaultInterval", 500)),
            intervals=data.get("intervals"),
        )


def app_dir() -> str:
    """Папка, где лежит exe (frozen) или main.py (разработка)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def songs_path() -> str:
    return os.path.join(app_dir(), "songs.json")


def load_songs() -> List[Song]:
    path = songs_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, list):
            return []
        return [Song.from_json(item) for item in raw]
    except (json.JSONDecodeError, OSError):
        return []


def save_songs(songs: List[Song]) -> None:
    path = songs_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump([s.to_json() for s in songs], f, ensure_ascii=False, indent=2)


def sanitize_sequence(raw: str) -> str:
    """Оставляет только допустимые ноты (QWERTYU / ASDFGHJ) и пробелы-паузы."""
    return "".join(ch for ch in raw if ch == " " or ch.lower() in ALLOWED_KEYS)
