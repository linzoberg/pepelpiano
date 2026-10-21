"""
Поток воспроизведения последовательности клавиш.
Работает в отдельном QThread, чтобы не подвешивать интерфейс,
и проверяет флаг остановки маленькими порциями сна, чтобы Esc/Стоп
срабатывали мгновенно, а не ждали окончания текущей паузы.
"""
from __future__ import annotations

import time

from PyQt5.QtCore import QThread, pyqtSignal

from .storage import Song

try:
    import keyboard  # эмуляция нажатий клавиш (SendInput)
except ImportError:  # pragma: no cover
    keyboard = None

SLEEP_CHUNK = 0.02  # c, шаг проверки флага остановки


class PlayerThread(QThread):
    progress = pyqtSignal(int, str)  # индекс ноты, символ
    finished_playing = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, song: Song, countdown_sec: int = 3, parent=None):
        super().__init__(parent)
        self.song = song
        self.countdown_sec = countdown_sec
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def _sleep_interruptible(self, seconds: float):
        end = time.monotonic() + seconds
        while not self._stop_flag and time.monotonic() < end:
            time.sleep(min(SLEEP_CHUNK, max(0.0, end - time.monotonic())))

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
            delay_ms = self.song.get_interval(idx)
            self._sleep_interruptible(delay_ms / 1000.0)

        self.finished_playing.emit()
