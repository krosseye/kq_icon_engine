from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from kq_icon_engine import KQIcon

from ..state import IconFilterState
from .grid import IconGrid
from .preview import PreviewPanel


class DemoWindow(QMainWindow):
    """Search bar and icon grid on the left, preview panel on the right.

    Spacing rule: 16 px around and between panels, 8 px padding inside them.
    """

    def __init__(self) -> None:
        super().__init__()
        self.resize(768, 600)
        self.setMinimumSize(768, 400)

        self.state = IconFilterState()
        self.search = self._create_search()
        self.grid = IconGrid(self.state)
        self.preview = PreviewPanel(self.state)

        left = QVBoxLayout()
        left.setSpacing(16)
        left.addWidget(self._framed(self.search))
        left.addWidget(self._framed(self.grid), 1)

        panels = QHBoxLayout()
        panels.setSpacing(16)
        panels.addLayout(left, 1)
        panels.addWidget(self.preview)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        layout.addLayout(panels, 1)
        layout.addWidget(self._create_credits(), alignment=Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(central)

        self.grid.iconSelected.connect(self.preview.set_icon)
        self.preview.changed.connect(self.grid.refresh)
        self.grid.refresh()

    @staticmethod
    def _framed(widget: QWidget) -> QFrame:
        """Wraps a widget in a rounded panel, matching the preview panel."""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(widget)
        return frame

    def _create_search(self) -> QLineEdit:
        search = QLineEdit()
        search.setPlaceholderText("Search icons...")
        search.setClearButtonEnabled(True)
        search.setFixedHeight(32)
        search.setMinimumWidth(320)
        search.addAction(
            KQIcon("magnifying-glass"), QLineEdit.ActionPosition.LeadingPosition
        )
        search.textChanged.connect(self._on_search)
        return search

    def _on_search(self, text: str) -> None:
        self.state.search_text = text.lower().strip()
        self.grid.refresh()

    @staticmethod
    def _create_credits() -> QLabel:
        label = QLabel(
            "Icons by <a href='https://phosphoricons.com'>Phosphor</a> • "
            "API by <a href='https://github.com/krosseye'>Killian W (krosseye)</a><br>"
            "Licensed under the <a href='https://opensource.org/license/MIT'>MIT License</a>"
        )
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setOpenExternalLinks(True)
        return label
