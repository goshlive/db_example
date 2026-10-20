"""Optional: load the guide's sample into existing EMPTY tables. No DDL or deletion."""
from db import cursor_scope


def main():
    with cursor_scope(prepared=True, write=True) as cursor:
        # Constant, developer-controlled table names are not user input.
        for table in ('CUSTOMER', 'MENU_ITEM', 'CUSTOMER_ORDER', 'ORDER_ITEM'):
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            if cursor.fetchall()[0][0]:
                raise ValueError('Refusing to seed: all four tables must be empty.')
        cursor.executemany('INSERT INTO CUSTOMER (CustomerID, CustomerName) VALUES (%s, %s)',
                           [('C01', 'Made'), ('C02', 'Ayu')])
        cursor.executemany('INSERT INTO MENU_ITEM (MenuItemID, MenuItemName) VALUES (%s, %s)',
                           [('M01', 'Fried Rice'), ('M02', 'Iced Tea')])
        cursor.executemany('INSERT INTO CUSTOMER_ORDER (OrderID, OrderDate, CustomerID) '
                           'VALUES (%s, %s, %s)',
                           [('O101', '2026-10-01', 'C01'), ('O102', '2026-10-01', 'C02'),
                            ('O103', '2026-10-02', 'C01')])
        cursor.executemany('INSERT INTO ORDER_ITEM '
                           '(OrderID, MenuItemID, Quantity, UnitPriceCharged) VALUES (%s, %s, %s, %s)',
                           [('O101', 'M01', 2, 25000), ('O101', 'M02', 1, 8000),
                            ('O102', 'M02', 2, 8000), ('O103', 'M01', 1, 27000)])
    print('Sample committed. No database or table was created.')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        raise SystemExit(f'Sample not loaded: {type(error).__name__}: {error}')
