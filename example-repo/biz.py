from repo import UserRepository
from orm import User

# -------------------------
# Small "business logic" example that depends on the abstract repository
# -------------------------
def register_user_flow(repo: UserRepository, username: str, email: str) -> User:
    # business rules: username must be >2 chars, email contains '@' (very simple)
    if len(username) <= 2:
        raise ValueError("username too short")
    if "@" not in email:
        raise ValueError("invalid email")

    user = User(id=None, username=username, email=email)
    new_id = repo.add(user)
    user.id = new_id
    return user

def rename_user_flow(repo: UserRepository, user_id: int, new_username: str) -> User:
    u = repo.get(user_id)
    if not u:
        raise ValueError("user not found")
    u.username = new_username
    if not repo.update(u):
        raise RuntimeError("update failed")
    return u