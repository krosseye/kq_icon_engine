import logging
import threading
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

LOGGER = logging.getLogger()


class _IconRenderer:
    """Handles SVG rendering and caching of pixmaps."""

    _pixmap_cache: OrderedDict[tuple[Path, int, int, float, int, FillMode], QPixmap] = (
        OrderedDict()
    )

    _MAX_PIXMAP_CACHE_SIZE: int = 500
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def set_cache_size(cls, size: int) -> None:
        with cls._lock:
            cls._MAX_PIXMAP_CACHE_SIZE = size

            if len(cls._pixmap_cache) > size:
                while len(cls._pixmap_cache) > size:
                    cls._pixmap_cache.popitem(last=False)

    @classmethod
    def clear_cache(cls) -> None:
        with cls._lock:
            cls._pixmap_cache.clear()

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

        key = (
            icon_path,
            size.width(),
            size.height(),
            dpr,
            color.rgba(),
            fill,
        )

        with cls._lock:
            if key in cls._pixmap_cache:
                pixmap = cls._pixmap_cache[key]
                cls._pixmap_cache.move_to_end(key)
                return pixmap

        renderer = QSvgRenderer(icon_path.as_posix())
        if not renderer.isValid():
            return QPixmap()

        physical_w = int(size.width() * dpr)
        physical_h = int(size.height() * dpr)

        image = QImage(
            physical_w, physical_h, QImage.Format.Format_ARGB32_Premultiplied
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

        rect = QRect(0, 0, physical_w, physical_h)
        if fill != FillMode.FLAT:
            gradient = QLinearGradient(0, 0, 0, float(physical_h))
            gradient.setColorAt(0.0, color.lighter(120))
            gradient.setColorAt(0.5, color)
            gradient.setColorAt(1.0, color.darker(120))
            img_painter.fillRect(rect, gradient)
        else:
            img_painter.fillRect(rect, color)

        img_painter.end()

        pixmap = QPixmap.fromImage(image)
        pixmap.setDevicePixelRatio(dpr)

        with cls._lock:
            cls._pixmap_cache[key] = pixmap
            if len(cls._pixmap_cache) > cls._MAX_PIXMAP_CACHE_SIZE:
                cls._pixmap_cache.popitem(last=False)

        return pixmap


class _IconLibrary:
    """Phosphor icon library management."""

    ICONS_DIR: Path | None = None
    DEFAULT_STYLE: IconStyle = IconStyle.REGULAR
    FALLBACK_ICON: str = "question"

    _path_cache: dict[tuple[str, IconStyle], Path] = {}
    _fallback_keys: set[tuple[str, IconStyle]] = set()
    _available_icons_cache: dict[IconStyle, list[str]] = {}
    _warned_missing: set[tuple[str, IconStyle]] = set()

    _lock: threading.Lock = threading.Lock()
    _initialised: bool = False

    @classmethod
    def setup(
        cls,
        icon_dir: Path,
        default_style: IconStyle = IconStyle.REGULAR,
        fallback_icon: str = "question",
        max_cache_size: int = 128,
    ) -> None:
        """Initializes the icon system.

        Args:
            icon_dir: Base directory containing icons.
            default_style: The default style to use.
            fallback_icon: Name of the icon to use as a fallback.
            max_cache_size: Maximum number of pixmaps to keep in memory.
        """
        with cls._lock:
            if cls._initialised:
                LOGGER.warning(
                    "Icon backend already initialised; reinitialising. "
                    "Call setup() only once at application startup."
                )

            cls.ICONS_DIR = Path(icon_dir)
            cls.DEFAULT_STYLE = default_style
            cls.FALLBACK_ICON = fallback_icon

            cls._path_cache.clear()
            cls._fallback_keys.clear()
            cls._available_icons_cache.clear()
            cls._warned_missing.clear()
            cls._initialised = True

        _IconRenderer.set_cache_size(max_cache_size)

    @classmethod
    def get_available_icons(cls, style: IconStyle) -> list[str]:
        """Returns a sorted list of unique icon names available for a given style.

        Performs a style-lazy scan, only indexing the requested style's directory.
        """
        if not cls.ICONS_DIR:
            return []

        with cls._lock:
            if style in cls._available_icons_cache:
                return list(cls._available_icons_cache[style])

            style_dir = cls.ICONS_DIR / style.value
            if not style_dir.is_dir():
                LOGGER.warning("Icon style directory '%s' not found.", style_dir)
                cls._available_icons_cache[style] = []
                return []

            icons: set[str] = set()
            try:
                for file in style_dir.iterdir():
                    if file.suffix.lower() == ".svg":
                        name = file.stem
                        if style != IconStyle.REGULAR:
                            name = name.removesuffix(f"-{style.value}")
                        icons.add(name)
            except OSError as e:
                LOGGER.error("Failed to index icons for style '%s': %s", style.value, e)
                cls._available_icons_cache[style] = []
                return []

            cls._available_icons_cache[style] = sorted(icons)
            return list(cls._available_icons_cache[style])

    @classmethod
    def resolve_path(cls, icon_name: str, style: IconStyle | None) -> Path:
        """Resolves the file path for an icon.

        Checks for file existence directly if the path is not cached,
        avoiding full library scans for simple path resolution.
        """
        if not cls.ICONS_DIR:
            return Path()

        style_key: IconStyle = style if style is not None else cls.DEFAULT_STYLE
        cache_key = (icon_name, style_key)

        with cls._lock:
            if cache_key in cls._path_cache:
                return cls._path_cache[cache_key]

        filename = (
            f"{icon_name}.svg"
            if style_key == IconStyle.REGULAR
            else f"{icon_name}-{style_key.value}.svg"
        )
        potential_path = cls.ICONS_DIR / style_key.value / filename

        if potential_path.exists():
            with cls._lock:
                cls._path_cache[cache_key] = potential_path
            return potential_path

        with cls._lock:
            if cache_key not in cls._warned_missing:
                LOGGER.warning(
                    "Icon '%s' not found in style '%s'. Using fallback '%s'.",
                    icon_name,
                    style_key.value,
                    cls.FALLBACK_ICON,
                )
                cls._warned_missing.add(cache_key)
            cls._fallback_keys.add(cache_key)

        fallback_filename = (
            f"{cls.FALLBACK_ICON}.svg"
            if style_key == IconStyle.REGULAR
            else f"{cls.FALLBACK_ICON}-{style_key.value}.svg"
        )
        fallback_path = cls.ICONS_DIR / style_key.value / fallback_filename

        if fallback_path.exists():
            with cls._lock:
                cls._path_cache[cache_key] = fallback_path
            return fallback_path

        LOGGER.error(
            "Fallback icon '%s' missing at %s", cls.FALLBACK_ICON, fallback_path
        )
        return Path()


_IconLibrary.setup(Path(__file__).parent / "icons")
