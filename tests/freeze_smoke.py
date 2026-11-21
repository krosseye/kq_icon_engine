"""Frozen by CI with PyInstaller; exits non-zero if icons are missing."""

import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication

from kq_icon_engine import IconStyle, KQIcon
from kq_icon_engine.backend import _IconLibrary

app = QApplication([])
count = len(_IconLibrary.get_available_icons(IconStyle.REGULAR))
renders = not KQIcon("acorn").pixmap(QSize(32, 32)).isNull()
print(f"icons found: {count}, acorn renders: {renders}")
sys.exit(0 if count and renders else 1)
