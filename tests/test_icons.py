from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication

from kq_icon_engine import IconStyle, KQIcon

app = QApplication.instance() or QApplication([])


def test_icon_renders() -> None:
    for style in IconStyle:
        pixmap = KQIcon("palette", style=style).pixmap(QSize(32, 32))
        assert not pixmap.isNull(), style
