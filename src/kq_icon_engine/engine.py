from pathlib import Path

from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QColor, QIcon, QIconEngine, QPainter, QPixmap

from .backend import _IconLibrary, _IconRenderer
from .theme import resolve_icon_color
from .types import FillMode, IconStyle


class KQIconEngine(QIconEngine):
    """Engine that renders a recolored SVG file."""

    def __init__(
        self,
        icon_path: Path,
        color: QColor | None = None,
        fill: FillMode = FillMode.FLAT,
    ) -> None:
        super().__init__()
        self.icon_path = icon_path
        self.color = color
        self.fill = fill

    def paint(
        self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State
    ) -> None:
        """Paints the icon into the given rectangle at the device's pixel ratio."""
        if rect.isEmpty():
            return
        device = painter.device()
        dpr = device.devicePixelRatioF() if device else 1.0
        color = resolve_icon_color(self.color, mode, state)
        pixmap = _IconRenderer.get_pixmap(
            self.icon_path, rect.size(), dpr, color, self.fill
        )
        painter.drawPixmap(rect, pixmap)

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        """Renders a QPixmap for the icon."""
        color = resolve_icon_color(self.color, mode, state)
        return _IconRenderer.get_pixmap(self.icon_path, size, 1.0, color, self.fill)

    def clone(self) -> "KQIconEngine":
        return KQIconEngine(self.icon_path, self.color, self.fill)

    def key(self) -> str:
        """Returns a key describing the engine state."""
        return ":".join(
            [
                "kqicon",
                str(self.icon_path),
                self.color.name(QColor.NameFormat.HexArgb) if self.color else "auto",
                self.fill.name.lower(),
            ]
        )


class KQIcon(QIcon):
    """Icon from the bundled Phosphor library."""

    def __init__(
        self,
        icon_name: str,
        color: QColor | None = None,
        style: IconStyle = IconStyle.REGULAR,
        fill: FillMode = FillMode.FLAT,
    ) -> None:
        """Initializes the icon by name.

        Args:
            icon_name: Icon name from the library.
            color: Optional color override.
            style: Style variant (e.g., Regular, Fill).
            fill: Fill rendering mode.
        """
        path = _IconLibrary.resolve_path(icon_name, style)
        super().__init__(KQIconEngine(path, color=color, fill=fill))


class KQCustomIcon(QIcon):
    """Icon loaded from an SVG file path."""

    def __init__(
        self,
        svg_icon_path: Path,
        color: QColor | None = None,
        fill: FillMode = FillMode.FLAT,
    ) -> None:
        """Initializes the icon with a file path.

        Args:
            svg_icon_path: Path to the SVG file.
            color: Optional color override.
            fill: Fill rendering mode.
        """
        super().__init__(KQIconEngine(svg_icon_path, color=color, fill=fill))
