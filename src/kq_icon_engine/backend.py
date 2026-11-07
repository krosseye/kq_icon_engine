import logging
import math
from collections import OrderedDict
from pathlib import Path

from PySide6.QtCore import QRect, QRectF, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QImage,
    QLinearGradient,
    QPainter,
    QPixmap,
)
from PySide6.QtSvg import QSvgRenderer

from .types import FillMode, IconStyle

LOGGER = logging.getLogger(__name__)

ICONS_DIR = Path(__file__).parent / "icons"
FALLBACK_ICON = "question"


def _icon_path(name: str, style: IconStyle) -> Path:
    """Builds the on-disk path for an icon."""
    filename = (
        f"{name}.svg" if style == IconStyle.REGULAR else f"{name}-{style.value}.svg"
    )
    return ICONS_DIR / style.value / filename


class _IconRenderer:
    """Handles SVG rendering and caching of pixmaps."""

    _MAX_PIXMAP_CACHE_SIZE: int = 128

    _pixmap_cache: OrderedDict[tuple[Path, int, int, float, int, FillMode], QPixmap] = (
        OrderedDict()
    )

    @classmethod
    def get_pixmap(
        cls,
        icon_path: Path,
        size: QSize,
        dpr: float,
        color: QColor,
        fill: FillMode = FillMode.FLAT,
    ) -> QPixmap:
        """Returns a cached QPixmap.

        Args:
            icon_path: Path to the SVG source.
            size: Requested logical size.
            dpr: Device Pixel Ratio for high-DPI scaling.
            color: The QColor to apply to the icon.
            fill: The fill mode to use.

        Returns:
            A rendered and colored QPixmap.
        """
        if size.isEmpty():
            return QPixmap()

        key = (icon_path, size.width(), size.height(), dpr, color.rgba(), fill)

        if key in cls._pixmap_cache:
            cls._pixmap_cache.move_to_end(key)
            return cls._pixmap_cache[key]

        renderer = QSvgRenderer(icon_path.as_posix())
        if not renderer.isValid():
            LOGGER.error("Invalid SVG: %s", icon_path)
            cls._pixmap_cache[key] = QPixmap()
            return cls._pixmap_cache[key]

        image = QImage(
            math.ceil(size.width() * dpr),
            math.ceil(size.height() * dpr),
            QImage.Format.Format_ARGB32_Premultiplied,
        )
        image.setDevicePixelRatio(dpr)
        image.fill(Qt.GlobalColor.transparent)

        img_painter = QPainter(image)
        img_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        img_painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        renderer.render(img_painter, QRectF(0, 0, size.width(), size.height()))

        img_painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_SourceIn
        )

        rect = QRect(0, 0, size.width(), size.height())
        if fill != FillMode.FLAT:
            gradient = QLinearGradient(0, 0, 0, float(size.height()))
            gradient.setColorAt(0.0, color.lighter(120))
            gradient.setColorAt(0.5, color)
            gradient.setColorAt(1.0, color.darker(120))
            img_painter.fillRect(rect, gradient)
        else:
            img_painter.fillRect(rect, color)

        img_painter.end()

        pixmap = QPixmap.fromImage(image)
        pixmap.setDevicePixelRatio(dpr)

        cls._pixmap_cache[key] = pixmap
        if len(cls._pixmap_cache) > cls._MAX_PIXMAP_CACHE_SIZE:
            cls._pixmap_cache.popitem(last=False)

        return pixmap


class _IconLibrary:
    """Phosphor icon library management."""

    _path_cache: dict[tuple[str, IconStyle], Path] = {}
    _available_icons_cache: dict[IconStyle, list[str]] = {}

    @classmethod
    def get_available_icons(cls, style: IconStyle) -> list[str]:
        """Returns a sorted list of unique icon names available for a given style.

        Performs a style-lazy scan, only indexing the requested style's directory.
        """
        if style not in cls._available_icons_cache:
            style_dir = ICONS_DIR / style.value
            names: set[str] = set()
            for file in style_dir.glob("*.svg"):
                name = file.stem
                if style != IconStyle.REGULAR:
                    name = name.removesuffix(f"-{style.value}")
                names.add(name)
            cls._available_icons_cache[style] = sorted(names)

        return list(cls._available_icons_cache[style])

    @classmethod
    def resolve_path(cls, icon_name: str, style: IconStyle) -> Path:
        """Resolves the file path for an icon, falling back to FALLBACK_ICON."""
        cache_key = (icon_name, style)

        if cache_key in cls._path_cache:
            return cls._path_cache[cache_key]

        path = _icon_path(icon_name, style)
        if not path.exists():
            LOGGER.warning(
                "Icon '%s' not found in style '%s'. Using fallback '%s'.",
                icon_name,
                style.value,
                FALLBACK_ICON,
            )
            path = _icon_path(FALLBACK_ICON, style)

        cls._path_cache[cache_key] = path
        return path
