from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import UserRole
from app.database.base import AuditMixin, Base


class User(Base, AuditMixin):
    """Sync va audit uchun 'kim qildi' ma'lumotini saqlaydi. To'liq autentifikatsiya emas —
    har bir kompyuterda joriy foydalanuvchi Sozlamalar bo'limida tanlanadi."""

    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, length=20), default=UserRole.MANAGER, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"
