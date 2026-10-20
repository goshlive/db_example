"""Deliberately unsafe string interpolation. Local teaching demonstration only."""
from db import cursor_scope
from dto import CustomerDTO, CustomerOrderDTO, OrderLineDTO


class RawRepository:
    def list_customers(self):
        with cursor_scope() as cursor:
            cursor.execute('SELECT CustomerID, CustomerName FROM CUSTOMER ORDER BY CustomerID')
            return [CustomerDTO(*row) for row in cursor.fetchall()]

    def get_customer(self, customer_id):
        with cursor_scope() as cursor:
            # UNSAFE: input becomes part of SQL syntax, including quotes and operators.
            cursor.execute(
                'SELECT CustomerID, CustomerName FROM CUSTOMER '
                f"WHERE CustomerID = '{customer_id}'"
            )
            rows = cursor.fetchall()
            return CustomerDTO(*rows[0]) if rows else None

    def create_customer(self, customer):
        with cursor_scope(write=True) as cursor:
            # UNSAFE: a legitimate apostrophe can already break this statement.
            cursor.execute(
                'INSERT INTO CUSTOMER (CustomerID, CustomerName) '
                f"VALUES ('{customer.customer_id}', '{customer.customer_name}')"
            )
        return customer

    def update_customer(self, customer_id, new_name):
        with cursor_scope(write=True) as cursor:
            # UNSAFE: never use this pattern with real application input.
            cursor.execute(
                f"UPDATE CUSTOMER SET CustomerName = '{new_name}' "
                f"WHERE CustomerID = '{customer_id}'"
            )
            return cursor.rowcount

    def delete_customer(self, customer_id):
        with cursor_scope(write=True) as cursor:
            cursor.execute(f"DELETE FROM CUSTOMER WHERE CustomerID = '{customer_id}'")
            return cursor.rowcount

    def search_customers(self, name):
        with cursor_scope() as cursor:
            # The SELECT-only injection demonstration calls this exact method.
            cursor.execute(
                'SELECT CustomerID, CustomerName FROM CUSTOMER '
                f"WHERE CustomerName = '{name}' ORDER BY CustomerID"
            )
            return [CustomerDTO(*row) for row in cursor.fetchall()]

    def customer_orders(self, customer_id):
        with cursor_scope() as cursor:
            # 1-N: the FK on CUSTOMER_ORDER matches its parent customer's PK.
            cursor.execute(f"""
                SELECT c.CustomerID, c.CustomerName, o.OrderID, o.OrderDate
                FROM CUSTOMER AS c
                JOIN CUSTOMER_ORDER AS o ON o.CustomerID = c.CustomerID
                WHERE c.CustomerID = '{customer_id}'
                ORDER BY o.OrderID
            """)
            return [CustomerOrderDTO(*row) for row in cursor.fetchall()]

    def order_details(self, order_id):
        with cursor_scope() as cursor:
            # M-N: ORDER_ITEM stores both parent IDs and the relationship's facts.
            cursor.execute(f"""
                SELECT o.OrderID, m.MenuItemID, m.MenuItemName,
                       i.Quantity, i.UnitPriceCharged,
                       i.Quantity * i.UnitPriceCharged AS LineAmount
                FROM CUSTOMER_ORDER AS o
                JOIN ORDER_ITEM AS i ON i.OrderID = o.OrderID
                JOIN MENU_ITEM AS m ON m.MenuItemID = i.MenuItemID
                WHERE o.OrderID = '{order_id}'
                ORDER BY m.MenuItemID
            """)
            return [OrderLineDTO(*row) for row in cursor.fetchall()]
