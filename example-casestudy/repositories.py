"""Console and Flask choose an implementation with the same public methods."""
from config import enabled
from prepared_sql import PreparedRepository
from raw_sql import RawRepository
from orm_repository import ORMRepository

MODES = ('raw', 'prepared', 'orm')


def get_repository(mode):
    if mode not in MODES:
        raise ValueError('Mode must be raw, prepared or orm.')
    if mode == 'raw' and not enabled('ALLOW_UNSAFE_SQL'):
        raise ValueError('Raw demo disabled. Set ALLOW_UNSAFE_SQL=true in the local .env.')
    return {'raw': RawRepository, 'prepared': PreparedRepository, 'orm': ORMRepository}[mode]()
