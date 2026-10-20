"""One connection and cursor per repository operation; never share a live cursor."""
from contextlib import contextmanager
import mysql.connector
from config import database_config


@contextmanager
def cursor_scope(*, prepared=False, write=False):
    connection = mysql.connector.connect(
        **database_config(), autocommit=False, use_pure=True,
        connection_timeout=5,
    )
    cursor = None
    try:
        # prepared=True uses the driver's prepared-statement cursor.
        cursor = connection.cursor(prepared=prepared)
        yield cursor
        if write:
            connection.commit()
        else:
            # End the read transaction before returning the connection.
            connection.rollback()
    except Exception:
        connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()
