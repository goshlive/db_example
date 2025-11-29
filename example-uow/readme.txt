Install modules:
pip install pika sqlalchemy pymysql cryptography

Init DB:
CREATE DATABASE uow_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
OR:
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS uow_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"


Run:
python main.py


EXAMPLE OUTPUT:
--- Balances (initial) ---
Account 1 (Alice): 100.00
Account 2 (Bob): 50.00
------------------------

Demo: successful transfer
  (inside tx) after transfer, balances:
--- Balances (inside tx) ---
Account 1 (Alice): 75.00
Account 2 (Bob): 75.00
------------------------

--- Balances (after commit) ---
Account 1 (Alice): 75.00
Account 2 (Bob): 75.00
------------------------

Demo: failing transfer (simulate error after debit)
  (inside tx) after debit, balances:
--- Balances (inside tx - after debit) ---
Account 1 (Alice): 45.00
Account 2 (Bob): 105.00
------------------------

  Caught exception: Simulated crash before credit
--- Balances (after rollback) ---
Account 1 (Alice): 75.00
Account 2 (Bob): 75.00
------------------------

