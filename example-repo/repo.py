from typing import List, Optional, Protocol
from orm import User, UserORM
from sqlalchemy.orm import Session as SASession

# -------------------------
# Repository pattern
# -------------------------
# Define an abstract interface (Protocol) that business code depends on
class UserRepository(Protocol):
    def add(self, user: User) -> int: ...
    def get(self, user_id: int) -> Optional[User]: ...
    def list_all(self) -> List[User]: ...
    def update(self, user: User) -> bool: ...
    def remove(self, user_id: int) -> bool: ...

# SQLAlchemy-based repository implementation
class SqlAlchemyUserRepository:
    def __init__(self, session: SASession):
        self.session = session

    def add(self, user: User) -> int:
        orm = UserORM.from_domain(user)
        self.session.add(orm)
        self.session.commit()
        self.session.refresh(orm)
        return orm.id

    def get(self, user_id: int) -> Optional[User]:
        orm = self.session.query(UserORM).get(user_id)
        return orm.to_domain() if orm else None

    def list_all(self) -> List[User]:
        orms = self.session.query(UserORM).all()
        return [o.to_domain() for o in orms]

    def update(self, user: User) -> bool:
        orm = self.session.query(UserORM).get(user.id)
        if not orm:
            return False
        orm.username = user.username
        orm.email = user.email
        self.session.commit()
        return True

    def remove(self, user_id: int) -> bool:
        orm = self.session.query(UserORM).get(user_id)
        if not orm:
            return False
        self.session.delete(orm)
        self.session.commit()
        return True

# In-memory repository (useful for unit tests / demo swap-out)
class InMemoryUserRepository:
    def __init__(self):
        self._data = {}
        self._next = 1

    def add(self, user: User) -> int:
        user_id = self._next
        self._next += 1
        u = User(id=user_id, username=user.username, email=user.email)
        self._data[user_id] = u
        return user_id

    def get(self, user_id: int) -> Optional[User]:
        return self._data.get(user_id)

    def list_all(self) -> List[User]:
        return list(self._data.values())

    def update(self, user: User) -> bool:
        if user.id not in self._data:
            return False
        self._data[user.id] = user
        return True

    def remove(self, user_id: int) -> bool:
        return self._data.pop(user_id, None) is not None