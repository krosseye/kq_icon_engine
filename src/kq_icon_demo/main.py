import sys

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from kq_icon_engine import FillMode, IconStyle, KQIcon

from .widgets.main_window import DemoWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("KQIcon Engine Demo")
    app.setWindowIcon(
        KQIcon(
            "alien",
            style=IconStyle.FILL,
            fill=FillMode.GRADIENT,
            color=QColor("green"),
        )
    )

    window = DemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
