"""Тёмная золотая тема в духе Genshin Impact."""

STYLESHEET = """
QWidget {
    background-color: #130b24;
    color: #f1e6d8;
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    font-size: 13px;
}

QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1d1340, stop:1 #120a22);
}

QLabel#Title {
    font-size: 20px;
    font-weight: 700;
    color: #f4cf7c;
}

QLabel#Subtitle {
    color: rgba(241, 230, 216, 0.55);
    font-size: 12px;
}

QFrame#Card {
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 12px;
}

QListWidget {
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    padding: 8px 10px;
    border-radius: 8px;
    margin: 2px;
}

QListWidget::item:selected {
    background-color: rgba(244, 207, 124, 0.18);
    color: #f4cf7c;
    border: 1px solid rgba(244, 207, 124, 0.4);
}

QListWidget::item:hover:!selected {
    background-color: rgba(255, 255, 255, 0.06);
}

QPushButton {
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 7px 14px;
    color: #f1e6d8;
}

QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.12);
}

QPushButton:pressed {
    background-color: rgba(255, 255, 255, 0.18);
}

QPushButton#Primary {
    background-color: #f4cf7c;
    color: #1a1226;
    font-weight: 700;
    border: none;
}

QPushButton#Primary:hover {
    background-color: #f8dd9c;
}

QPushButton#Danger {
    background-color: rgba(220, 80, 80, 0.18);
    border: 1px solid rgba(220, 80, 80, 0.4);
    color: #ff9d9d;
}

QPushButton#Danger:hover {
    background-color: rgba(220, 80, 80, 0.3);
}

/* ИЗМЕНЕНИЕ: стиль переключателя "Скрытая задержка".
   В выключенном состоянии кнопка выглядит как обычная (наследует QPushButton).
   Во включённом состоянии (:checked) подсвечивается мягким зелёным —
   чтобы было видно, что режим "игры как человек" активен, но без лишних деталей в интерфейсе. */
QPushButton#Toggle:checked {
    background-color: rgba(120, 220, 140, 0.20);
    border: 1px solid rgba(120, 220, 140, 0.55);
    color: #bdf5c8;
    font-weight: 600;
}

QPushButton#Toggle:checked:hover {
    background-color: rgba(120, 220, 140, 0.30);
}

QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QTableWidget {
    background-color: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 6px;
    color: #f1e6d8;
    selection-background-color: #f4cf7c;
    selection-color: #1a1226;
}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {
    border: 1px solid rgba(244, 207, 124, 0.6);
}

QHeaderView::section {
    background-color: rgba(255, 255, 255, 0.06);
    color: #f1e6d8;
    padding: 6px;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

QTableWidget {
    gridline-color: rgba(255, 255, 255, 0.07);
}

QProgressBar {
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    text-align: center;
    color: #f1e6d8;
}

QProgressBar::chunk {
    background-color: #f4cf7c;
    border-radius: 8px;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: rgba(244, 207, 124, 0.35);
    border-radius: 5px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(244, 207, 124, 0.55);
}

QCheckBox {
    spacing: 8px;
}

QToolTip {
    background-color: #1d1340;
    color: #f1e6d8;
    border: 1px solid rgba(244, 207, 124, 0.4);
    padding: 4px;
}
"""


KEY_IDLE = """
QLabel {
    background-color: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    color: rgba(241,230,216,0.8);
    font-weight: 600;
    font-size: 15px;
}
"""

KEY_ACTIVE = """
QLabel {
    background-color: #f4cf7c;
    border: 1px solid #ffe9b0;
    border-radius: 8px;
    color: #1a1226;
    font-weight: 800;
    font-size: 15px;
}
"""
