from pathlib import Path

import pytest
from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QGuiApplication, QIcon, QImage, QPainter, QPalette

from kq_icon_engine import FillMode, IconStyle, KQCustomIcon, KQIcon
from kq_icon_engine.engine import KQIconEngine

RED = QColor(255, 0, 0)


def _center(icon: QIcon, mode: QIcon.Mode = QIcon.Mode.Normal) -> QColor:
    return icon.pixmap(QSize(16, 16), mode).toImage().pixelColor(8, 8)


class TestKQIcon:
    @pytest.mark.parametrize("style", list(IconStyle))
    @pytest.mark.parametrize("fill", list(FillMode))
    def test_renders_non_empty_pixmap_for_every_style_and_fill(
        self, style: IconStyle, fill: FillMode
    ) -> None:
        pixmap = KQIcon("palette", style=style, fill=fill).pixmap(QSize(32, 32))
        assert not pixmap.isNull()
        assert pixmap.size() == QSize(32, 32)

    def test_unknown_icon_renders_same_pixels_as_fallback(self) -> None:
        missing = KQIcon("no-such-icon", color=RED).pixmap(QSize(32, 32)).toImage()
        fallback = KQIcon("question", color=RED).pixmap(QSize(32, 32)).toImage()
        assert not missing.isNull()
        assert missing == fallback

    def test_different_styles_render_different_artwork(self) -> None:
        thin = KQIcon("acorn", color=RED, style=IconStyle.THIN).pixmap(QSize(32, 32))
        bold = KQIcon("acorn", color=RED, style=IconStyle.BOLD).pixmap(QSize(32, 32))
        assert thin.toImage() != bold.toImage()

    def test_explicit_color_is_used(self) -> None:
        icon = KQIcon("square", color=RED, style=IconStyle.FILL)
        assert _center(icon).rgb() == RED.rgb()

    def test_default_color_follows_application_palette(self) -> None:
        palette = QPalette(QGuiApplication.palette())
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#00ff00"))
        QGuiApplication.setPalette(palette)
        icon = KQIcon("square", style=IconStyle.FILL)
        assert _center(icon).rgb() == QColor("#00ff00").rgb()

    def test_disabled_mode_renders_faded(self) -> None:
        icon = KQIcon("square", color=RED, style=IconStyle.FILL)
        normal = _center(icon, QIcon.Mode.Normal)
        disabled = _center(icon, QIcon.Mode.Disabled)
        assert disabled.alpha() < normal.alpha()

    def test_plain_qicon_copy_keeps_rendering(self) -> None:
        # The demo grid relies on this (Qt views only see a plain QIcon).
        icon = QIcon(KQIcon("square", color=RED, style=IconStyle.FILL))
        assert _center(icon).rgb() == RED.rgb()


class TestKQCustomIcon:
    def test_renders_external_svg_in_requested_color(self, solid_svg: Path) -> None:
        assert _center(KQCustomIcon(solid_svg, color=RED)).rgb() == RED.rgb()

    def test_missing_file_yields_null_pixmap(self, tmp_path: Path) -> None:
        assert KQCustomIcon(tmp_path / "nope.svg").pixmap(QSize(16, 16)).isNull()

    def test_invalid_svg_yields_null_pixmap(self, broken_svg: Path) -> None:
        assert KQCustomIcon(broken_svg).pixmap(QSize(16, 16)).isNull()


class TestKQIconEngine:
    def test_key_encodes_path_color_and_fill(self, solid_svg: Path) -> None:
        engine = KQIconEngine(solid_svg, QColor(255, 0, 0, 128), FillMode.GRADIENT)
        assert engine.key() == f"kqicon:{solid_svg}:#80ff0000:gradient"

    def test_key_uses_auto_when_color_is_palette_driven(self, solid_svg: Path) -> None:
        assert KQIconEngine(solid_svg).key() == f"kqicon:{solid_svg}:auto:flat"

    def test_keys_differ_when_any_attribute_differs(
        self, solid_svg: Path, tmp_path: Path
    ) -> None:
        keys = {
            KQIconEngine(solid_svg).key(),
            KQIconEngine(solid_svg, RED).key(),
            KQIconEngine(solid_svg, fill=FillMode.GRADIENT).key(),
            KQIconEngine(tmp_path / "other.svg").key(),
        }
        assert len(keys) == 4

    def test_clone_is_independent_with_identical_state(self, solid_svg: Path) -> None:
        original = KQIconEngine(solid_svg, RED, FillMode.GRADIENT)
        copy = original.clone()
        assert copy is not original
        assert copy.key() == original.key()
        original.fill = FillMode.FLAT
        assert copy.fill == FillMode.GRADIENT

    def test_paint_fills_target_rect_only(self, solid_svg: Path) -> None:
        image = QImage(32, 32, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        KQIconEngine(solid_svg, RED).paint(
            painter, QRect(8, 8, 16, 16), QIcon.Mode.Normal, QIcon.State.Off
        )
        painter.end()
        assert image.pixelColor(16, 16).rgb() == RED.rgb()
        assert image.pixelColor(2, 2).alpha() == 0
        assert image.pixelColor(28, 28).alpha() == 0

    def test_paint_renders_at_device_pixel_ratio(self, solid_svg: Path) -> None:
        image = QImage(32, 32, QImage.Format.Format_ARGB32_Premultiplied)
        image.setDevicePixelRatio(2.0)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        KQIconEngine(solid_svg, RED).paint(
            painter, QRect(0, 0, 16, 16), QIcon.Mode.Normal, QIcon.State.Off
        )
        painter.end()
        # Logical 16x16 at dpr 2 must cover all 32x32 physical pixels.
        assert image.pixelColor(31, 31).rgb() == RED.rgb()

    def test_paint_with_empty_rect_draws_nothing(self, solid_svg: Path) -> None:
        image = QImage(8, 8, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        KQIconEngine(solid_svg, RED).paint(
            painter, QRect(0, 0, 0, 0), QIcon.Mode.Normal, QIcon.State.Off
        )
        painter.end()
        assert all(
            image.pixelColor(x, y).alpha() == 0 for x in range(8) for y in range(8)
        )
