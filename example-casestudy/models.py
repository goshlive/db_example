"""Map existing tables. Importing this file never creates or changes a table."""
from datetime import date
from decimal import Decimal
from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = 'CUSTOMER'
    # Left: Python attribute. Quoted name: existing database column.
    customer_id: Mapped[str] = mapped_column('CustomerID', String(10), primary_key=True)
    customer_name: Mapped[str] = mapped_column('CustomerName', String(100), nullable=False)
    # One customer -> a collection of orders. FK ownership is on CustomerOrder.
    # Let the existing database FK reject deletion; do not null the child FKs.
    orders: Mapped[list['CustomerOrder']] = relationship(
        back_populates='customer', passive_deletes='all'
    )


class CustomerOrder(Base):
    __tablename__ = 'CUSTOMER_ORDER'
    order_id: Mapped[str] = mapped_column('OrderID', String(10), primary_key=True)
    order_date: Mapped[date] = mapped_column('OrderDate', Date, nullable=False)
    customer_id: Mapped[str] = mapped_column(
        'CustomerID', ForeignKey('CUSTOMER.CustomerID'), nullable=False
    )
    customer: Mapped['Customer'] = relationship(back_populates='orders')
    items: Mapped[list['OrderItem']] = relationship(back_populates='order')


class MenuItem(Base):
    __tablename__ = 'MENU_ITEM'
    menu_item_id: Mapped[str] = mapped_column('MenuItemID', String(10), primary_key=True)
    menu_item_name: Mapped[str] = mapped_column('MenuItemName', String(100), nullable=False)
    order_lines: Mapped[list['OrderItem']] = relationship(back_populates='menu_item')


class OrderItem(Base):
    __tablename__ = 'ORDER_ITEM'
    __table_args__ = (
        CheckConstraint('Quantity > 0', name='ck_quantity'),
        CheckConstraint('UnitPriceCharged >= 0', name='ck_price'),
    )
    # These two attributes form ONE composite primary key.
    order_id: Mapped[str] = mapped_column(
        'OrderID', ForeignKey('CUSTOMER_ORDER.OrderID'), primary_key=True
    )
    menu_item_id: Mapped[str] = mapped_column(
        'MenuItemID', ForeignKey('MENU_ITEM.MenuItemID'), primary_key=True
    )
    quantity: Mapped[int] = mapped_column('Quantity', Integer, nullable=False)
    unit_price_charged: Mapped[Decimal] = mapped_column(
        'UnitPriceCharged', Numeric(12, 2), nullable=False
    )
    # Association object: the M-N bridge carries quantity and historical price.
    order: Mapped['CustomerOrder'] = relationship(back_populates='items')
    menu_item: Mapped['MenuItem'] = relationship(back_populates='order_lines')
