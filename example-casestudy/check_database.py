"""Read-only checks of the existing schema and expected demonstration records."""
import sys
from db import cursor_scope
from prepared_sql import PreparedRepository

EXPECTED = {'CUSTOMER': {'CustomerID', 'CustomerName'},
            'CUSTOMER_ORDER': {'OrderID', 'OrderDate', 'CustomerID'},
            'MENU_ITEM': {'MenuItemID', 'MenuItemName'},
            'ORDER_ITEM': {'OrderID', 'MenuItemID', 'Quantity', 'UnitPriceCharged'}}


def main():
    try:
        with cursor_scope() as cursor:
            cursor.execute('SELECT DATABASE(), VERSION()')
            print('Connected:', cursor.fetchone())
            cursor.execute('SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS '
                           'WHERE TABLE_SCHEMA = DATABASE()')
            actual = {}
            for table, column in cursor.fetchall():
                actual.setdefault(table, set()).add(column)
            problems = [f'{table}: missing {sorted(columns - actual.get(table, set()))}'
                        for table, columns in EXPECTED.items()
                        if columns - actual.get(table, set())]
            if problems:
                raise ValueError('Schema mismatch. ' + '; '.join(problems))
        print('All four tables and required columns found.')
        repo = PreparedRepository()
        print('Customers:', len(repo.list_customers()))
        print('C01 orders:', len(repo.customer_orders('C01')), '(reference sample: 2)')
        print('O101 items:', len(repo.order_details('O101')), '(reference sample: 2)')
        print('Empty join results are expected if you have not loaded the sample data.')
        return 0
    except Exception as error:
        print(f'Check failed: {type(error).__name__}: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
