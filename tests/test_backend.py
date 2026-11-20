import logging
from pathlib import Path
from typing import Any

import pytest
from PySide6.QtCore import QSize
from PySide6.QtGui import QColor

from kq_icon_engine.backend import (
    FALLBACK_ICON,
    ICONS_DIR,
    _IconLibrary,
    _IconRenderer,
)
from kq_icon_engine.types import FillMode, IconStyle

RED = QColor(255, 0, 0)


def _opaque_pixels(pixmap):  # type: ignore[no-untyped-def]
    image = pixmap.toImage()
    return [
        image.pixelColor(x, y)
        for y in range(image.height())
        for x in range(image.width())
        if image.pixelColor(x, y).alpha() == 255
    ]


class TestIconLibrary:
    @pytest.mark.parametrize("style", list(IconStyle))
    def test_every_style_exposes_the_same_icon_names(self, style: IconStyle) -> None:
        # A missing variant would silently render the fallback "?" instead.
        assert _IconLibrary.get_available_icons(
            style
        ) == _IconLibrary.get_available_icons(IconStyle.REGULAR)

    @pytest.mark.parametrize("style", list(IconStyle))
    def test_every_listed_name_resolves_to_its_own_file(self, style: IconStyle) -> None:
        for name in _IconLibrary.get_available_icons(style):
            path = _IconLibrary.resolve_path(name, style)
            assert path.exists()
            assert path.parent == ICONS_DIR / style.value
            assert path.stem in (name, f"{name}-{style.value}")

    def test_names_are_sorted_unique_and_stripped_of_style_suffix(self) -> None:
        names = _IconLibrary.get_available_icons(IconStyle.BOLD)
        assert names == sorted(set(names))
        assert "acorn" in names
        assert not any(n.endswith("-bold") for n in names)

    def test_suffix_strip_does_not_mangle_names_containing_style_word(self) -> None:
        # "square-half" must not lose "-half"; "-fill" only strips as a suffix.
        names = _IconLibrary.get_available_icons(IconStyle.FILL)
        assert "square-half" in names
        assert "square" in names

    def test_returned_list_is_a_copy(self) -> None:
        names = _IconLibrary.get_available_icons(IconStyle.REGULAR)
        names.clear()
        assert _IconLibrary.get_available_icons(IconStyle.REGULAR)

    @pytest.mark.parametrize(
        ("style", "filename"),
        [(IconStyle.REGULAR, "acorn.svg"), (IconStyle.DUOTONE, "acorn-duotone.svg")],
    )
    def test_resolve_path_uses_style_naming_convention(
        self, style: IconStyle, filename: str
    ) -> None:
        assert (
            _IconLibrary.resolve_path("acorn", style)
            == ICONS_DIR / style.value / filename
        )

    @pytest.mark.parametrize("style", list(IconStyle))
    def test_unknown_icon_falls_back_to_question_icon_in_same_style(
        self, style: IconStyle, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.WARNING):
            path = _IconLibrary.resolve_path("does-not-exist", style)
        assert path == _IconLibrary.resolve_path(FALLBACK_ICON, style)
        assert path.exists()
        assert "does-not-exist" in caplog.text

    @pytest.mark.parametrize("style", [IconStyle.REGULAR, IconStyle.BOLD])
    @pytest.mark.parametrize("name", ["", "../regular/acorn", "ACORN", "acorn.svg"])
    def test_malformed_names_fall_back_on_every_os(
        self, name: str, style: IconStyle
    ) -> None:
        # Case-insensitive filesystems (Windows/macOS) must not change the result.
        path = _IconLibrary.resolve_path(name, style)
        assert path == _IconLibrary.resolve_path(FALLBACK_ICON, style)

    def test_fallback_warning_logged_once_per_name_and_style(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.WARNING):
            for _ in range(3):
                _IconLibrary.resolve_path("nope", IconStyle.THIN)
        assert len(caplog.records) == 1


