import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QGuiApplication, QIcon

from kq_icon_demo.state import IconFilterState
from kq_icon_demo.widgets.grid import IconGrid
from kq_icon_demo.widgets.main_window import DemoWindow
from kq_icon_demo.widgets.preview import PreviewPanel
from kq_icon_engine import FillMode, IconStyle
from kq_icon_engine.backend import _IconLibrary


@pytest.fixture
def window() -> DemoWindow:
    return DemoWindow()


def _names(grid: IconGrid) -> list[str]:
    return grid.model().stringList()  # type: ignore[attr-defined]


class TestIconGrid:
    def test_shows_every_icon_with_empty_search(self) -> None:
        grid = IconGrid(IconFilterState())
        grid.refresh()
        assert _names(grid) == _IconLibrary.get_available_icons(IconStyle.REGULAR)

    def test_search_filters_by_substring(self) -> None:
        state = IconFilterState(search_text="arrow")
        grid = IconGrid(state)
        grid.refresh()
        assert _names(grid)
        assert all("arrow" in n for n in _names(grid))

    def test_search_with_no_matches_yields_empty_grid(self) -> None:
        grid = IconGrid(IconFilterState(search_text="zzz-nothing"))
        grid.refresh()
        assert _names(grid) == []

    def test_decoration_role_is_plain_renderable_qicon(self) -> None:
        grid = IconGrid(IconFilterState(search_text="acorn"))
        grid.refresh()
        decoration = grid.model().index(0, 0).data(Qt.ItemDataRole.DecorationRole)
        assert type(decoration) is QIcon
        assert not decoration.pixmap(32, 32).isNull()

    def test_tooltip_is_icon_name(self) -> None:
        grid = IconGrid(IconFilterState(search_text="acorn"))
        grid.refresh()
        assert grid.model().index(0, 0).data(Qt.ItemDataRole.ToolTipRole) == "acorn"

    def test_selecting_a_cell_emits_icon_name(self) -> None:
        grid = IconGrid(IconFilterState(search_text="acorn"))
        grid.refresh()
        received: list[str] = []
        grid.iconSelected.connect(received.append)
        grid.setCurrentIndex(grid.model().index(0, 0))
        assert received == ["acorn"]


class TestDemoWindow:
    def test_search_is_case_and_whitespace_insensitive(
        self, window: DemoWindow
    ) -> None:
        window.search.setText("  ACORN ")
        assert window.state.search_text == "acorn"
        assert _names(window.grid) == ["acorn"]

    def test_clearing_search_restores_full_list(self, window: DemoWindow) -> None:
        window.search.setText("acorn")
        window.search.clear()
        assert len(_names(window.grid)) == len(
            _IconLibrary.get_available_icons(IconStyle.REGULAR)
        )

    def test_grid_selection_updates_preview(self, window: DemoWindow) -> None:
        window.search.setText("acorn")
        window.grid.setCurrentIndex(window.grid.model().index(0, 0))
        assert window.preview.name_label.text() == "acorn"
        assert window.preview.copy_name_btn.isEnabled()

    def test_style_change_in_preview_updates_shared_state_and_grid(
        self, window: DemoWindow
    ) -> None:
        sel = window.preview.style_selector
        sel.setCurrentIndex(sel.findData(IconStyle.DUOTONE))
        assert window.state.style == IconStyle.DUOTONE
        assert _names(window.grid) == _IconLibrary.get_available_icons(
            IconStyle.DUOTONE
        )


class TestPreviewPanel:
    def test_copy_buttons_disabled_until_icon_selected(self) -> None:
        panel = PreviewPanel(IconFilterState())
        assert not panel.copy_name_btn.isEnabled()
        assert not panel.copy_code_btn.isEnabled()
        assert not panel.preview_label.pixmap().isNull()  # placeholder art

    def test_settings_change_emits_changed_and_updates_fill(self) -> None:
        state = IconFilterState()
        panel = PreviewPanel(state)
        fired: list[bool] = []
        panel.changed.connect(lambda: fired.append(True))
        panel.fill_mode_selector.setCurrentIndex(
            panel.fill_mode_selector.findData(FillMode.GRADIENT)
        )
        assert state.fill == FillMode.GRADIENT
        assert fired

    @pytest.mark.parametrize(
        ("state", "expected"),
        [
            (IconFilterState(), 'KQIcon("acorn")'),
            (
                IconFilterState(style=IconStyle.BOLD, fill=FillMode.GRADIENT),
                'KQIcon("acorn", style=IconStyle.BOLD, fill=FillMode.GRADIENT)',
            ),
            (
                IconFilterState(color=QColor("#ff8800")),
                'KQIcon("acorn", color=QColor("#ff8800"))',
            ),
        ],
    )
    def test_copy_snippet_produces_minimal_valid_code(
        self, state: IconFilterState, expected: str
    ) -> None:
        panel = PreviewPanel(state)
        panel.set_icon("acorn")
        panel.copy_code_btn.click()
        assert QGuiApplication.clipboard().text() == expected

    def test_copy_name_puts_icon_name_on_clipboard(self) -> None:
        panel = PreviewPanel(IconFilterState())
        panel.set_icon("acorn")
        panel.copy_name_btn.click()
        assert QGuiApplication.clipboard().text() == "acorn"
