from sqlalchemy import select

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username, User.deleted_at.is_(None))
        return self.session.execute(stmt).scalar_one_or_none()
