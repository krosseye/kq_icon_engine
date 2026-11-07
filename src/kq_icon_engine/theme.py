from PySide6.QtGui import QColor, QGuiApplication, QIcon, QPalette


def resolve_icon_color(
    base_color: QColor | None, mode: QIcon.Mode, state: QIcon.State
) -> QColor:
    """Resolves the final icon color for a mode.

    Args:
        base_color: Optional base color. If None, the palette's text color is used.
        mode: The icon mode (Normal, Disabled, Active, Selected).
        state: The icon state (On, Off).
    """
    if base_color is None:
        app = QGuiApplication.instance()
        palette = app.palette() if isinstance(app, QGuiApplication) else QPalette()
        group = (
            QPalette.ColorGroup.Disabled
            if mode == QIcon.Mode.Disabled
            else QPalette.ColorGroup.Normal
        )
        role = (
            QPalette.ColorRole.HighlightedText
            if mode == QIcon.Mode.Selected
            else QPalette.ColorRole.WindowText
        )
        color = palette.color(group, role)
    else:
        color = QColor(base_color)
        if mode == QIcon.Mode.Disabled:
            color.setAlphaF(color.alphaF() * 0.4)
            return color

    if mode == QIcon.Mode.Active:
        lightness = color.lightness()
        lightness = lightness + 30 if lightness < 128 else lightness - 30
        return QColor.fromHsl(
            color.hslHue(), color.hslSaturation(), lightness, color.alpha()
        )
    return color
