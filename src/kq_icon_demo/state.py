from dataclasses import dataclass

from PySide6.QtGui import QColor

from kq_icon_engine.types import FillMode, IconStyle


@dataclass
class IconFilterState:
    """Holds the current state of icon filters."""

    search_text: str = ""
    style: IconStyle = IconStyle.REGULAR
    fill: FillMode = FillMode.FLAT
    color: QColor | None = None
