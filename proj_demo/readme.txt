Install modules:
pip install sqlalchemy pymysql

Run:
python Test.py


EXAMPLE OUTPUT:
Balance: None
(4, 'Doni', Decimal('200.00'))
(5, 'Sinta', Decimal('150.00'))
(6, 'Ryan', Decimal('300.00'))
(1, 1, 'update_balance', Decimal('-50.00'), datetime.datetime(2025, 11, 30, 6, 48, 2))
(2, 2, 'update_balance', Decimal('50.00'), datetime.datetime(2025, 11, 30, 6, 48, 2))
(3, 1, 'update_balance', Decimal('10.00'), datetime.datetime(2025, 11, 30, 6, 48, 2))