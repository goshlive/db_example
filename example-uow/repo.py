# repo.py
from models import Account

class AccountRepository:
    def __init__(self, session):
        self.session = session

    def get(self, account_id):
        return self.session.query(Account).get(account_id)

    def list_all(self):
        return self.session.query(Account).all()

    def debit(self, account_id, amount_cents):
        """Subtract amount from account. Raises ValueError if insufficient funds."""
        acc = self.get(account_id)
        if acc is None:
            raise ValueError(f"Account {account_id} not found")
        if acc.balance_cents < amount_cents:
            raise ValueError(f"Insufficient funds in account {account_id}")
        acc.balance_cents -= amount_cents
        # no commit here; UnitOfWork controls transaction

    def credit(self, account_id, amount_cents):
        acc = self.get(account_id)
        if acc is None:
            raise ValueError(f"Account {account_id} not found")
        acc.balance_cents += amount_cents

    def transfer(self, from_id, to_id, amount_cents):
        """Helper that performs debit then credit in same session."""
        self.debit(from_id, amount_cents)
        self.credit(to_id, amount_cents)
