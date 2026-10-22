from __future__ import annotations

import json
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QFrame,
    QSpinBox,
    QCheckBox,
    QTableWidget,
    QTableWidgetItem,
    QProgressBar,
    QMessageBox,
    QFileDialog,
    QAbstractItemView,
    QHeaderView,
)

try:
    import keyboard
except ImportError:  # pragma: no cover
    keyboard = None

from core.storage import Song, load_songs, save_songs, songs_path
from core.player import PlayerThread
from ui.dialogs import SongDialog
from ui.styles import STYLESHEET, KEY_IDLE, KEY_ACTIVE

ROW_1 = list("QWERTYU")
ROW_2 = list("ASDFGHJ")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Genshin Piano")
        self.resize(980, 620)
        self.setStyleSheet(STYLESHEET)

        self.songs: list[Song] = load_songs()
        self.current_song: Song | None = None
        self.player_thread: PlayerThread | None = None
        self.key_labels: dict[str, QLabel] = {}

        # ИЗМЕНЕНИЕ: состояние переключателя "Скрытая задержка".
        # По умолчанию выключено (программа играет строго по заданным интервалам).
        self.stealth_delay_enabled: bool = False

        self._build_ui()
        self._refresh_song_list()
        if self.songs:
            self.song_list.setCurrentRow(0)

        self._register_global_hotkey()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("🎹 Genshin Piano")
        title.setObjectName("Title")
        subtitle = QLabel("Автоматическое воспроизведение мелодий на клавиатуре")
        subtitle.setObjectName("Subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch(1)

        # ИЗМЕНЕНИЕ: кнопка-переключатель "Скрытая задержка" слева от "Импорт из файла".
        # Это чекнутая (checkable) кнопка: нажата = включено, не нажата = выключено.
        # Сама кнопка и её состояние не раскрывают пользователю никаких цифр —
        # это просто тумблер "играть монотонно / играть как человек".
        self.stealth_btn = QPushButton("Скрытая задержка")
        self.stealth_btn.setObjectName("Toggle")
        self.stealth_btn.setCheckable(True)
        self.stealth_btn.setChecked(False)
        self.stealth_btn.setToolTip(
            "Добавляет незаметную случайную задержку (1–30 мс) к каждой клавише,\n"
            "включая пробел-паузу, чтобы игра звучала менее роботизированно."
        )
        self.stealth_btn.toggled.connect(self._on_stealth_toggle)
        header.addWidget(self.stealth_btn)

        import_btn = QPushButton("Импорт из файла")
        import_btn.clicked.connect(self._import_songs)
        export_btn = QPushButton("Экспорт всех")
        export_btn.clicked.connect(self._export_songs)
        header.addWidget(import_btn)
        header.addWidget(export_btn)
        root.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(12)
        root.addLayout(body, 1)

        # --- Левая колонка: список мелодий ---
        left = QFrame()
        left.setObjectName("Card")
        left.setFixedWidth(260)
        left_layout = QVBoxLayout(left)

        left_header = QHBoxLayout()
        left_header.addWidget(QLabel("Мелодии"))
        left_header.addStretch(1)
        add_btn = QPushButton("+ Добавить")
        add_btn.setObjectName("Primary")
        add_btn.clicked.connect(self._add_song)
        left_header.addWidget(add_btn)
        left_layout.addLayout(left_header)

        self.song_list = QListWidget()
        self.song_list.currentRowChanged.connect(self._on_song_selected)
        left_layout.addWidget(self.song_list, 1)

        list_btn_row = QHBoxLayout()
        edit_btn = QPushButton("Изменить")
        edit_btn.clicked.connect(self._edit_song)
        del_btn = QPushButton("Удалить")
        del_btn.setObjectName("Danger")
        del_btn.clicked.connect(self._delete_song)
        list_btn_row.addWidget(edit_btn)
        list_btn_row.addWidget(del_btn)
        left_layout.addLayout(list_btn_row)

        body.addWidget(left)

        # --- Правая колонка: детали / проигрывание ---
        right = QVBoxLayout()
        right.setSpacing(12)
        body.addLayout(right, 1)

        info_card = QFrame()
        info_card.setObjectName("Card")
        info_layout = QVBoxLayout(info_card)
        self.song_title_label = QLabel("Выберите мелодию слева")
        self.song_title_label.setObjectName("Title")
        self.song_title_label.setStyleSheet("font-size:16px;")
        self.sequence_label = QLabel("")
        self.sequence_label.setWordWrap(True)
        self.sequence_label.setStyleSheet("color: rgba(241,230,216,0.6); font-family: Consolas, monospace;")
        info_layout.addWidget(self.song_title_label)
        info_layout.addWidget(self.sequence_label)
        right.addWidget(info_card)

        # Клавиатура
        keyboard_card = QFrame()
        keyboard_card.setObjectName("Card")
        kb_layout = QVBoxLayout(keyboard_card)
        kb_layout.addWidget(QLabel("Виртуальная клавиатура"))
        grid = QGridLayout()
        grid.setSpacing(6)
        for col, k in enumerate(ROW_1):
            lbl = self._make_key_label(k)
            grid.addWidget(lbl, 0, col)
            self.key_labels[k] = lbl
        for col, k in enumerate(ROW_2):
            lbl = self._make_key_label(k)
            grid.addWidget(lbl, 1, col + 1)
            self.key_labels[k] = lbl
        kb_layout.addLayout(grid)
        right.addWidget(keyboard_card)

        # Управление воспроизведением
        controls_card = QFrame()
        controls_card.setObjectName("Card")
        controls_layout = QVBoxLayout(controls_card)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Обратный отсчёт перед стартом, сек:"))
        self.countdown_spin = QSpinBox()
        self.countdown_spin.setRange(0, 10)
        self.countdown_spin.setValue(3)
        row1.addWidget(self.countdown_spin)
        row1.addStretch(1)

        self.play_btn = QPushButton("▶  Играть")
        self.play_btn.setObjectName("Primary")
        self.play_btn.clicked.connect(self._on_play_clicked)
        self.stop_btn = QPushButton("⏹  Стоп")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        row1.addWidget(self.play_btn)
        row1.addWidget(self.stop_btn)
        controls_layout.addLayout(row1)

        self.status_label = QLabel("Готово. Глобальная остановка — клавиша Esc.")
        self.status_label.setStyleSheet("color: rgba(241,230,216,0.6);")
        controls_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        controls_layout.addWidget(self.progress_bar)

        right.addWidget(controls_card)

        # Индивидуальные интервалы
        intervals_card = QFrame()
        intervals_card.setObjectName("Card")
        intervals_layout = QVBoxLayout(intervals_card)
        header_row = QHBoxLayout()
        self.custom_checkbox = QCheckBox("Индивидуальный интервал для каждой клавиши")
        self.custom_checkbox.stateChanged.connect(self._on_custom_toggle)
        header_row.addWidget(self.custom_checkbox)
        header_row.addStretch(1)
        reset_btn = QPushButton("Сбросить к единому интервалу")
        reset_btn.clicked.connect(self._reset_intervals)
        header_row.addWidget(reset_btn)
        intervals_layout.addLayout(header_row)

        self.intervals_table = QTableWidget(0, 3)
        self.intervals_table.setHorizontalHeaderLabels(["#", "Клавиша", "Задержка, мс"])
        self.intervals_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.intervals_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.intervals_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.intervals_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.intervals_table.setMaximumHeight(220)
        self.intervals_table.itemChanged.connect(self._on_interval_item_changed)
        intervals_layout.addWidget(self.intervals_table)

        right.addWidget(intervals_card, 1)

    def _make_key_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFixedSize(44, 44)
        lbl.setStyleSheet(KEY_IDLE)
        return lbl

    # ------------------------------------------------------------- helpers

    def _refresh_song_list(self):
        self.song_list.blockSignals(True)
        self.song_list.clear()
        for s in self.songs:
            item = QListWidgetItem(s.name)
            self.song_list.addItem(item)
        self.song_list.blockSignals(False)

    def _persist(self):
        save_songs(self.songs)

    def _highlight_key(self, ch: str | None):
        for k, lbl in self.key_labels.items():
            lbl.setStyleSheet(KEY_ACTIVE if ch and k == ch.upper() else KEY_IDLE)

    def _populate_intervals_table(self):
        self.intervals_table.blockSignals(True)
        self.intervals_table.setRowCount(0)
        song = self.current_song
        if song:
            for idx, ch in enumerate(song.sequence):
                row = self.intervals_table.rowCount()
                self.intervals_table.insertRow(row)
                idx_item = QTableWidgetItem(str(idx + 1))
                idx_item.setFlags(idx_item.flags() & ~Qt.ItemIsEditable)
                key_item = QTableWidgetItem("␣" if ch == " " else ch.upper())
                key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)
                delay_item = QTableWidgetItem(str(song.get_interval(idx)))
                self.intervals_table.setItem(row, 0, idx_item)
                self.intervals_table.setItem(row, 1, key_item)
                self.intervals_table.setItem(row, 2, delay_item)
        self.intervals_table.blockSignals(False)
        self.intervals_table.setEnabled(bool(self.custom_checkbox.isChecked()))

    # ------------------------------------------------------------- signals

    def _on_song_selected(self, row: int):
        if row < 0 or row >= len(self.songs):
            self.current_song = None
            self.song_title_label.setText("Выберите мелодию слева")
            self.sequence_label.setText("")
            self.intervals_table.setRowCount(0)
            return
        song = self.songs[row]
        self.current_song = song
        self.song_title_label.setText(song.name)
        self.sequence_label.setText(
            f"Последовательность ({len(song.sequence)} нот): {song.sequence.upper()}\n"
            f"Интервал по умолчанию: {song.default_interval} мс"
        )
        self.custom_checkbox.blockSignals(True)
        self.custom_checkbox.setChecked(bool(song.intervals))
        self.custom_checkbox.blockSignals(False)
        self._populate_intervals_table()

    def _on_custom_toggle(self, _state):
        song = self.current_song
        if not song:
            return
        if self.custom_checkbox.isChecked():
            if not song.intervals or len(song.intervals) != len(song.sequence):
                song.intervals = [song.default_interval] * len(song.sequence)
        else:
            song.intervals = None
        self._persist()
        self._populate_intervals_table()

    def _on_interval_item_changed(self, item: QTableWidgetItem):
        if item.column() != 2 or not self.current_song:
            return
        song = self.current_song
        if not song.intervals or len(song.intervals) != len(song.sequence):
            song.intervals = [song.default_interval] * len(song.sequence)
        try:
            value = max(10, int(item.text()))
        except ValueError:
            value = song.default_interval
        row = item.row()
        if 0 <= row < len(song.intervals):
            song.intervals[row] = value
        self._persist()

    def _reset_intervals(self):
        song = self.current_song
        if not song:
            return
        song.intervals = [song.default_interval] * len(song.sequence) if self.custom_checkbox.isChecked() else None
        self._persist()
        self._populate_intervals_table()

    # ИЗМЕНЕНИЕ: обработчик переключателя "Скрытая задержка".
    # Ничего не пишет в songs.json, не трогает таблицу интервалов и статус —
    # просто запоминает состояние тумблера для следующего запуска воспроизведения.
    def _on_stealth_toggle(self, checked: bool):
        self.stealth_delay_enabled = checked

    # --------------------------------------------------------- list actions

    def _add_song(self):
        dlg = SongDialog(parent=self)
        if dlg.exec_():
            self.songs.append(dlg.result_song)
            self._persist()
            self._refresh_song_list()
            self.song_list.setCurrentRow(len(self.songs) - 1)

    def _edit_song(self):
        row = self.song_list.currentRow()
        if row < 0:
            return
        dlg = SongDialog(self.songs[row], parent=self)
        if dlg.exec_():
            self.songs[row] = dlg.result_song
            self._persist()
            self._refresh_song_list()
            self.song_list.setCurrentRow(row)

    def _delete_song(self):
        row = self.song_list.currentRow()
        if row < 0:
            return
        confirm = QMessageBox.question(
            self, "Удалить", f"Удалить мелодию «{self.songs[row].name}»?"
        )
        if confirm == QMessageBox.Yes:
            del self.songs[row]
            self._persist()
            self._refresh_song_list()

    def _import_songs(self):
        path, _ = QFileDialog.getOpenFileName(self, "Импорт мелодий", "", "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            items = raw if isinstance(raw, list) else [raw]
            existing_ids = {s.id for s in self.songs}
            added = 0
            for item in items:
                song = Song.from_json(item)
                if song.id in existing_ids:
                    import uuid

                    song.id = uuid.uuid4().hex
                self.songs.append(song)
                added += 1
            self._persist()
            self._refresh_song_list()
            QMessageBox.information(self, "Импорт", f"Импортировано мелодий: {added}")
        except Exception as exc:
            QMessageBox.warning(self, "Ошибка импорта", str(exc))

    def _export_songs(self):
        path, _ = QFileDialog.getSaveFileName(self, "Экспорт мелодий", "songs_export.json", "JSON (*.json)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump([s.to_json() for s in self.songs], f, ensure_ascii=False, indent=2)

    # -------------------------------------------------------- playback

    def _on_play_clicked(self):
        if not self.current_song or not self.current_song.sequence:
            QMessageBox.information(self, "Genshin Piano", "Сначала выберите мелодию с нотами.")
            return
        if keyboard is None:
            QMessageBox.warning(
                self,
                "Нужна библиотека keyboard",
                "Установите зависимость: pip install keyboard",
            )
            return

        self.play_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setMaximum(len(self.current_song.sequence))
        self.progress_bar.setValue(0)

        # ИЗМЕНЕНИЕ: передаём в поток воспроизведения текущее состояние
        # тумблера "Скрытая задержка". Остальная логика не изменена.
        self.player_thread = PlayerThread(
            self.current_song,
            self.countdown_spin.value(),
            stealth_delay=self.stealth_delay_enabled,
        )
        self.player_thread.progress.connect(self._on_playback_progress)
        self.player_thread.finished_playing.connect(self._on_playback_finished)
        self.player_thread.error.connect(self._on_playback_error)
        self.player_thread.start()

    def _on_stop_clicked(self):
        if self.player_thread:
            self.player_thread.stop()
        self.status_label.setText("Остановлено пользователем.")

    def _on_playback_progress(self, index: int, ch: str):
        if index == -1:
            self.status_label.setText(ch)
            self._highlight_key(None)
            return
        self.status_label.setText(f"Нота {index + 1}/{len(self.current_song.sequence)}: '{ch.upper()}'")
        self.progress_bar.setValue(index + 1)
        self._highlight_key(ch)

    def _on_playback_finished(self):
        self.play_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._highlight_key(None)
        if "Остановлено" not in self.status_label.text():
            self.status_label.setText("Воспроизведение завершено.")
        self.player_thread = None

    def _on_playback_error(self, message: str):
        QMessageBox.warning(self, "Ошибка воспроизведения", message)

    # ------------------------------------------------------------ hotkeys

    def _register_global_hotkey(self):
        if keyboard is None:
            return
        try:
            keyboard.add_hotkey("esc", self._global_stop)
        except Exception:
            pass

    def _global_stop(self):
        if self.player_thread and self.player_thread.isRunning():
            self.player_thread.stop()

    def closeEvent(self, event):
        if self.player_thread and self.player_thread.isRunning():
            self.player_thread.stop()
            self.player_thread.wait(500)
        save_songs(self.songs)
        super().closeEvent(event)
