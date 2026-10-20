"""
Genshin Piano — десктоп-клиент для автоматического воспроизведения мелодий
на клавиатуре (ряды QWERTYU / ASDFGHJ) в стиле виндхарпа/лиры Genshin Impact.

Запуск:   python main.py
Сборка в exe:  python build_exe.py   (см. README.md)
"""
import sys

from PyQt5.QtWidgets import QApplication

from ui.window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Genshin Piano")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
