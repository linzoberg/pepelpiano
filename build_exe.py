"""
Автоматическая сборка Genshin Piano в один .exe файл через PyInstaller.

Использование:
    pip install pyinstaller
    python build_exe.py

Результат: dist/GenshinPiano.exe
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
APP_NAME = "GenshinPiano"


def clean():
    for folder in ("build", "dist", "__pycache__"):
        path = ROOT / folder
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
    for spec in ROOT.glob("*.spec"):
        spec.unlink(missing_ok=True)


def build():
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--name",
        APP_NAME,
        "main.py",
    ]
    print("Запуск:", " ".join(cmd))
    subprocess.run(cmd, cwd=str(ROOT), check=True)


def copy_songs_json():
    src = ROOT / "songs.json"
    dist = ROOT / "dist"
    if src.exists() and dist.exists():
        shutil.copy(src, dist / "songs.json")


def main():
    print("Очистка старых артефактов сборки...")
    clean()
    print("Сборка exe через PyInstaller...")
    build()
    copy_songs_json()
    exe_path = ROOT / "dist" / f"{APP_NAME}.exe"
    print(f"\nГотово! Файл: {exe_path}")
    print("Рядом в папке dist/ лежит songs.json с вашими мелодиями.")


if __name__ == "__main__":
    main()
