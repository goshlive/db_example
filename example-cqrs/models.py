# models.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# Adjust this URL for your MySQL server
MYSQL_URL = "mysql+pymysql://root:Br4v02009@127.0.0.1/cqrs_demo?charset=utf8mb4"

# Engine / Session shared by producer & consumer
engine = create_engine(MYSQL_URL, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Write model (normalized, transactional)
class UserWrite(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), nullable=False)

# Read model (denormalized, optimized for queries)
class UserView(Base):
    __tablename__ = "user_views"
    id = Column(Integer, primary_key=True)  # same id as write model
    username = Column(String(100))
    email = Column(String(200))
    display_name = Column(String(200))

def init_db():
    # Create DB tables if missing
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    print("DB tables created (if not existed).")
