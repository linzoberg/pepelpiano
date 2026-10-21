"""
Поток воспроизведения последовательности клавиш.
Работает в отдельном QThread, чтобы не подвешивать интерфейс,
и проверяет флаг остановки маленькими порциями сна, чтобы Esc/Стоп
срабатывали мгновенно, а не ждали окончания текущей паузы.
"""
from __future__ import annotations

import random
import time

from PyQt5.QtCore import QThread, pyqtSignal

from .storage import Song

try:
    import keyboard  # эмуляция нажатий клавиш (SendInput)
except ImportError:  # pragma: no cover
    keyboard = None

SLEEP_CHUNK = 0.02  # c, шаг проверки флага остановки

# --- "Скрытая задержка" ---------------------------------------------------
# Диапазон случайного микро-пинга (в миллисекундах), который незаметно
# добавляется к интервалу КАЖДОЙ клавиши (включая пробел-паузу), чтобы
# игра выглядела как нажатия живого человека, а не монотонная автоматика.
# Значение генерируется заново для каждой ноты при каждом проигрывании,
# не сохраняется и не отображается в интерфейсе/таблице интервалов.
HIDDEN_DELAY_MIN_MS = 1
HIDDEN_DELAY_MAX_MS = 20


class PlayerThread(QThread):
    progress = pyqtSignal(int, str)  # индекс ноты, символ
    finished_playing = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(
        self,
        song: Song,
        countdown_sec: int = 3,
        hidden_delay: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.song = song
        self.countdown_sec = countdown_sec
        self.hidden_delay = hidden_delay
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def _sleep_interruptible(self, seconds: float):
        end = time.monotonic() + seconds
        while not self._stop_flag and time.monotonic() < end:
            time.sleep(min(SLEEP_CHUNK, max(0.0, end - time.monotonic())))

    def _note_delay_seconds(self, idx: int) -> float:
        """Интервал после ноты в секундах, с учётом скрытой задержки (если включена)."""
        delay_ms = self.song.get_interval(idx)
        if self.hidden_delay:
            # Свой случайный микро-пинг для КАЖДОЙ клавиши (и паузы) при каждом
            # проигрывании — не трогает значения song.get_interval/UI.
            delay_ms += random.uniform(HIDDEN_DELAY_MIN_MS, HIDDEN_DELAY_MAX_MS)
        return delay_ms / 1000.0

    def run(self):
        if keyboard is None:
            self.error.emit(
                "Библиотека 'keyboard' не установлена. Выполните:\npip install keyboard"
            )
            return

        # Обратный отсчёт, чтобы успеть переключиться в окно игры
        for remaining in range(self.countdown_sec, 0, -1):
            if self._stop_flag:
                self.finished_playing.emit()
                return
            self.progress.emit(-1, f"Старт через {remaining}…")
            self._sleep_interruptible(1.0)

        for idx, ch in enumerate(self.song.sequence):
            if self._stop_flag:
                break
            if ch != " ":
                try:
                    keyboard.press_and_release(ch.lower())
                except Exception as exc:  # pragma: no cover
                    self.error.emit(f"Не удалось нажать клавишу '{ch}': {exc}")
                    break
            self.progress.emit(idx, ch)
            self._sleep_interruptible(self._note_delay_seconds(idx))

        self.finished_playing.emit()
