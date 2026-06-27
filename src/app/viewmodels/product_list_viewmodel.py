"""Mahsulotlar ro'yxati sahifasi uchun ViewModel: qidiruv, yaratish, tahrirlash, o'chirish."""

from collections.abc import Sequence

from PySide6.QtCore import Signal

from app.models.product import Product
from app.services.product_service import ProductService
from app.viewmodels.base_viewmodel import BaseViewModel


class ProductListViewModel(BaseViewModel):
    products_changed = Signal(list)

    def __init__(self, service: ProductService | None = None) -> None:
        super().__init__()
        self._service = service or ProductService()
        self._products: Sequence[Product] = []

    @property
    def products(self) -> Sequence[Product]:
        return self._products

    def load(self, query: str = "") -> None:
        def action() -> None:
            self._products = self._service.search(query) if query.strip() else self._service.list(limit=200)
            self.products_changed.emit(list(self._products))

        self.run_safely(action)

    def create(self, *, name: str, sku: str | None, unit: str, description: str | None) -> bool:
        def action() -> None:
            self._service.create(name=name, sku=sku, unit=unit, description=description)
            self.load()

        return self.run_safely(action)

    def update(
        self,
        product_id: int,
        *,
        name: str,
        sku: str | None,
        unit: str,
        description: str | None,
        is_active: bool,
    ) -> bool:
        def action() -> None:
            self._service.update(
                product_id, name=name, sku=sku, unit=unit, description=description, is_active=is_active
            )
            self.load()

        return self.run_safely(action)

    def delete(self, product_id: int) -> bool:
        def action() -> None:
            self._service.soft_delete(product_id)
            self.load()

        return self.run_safely(action)
