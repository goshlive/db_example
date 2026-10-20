"""DTOs contain data only. They do not execute SQL or hold a database connection."""
from dataclasses import asdict, dataclass, is_dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class CustomerDTO:
    customer_id: str
    customer_name: str


@dataclass(frozen=True)
class CustomerOrderDTO:
    customer_id: str
    customer_name: str
    order_id: str
    order_date: date


@dataclass(frozen=True)
class OrderLineDTO:
    order_id: str
    menu_item_id: str
    menu_item_name: str
    quantity: int
    unit_price_charged: Decimal
    line_amount: Decimal


def to_plain(value):
    """Create JSON-friendly data without losing decimal currency precision."""
    if is_dataclass(value):
        return to_plain(asdict(value))
    if isinstance(value, dict):
        return {key: to_plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_plain(item) for item in value]
    if isinstance(value, (date, Decimal)):
        return str(value)
    return value
