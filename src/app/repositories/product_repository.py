from collections.abc import Sequence

from sqlalchemy import select

from app.models.product import Product
from app.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    model = Product

    def get_by_sku(self, sku: str) -> Product | None:
        stmt = select(Product).where(Product.sku == sku, Product.deleted_at.is_(None))
        return self.session.execute(stmt).scalar_one_or_none()

    def search_by_name(self, query: str, *, limit: int = 20) -> Sequence[Product]:
        stmt = (
            select(Product)
            .where(Product.name.ilike(f"%{query}%"), Product.deleted_at.is_(None))
            .order_by(Product.name)
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()
