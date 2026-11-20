import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtGui import QGuiApplication, QPalette
from PySide6.QtWidgets import QApplication

from kq_icon_engine.backend import _IconLibrary, _IconRenderer

APP = QApplication.instance() or QApplication([])

# Full-bleed square so every pixel of the rendered icon is covered.
SOLID_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
    '<rect width="16" height="16" fill="black"/></svg>'
)


@pytest.fixture(autouse=True)
def _isolate_global_state() -> Iterator[None]:
    """Class-level caches and the app palette leak between tests otherwise."""
    palette = QPalette(QGuiApplication.palette())
    _IconRenderer._pixmap_cache.clear()
    _IconLibrary._path_cache.clear()
    _IconLibrary._available_icons_cache.clear()
    yield
    QGuiApplication.setPalette(palette)
    _IconRenderer._pixmap_cache.clear()
    _IconLibrary._path_cache.clear()
    _IconLibrary._available_icons_cache.clear()


@pytest.fixture
def solid_svg(tmp_path: Path) -> Path:
    path = tmp_path / "solid.svg"
    path.write_text(SOLID_SVG, encoding="utf-8")
    return path


@pytest.fixture
def broken_svg(tmp_path: Path) -> Path:
    path = tmp_path / "broken.svg"
    path.write_text("<svg this is not xml", encoding="utf-8")
    return path
