from PySide6.QtCore import (
    QModelIndex,
    QPersistentModelIndex,
    QSize,
    QStringListModel,
    Qt,
    Signal,
)
from PySide6.QtGui import QIcon, QPalette, QResizeEvent
from PySide6.QtWidgets import QAbstractItemView, QFrame, QListView

from kq_icon_engine.backend import _IconLibrary
from kq_icon_engine.engine import KQIcon

from ..state import IconFilterState

CELL_SIZE = 128


class _IconModel(QStringListModel):
    """Icon names; each icon is built only when the view paints its cell."""

    def __init__(self, state: IconFilterState) -> None:
        super().__init__()
        self.state = state

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object:
        name = super().data(index, Qt.ItemDataRole.DisplayRole)
        if role == Qt.ItemDataRole.DecorationRole:
            s = self.state
            # Plain QIcon: PySide stores a QIcon subclass as a Python object,
            # which the C++ delegate can't read, so the cell would stay blank.
            return QIcon(KQIcon(name, color=s.color, style=s.style, fill=s.fill))
        if role == Qt.ItemDataRole.ToolTipRole:
            return name
        return super().data(index, role)


class IconGrid(QListView):
    """Scrollable grid of every icon matching the current filters."""

    iconSelected = Signal(str)

    def __init__(self, state: IconFilterState) -> None:
        super().__init__()
        self._model = _IconModel(state)
        self.setModel(self._model)

        self.setViewMode(QListView.ViewMode.IconMode)
        self.setMovement(QListView.Movement.Static)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setUniformItemSizes(True)
        self.setIconSize(QSize(64, 64))
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(16)
        self.setFrameShape(QFrame.Shape.NoFrame)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.transparent)
        self.setPalette(palette)

        self.selectionModel().currentChanged.connect(self._on_current_changed)

    def refresh(self) -> None:
        """Re-applies the search filter and repaints with the current style."""
        state = self._model.state
        names = [
            name
            for name in _IconLibrary.get_available_icons(state.style)
            if state.search_text in name
        ]
        if names != self._model.stringList():
            self._model.setStringList(names)
        self.viewport().update()

    def resizeEvent(self, event: QResizeEvent) -> None:
        scrollbar = self.verticalScrollBar().sizeHint().width()
        width = self.contentsRect().width() - scrollbar - 1
        columns = max(1, width // CELL_SIZE)
        self.setGridSize(QSize(width // columns, CELL_SIZE))
        super().resizeEvent(event)

    def _on_current_changed(self, current: QModelIndex) -> None:
        if current.isValid():
            self.iconSelected.emit(current.data())
