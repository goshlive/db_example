from sqlalchemy.orm import Session as SASession
from typing import Optional
from orm import UserORM

# -------------------------
# DAO example
# -------------------------
# DAO often exposes persistence-oriented operations (CRUD) and may leak SQLAlchemy/session details
class UserDAO:
    def __init__(self, session: SASession):
        self.session = session

    def insert(self, username: str, email: str) -> int:
        # returns generated id
        user = UserORM(username=username, email=email)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user.id

    def update_email(self, user_id: int, new_email: str) -> bool:
        user = self.session.query(UserORM).get(user_id)
        if not user:
            return False
        user.email = new_email
        self.session.commit()
        return True

    def get_by_id(self, user_id: int) -> Optional[UserORM]:
        return self.session.query(UserORM).get(user_id)

    def delete(self, user_id: int) -> bool:
        user = self.session.query(UserORM).get(user_id)
        if not user:
            return False
        self.session.delete(user)
        self.session.commit()
        return True