class TestIconRenderer:
    @pytest.mark.parametrize(
        "size", [QSize(0, 0), QSize(0, 16), QSize(16, 0), QSize(-1, -1)]
    )
    def test_empty_size_returns_null_pixmap(self, solid_svg: Path, size: QSize) -> None:
        assert _IconRenderer.get_pixmap(solid_svg, size, 1.0, RED).isNull()

    def test_flat_fill_paints_icon_shape_in_requested_color(
        self, solid_svg: Path
    ) -> None:
        pixmap = _IconRenderer.get_pixmap(solid_svg, QSize(8, 8), 1.0, RED)
        pixels = _opaque_pixels(pixmap)
        assert len(pixels) == 64
        assert all(p.rgb() == RED.rgb() for p in pixels)

    def test_transparent_areas_stay_transparent(self) -> None:
        path = _IconLibrary.resolve_path("circle", IconStyle.REGULAR)
        image = _IconRenderer.get_pixmap(path, QSize(64, 64), 1.0, RED).toImage()
        assert image.pixelColor(0, 0).alpha() == 0
        assert image.pixelColor(32, 32).alpha() == 0  # ring centre is hollow

    def test_color_alpha_is_respected(self, solid_svg: Path) -> None:
        pixmap = _IconRenderer.get_pixmap(
            solid_svg, QSize(4, 4), 1.0, QColor(0, 0, 255, 100)
        )
        assert pixmap.toImage().pixelColor(2, 2).alpha() == pytest.approx(100, abs=1)

    def test_gradient_is_lighter_at_top_than_bottom(self, solid_svg: Path) -> None:
        image = _IconRenderer.get_pixmap(
            solid_svg, QSize(32, 32), 1.0, QColor(0, 128, 0), FillMode.GRADIENT
        ).toImage()
        top, bottom = image.pixelColor(16, 0), image.pixelColor(16, 31)
        assert top.lightness() > bottom.lightness()
        assert top.hslHue() == bottom.hslHue() == QColor(0, 128, 0).hslHue()

    @pytest.mark.parametrize(
        ("logical", "dpr", "physical"),
        [(16, 1.0, 16), (16, 2.0, 32), (15, 1.5, 23), (10, 1.25, 13)],
    )
    def test_physical_size_scales_with_device_pixel_ratio(
        self, solid_svg: Path, logical: int, dpr: float, physical: int
    ) -> None:
        pixmap = _IconRenderer.get_pixmap(solid_svg, QSize(logical, logical), dpr, RED)
        assert pixmap.size() == QSize(physical, physical)
        assert pixmap.devicePixelRatio() == dpr

    def test_non_square_size_is_honoured(self, solid_svg: Path) -> None:
        pixmap = _IconRenderer.get_pixmap(solid_svg, QSize(40, 10), 1.0, RED)
        assert pixmap.size() == QSize(40, 10)

    def test_identical_requests_are_served_from_cache(self, solid_svg: Path) -> None:
        first = _IconRenderer.get_pixmap(solid_svg, QSize(16, 16), 1.0, RED)
        solid_svg.write_text("<svg broken", encoding="utf-8")
        second = _IconRenderer.get_pixmap(solid_svg, QSize(16, 16), 1.0, RED)
        assert not second.isNull()
        assert second.cacheKey() == first.cacheKey()

    @pytest.mark.parametrize(
        "change",
        [
            {"size": QSize(17, 16)},
            {"dpr": 2.0},
            {"color": QColor(254, 0, 0)},
            {"color": QColor(255, 0, 0, 254)},
            {"fill": FillMode.GRADIENT},
        ],
    )
    def test_any_parameter_change_renders_fresh(
        self, solid_svg: Path, change: dict[str, Any]
    ) -> None:
        base: dict[str, Any] = {
            "size": QSize(16, 16),
            "dpr": 1.0,
            "color": RED,
            "fill": FillMode.FLAT,
        }
        first = _IconRenderer.get_pixmap(solid_svg, **base)
        second = _IconRenderer.get_pixmap(solid_svg, **(base | change))
        assert second.cacheKey() != first.cacheKey()

    def test_cache_evicts_least_recently_used_entry(
        self, solid_svg: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(_IconRenderer, "_MAX_PIXMAP_CACHE_SIZE", 2)

        def get(n: int):  # type: ignore[no-untyped-def]
            return _IconRenderer.get_pixmap(solid_svg, QSize(n, n), 1.0, RED)

        a, b = get(1), get(2)
        assert get(1).cacheKey() == a.cacheKey()
        get(3)
        assert get(1).cacheKey() == a.cacheKey()
        assert get(2).cacheKey() != b.cacheKey()

    def test_cache_never_exceeds_max_size(self, solid_svg: Path) -> None:
        for n in range(1, _IconRenderer._MAX_PIXMAP_CACHE_SIZE + 20):
            _IconRenderer.get_pixmap(solid_svg, QSize(n, 1), 1.0, RED)
        assert len(_IconRenderer._pixmap_cache) == _IconRenderer._MAX_PIXMAP_CACHE_SIZE

    def test_cache_stays_bounded_with_invalid_svgs(self, broken_svg: Path) -> None:
        for n in range(1, _IconRenderer._MAX_PIXMAP_CACHE_SIZE + 20):
            _IconRenderer.get_pixmap(broken_svg, QSize(n, 1), 1.0, RED)
        assert len(_IconRenderer._pixmap_cache) <= _IconRenderer._MAX_PIXMAP_CACHE_SIZE

    @pytest.mark.parametrize("fixture", ["broken_svg", "missing"])
    def test_unrenderable_svg_returns_null_pixmap_and_logs_error(
        self,
        fixture: str,
        request: pytest.FixtureRequest,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        path = (
            tmp_path / "missing.svg"
            if fixture == "missing"
            else request.getfixturevalue(fixture)
        )
        with caplog.at_level(logging.ERROR):
            pixmap = _IconRenderer.get_pixmap(path, QSize(16, 16), 1.0, RED)
        assert pixmap.isNull()
        assert str(path.name) in caplog.text
