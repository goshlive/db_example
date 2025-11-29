# main.py
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import init_db, seed_data, Account
from repo import AccountRepository
from uow import UnitOfWork

# SQLAlchemy engine
MYSQL_URL = "mysql+pymysql://root:Br4v02009@127.0.0.1/uow_demo?charset=utf8mb4"
engine = create_engine(MYSQL_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)

def print_balances(session, label=""):
    accounts = session.query(Account).order_by(Account.id).all()
    print("--- Balances", label, "---")
    for a in accounts:
        print(f"Account {a.id} ({a.owner}): {a.balance_cents/100:.2f}")
    print("------------------------\n")

def demo_successful_transfer(a_from, a_to, amount_cents):
    print("Demo: successful transfer")
    # Use UnitOfWork: commit at end
    with UnitOfWork(SessionLocal) as session:
        repo = AccountRepository(session)
        repo.transfer(a_from, a_to, amount_cents)
        # optionally inspect inside transaction:
        print("  (inside tx) after transfer, balances:")
        print_balances(session, label="(inside tx)")
    # committed
    # open a fresh session to show final state
    s = SessionLocal()
    print_balances(s, label="(after commit)")
    s.close()

def demo_failing_transfer(a_from, a_to, amount_cents):
    print("Demo: failing transfer (simulate error after debit)")
    try:
        with UnitOfWork(SessionLocal) as session:
            repo = AccountRepository(session)
            # perform debit
            repo.debit(a_from, amount_cents)
            print("  (inside tx) after debit, balances:")
            print_balances(session, label="(inside tx - after debit)")
            # simulate an error before credit (e.g., network / app bug)
            raise RuntimeError("Simulated crash before credit")
            # never reached:
            repo.credit(a_to, amount_cents)
    except Exception as e:
        print("  Caught exception:", e)
    # after roll back, fresh session shows original balances unchanged
    s = SessionLocal()
    print_balances(s, label="(after rollback)")
    s.close()

def main():
    # create tables if needed
    init_db(engine)

    # seed initial data if table empty
    s = SessionLocal()
    ids = seed_data(s)
    # print initial balances
    print_balances(s, label="(initial)")
    s.close()

    a_from, a_to = ids[0], ids[1]
    amount = 2500  # cents = 25.00

    demo_successful_transfer(a_from, a_to, amount)

    # wait briefly to separate demos
    time.sleep(1)

    # failing transfer: try to transfer more than available or simulate crash
    amount = 3000  # cents = 30.00
    demo_failing_transfer(a_from, a_to, amount)

    # wait briefly to separate demos
    time.sleep(1)

    demo_successful_transfer(a_from, a_to, amount)

if __name__ == "__main__":
    main()
