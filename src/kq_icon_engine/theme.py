from PySide6.QtGui import (
    QColor,
    QGuiApplication,
    QIcon,
    QPalette,
)


class ThemeManager:
    """Handles application-wide icon color resolution."""

    @classmethod
    def _get_current_palette(cls) -> QPalette:
        """Retrieves the current application palette or a default.

        Returns:
            QPalette: The active application palette.
        """
        app = QGuiApplication.instance()
        return app.palette() if isinstance(app, QGuiApplication) else QPalette()

    @classmethod
    def resolve_icon_color(
        cls,
        base_color: QColor | None,
        mode: QIcon.Mode,
        state: QIcon.State,
    ) -> QColor:
        """Resolves the final QColor for an icon.

        Args:
            base_color: Optional base color. If None,
                        the theme's default text color is used.
            mode: The icon mode (Normal, Disabled, Active, Selected).
            state: The icon state (On, Off).

        Returns:
            QColor: The resolved color after applying adjustments.
        """
        if base_color:
            resolved_color = base_color
        else:
            palette = cls._get_current_palette()
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
            resolved_color = palette.color(group, role)

        if mode == QIcon.Mode.Disabled:
            return resolved_color.darker(150) if base_color else resolved_color
        elif mode == QIcon.Mode.Active:
            return resolved_color.lighter(120)
        else:
            return resolved_color
