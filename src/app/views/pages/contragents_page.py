"""Kontragentlar ro'yxati: qidiruv, qo'shish, tahrirlash, o'chirish — MVVM namunaviy modul."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from app.models.contragent import Contragent
from app.viewmodels.contragent_list_viewmodel import ContragentListViewModel
from app.views.dialogs.contragent_detail_dialog import ContragentDetailDialog
from app.views.dialogs.contragent_form_dialog import ContragentFormDialog

_COLUMNS = ("Nomi", "INN", "Telefon", "Manzil", "Holati")


class ContragentsPage(QWidget):
    def __init__(self, view_model: ContragentListViewModel | None = None, parent=None) -> None:
        super().__init__(parent)
        self._view_model = view_model or ContragentListViewModel()
        self._view_model.contragents_changed.connect(self._render_rows)
        self._view_model.error_occurred.connect(self._show_error)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Kontragent nomi bo'yicha qidirish...")
        self._search_input.textChanged.connect(self._on_search_changed)

        add_button = QPushButton(" Yangi kontragent")
        add_button.setObjectName("PrimaryButton")
        add_button.setIcon(qta.icon("fa5s.plus", color="#FFFFFF"))
        add_button.clicked.connect(self._on_add_clicked)

        edit_button = QPushButton(" Tahrirlash")
        edit_button.setIcon(qta.icon("fa5s.edit"))
        edit_button.clicked.connect(self._on_edit_clicked)

        delete_button = QPushButton(" O'chirish")
        delete_button.setIcon(qta.icon("fa5s.trash-alt"))
        delete_button.clicked.connect(self._on_delete_clicked)

        page_title = QLabel("Kontragentlar")
        page_title.setObjectName("PageTitle")

        toolbar = QHBoxLayout()
        toolbar.addWidget(page_title)
        toolbar.addWidget(self._search_input, stretch=1)
        toolbar.addWidget(edit_button)
        toolbar.addWidget(delete_button)
        toolbar.addWidget(add_button)

        self._table = QTableWidget(0, len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setDefaultSectionSize(38)
        self._table.setShowGrid(False)
        self._table.setFrameShape(QFrame.Shape.NoFrame)
        self._table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._table.horizontalHeader().setHighlightSections(False)
        self._table.setMouseTracking(True)
        self._table.doubleClicked.connect(self._on_row_double_clicked)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        content = QWidget()
        content.setObjectName("ContentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 16, 20, 16)
        content_layout.setSpacing(12)
        content_layout.addLayout(toolbar)
        content_layout.addWidget(self._table)

        outer_layout.addWidget(content)

        self._view_model.load()

    def _on_row_double_clicked(self) -> None:
        contragent = self._selected_contragent()
        if contragent is None:
            return
        dialog = ContragentDetailDialog(contragent.id, parent=self)
        dialog.exec()

    def _on_search_changed(self, text: str) -> None:
        self._view_model.load(text)

    def _on_add_clicked(self) -> None:
        dialog = ContragentFormDialog(parent=self)
        if dialog.exec():
            self._view_model.create(**dialog.values)

    def _on_edit_clicked(self) -> None:
        contragent = self._selected_contragent()
        if contragent is None:
            return
        dialog = ContragentFormDialog(contragent, parent=self)
        if dialog.exec():
            values = dialog.values
            self._view_model.update(
                contragent.id,
                name=values["name"],
                inn=values["inn"],
                phone=values["phone"],
                address=values["address"],
                contact_person=contragent.contact_person,
                notes=contragent.notes,
                is_active=contragent.is_active,
            )

    def _on_delete_clicked(self) -> None:
        contragent = self._selected_contragent()
        if contragent is None:
            return
        confirm = QMessageBox.question(
            self,
            "Tasdiqlash",
            f"'{contragent.name}' kontragentini o'chirishni tasdiqlaysizmi?",
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._view_model.delete(contragent.id)

    def _selected_contragent(self) -> Contragent | None:
        row = self._table.currentRow()
        if row < 0 or row >= len(self._view_model.contragents):
            return None
        return self._view_model.contragents[row]

    def _render_rows(self, contragents: list[Contragent]) -> None:
        self._table.setRowCount(len(contragents))
        for row, contragent in enumerate(contragents):
            values = (
                contragent.name,
                contragent.inn or "",
                contragent.phone or "",
                contragent.address or "",
                "Faol" if contragent.is_active else "Faol emas",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 4:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._table.setItem(row, column, item)

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Xatolik", message)
