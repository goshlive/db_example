# models.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner = Column(String(100), nullable=False)
    balance_cents = Column(Integer, nullable=False, default=0)  # store money in cents (integers)

def init_db(engine):
    Base.metadata.create_all(engine)

def seed_data(session):
    # Only insert seed if table empty
    if session.query(Account).count() == 0:
        a1 = Account(owner="Alice", balance_cents=10000)   # 100.00
        a2 = Account(owner="Bob", balance_cents=5000)      # 50.00
        session.add_all([a1, a2])
        session.commit()
        return [a1.id, a2.id]
    else:
        return [a.id for a in session.query(Account).all()]
