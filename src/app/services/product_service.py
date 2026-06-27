"""Mahsulotlar bilan bog'liq biznes qoidalari: SKU noyobligi."""

from collections.abc import Sequence

from app.core.exceptions import DuplicateError
from app.database.session import session_scope
from app.models.product import Product
from app.repositories.product_repository import ProductRepository


class ProductService:
    def create(
        self,
        *,
        name: str,
        sku: str | None = None,
        unit: str = "kg",
        description: str | None = None,
    ) -> Product:
        with session_scope() as session:
            repo = ProductRepository(session)
            if sku and repo.get_by_sku(sku) is not None:
                raise DuplicateError("Product", "sku", sku)
            return repo.add(Product(name=name, sku=sku, unit=unit, description=description))

    def update(
        self,
        product_id: int,
        *,
        name: str,
        sku: str | None,
        unit: str,
        description: str | None,
        is_active: bool,
    ) -> Product:
        with session_scope() as session:
            repo = ProductRepository(session)
            product = repo.get_by_id_or_raise(product_id)

            if sku and sku != product.sku:
                existing = repo.get_by_sku(sku)
                if existing is not None and existing.id != product_id:
                    raise DuplicateError("Product", "sku", sku)

            product.name = name
            product.sku = sku
            product.unit = unit
            product.description = description
            product.is_active = is_active
            session.flush()
            return product

    def soft_delete(self, product_id: int) -> None:
        with session_scope() as session:
            repo = ProductRepository(session)
            product = repo.get_by_id_or_raise(product_id)
            repo.soft_delete(product)

    def get(self, product_id: int) -> Product:
        with session_scope() as session:
            return ProductRepository(session).get_by_id_or_raise(product_id)

    def list(self, *, limit: int = 50, offset: int = 0) -> Sequence[Product]:
        with session_scope() as session:
            return ProductRepository(session).list(limit=limit, offset=offset)

    def search(self, query: str, *, limit: int = 20) -> Sequence[Product]:
        with session_scope() as session:
            return ProductRepository(session).search_by_name(query, limit=limit)
