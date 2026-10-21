"""
Поток воспроизведения последовательности клавиш.
Работает в отдельном QThread, чтобы не подвешивать интерфейс,
и проверяет флаг остановки маленькими порциями сна, чтобы Esc/Стоп
срабатывали мгновенно, а не ждали окончания текущей паузы.

ИЗМЕНЕНИЕ: добавлена опциональная "скрытая задержка" — для КАЖДОЙ
клавиши (в том числе пробела-паузы) к заданному интервалу прибавляется
случайное число миллисекунд от STEALTH_MIN_MS до STEALTH_MAX_MS.
Значение каждый раз новое (пересчитывается внутри цикла воспроизведения),
нигде не сохраняется и не показывается в интерфейсе — таблица
индивидуальных интервалов и сам объект Song остаются без изменений.
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

# Диапазон "скрытой задержки" (мс), добавляется незаметно к каждой ноте и паузе,
# если соответствующая опция включена пользователем.
STEALTH_MIN_MS = 1
STEALTH_MAX_MS = 20


class PlayerThread(QThread):
    progress = pyqtSignal(int, str)  # индекс ноты, символ
    finished_playing = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(
        self,
        song: Song,
        countdown_sec: int = 3,
        stealth_delay: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.song = song
        self.countdown_sec = countdown_sec
        self.stealth_delay = stealth_delay
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

            # Базовый интервал этой ноты/паузы — как задано в интерфейсе,
            # он не меняется и не "портится" визуально ни в таблице, ни в статусе.
            delay_ms = self.song.get_interval(idx)

            # "Скрытая задержка": добавляем к КАЖДОЙ клавише (и пробелу тоже)
            # новое случайное число мс из диапазона [1; 20], чтобы ритм не был
            # идеально монотонным, как у робота. Значение рассчитывается заново
            # для каждой ноты при каждом проигрывании.
            if self.stealth_delay:
                delay_ms += random.randint(STEALTH_MIN_MS, STEALTH_MAX_MS)

            self._sleep_interruptible(delay_ms / 1000.0)

        self.finished_playing.emit()
