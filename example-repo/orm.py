from typing import Optional
from dataclasses import dataclass
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

# -------------------------
# Domain model (pure Python)
# -------------------------
@dataclass
class User:
    id: Optional[int]
    username: str
    email: str

# -------------------------
# SQLAlchemy model
# -------------------------
Base = declarative_base()

class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(200), nullable=False)

    def to_domain(self) -> User:
        return User(id=self.id, username=self.username, email=self.email)

    @staticmethod
    def from_domain(u: User) -> "UserORM":
        # don't set id if None - let DB autogen
        return UserORM(id=u.id, username=u.username, email=u.email)