"""Same repository operations as cursor versions, implemented with ORM objects."""
from functools import lru_cache
from sqlalchemy import create_engine, select
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from config import database_config, enabled
from dto import CustomerDTO, CustomerOrderDTO, OrderLineDTO
from models import Customer, CustomerOrder, MenuItem, OrderItem


@lru_cache(maxsize=1)
def session_factory():
    config = database_config()
    url = URL.create(
        'mysql+mysqlconnector', username=config['user'], password=config['password'],
        host=config['host'], port=config['port'], database=config['database'],
        query={'charset': 'utf8mb4'},
    )
    # The engine/pool can be reused. A Session is created separately per operation.
    engine = create_engine(
        url, echo=enabled('SQL_ECHO'), pool_pre_ping=True,
        connect_args={'use_pure': True, 'connection_timeout': 5},
    )
    return sessionmaker(bind=engine)


class ORMRepository:
    def __init__(self, sessions=None):
        self.sessions = sessions if sessions is not None else session_factory()

    def list_customers(self):
        with self.sessions() as session:
            customers = session.scalars(select(Customer).order_by(Customer.customer_id)).all()
            return [CustomerDTO(c.customer_id, c.customer_name) for c in customers]

    def get_customer(self, customer_id):
        with self.sessions() as session:
            customer = session.get(Customer, customer_id)
            # Return a DTO while the session is open, not a lazy-loading ORM object.
            return CustomerDTO(customer.customer_id, customer.customer_name) if customer else None

    def create_customer(self, customer):
        # begin() commits on success, rolls back on error and closes the session.
        with self.sessions.begin() as session:
            session.add(Customer(
                customer_id=customer.customer_id, customer_name=customer.customer_name
            ))
        return customer

    def update_customer(self, customer_id, new_name):
        with self.sessions.begin() as session:
            customer = session.get(Customer, customer_id)
            if customer is None:
                return 0
            customer.customer_name = new_name
            # Dirty checking sends UPDATE when the transaction is flushed/committed.
            return 1

    def delete_customer(self, customer_id):
        with self.sessions.begin() as session:
            customer = session.get(Customer, customer_id)
            if customer is None:
                return 0
            session.delete(customer)
            return 1

    def search_customers(self, name):
        with self.sessions() as session:
            # ORM expressions bind values. Never build text(f'...{input}...').
            statement = select(Customer).where(
                Customer.customer_name == name
            ).order_by(Customer.customer_id)
            return [CustomerDTO(c.customer_id, c.customer_name)
                    for c in session.scalars(statement).all()]

    def customer_orders(self, customer_id):
        with self.sessions() as session:
            statement = (
                select(Customer.customer_id, Customer.customer_name,
                       CustomerOrder.order_id, CustomerOrder.order_date)
                .select_from(Customer)
                .join(Customer.orders)
                .where(Customer.customer_id == customer_id)
                .order_by(CustomerOrder.order_id)
            )
            return [CustomerOrderDTO(*row) for row in session.execute(statement).all()]

    def order_details(self, order_id):
        with self.sessions() as session:
            statement = (
                select(CustomerOrder.order_id, MenuItem.menu_item_id,
                       MenuItem.menu_item_name, OrderItem.quantity,
                       OrderItem.unit_price_charged,
                       (OrderItem.quantity * OrderItem.unit_price_charged).label('LineAmount'))
                .select_from(CustomerOrder)
                .join(CustomerOrder.items)
                .join(OrderItem.menu_item)
                .where(CustomerOrder.order_id == order_id)
                .order_by(MenuItem.menu_item_id)
            )
            return [OrderLineDTO(*row) for row in session.execute(statement).all()]
