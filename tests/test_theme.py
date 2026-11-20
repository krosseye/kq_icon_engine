import pytest
from PySide6.QtGui import QColor, QGuiApplication, QIcon, QPalette

from kq_icon_engine.theme import resolve_icon_color

Mode = QIcon.Mode
State = QIcon.State


def _set_palette(window_text: str, highlighted_text: str, disabled_text: str) -> None:
    palette = QPalette(QGuiApplication.palette())
    palette.setColor(
        QPalette.ColorGroup.Normal, QPalette.ColorRole.WindowText, QColor(window_text)
    )
    palette.setColor(
        QPalette.ColorGroup.Normal,
        QPalette.ColorRole.HighlightedText,
        QColor(highlighted_text),
    )
    palette.setColor(
        QPalette.ColorGroup.Disabled,
        QPalette.ColorRole.WindowText,
        QColor(disabled_text),
    )
    QGuiApplication.setPalette(palette)


class TestExplicitColor:
    def test_normal_mode_returns_color_unchanged(self) -> None:
        assert resolve_icon_color(QColor("#123456"), Mode.Normal, State.Off) == QColor(
            "#123456"
        )

    def test_selected_mode_keeps_explicit_color(self) -> None:
        assert resolve_icon_color(QColor("#123456"), Mode.Selected, State.On) == QColor(
            "#123456"
        )

    def test_disabled_mode_scales_alpha_to_40_percent(self) -> None:
        result = resolve_icon_color(QColor(200, 10, 10, 255), Mode.Disabled, State.Off)
        assert (result.red(), result.green(), result.blue()) == (200, 10, 10)
        assert result.alphaF() == pytest.approx(0.4, abs=1 / 255)

    def test_disabled_mode_compounds_existing_translucency(self) -> None:
        result = resolve_icon_color(QColor(0, 0, 0, 128), Mode.Disabled, State.Off)
        assert result.alphaF() == pytest.approx(128 / 255 * 0.4, abs=1 / 255)

    def test_does_not_mutate_callers_color(self) -> None:
        base = QColor(10, 20, 30, 255)
        resolve_icon_color(base, Mode.Disabled, State.Off)
        resolve_icon_color(base, Mode.Active, State.Off)
        assert base == QColor(10, 20, 30, 255)

    def test_active_mode_lightens_dark_color_by_30(self) -> None:
        base = QColor.fromHsl(200, 100, 50)
        result = resolve_icon_color(base, Mode.Active, State.Off)
        assert result.lightness() == 80
        assert result.hslHue() == 200
        assert result.hslSaturation() == 100

    def test_active_mode_darkens_light_color_by_30(self) -> None:
        result = resolve_icon_color(QColor.fromHsl(10, 50, 200), Mode.Active, State.Off)
        assert result.lightness() == 170

    @pytest.mark.parametrize(("lightness", "expected"), [(127, 157), (128, 98)])
    def test_active_mode_switches_direction_at_midpoint(
        self, lightness: int, expected: int
    ) -> None:
        result = resolve_icon_color(
            QColor.fromHsl(0, 0, lightness), Mode.Active, State.Off
        )
        assert result.lightness() == expected

    @pytest.mark.parametrize("lightness", [0, 255])
    def test_active_mode_stays_in_range_at_extremes(self, lightness: int) -> None:
        result = resolve_icon_color(
            QColor.fromHsl(0, 0, lightness), Mode.Active, State.Off
        )
        assert result.isValid()
        assert result.lightness() == (30 if lightness == 0 else 225)

    def test_active_mode_preserves_alpha(self) -> None:
        base = QColor.fromHsl(0, 0, 50, 77)
        assert resolve_icon_color(base, Mode.Active, State.Off).alpha() == 77


class TestPaletteColor:
    def test_normal_mode_uses_window_text(self) -> None:
        _set_palette("#ff0000", "#00ff00", "#0000ff")
        assert resolve_icon_color(None, Mode.Normal, State.Off) == QColor("#ff0000")

    def test_selected_mode_uses_highlighted_text(self) -> None:
        _set_palette("#ff0000", "#00ff00", "#0000ff")
        assert resolve_icon_color(None, Mode.Selected, State.On) == QColor("#00ff00")

    def test_disabled_mode_uses_disabled_group_without_extra_fade(self) -> None:
        _set_palette("#ff0000", "#00ff00", "#0000ff")
        result = resolve_icon_color(None, Mode.Disabled, State.Off)
        assert result == QColor("#0000ff")
        assert result.alpha() == 255

    def test_active_mode_adjusts_palette_color(self) -> None:
        _set_palette("#000000", "#ffffff", "#808080")
        assert resolve_icon_color(None, Mode.Active, State.Off).lightness() == 30

    def test_follows_palette_changes_at_call_time(self) -> None:
        _set_palette("#ff0000", "#00ff00", "#0000ff")
        first = resolve_icon_color(None, Mode.Normal, State.Off)
        _set_palette("#00ffff", "#00ff00", "#0000ff")
        assert first == QColor("#ff0000")
        assert resolve_icon_color(None, Mode.Normal, State.Off) == QColor("#00ffff")
