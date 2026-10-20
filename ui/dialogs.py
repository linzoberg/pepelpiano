from __future__ import annotations

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QPushButton,
    QMessageBox,
)

from core.storage import Song, sanitize_sequence


class SongDialog(QDialog):
    """Диалог добавления / редактирования мелодии."""

    def __init__(self, song: Song | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Мелодия" if song is None else "Редактировать мелодию")
        self.setMinimumWidth(420)
        self._song = song

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Название произведения"))
        self.name_edit = QLineEdit(song.name if song else "")
        self.name_edit.setPlaceholderText("Например: 1. Я вас любила, любовь моя")
        layout.addWidget(self.name_edit)

        layout.addWidget(
            QLabel("Последовательность нот (QWERTYU / ASDFGHJ, пробел — пауза)")
        )
        self.sequence_edit = QTextEdit(song.sequence if song else "")
        self.sequence_edit.setPlaceholderText("qjhehqerwwqwrejwqdqjhehqewrredwqjhh")
        self.sequence_edit.setFixedHeight(80)
        layout.addWidget(self.sequence_edit)

        interval_row = QHBoxLayout()
        interval_row.addWidget(QLabel("Интервал по умолчанию, мс:"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(10, 5000)
        self.interval_spin.setSingleStep(50)
        self.interval_spin.setValue(song.default_interval if song else 500)
        interval_row.addWidget(self.interval_spin)
        interval_row.addStretch(1)
        layout.addLayout(interval_row)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("Primary")
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _on_save(self):
        name = self.name_edit.text().strip()
        raw_sequence = self.sequence_edit.toPlainText().strip()
        sequence = sanitize_sequence(raw_sequence)

        if not name:
            QMessageBox.warning(self, "Проверка", "Введите название мелодии.")
            return
        if not sequence:
            QMessageBox.warning(
                self,
                "Проверка",
                "Последовательность пуста или содержит только недопустимые символы.\n"
                "Разрешены буквы Q W E R T Y U A S D F G H J и пробелы.",
            )
            return

        intervals = self._song.intervals if self._song else None
        if intervals and len(intervals) != len(sequence):
            # Длина последовательности изменилась — сбрасываем индивидуальные интервалы
            intervals = None

        self.result_song = Song(
            name=name,
            sequence=sequence,
            default_interval=self.interval_spin.value(),
            intervals=intervals,
        )
        if self._song:
            self.result_song.id = self._song.id

        self.accept()
