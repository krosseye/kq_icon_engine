from pathlib import Path
from typing import Optional, Tuple

from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import (
    QColor,
    QGuiApplication,
    QIcon,
    QIconEngine,
    QPainter,
    QPixmap,
)

from .backend import _IconLibrary, _IconRenderer
from .theme import ThemeManager
from .types import FillMode, IconStyle


class _KQBaseIconEngine(QIconEngine):
    """Base engine for SVG processing."""

    def __init__(
        self, color: Optional[QColor] = None, fill: FillMode = FillMode.FLAT
    ) -> None:
        super().__init__()
        self.color = color
        self.fill = fill

    def _get_icon_path(self) -> Path:
        """Returns the path to the SVG file.

        Returns:
            Path: Path to the source icon.
        """
        raise NotImplementedError

    def _resolve(
        self, mode: QIcon.Mode, state: QIcon.State, dpr: Optional[float] = None
    ) -> Tuple[Path, QColor, float, FillMode]:
        """Resolves icon parameters for the current context.

        Args:
            mode: The icon mode.
            state: The icon state.
            dpr: Optional device pixel ratio override.

        Returns:
            Tuple[Path, QColor, float, FillMode]: Resolved rendering parameters.
        """
        icon_path = self._get_icon_path()
        color = ThemeManager.resolve_icon_color(self.color, mode, state)
        if dpr is None:
            screen = QGuiApplication.primaryScreen()
            dpr = screen.devicePixelRatio() if screen else 1.0
        return icon_path, color, dpr, self.fill

    def paint(
        self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State
    ) -> None:
        """Paints the icon into the given rectangle.

        Args:
            painter: The QPainter instance.
            rect: Target boundaries.
            mode: Icon mode.
            state: Icon state.
        """
        if (
            rect.isEmpty()
            or not (icon_path := self._get_icon_path())
            or str(icon_path) == "."
        ):
            return

        dpr = painter.device().devicePixelRatioF() if painter.device() else 1.0
        _, color, _, fill = self._resolve(mode, state, dpr)

        pixmap = _IconRenderer.get_pixmap(icon_path, rect.size(), dpr, color, fill)
        painter.drawPixmap(rect, pixmap)

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        """Renders a QPixmap for the icon.

        Args:
            size: Logical size of the pixmap.
            mode: Icon mode.
            state: Icon state.

        Returns:
            QPixmap: The rendered icon image.
        """
        if size.isEmpty():
            return QPixmap()

        icon_path, color, dpr, fill = self._resolve(mode, state)
        return _IconRenderer.get_pixmap(icon_path, size, dpr, color, fill)

    def actualSize(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QSize:
        """Returns the requested size as the actual size, as SVGs are scalable."""
        return size

    def availableSizes(
        self, mode: QIcon.Mode = QIcon.Mode.Normal, state: QIcon.State = QIcon.State.Off
    ) -> list[QSize]:
        """Returns an empty list to indicate the icon is scalable.

        Args:
            mode: The icon mode.
            state: The icon state.
        """
        return []

    def clone(self) -> "_KQBaseIconEngine":
        raise NotImplementedError

    def key(self) -> str:
        raise NotImplementedError


class KQIconEngine(_KQBaseIconEngine):
    """Engine for library-managed icons (name + style)."""

    def __init__(
        self,
        icon_name: str,
        color: Optional[QColor] = None,
        style: IconStyle = IconStyle.REGULAR,
        fill: FillMode = FillMode.FLAT,
    ) -> None:
        super().__init__(color, fill)
        self.icon_name = icon_name
        self.style = style

    def _get_icon_path(self) -> Path:
        """Resolves path via the icon library."""
        return _IconLibrary.resolve_path(self.icon_name, self.style)

    def clone(self) -> "KQIconEngine":
        """Creates a deep copy of the engine.

        Returns:
            KQIconEngine: A new engine instance with identical state.
        """
        return KQIconEngine(self.icon_name, self.color, self.style, self.fill)

    def key(self) -> str:
        """Returns a unique key for the configuration.

        Returns:
            str: Cache key representing the engine state.
        """
        return ":".join(
            [
                "kqicon",
                self.icon_name,
                self.style.value,
                self.color.name(QColor.NameFormat.HexArgb) if self.color else "auto",
                self.fill.name.lower(),
            ]
        )


class KQCustomIconEngine(_KQBaseIconEngine):
    """Engine for icons loaded directly from a file path."""

    def __init__(
        self,
        icon_path: Path,
        color: Optional[QColor] = None,
        fill: FillMode = FillMode.FLAT,
    ) -> None:
        super().__init__(color, fill)
        self.icon_path = icon_path

    def _get_icon_path(self) -> Path:
        """Returns the explicit file path."""
        return self.icon_path

    def clone(self) -> "KQCustomIconEngine":
        """Creates a deep copy of the engine.

        Returns:
            KQCustomIconEngine: A new engine instance with identical state.
        """
        return KQCustomIconEngine(self.icon_path, self.color, self.fill)

    def key(self) -> str:
        """Returns a unique key for the configuration.

        Returns:
            str: Cache key representing the engine state.
        """
        return ":".join(
            [
                "kqcustom",
                str(self.icon_path),
                self.color.name(QColor.NameFormat.HexArgb) if self.color else "auto",
                self.fill.name.lower(),
            ]
        )


class KQIcon(QIcon):
    """Icon subclass for Phosphor icons library."""

    def __init__(
        self,
        icon_name: str,
        color: Optional[QColor] = None,
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
        super().__init__(KQIconEngine(icon_name, color=color, style=style, fill=fill))


class KQCustomIcon(QIcon):
    """Icon subclass for loading SVGs from file paths."""

    def __init__(
        self,
        svg_icon_path: Path,
        color: Optional[QColor] = None,
        fill: FillMode = FillMode.FLAT,
    ) -> None:
        """Initializes the icon with a file path.

        Args:
            svg_icon_path: Path to the SVG file.
            color: Optional color override.
            fill: Fill rendering mode.
        """
        super().__init__(KQCustomIconEngine(svg_icon_path, color=color, fill=fill))
