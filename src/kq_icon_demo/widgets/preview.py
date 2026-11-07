from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QGuiApplication, QPalette
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QFormLayout,
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from kq_icon_engine.engine import KQIcon
from kq_icon_engine.types import FillMode, IconStyle

from ..state import IconFilterState


class PreviewPanel(QFrame):
    """Detailed view and control panel for a selected icon."""

    changed = Signal()

    def __init__(self, state: IconFilterState) -> None:
        super().__init__()
        self.state = state
        self._selected_icon: str | None = None

        self.setFixedWidth(280)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setAutoFillBackground(True)

        self._scroll_area = QScrollArea(self)
        self._scroll_area.setWidgetResizable(True)

        palette = self._scroll_area.palette()
        palette.setColor(self._scroll_area.backgroundRole(), Qt.GlobalColor.transparent)
        self._scroll_area.setPalette(palette)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.container = QWidget()
        self.container.setAutoFillBackground(False)
        self.container.setObjectName("PreviewContainer")
        self._scroll_area.setWidget(self.container)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.addWidget(self._scroll_area)

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.preview_label = QLabel()
        self.preview_label.setFixedSize(160, 160)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel("<em>Select an icon</em>")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        font = self.name_label.font()
        font.setBold(True)
        font.setPointSize(16)
        self.name_label.setFont(font)

        layout.addWidget(self.preview_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)

        controls_group = QWidget()
        form_layout = QFormLayout(controls_group)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setVerticalSpacing(16)
        form_layout.setHorizontalSpacing(16)
        form_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        settings_header = QLabel("<b>Icon Settings</b>")
        layout.addWidget(settings_header)

        self.style_selector = QComboBox()
        self.style_selector.setFixedHeight(32)
        for style in IconStyle:
            self.style_selector.addItem(style.capitalize(), style)
        self.style_selector.setCurrentIndex(
            self.style_selector.findData(self.state.style)
        )
        self.style_selector.currentIndexChanged.connect(self._on_settings_changed)
        form_layout.addRow("Style:", self.style_selector)

        self.fill_mode_selector = QComboBox()
        self.fill_mode_selector.setFixedHeight(32)
        for mode in FillMode:
            display_name = mode.name.replace("_", " ").title()
            self.fill_mode_selector.addItem(display_name, mode)
        self.fill_mode_selector.setCurrentIndex(
            self.fill_mode_selector.findData(self.state.fill)
        )
        self.fill_mode_selector.currentIndexChanged.connect(self._on_settings_changed)
        form_layout.addRow("Fill Mode:", self.fill_mode_selector)

        self.color_picker_btn = QPushButton(" Select Color...")
        self.color_picker_btn.setFixedHeight(32)
        self.color_picker_btn.setIcon(KQIcon("palette"))
        self.color_picker_btn.clicked.connect(self._open_color_dialog)
        form_layout.addRow("Color:", self.color_picker_btn)

        layout.addWidget(controls_group)
        layout.addStretch()

        self.copy_name_btn = QPushButton(" Copy Name")
        self.copy_name_btn.setFixedHeight(32)
        self.copy_name_btn.setIcon(KQIcon("copy"))
        self.copy_name_btn.clicked.connect(self._copy_name)

        self.copy_code_btn = QPushButton(" Copy Code Snippet")
        self.copy_code_btn.setFixedHeight(32)
        self.copy_code_btn.setIcon(KQIcon("code"))
        self.copy_code_btn.clicked.connect(self._copy_snippet)

        layout.addWidget(self.copy_name_btn)
        layout.addWidget(self.copy_code_btn)

        self._update_preview()

    def _open_color_dialog(self) -> None:
        initial = self.state.color or self.palette().color(
            QPalette.ColorRole.WindowText
        )
        color = QColorDialog.getColor(initial, self, "Select Icon Color")
        if color.isValid():
            self.state.color = color
            self._on_settings_changed()

    def set_icon(self, icon_name: str) -> None:
        self._selected_icon = icon_name
        self.name_label.setText(icon_name)
        self._update_preview()

    def _update_preview(self) -> None:
        if not self._selected_icon:
            self.preview_label.setPixmap(
                KQIcon("cursor-click", style=IconStyle.DUOTONE).pixmap(QSize(128, 128))
            )
            self.copy_name_btn.setEnabled(False)
            self.copy_code_btn.setEnabled(False)
            return

        self.copy_name_btn.setEnabled(True)
        self.copy_code_btn.setEnabled(True)

        icon = KQIcon(
            self._selected_icon,
            color=self.state.color,
            style=self.state.style,
            fill=self.state.fill,
        )
        self.preview_label.setPixmap(icon.pixmap(QSize(128, 128)))

    def _on_settings_changed(self) -> None:
        self.state.style = IconStyle(self.style_selector.currentData())
        self.state.fill = self.fill_mode_selector.currentData()
        self._update_preview()
        self.changed.emit()

    def _copy_name(self) -> None:
        if self._selected_icon:
            QGuiApplication.clipboard().setText(self._selected_icon)

    def _copy_snippet(self) -> None:
        if not self._selected_icon:
            return

        args = [f'"{self._selected_icon}"']
        if self.state.style != IconStyle.REGULAR:
            args.append(f"style=IconStyle.{self.state.style.name}")
        if self.state.fill != FillMode.FLAT:
            args.append(f"fill=FillMode.{self.state.fill.name}")
        if self.state.color is not None:
            args.append(f'color=QColor("{self.state.color.name()}")')

        snippet = f"KQIcon({', '.join(args)})"
        QGuiApplication.clipboard().setText(snippet)
