from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import AuditMixin, Base


class Product(Base, AuditMixin):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    sku: Mapped[str | None] = mapped_column(String(50), unique=True)
    unit: Mapped[str] = mapped_column(String(20), default="kg", nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name!r}>"
