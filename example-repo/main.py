from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from orm import Base, User
from dao import UserDAO
from repo import SqlAlchemyUserRepository, InMemoryUserRepository
from biz import register_user_flow, rename_user_flow

# -------------------------
# Demo usage (MySQL)
# -------------------------
def demo_with_mysql():
    print("=== demo using SQLAlchemy repository (MySQL) ===")

    # SQLAlchemy engine for MySQL using pymysql driver
    # note: charset=utf8mb4 recommended for unicode
    MYSQL_URL = "mysql+pymysql://root:Br4v02009@127.0.0.1/repo_demo?charset=utf8mb4"
    engine = create_engine(MYSQL_URL, echo=False, future=True)

    # Create tables (if they don't exist)
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    # Use a session for DAO demonstration
    s = SessionLocal()

    # show DAO usage (direct persistence helper)
    print("\n-- DAO example (shows lower-level API) --")
    dao = UserDAO(s)
    john_id = dao.insert("john", "john@example.com")
    print("DAO inserted john id:", john_id)
    orm_obj = dao.get_by_id(john_id)
    print("DAO get:", orm_obj.username, orm_obj.email)
    dao.update_email(john_id, "john@school.edu")
    orm2 = dao.get_by_id(john_id)
    print("DAO after update email:", orm2.username, orm2.email)

    # show Repository usage (business logic talks to repo interface)
    print("\n-- Repository example (clean domain model, swappable impl) --")
    s2 = SessionLocal()
    repo = SqlAlchemyUserRepository(s2)
    doe = register_user_flow(repo, "Doe", "doe@example.com")
    print("Registered via repo:", doe)
    all_users = repo.list_all()
    print("Repo list_all:", all_users)
    renamed = rename_user_flow(repo, doe.id, "robert")
    print("Renamed:", renamed)

    # Close sessions
    s.close()
    s2.close()

def demo_with_inmemory_repo():
    print("\n=== demo using InMemory repository ===")
    repo = InMemoryUserRepository()
    john = register_user_flow(repo, "john", "john@example.com")
    print("InMemory added:", john)
    print("List:", repo.list_all())
    # If your User dataclass is in orm.py or elsewhere import it accordingly.
    # from orm import User
    repo.update(User(id=john.id, username="ali", email=john.email))
    print("After update:", repo.get(john.id))

if __name__ == "__main__":
    demo_with_mysql()
    demo_with_inmemory_repo()
