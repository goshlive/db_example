"""Hand-written SQL with server-side prepared statements and separate values."""
from db import cursor_scope
from dto import CustomerDTO, CustomerOrderDTO, OrderLineDTO


class PreparedRepository:
    def list_customers(self):
        with cursor_scope(prepared=True) as cursor:
            cursor.execute('SELECT CustomerID, CustomerName FROM CUSTOMER ORDER BY CustomerID')
            return [CustomerDTO(*row) for row in cursor.fetchall()]

    def get_customer(self, customer_id):
        with cursor_scope(prepared=True) as cursor:
            # Do not quote %s. The driver binds a value, not SQL syntax.
            cursor.execute(
                'SELECT CustomerID, CustomerName FROM CUSTOMER WHERE CustomerID = %s',
                (customer_id,),  # A one-element tuple needs the comma.
            )
            rows = cursor.fetchall()
            return CustomerDTO(*rows[0]) if rows else None

    def create_customer(self, customer):
        with cursor_scope(prepared=True, write=True) as cursor:
            cursor.execute(
                'INSERT INTO CUSTOMER (CustomerID, CustomerName) VALUES (%s, %s)',
                (customer.customer_id, customer.customer_name),
            )
        return customer

    def update_customer(self, customer_id, new_name):
        with cursor_scope(prepared=True, write=True) as cursor:
            cursor.execute(
                'UPDATE CUSTOMER SET CustomerName = %s WHERE CustomerID = %s',
                (new_name, customer_id),
            )
            return cursor.rowcount

    def delete_customer(self, customer_id):
        with cursor_scope(prepared=True, write=True) as cursor:
            cursor.execute('DELETE FROM CUSTOMER WHERE CustomerID = %s', (customer_id,))
            return cursor.rowcount

    def search_customers(self, name):
        with cursor_scope(prepared=True) as cursor:
            # Apostrophes and injection payloads remain ordinary search values.
            cursor.execute(
                'SELECT CustomerID, CustomerName FROM CUSTOMER '
                'WHERE CustomerName = %s ORDER BY CustomerID',
                (name,),
            )
            return [CustomerDTO(*row) for row in cursor.fetchall()]

    def customer_orders(self, customer_id):
        with cursor_scope(prepared=True) as cursor:
            # 1-N remains the same join. Only the input handling changes.
            cursor.execute("""
                SELECT c.CustomerID, c.CustomerName, o.OrderID, o.OrderDate
                FROM CUSTOMER AS c
                JOIN CUSTOMER_ORDER AS o ON o.CustomerID = c.CustomerID
                WHERE c.CustomerID = %s
                ORDER BY o.OrderID
            """, (customer_id,))
            return [CustomerOrderDTO(*row) for row in cursor.fetchall()]

    def order_details(self, order_id):
        with cursor_scope(prepared=True) as cursor:
            # The complete ORDER_ITEM pair identifies one purchased occurrence.
            cursor.execute("""
                SELECT o.OrderID, m.MenuItemID, m.MenuItemName,
                       i.Quantity, i.UnitPriceCharged,
                       i.Quantity * i.UnitPriceCharged AS LineAmount
                FROM CUSTOMER_ORDER AS o
                JOIN ORDER_ITEM AS i ON i.OrderID = o.OrderID
                JOIN MENU_ITEM AS m ON m.MenuItemID = i.MenuItemID
                WHERE o.OrderID = %s
                ORDER BY m.MenuItemID
            """, (order_id,))
            return [OrderLineDTO(*row) for row in cursor.fetchall()]
